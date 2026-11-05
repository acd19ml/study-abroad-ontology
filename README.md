# 留学申请业务本体模型

仓库：[`study-abroad-ontology`](https://github.com/acd19ml/study-abroad-ontology)。

依据[业务世界模型驱动的 Agent 友好开发实践标准](业务世界模型驱动的%20Agent%20友好开发实践标准.html)，梳理个人留学咨询的业务需求、服务边界、判断依据和可复用知识。

**首场景：为指定学生准备指定项目的 PS。已有 [模型源 v0.1 草案](model/README.md)及[交互 HTML 浏览器](generated/ps-model-explorer.html)。** 展示由源生成，业务改动先修改模型再生成并检查同步。范围、负责人及业务发现稿已确认；新增模型结构仍待评审，阶段 0 计量项保留未决，未宣称阶段 2 验收通过。依据见[用户记录](docs/sources/stage-0-2026-11-02.md)。

**建模的核心用途是让 AI 自主完成任务准备和受约束的工作。** AI 应主动获取项目要求、检索客户背景、组装任务上下文、执行和检查，再由顾问最后确认；不依赖顾问每次先查官网、逐条重述约束和手工拼接全部材料。详细目标见[Agent 自主工作需求](docs/discovery/agent-autonomy-requirements.md)，用户原意见[建模目标澄清](docs/sources/modeling-objective-2026-10-31.md)。

已确认项目要求采用数据库优先，缺失时查学校官方网站，结构化入库后使用。申请系统由顾问手动操作，差异和业务变化由顾问反馈或手动平台修改；当前只梳理影响范围，聚合根、事件任务及实现机制后置。

## 当前讨论入口

**当前可在 [交互 HTML](generated/ps-model-explorer.html) 中浏览模型，并对照 [结构评审提案](docs/proposals/ps-model-v0.1.md)及 [2026-11-02 评审修订提案](docs/proposals/ps-model-change-2026-11-02.md)。阶段 0 至 2 已通过；阶段 3 [架构决策记录](docs/adr/README.md)已起草待采纳；下一步是网页版只读[模型问答 AI](docs/proposals/model-qa-agent-v0.1.md)及其[评测问题集](evals/model-qa/README.md)。** 可点开节点属性、边的定义、状态转换和来源。页面为只读投影，修改回到[模型源](model/README.md)；它不代表已部署图数据库或运行时业务 Agent。

1. 从下方业务轮廓理解已确认服务和待确认环节。
2. 结合自主工作目标，在[未决问题](docs/scenarios/first-scenario/questions.md)中记录业务结论，逐项说明任务所需事实、资料关系、约束、判断依据和人工决策点。
3. [首场景画布](docs/scenarios/first-scenario/canvas.md)已区分阶段 0 的目标与边界、阶段 1 的业务含义确认、阶段 2 的模型表达与校验。先用既有业务规则和假设情景检查模型准备内容，真实案例不作为当前必须提供的前置条件；基线和阈值仍单独列明待对齐，不虚构阶段通过。

业务轮廓先看[端到端业务运作与系统职责草案](docs/discovery/service-workflow.md)，术语见[业务术语表](CONTEXT.md)。草案正等待用户确认，尚不构成已生效规则。

自主工作的信息缺口、资料冲突与最终确认信息已确认；[客户知识复用与 PS 任务范围](docs/discovery/customer-knowledge-and-task-scope.md)已确认官网最低条件入库、已达标优先及组内按截止排序。未达标项目是否继续由顾问与客户人工决定，记录原因与最终选择；AI 不自动取消，也不将继续申请改记为已达标。

[项目 PS 任务说明](docs/discovery/ps-task-context.md)连接所需学生与项目资料、已确认约束、产出及检查依据；其中写作方法明确标为参考草案。已确认学生背景事实共用、通用初稿按方向准备、最终稿逐项目定制；允许直接起草项目稿，方向初稿用于复用而非必经步骤。已整理[业务概念与关系](docs/discovery/business-concepts.md)；沟通知识复用、跟进节奏与求职服务边界已确认，后续优先整体审阅场景产出物。

客户价值与咨询方式见[专业依据与持续咨询](docs/discovery/trust-and-consultation.md)；项目建议表、材料要求和客户选择见[项目信息与申请时间表](docs/discovery/project-research-and-selection.md)。本轮确认依据见[专业经验与项目字段记录](docs/sources/business-brief-2026-10-31-value-and-projects.md)。

业务背景见[首次需求陈述记录](docs/sources/business-brief-2026-10-30.md)及[补充陈述](docs/sources/business-brief-2026-10-30-followup.md)，现有合同依据见[协议 V3 业务材料索引](docs/sources/contract-v3.md)。其中的业务愿景、客户痛点假设与候选功能尚不代表首期实施范围。

最新业务确认见[选校、客户确认与辅导边界](docs/sources/business-brief-2026-10-30-selection.md)，已同步至流程草案与场景画布。

2026-10-31 更新：[资料收集与递交管理确认](docs/sources/business-brief-2026-10-31-intake.md)已记录；[微信背景挖掘方案 v0.4](docs/discovery/client-intake-and-background.md)已纳入中文确认后 AI 生成英文的流程；[申请跟进与账号管理](docs/discovery/application-tracking.md)整理了独立递交状态和学生专用邮箱需求，其余草案供继续讨论确认。

邮件职责已确认到申请相关性判断、事件分类及顾问待办，提醒仅给顾问；纯通知可以没有待办，多事项分别提取，不确定时保留原文和疑问交顾问判断。邮件是完整业务中的辅助需求，不指定为首个开发场景。

`first-scenario` 当前保存首个 PS 场景资料，目录名不是业务上下文或模型元素 ID；正式模型 ID 后续确定。

## 目录约定

当前文件用于业务需求讨论。后续需要正式建模或实现时，可按实际阶段增加以下目录：

- `docs/scenarios/`：场景画布、事件流、未决问题。
- `docs/sources/`、`docs/cases/`：原始业务材料与案例。
- `docs/adr/`、`docs/proposals/`：架构决策与模型变更提案。
- `model/meta/`、`model/contexts/<上下文>/`：元模型 Schema 与业务模型唯一权威源。
- `generated/`：由模型生成的代码、规则、契约、测试和文档，禁止手改。
- `src/`：已声明的扩展点、适配器、控制层、上下文组装与应用入口。
- `tests/scenarios/`：独立编写的业务场景验收测试。
- `evals/`：场景包含业务 Agent 时的评测集与验证报告。
- `tools/generator/`、`tools/checks/`：生成器与校验工具。

模型文件按标准第 5.7 节组织。实现映射覆盖从阶段 4 起强制执行。

## 验证与运行

已有模型源、离线校验、假设业务谓词测试及 HTML 投影生成器；业务应用、数据库和运行时控制层尚未实现。技术栈和业务执行映射在后续阶段确定。

```sh
python3 tools/checks/validate_model.py
python3 tools/checks/sync_model_refs.py
python3 -m unittest discover -s tests/model -p 'test_*.py' -v
python3 tools/generator/render_model.py
python3 tools/generator/render_model.py --check
python3 -m unittest discover -s tests/generator -p 'test_*.py' -v
```

校验环境与限制见 [模型说明](model/README.md)。Git 用于保存源码版本；当前模型为可评审草案，提交源码不等于业务规则已生效或阶段验收通过。
