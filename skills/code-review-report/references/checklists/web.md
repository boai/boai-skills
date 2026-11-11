# TypeScript / JavaScript / 前端检查清单

- 相等判断：`==` 与 `===` 混用；`NaN`、`null` 与 `undefined` 的判断
- 异步：`await` 漏写、Promise 没有 `catch`、`forEach` 里用 `async` 不等待
- 错误处理：`try/catch` 包不住异步回调；错误被静默吞掉
- 空值：可选链 `?.` 与默认值 `??` 是否覆盖；解构深层对象
- 状态：闭包捕获旧状态（React `useEffect` 依赖缺失）、重复渲染
- 事件：监听器 / 定时器 / 订阅在卸载时是否清理
- 内存：大对象常驻、闭包引用 DOM、缓存无上限
- XSS：`innerHTML`、`dangerouslySetInnerHTML`、`v-html` 是否直接插入用户输入
- 安全：token 存 `localStorage`、URL 参数直接拼进请求、CSRF 防护
- 依赖：新增依赖的必要性、版本锁定、供应链风险
- 数值：浮点精度、`parseInt` 缺基数、大整数精度丢失
- 国际化：硬编码文案、日期/货币格式
- 性能：大列表未虚拟化、重复请求、图片未懒加载
- 兼容性：新 API 在目标浏览器 / WebView 是否支持
