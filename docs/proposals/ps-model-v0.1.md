# PS 模型源 v0.1 评审提案

- 日期：2026-11-02。
- 依据：用户明确要求先按实践标准建立模型源，再制作 HTML。该指令授权创建源草案，不代表阶段 0 未决计量项已解决。
- 入口：[模型源说明](../../model/README.md)、[版本清单](../../model/model.yaml)。
- 业务依据：[已整体确认的发现稿](../scenarios/first-scenario/discovery.md)、[历轮原始确认](../sources/modeling-objective-2026-10-31.md)、[资料核对记录](../sources/business-brief-2026-10-31-intake.md)。
- 状态：待业务与结构评审；全部元素 `draft`，无合入或发布结论。

## 这次首次形成的表达

- 按标准组织价值、对象关系、聚合命令事件、规则与人工决策、角色等源文件；每个元素有稳定格式 ID、版本、负责人、出处。
- `obj.ps.task` 表达单学生、单项目、单申请季的 PS 工作项；稿件、确认、检查结果和问题保留关联，中文与英文使用具体版本对应。
- `obj.ps.student_context` 是文书准备所用学生上下文读视图，原材料与确认依据保持外部引用，不把它扩张成完整客户管理。
- `obj.ps.program_knowledge` 表达具体项目及申请季的知识记录，区分官方来源与顾问反馈、已知要求与查无结果，并保留课程和要求的结构化关联。
- 学生背景、项目词数、课程名称等具体业务记录不在模型源中虚构。测试仅用明确标注的假设值。

## 需要整体评审的结构选择

1. **三个聚合边界**：`agg.ps.task`、`agg.ps.student_context`、`agg.ps.program_knowledge`。后两个用于本场景的资料读视图/知识版本，不声称原始学生业务或完整学校业务都属于文书准备。跨聚合用引用或只读关联。
2. **状态与版本**：任务从已发起、上下文准备、中文准备与确认、英文准备与检查到顾问确认。中文更改回到待核对版本，保留旧稿和确认记录；没有方向初稿也可起草。状态键和命令粒度是首次提案。
3. **确认契约**：生成英文要对应当前中文确认；最终确认要对应本次检查的英文。后者的精确版本门槛、核对证据的必填方式、计量不一致时的转人工条件是为避免误用而提出的结构化契约，尚待用户评审。
4. **执行等级**：人作出的选择和确认仅人工，AI 准备与检查先按执行后复核描述。这是保守草案，不视为已完成阶段 3 架构决策。
5. **规则绑定及副作用**：条件使用业务属性表达式，输入按关联实例绑定；命令后置含义和保留属性已声明。尚无运行时命令处理器、查询绑定器或强制执行层，静态检查不能替代它们。

上述结构与契约依照已确认业务含义起草，但不把结构性选择冒充用户逐项确认。

## 旧本体框架暂如何处理

用户提出过价值流、业务能力、业务流、业务活动、业务对象、业务实体、业务状态、业务事实、业务规则、业务特性、业务子特性、业务术语、解决方案场景等分类。

当前先采用本项目标准第 5 章的元素类型。旧分类中“业务实体”“业务事实”“业务特性”的原始定义尚未提供，不直接映射成当前标签；价值流、能力与场景等扩展可另行评审。元模型类型、领域定义、具体学生/稿件记录分别表达，不将三者混在一层。

HTML 应从这些源定义读取对象、关系及属性，不能另建一套硬编码关系作为权威源。用户已进一步授权生成[交互 HTML](../../generated/ps-model-explorer.html)，并要求先改模型再同步；该投影不改变本提案的待评审状态。

## 校验范围与明确未完成项

校验覆盖 Schema、ID 与引用、来源文件、聚合封装、状态转换和可达性、规则与人工决策、业务属性引用、指标统计对象、角色覆盖。实现映射从阶段 4 才强制；空策略表示用户仅确认影响范围，自动跨聚合传播和时限没有擅自设定。

模型问题走查使用假设条件验证关键判断，不能证明真实官网读取、资料检索或英文写作质量，也不证明所有量化实例绑定、命令副作用与控制层已实现。

- 阶段 0：指标口径、基线和验收阈值仍待对齐，`metric.ps.manual_context_categories` 的基线为 `null`，目标 0 是待审提案。
- 阶段 2：正式结构草案已形成；业务方对新增结构和规范性契约尚未评审，不能宣布通过。
- 阶段 3、4：业务技术栈、扩展点、运行时控制层、代码及工具投影生成器、实现映射未完成。当前仅实现只读 HTML 投影生成器，不将其记为完整阶段 4 交付。
- 版本管理：源码使用 Git 保存并推送到用户指定仓库；清单版本仍为草案标识，Git 提交与业务评审合入、模型激活及发布分别记录。

## 关联元素

`ctx.ps.preparation`、`goal.ps.autonomous_context`、`metric.ps.manual_context_categories`、`agg.ps.task`、`agg.ps.student_context`、`agg.ps.program_knowledge`、`obj.ps.task`、`obj.ps.draft`、`obj.ps.confirmation`、`rule.ps.current_version_checked`、`rule.ps.confirmed_fact_has_evidence`、`rule.ps.confirm_current_english`、`hdp.ps.length_measurement`。

<!-- MODEL-REFS:START -->
## 模型关联索引

此段由 `tools/checks/sync_model_refs.py` 根据模型源的 `refs` 同步，仅用于双向定位。

- `agg.ps.program_knowledge`
- `agg.ps.student_context`
- `agg.ps.task`
- `cmd.ps.assemble_context`
- `cmd.ps.check_english`
- `cmd.ps.confirm_chinese`
- `cmd.ps.confirm_final`
- `cmd.ps.generate_english`
- `cmd.ps.prepare_chinese`
- `cmd.ps.record_continuation`
- `cmd.ps.record_issue`
- `cmd.ps.record_official_knowledge`
- `cmd.ps.record_portal_feedback`
- `cmd.ps.record_student_context`
- `cmd.ps.refresh_official_knowledge`
- `cmd.ps.refresh_student_context`
- `cmd.ps.request_ps`
- `cmd.ps.resolve_issue`
- `cmd.ps.revise_chinese`
- `ctx.ps.preparation`
- `evt.ps.chinese_confirmed`
- `evt.ps.chinese_prepared`
- `evt.ps.chinese_revised`
- `evt.ps.context_assembled`
- `evt.ps.continuation_recorded`
- `evt.ps.english_checked`
- `evt.ps.english_generated`
- `evt.ps.final_confirmed`
- `evt.ps.issue_recorded`
- `evt.ps.issue_resolved`
- `evt.ps.official_knowledge_recorded`
- `evt.ps.official_knowledge_refreshed`
- `evt.ps.portal_feedback_recorded`
- `evt.ps.ps_requested`
- `evt.ps.student_context_recorded`
- `evt.ps.student_context_refreshed`
- `metric.ps.manual_context_categories`
- `rule.ps.confirm_current_english`
- `rule.ps.confirmed_fact_has_evidence`
- `rule.ps.current_version_checked`
- `rule.ps.customer_choice_evidence`
- `rule.ps.length_measurement_unknown`
<!-- MODEL-REFS:END -->
