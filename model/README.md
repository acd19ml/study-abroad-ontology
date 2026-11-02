# PS 业务模型源 v0.1

当前为用户要求优先建立的模型源草案，已从源生成[交互 HTML 投影](../generated/ps-model-explorer.html)。业务含义依据已获整体认可的 PS 发现稿；聚合、状态、命令、执行等级等首次结构化表达仍待评审。所有元素均为 `draft`，未合入、发布或宣称阶段 2 通过。

## 修改入口

- [model.yaml](model.yaml)：文件清单、版本和阶段未决项。
- [meta/model.schema.json](meta/model.schema.json)：机器可读元模型 Schema。
- [contexts/ps/value.yaml](contexts/ps/value.yaml)：上下文、目标与待确认指标。
- [contexts/ps/objects.yaml](contexts/ps/objects.yaml)：业务对象、属性、关系与内联状态定义。
- [contexts/ps/aggregates.yaml](contexts/ps/aggregates.yaml)：聚合、命令、事件和不变量。
- [contexts/ps/rules.yaml](contexts/ps/rules.yaml)：条件、约束强度、动作和人工决策点。
- [contexts/ps/roles.yaml](contexts/ps/roles.yaml)：顾问、学生和业务 AI 的命令职责。
- [contexts/ps/policies.yaml](contexts/ps/policies.yaml)：当前为空；仅确认变化影响范围，不擅自定义自动传播策略及期限。
- [contexts/ps/mappings.yaml](contexts/ps/mappings.yaml)：当前为空；数据库表、接口等实现映射后置。

后续模型变更直接修改这些源文件并校验。将来生成的 HTML、图谱、代码及规则投影不成为第二个修改入口。

当前 HTML 的生成与同步命令：

```sh
python3 tools/generator/render_model.py
python3 tools/generator/render_model.py --check
```

生成器先校验模型，再嵌入数据；源或页面失同步会被 `--check` 检测。持续同步和模板说明见[生成器文档](../tools/generator/README.md)。

## 三个层次

元模型 Schema 规定对象、关系、规则、命令等元素的语法；`contexts/ps` 定义 PS 业务概念和约束；真实学生、学校课程、要求数值、稿件版本是未来运行时业务记录，不塞进当前定义文件。假设数据仅放在 `tests/model/`。

规则使用 `normative` / `reference`，关系使用标准规定的 `composition` / `reference` / `association`，`semantic` 补充具体业务含义。旧框架中的价值流、能力、特性等类型未被直接混入本元模型，见[评审提案](../docs/proposals/ps-model-v0.1.md)。

## 校验

环境：Python 3.10+、PyYAML；依赖清单见 [requirements.txt](../tools/checks/requirements.txt)。当前环境已提供 PyYAML 6.0.3。

```sh
python3 tools/checks/validate_model.py
python3 tools/checks/sync_model_refs.py
python3 -m unittest discover -s tests/model -p 'test_*.py' -v
```

校验默认检查阶段 2 的结构要求。`--phase 4` 额外要求实现映射覆盖，当前应失败；`--release` 额外要求模型激活及阶段 0 等通过记录，当前也应失败。失败是明确的阶段约束，不应通过虚构映射、基线或激活状态绕过。

引用索引由 `python3 tools/checks/sync_model_refs.py --write` 同步，只更新来源文档中明确标记的 ID 索引块，不改写原始业务陈述。

可选 `--report docs/reports/ps-model-validation.json` 保存结构化检查结果；报告可重建，源仍在 `model/`。

结构校验、业务谓词走查、业务方确认、真实系统执行验证分别记录。当前校验器不会操作数据库、官网、客户资料、网申或邮箱，也不是运行时 Agent 控制层。

源码使用 Git 进行版本管理。版本清单标识当前模型草案，源码提交与业务评审、模型激活和发布分别记录；不因推送仓库而宣称模型发布流程已完成。
