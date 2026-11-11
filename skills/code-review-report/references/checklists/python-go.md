# Python / Go 检查清单

## Python

- 可变默认参数：`def f(x=[])`、`def f(x={})`
- 异常：`except:` 裸捕获、`except Exception: pass`、异常信息丢失
- 资源：文件 / 连接 / 锁是否用 `with`
- 并发：GIL 不是万能锁，`asyncio` 中调用阻塞函数、共享状态无锁
- 类型：动态类型导致运行时才发现的错误；`None` 与假值混淆
- 字符串：`%` / `format` / f-string 拼接 SQL、命令注入
- 迭代：遍历中修改列表、迭代器耗尽后继续用
- 时区：`datetime.now()` 无时区、`astimezone` 混用
- 依赖：版本未锁定、导入副作用
- 序列化：`pickle` 反序列化不可信数据、`eval`

## Go

- `err` 是否检查；`_` 丢弃错误
- `defer` 在循环内积累、`defer` 参数提前求值
- goroutine 泄漏：无退出条件的 `for {}`、channel 无人接收
- `context` 是否传递并处理取消
- 并发：map 并发读写、共享变量无锁
- nil：nil map 写入、nil interface 与 nil 指针的判断
- slice：共享底层数组导致意外修改、`append` 后原 slice 变化
- 资源：`resp.Body` 是否关闭、文件句柄是否释放
- 错误包装：是否用 `%w` 保留错误链
- 时间：`time.Now()` 时区、`time.Parse` 布局写错

## Rust

- `unwrap()` / `expect()` 是否用在可能失败的路径上
- 错误是否用 `?` 传播，而不是吞掉或 `panic!`
- 借用检查：不必要的 `clone()`、生命周期标注是否掩盖了所有权问题
- `unsafe` 块是否有明确的安全前提说明
- 并发：`Send` / `Sync` 约束、`Mutex` 死锁、channel 阻塞
- 整数溢出（debug 下 panic、release 下回绕）、`as` 截断
- 切片索引越界、`String` 与 `&str` 混用导致的额外分配
- 异步：`tokio::spawn` 任务泄漏、`select!` 分支取消安全
