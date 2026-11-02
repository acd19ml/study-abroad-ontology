# 元模型与表达约定

本 Schema 依据实践标准第 5.1—5.7 节及附录 A 建立，正式实例位于 `model/contexts/ps/`。

- 每个顶层元素具有 `id/type/name/status/owner/since/refs/context/basis`。`id` 遵守标准前缀和三段格式；`basis` 区分已有业务确认与 Agent 首次结构化提案，不代替 `status`。
- 状态随所属对象内联于 `lifecycle`，用对象 ID 和稳定状态值定位；转换显式引用命令 ID。标准未列独立状态 ID 前缀，本版不擅自增加前缀。该内联方式作为草案表达约定待评审。
- 元模型类型的中文名称保存在 Schema 的 `title`，状态的中文名称保存在 `lifecycle.labels`；展示层从源读取名称，不另存一份业务标签字典。状态名称如有修改，先修改此源定义并重新校验、生成。
- 初建对象的命令用 `transition.creates: true`、空 `allowed_in`，对应 `from: null` 的创建边；普通命令必须列已有前置状态。`to: same` 展开成合法前置状态的自环。
- 关系的 `kind` 是组合、引用或关联。`semantic` 是关系业务含义，不能用它跳过组合不得跨聚合的约束。
- `condition` 是受限表达式树，操作符当前为 `all/any/not/eq/ne/gt/is_null`。业务属性用 `{concept: 对象ID, attribute: 业务属性名}` 引用，禁止混入任意代码、SQL、数据库字段表达式。
- 规则的 `condition` 为真时才命中 `action`。条件缺少绑定资料时为未知，不自动算通过。`flag` 是保留标记继续工作，`escalate` 必须关联人工决策点。
- 单条 `allow` 只表示该条件本身不是阻碍，不覆盖其他规则的 `deny` 或人工决定；多规则仲裁与命令副作用由后续运行时控制层实现。
- 条件中不同对象的具体实例如何绑定，由相应命令参数和关联读取负责；当前校验器只检查定义与假设情景谓词，尚未实现多记录查询、量化绑定或运行时规则调度。
- 命令的 `effects` 是业务后置含义；`preserves` 是必须保持的业务属性引用，供后续实现契约使用。当前检查引用有效，但不假称这些后置条件已经有运行时强制执行器。
- 规范性规则只可使用 `allow/deny/escalate/flag`；人工决策点包括负责人和判断指引。项目数值通过业务记录提供，不在规则里写死某校词数或成绩。
- 角色及命令执行等级先给出保守草案。模型当前均为 `draft`，这些定义不直接授予现有工具对外操作权限。

## Schema 校验实现

Schema 文件采用 JSON Schema 2020-12 写法。本仓库的离线校验器完整执行本文件用到的有限关键字集合：`$ref/$defs/type/enum/pattern/anyOf/properties/required/additionalProperties/items/minItems`；`$schema/$id/title` 为声明或标注。遇到不支持的关键字会报错，不静默跳过。

该实现不宣称支持整个 JSON Schema 标准；更换完整校验库时可继续使用此 Schema。跨元素引用、聚合、状态闭合和规则业务引用由独立语义检查实现。

后续如扩展元模型，先修改 Schema 与检查器，再变更业务源；不在可视化页面中私自新增模型类型。
