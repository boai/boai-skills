# Java / Kotlin 检查清单

- 空指针：`Optional` 使用是否得当，`!!` 是否滥用（Kotlin），返回值可能为 null 未判空
- 集合：遍历中修改集合（`ConcurrentModificationException`）、`HashMap` 并发写
- 并发：线程池是否复用、是否有无界队列、`synchronized` 粒度、`volatile` 缺失
- 资源：流 / 连接 / 游标是否 `try-with-resources` 或 `use {}` 关闭
- 事务：`@Transactional` 是否自调用失效、异常是否被吞导致不回滚
- 数据库：N+1 查询、缺少索引、SQL 拼接注入、分页深翻
- 数值：`BigDecimal` 的 `equals` 与 `compareTo`、金额用 `double`
- 时间：`SimpleDateFormat` 线程不安全、时区、`LocalDateTime` 与 `Date` 混用
- 序列化：字段新增/删除的兼容性、`serialVersionUID`
- 异常：捕获 `Exception` 后不处理、日志只打 `e.getMessage()` 丢失堆栈
- 枚举：`switch` 缺 default、枚举新增值导致老逻辑失效
- 缓存：key 设计、过期时间、缓存穿透/击穿、序列化兼容
- 幂等与重试：消息重复消费、接口重复提交
- 安全：越权（IDOR）、参数校验、日志脱敏、反序列化漏洞
