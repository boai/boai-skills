# Swift / iOS 检查清单

## 崩溃类（优先看）

- 强解包 `!`：`as!`、`try!`、`array[0]`、`dict["k"]!`、IBOutlet 未连接
- 数组越界：`indices` 与 `count` 混用、删除元素后继续遍历
- 字符串下标：用整数偏移取 `String` 字符
- 类型转换失败、JSON 字段类型与模型不一致
- 主线程访问 UI 以外线程修改 UI
- 递归 / 死锁：`DispatchQueue.main.sync` 在主线程调用
- 除零、`Int` 溢出（`Int.max + 1`）
- 强制解包 Optional 链中间环节为 nil

## 内存与生命周期

- 闭包捕获 `self` 未加 `[weak self]` / `[unowned self]`，尤其是长期持有的回调
- `delegate` 是否 `weak`；`NotificationCenter` 观察者是否移除
- `Timer` 是否 `invalidate()`；`CADisplayLink` 是否暂停
- `Combine` 的 `AnyCancellable` 是否被持有；`sink` 里是否强引用 self
- `URLSession` 回调、`WKNavigationDelegate` 是否造成页面无法释放
- 大循环里是否缺少 `autoreleasepool`
- 单例持有大量数据、缓存无上限

## 线程与并发

- UI 更新是否回到主线程（`DispatchQueue.main.async` / `@MainActor`）
- `@MainActor` 标注是否覆盖所有 UI 入口；跨 actor 访问是否 `await`
- `Sendable` 遵守；可变类跨线程传递
- `Task` 是否在页面销毁时取消；`Task.detached` 是否捕获了不该捕获的状态
- 数据竞争：多线程写同一数组 / 字典 / 属性
- 锁的使用：是否在锁内做耗时操作、是否有嵌套锁死锁风险

## 网络与数据

- 请求失败、超时、取消、重试的处理
- 响应解析失败是否会导致空白页 / 崩溃
- 是否在请求回调里强解包 `response` / `data`
- 分页：重复请求、最后一页、空列表
- 敏感信息是否放 `UserDefaults`（应放 Keychain）
- 日志是否打印 token、手机号、身份证、车架号

## UI 与体验

- `UITableView` / `UICollectionView` cell 复用是否重置状态（`prepareForReuse`）
- `viewDidLoad` / `viewWillAppear` 是否重复添加子视图或重复请求
- 约束冲突、safe area、刘海/灵动岛、横竖屏
- 深色模式颜色是否写死；动态字体是否支持
- 空数据、加载中、失败三种状态是否都有 UI
- 按钮防重复点击；异步操作期间是否禁用
- 键盘遮挡、输入校验、粘贴长文本

## 工程与规范

- 硬编码文案（应走多语言）；硬编码颜色 / 尺寸（应走设计 token）
- 系统版本兼容是否用 `#available`，而不是直接调用新 API
- 权限使用前是否检查并处理拒绝（相机、定位、通知、蓝牙）
- `Info.plist` 权限描述是否齐全，缺少会导致审核被拒 / 崩溃
- ATS 是否被全局关闭；是否允许任意 HTTP
- 循环引用检查工具：Instruments Leaks / Memory Graph
- 新增文件是否加入 target（漏加会导致编译或运行时找不到）
- 资源文件是否加入 Copy Bundle Resources
