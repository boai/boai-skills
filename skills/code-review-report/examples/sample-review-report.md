# DemoCarApp 代码评审报告

- **评审范围**: `main` → `feature/remote-control`
- **评审时间**: 2026-11-11 18:10
- **变更规模**: 5 个文件 | +98 / -23 行 | 4 次提交
- **评审模式**: 分支对比
- **结论**: ⛔ 暂不可合并

> 一句话总评：这批改动完成了远程空调、车门控制两个主功能，但引入了明文密钥、强解包、空数组越界、静默失败和并发写五类阻断问题，修复前不建议合并或提测。

## 一、问题汇总

| 级别 | 数量 | 说明 |
|------|------|------|
| 🔴 阻断 | 5 | 安全泄露、崩溃、请求永不回调、并发写 |
| 🟠 严重 | 5 | 内存泄漏、主线程 UI、Timer 泄漏、按钮不可见、强解包 |
| 🟡 建议 | 5 | 硬编码文案、未使用参数、业务码未校验等 |
| 🟢 好评 | 3 | 弱引用、错误兜底、文案资源补齐 |

## 二、🔴 阻断问题（必须修复）

### 1. API Token 明文硬编码在源码里

- **位置**: `Sources/Vehicle/DoorService.swift:5`
- **现象**: 访问凭证以字面量写在类属性里，任何拿到仓库或 App 包体的人都能直接提取，进而调用车辆解锁接口。
- **触发条件**: 代码仓库共享、外包/离职交接、App 包被反编译，均可获取该 token。
- **修复建议**: 立即从代码移除并轮换该 token；改为登录后由服务端下发短期凭证，客户端存入 Keychain，请求时按需读取。

### 2. 响应强转 HTTPURLResponse 会崩溃

- **位置**: `Sources/Vehicle/DoorService.swift:19`
- **现象**: `response as! HTTPURLResponse` 在 `response` 为 nil 或不是 HTTP 响应时直接崩溃，车门解锁变成闪退。
- **触发条件**: 请求被代理/中间层拦截返回非 HTTP 响应、系统返回空响应、单元测试使用 mock 响应。
- **修复建议**:

```swift
guard let http = response as? HTTPURLResponse else {
    completion(false)
    return
}
completion(http.statusCode == 200)
```

### 3. 车辆列表为空时数组越界崩溃

- **位置**: `Sources/Vehicle/VehicleListViewController.swift:41`
- **现象**: `vehicles[0]` 在下标 0 不存在时触发 `Fatal error: Index out of range`。
- **触发条件**: 新账号未绑定车辆、列表接口失败、页面刚打开列表尚未加载完成就点击「远程开空调」。
- **修复建议**:

```swift
guard let vehicle = vehicles.first else {
    // 提示「暂无可用车辆」
    return
}
```

同时建议在列表为空时禁用按钮。

### 4. 请求失败时 completion 永不回调，调用方永久等待

- **位置**: `Sources/Network/APIClient.swift:13`（相关：第 9、12 行）
- **现象**: URL 非法、响应体为空、JSON 解析失败三种情况都直接 `return` 或 `try?` 吞掉错误，`completion` 一次都不会执行。调用方的 loading 永远不结束，用户看到的是「一直转圈」。
- **触发条件**: 接口返回非 JSON（网关错误页）、空 body、后端字段变更导致解析失败、URL 含非法字符。
- **修复建议**: 每种失败路径都必须回调，且保留错误信息：

```swift
guard let url = URL(string: urlString) else {
    completion(.failure(URLError(.badURL)))
    return
}
guard let data = data else {
    completion(.failure(URLError(.badServerResponse)))
    return
}
do {
    completion(.success(try JSONDecoder().decode(T.self, from: data)))
} catch {
    completion(.failure(error))
}
```

### 5. 待发指令数组存在并发写，可能崩溃

- **位置**: `Sources/Vehicle/RemoteClimateService.swift:19`
- **现象**: `pendingCommands` 是普通数组，`append` 与 `removeAll` 没有任何同步。多个线程同时写入会破坏数组内部结构，出现 `EXC_BAD_ACCESS` 或数据丢失。
- **触发条件**: 用户快速连点、多个页面同时下发指令、后台任务与主线程同时操作该服务。
- **修复建议**: 用串行队列或锁保护，或把整个服务标记 `@MainActor` 并要求所有调用在主线程；按当前 UI 场景，主线程隔离最简单。

## 三、🟠 严重问题（应当修复）

### 1. 闭包强引用 self，页面无法释放

- **位置**: `Sources/Vehicle/VehicleListViewController.swift:35`
- **现象**: `RemoteClimateService.shared` 持有 `observeState` 传入的闭包，闭包又强引用 VC，形成「单例 → 闭包 → VC」的引用链，页面退出后永不释放，Timer、图片、请求回调都会跟着泄漏。
- **触发条件**: 每次进入车辆列表都会注册一次，页面反复进出时泄漏累积。
- **修复建议**: 使用 `[weak self]`，并在注册前考虑是否覆盖旧 handler。

### 2. UI 在后台线程刷新

- **位置**: `Sources/Vehicle/VehicleListViewController.swift:27`（相关：`Sources/Vehicle/RemoteClimateService.swift:25`）
- **现象**: 本次改动删掉了原来的 `DispatchQueue.main.async`，`reloadData()` 直接在 URLSession 回调线程执行；同时 `onStateChanged` 也在后台线程触发。UIKit 要求主线程操作，轻则界面错乱，重则崩溃。
- **触发条件**: 车辆列表加载完成、远程空调状态回调。
- **修复建议**: 回到主线程再改数据源和刷新 UI，或在 VC 层统一 `@MainActor`。

### 3. Timer 强引用 self，且没有停止入口

- **位置**: `Sources/Network/APIClient.swift:21`
- **现象**: Timer 的闭包强引用 `self`，`APIClient` 又持有 `pollingTimer`，形成循环引用；没有 `deinit`、没有 `stopTokenPolling`，轮询一旦启动就永久运行。
- **触发条件**: 调用 `startTokenPolling()` 后。
- **修复建议**: 闭包用 `[weak self]`，补 `deinit { pollingTimer?.invalidate() }` 和停止方法。

### 4. 「远程开空调」按钮没有布局，实际不可见

- **位置**: `Sources/Vehicle/VehicleListViewController.swift:13`
- **现象**: 按钮只 `addSubview`，没有设置 frame 或约束，默认尺寸为 0，用户看不到也点不到，功能入口实际不存在。
- **触发条件**: 进入车辆列表页。
- **修复建议**: 用 Auto Layout 固定位置和尺寸，或放到导航栏/卡片内。

### 5. URL 强解包，车辆 ID 含特殊字符时崩溃

- **位置**: `Sources/Vehicle/DoorService.swift:9`
- **现象**: `URL(string: urlString)!` 在 `vehicleId` 含空格、中文、`#` 等未转义字符时返回 nil，直接崩溃。
- **触发条件**: 服务端下发的车辆 ID 含非 URL 安全字符，或未来 ID 规则变化。
- **修复建议**: 用 `URLComponents` 拼接并对路径参数做 percent-encoding，再用 `guard let` 处理失败。

## 四、🟡 建议（可选优化）

| # | 位置 | 建议 |
|---|------|------|
| 1 | `Sources/Vehicle/VehicleListViewController.swift:15` | 已补多语言 key，但标题仍写死中文，应改用本地化字符串 |
| 2 | `Sources/Vehicle/VehicleListViewController.swift:35` | `isOn` 参数未使用，说明状态处理不完整，建议接入状态展示或移除参数 |
| 3 | `Sources/Vehicle/DoorService.swift:13` | 只看 HTTP 状态码，未校验响应体里的业务错误码，建议按统一响应结构解析 |
| 4 | `Sources/Vehicle/RemoteClimateService.swift:32` | `pendingCommands` 只在手动取消时清空，成功/失败后未移除，长期运行会持续增长 |
| 5 | `Sources/Vehicle/VehicleListViewController.swift:42` | 温度 24 为魔法数字，建议抽成默认值常量或从车辆配置读取 |

## 五、🟢 做得好的地方

- `Sources/Vehicle/VehicleListViewController.swift:23`：列表请求使用 `[weak self]`，并对失败路径做了日志记录，避免了常见的强引用和静默失败。
- `Sources/Vehicle/DoorService.swift:14`：网络错误时回调 `completion(false)` 并记录日志，调用方不会无限等待。
- `Resources/Localizable.strings:2`：提前补齐了远程控制相关文案 key，为多语言接入打好了基础。

## 六、评审说明

- 本次评审覆盖 5 个文件：`APIClient.swift`、`DoorService.swift`、`RemoteClimateService.swift`、`VehicleListViewController.swift`、`Localizable.strings`。
- 未发生 diff 截断，全部改动已纳入评审。
- 未能确认的点：`ClimateState.temperature` 是否一定随响应返回、车门解锁接口的业务错误码结构，建议作者补充接口文档或在 PR 中说明。
- 本次只评审 `main..feature/remote-control` 引入的问题，仓库其他历史代码未纳入范围。
