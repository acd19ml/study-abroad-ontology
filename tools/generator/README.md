# 模型 HTML 投影生成器

输入是经校验的模型源与元模型 Schema，输出为[只读交互 HTML](../../generated/ps-model-explorer.html)。页面包括所有模型元素及来源，业务对象关系、命令与规则邻域、状态流转、元模型类型四个视图。数据内嵌，直接打开即可，不需要服务器或联网。

首屏的元素数量、业务对象、关系线和初始属性在生成阶段直接写入 HTML，JavaScript 启动后增强交互。脚本未运行时仍可阅读初始模型；启动异常会在页面顶部显示具体提示，避免无解释的空白。

```sh
python3 tools/generator/render_model.py
python3 tools/generator/render_model.py --check
```

`--check` 根据当前模型、Schema、生成器和模板重算输出；HTML 缺失、源已变而未生成，或生成文件被手动编辑时返回非零。

首选入口是 `generated/ps-model-explorer.html`；原 `generated/ps-model.html` 作为兼容入口由同一生成器写入相同内容，两个入口均纳入一致性检查。内部模板使用 `.html.tpl` 后缀，不作为交付页面。

写出前必须确认全部模板占位符已展开，且最终页面中的 JSON 与本次已验证模型完全一致；检查失败时保留上一份有效产物，防止把未展开模板作为可交互页面交付。

需要持续同步时：

```sh
python3 tools/generator/render_model.py --watch
```

监测到有效模型或模板变化后重新生成；浏览器刷新后读取新快照。模型不合法时保留上一份有效 HTML，并输出错误，不把旧页面误写成最新模型。

## 修改顺序

1. 业务概念、属性、关系、规则、命令或状态名称变更：修改 `model/`。模型源的状态和业务评审约定继续适用。
2. 必要时运行 `python3 tools/checks/sync_model_refs.py --write` 同步来源索引，执行模型校验和对应测试。
3. 运行生成器并执行 `--check`，再刷新页面。禁止直接修改 `generated/ps-model-explorer.html`。
4. 布局或交互变更：修改[模板](templates/model-explorer.html.tpl)或生成器，不借此修改业务含义，然后重新生成。

## 投影边界

- 显式业务边来自 `relation` 元素；其他边来自命令、聚合、规则等模型字段，并在详情标明来源字段。
- 元模型类型中文名来自 Schema 的 `title`；状态中文名来自对象的 `lifecycle.labels`。
- 内联状态、创建起点和分类关系使用投影 ID，不伪装成新建的顶层业务元素或真实学生记录。
- 原始定义、来源文件、版本、源指纹及待评审状态保留在 HTML。页面的坐标等布局信息不会回写模型。
- HTML 不是数据库、业务命令执行器或可直接编辑的业务模型；真实业务副作用不在本投影范围内。

## 检查

```sh
python3 -m unittest discover -s tests/model -p 'test_*.py' -v
python3 -m unittest discover -s tests/generator -p 'test_*.py' -v
```

生成器测试检查源元素和边完整保留、输出确定性、源变更与手改的失同步检测、无效模型不覆盖有效输出。Node.js 可用时，执行真实页面脚本的 DOM 模拟交互检查；它不是浏览器渲染或视觉验收。

测试另用真实 HTML 标记检查脚本启动前的首屏数据；原先只在脚本执行后检查 DOM，未覆盖脚本未执行时的空白路径。具体浏览器的脚本权限、初始化环境和视觉布局仍需与原生浏览器的表现分别确认。

## 打开后没有交互时

确认打开的是 `generated/ps-model-explorer.html`，而不是带数据占位符的 `tools/generator/templates/model-explorer.html.tpl`。模型数据已经包含在生成文件中，不需要额外加载 JSON 或 YAML。

- 顶部初始化提示消失：交互启动成功，可以点击节点或切换视图。
- 顶部一直显示“交互尚未启动”：当前打开方式可能未执行脚本，初始静态模型仍应显示。
- 顶部显示“交互初始化失败”：保留显示的具体错误，用于定位运行环境；不将无数据简单归因于模型源缺失。

如果提示中出现 `@@MODEL_PAYLOAD@@`，读到的是未展开模板内容，不能靠刷新模型数据解决。请使用首选生成入口；若直接打开内部模板，页面会明确提示正确入口，不再直接报 JSON 语法错误。
