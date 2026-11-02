# 模型变更提案：v0.1 评审修订

- 提出人 / 日期：Agent（需求整理）/ 2026-11-02。
- 来源：对[模型源 v0.1 草案](ps-model-v0.1.md)的整体评审，以及[用户评审答复](../sources/model-review-2026-11-02.md)。
- 状态：第一、二部分均已改入模型源（第二部分经用户 2026-11-02 “按你的建议处理，改进模型”同意），元素仍为 `draft`。用户于 2026-11-02 确认阶段 2 通过，后续继续完善。
- 用户安排：先修第 1 到第 4 项并补假设场景，再把第 5 到第 9 项写成提案条目，然后做整体业务评审。第 5 到第 11 项及 Q-078、Q-079 已按用户同意改入。

## 一、已改入模型源（第 1 到第 4 项）

每项都在 [`tests/model/scenarios.yaml`](../../tests/model/scenarios.yaml) 中有假设场景，证明错误情形会被拦住；场景只用标注为假设的值，不是客户资料或真实学校要求。

### 1. “未确认”的录入不能推进确认状态

- **问题**：确认记录有“明确确认 / 未确认”字段，但确认规则不检查它；录入一条“未确认”也会把任务推进到“中文已确认”或“顾问已确认”。
- **变更**：
  - `rule.ps.confirm_current_chinese`、`rule.ps.confirm_current_english` 增加“确认结果不是明确确认则拒绝”。
  - 按用户答复，`cmd.ps.confirm_chinese` 改名“录入学生对中文内容的确认”，执行角色从学生改为顾问；`obj.ps.confirmation.evidence_ref` 改为可空，顾问录入时不要求附学生依据。`role.ps.student` 不再直接执行命令，但仍是确认决定的作出者（`actor_ref`）。
- **补充（Q-074）**：用户确认顾问标记经历已核对、记录客户是否继续申请也一样处理，不要求附依据。已删除 `rule.ps.confirmed_fact_has_evidence`、`rule.ps.customer_choice_evidence` 两条 Agent 提出的规则；`obj.ps.background_fact.verification_ref`、`obj.ps.continuation_decision.customer_evidence_ref` 改为选填。两条规则从未生效，没有其他元素引用，直接删除不违反 ID 不复用的约定。
- **拦截场景**：“录入的学生回复为未确认时不能推进中文确认”“顾问最终确认记录为未确认时不能完成”。
- **批准人**：业务方（规范性规则）；角色调整同时需工程实现确认。

### 2. 规则写清“针对哪一条记录、是任一条还是每一条”

- **问题**：经历、要求、检查结果在任务中都是多条记录，原规则把它们当单个对象，没有说明取哪一条。比如“已知要求未通过不能最终确认”可能被一份旧版本的检查结果误触发，也可能漏掉当前版本的结果。
- **变更**：
  - 元模型增加规则的 `bindings`（本次命令提交的新记录、或沿单值关系取得的对象）和 `exists` / `each` 量词，见[元模型说明](../../model/meta/README.md)。校验器检查条件中每个对象都有明确来源、关系路径能从命令所属聚合走到。
  - 规则改为明确绑定：上下文检查针对本次组装的上下文；中文稿检查针对本次提交的中文稿；“已知要求未通过”只看与当前英文版本对应的检查结果。
  - 原 `rule.ps.same_student_facts` 同时作用于组装上下文和准备中文稿，两者检查的记录不同，拆为：`rule.ps.same_student_facts`（上下文选取的经历）和新增的 `rule.ps.draft_facts_same_student`（中文稿引用的经历）。业务含义不变，仍来自已确认的“只用本学生的经历”。
- **拦截场景**：“上下文混入一条其他学生经历即拒绝”“中文稿引用其他学生经历即拒绝”“当前英文的检查未通过时不能最终确认”；反例“旧版检查未通过不阻断已通过的当前版本”。
- **批准人**：业务方确认规则含义；元模型语法由工程实现评审。

### 3. 官网要求与顾问网申反馈分别成条保留

- **问题**：来源类别原来只有一个值，挂在整条项目知识记录上。同一项目、同一申请季无法同时保留官网要求和顾问网申反馈；记录一旦标为顾问反馈，之后的官网更新会被拒绝。
- **变更**：`source_kind` 从 `obj.ps.program_knowledge` 移到每条 `obj.ps.requirement`。官网知识命令与网申反馈命令都增加 `requirement_refs` 参数，`rule.ps.official_source` 只检查本次官网命令写入的要求，`rule.ps.unknown_is_not_unrestricted` 只检查本次写入的要求。
- **拦截场景**：“官网知识命令写入顾问反馈来源的要求即拒绝”；反例“已有顾问网申反馈时仍可写入官网要求”。
- **批准人**：业务方。

### 4. 转交顾问判断的位置改到 AI 检查，而不是顾问自己的确认

- **问题**：“仍有未知要求”“长度计量待核对”两条原本在顾问最终确认时转人工，而最终确认本来就是顾问操作，转了等于没转。另外，原长度规则会在 AI 检查时直接拒绝，导致超长稿件连“未通过”的检查结果都无法记录。
- **变更**：
  - `rule.ps.unknown_requirements_human_review`、`rule.ps.length_measurement_unknown` 只作用于 AI 执行的 `cmd.ps.check_english`：检查挂起，交顾问按对应人工决策点判断。
  - `rule.ps.ps_length_limit` 改为“超出已查明长度限制的稿件不得记为已知要求通过”：AI 可以如实记录未通过，但不能记为通过；顾问最终确认继续由 `rule.ps.final_known_requirements` 拦截。这是画布中“不能把超过限制的稿件说成合格”的直接表达。
  - 校验器新增：转人工规则不得作用于人工执行的命令。
- **拦截场景**：“检查发现未知要求时交顾问”“计量单位不同先交人工核对”“超长稿件不能记为已知要求通过”；反例“超长稿件可如实记为未通过”。
- **批准人**：业务方。

## 二、已同意并改入的条目（第 5 到第 11 项）

以下各项的“建议”已按用户答复改入模型源，落地方式见本节末尾“改入对照”。

以下涉及新增对象、状态或执行机制，须业务方与工程实现评审后再改模型。

### 5. 表达“已获客户审核的其他项目 PS”

- **现状**：S3 成功标准要求 AI 主动参考同一学生其他项目已获客户审核的 PS，但稿件没有审核状态，确认范围只有“学生中文确认”和“顾问最终确认”；`rule.ps.same_student_reference_ps` 只检查同一学生。
- **已确认（第三轮）**：与客户多轮交付、反馈后最终定稿、不再修改的英文稿，就是已审核 PS；不另设客户认可步骤。
- **建议**：不新增确认范围。可参考稿须同时满足：属于同一学生；来自其他项目的任务；是该任务顾问最终确认的英文版本（`consultant_final` 且明确确认）。中间交付版本不作为已审核 PS 参考，可作为一般背景素材。
- **影响**：`obj.ps.confirmation`、`rel.ps.packet_approved_ps`、`rule.ps.same_student_reference_ps`、`cmd.ps.assemble_context`。
- **批准人**：业务方。**验证**：假设“两个项目审核情况不同”，只有已审核的一份进入参考。

### 6. 方向初稿的归属

- **现状**：方向初稿按学生和申请方向准备，不属于某个项目任务；模型却把它放在项目任务聚合内，没有命令能创建它。
- **建议**：方向初稿作为学生资料的一部分（学生上下文读视图中的成员或外部引用），项目任务只引用。
- **影响**：`obj.ps.draft`、`agg.ps.task`、`agg.ps.student_context`、`obj.ps.context_packet.generic_draft_refs`。
- **批准人**：工程实现与业务方（聚合边界）。**验证**：假设“已有方向初稿 / 没有方向初稿”两种情形都能准备项目稿。

### 7. 学生背景或项目要求变化后，标出需要重新评估的稿件

- **现状**：已确认“受影响需要评估、不等于自动重写”，模型没有任何表达。重新组装上下文会覆盖旧记录，稿件也不记录用的是哪一版资料。
- **建议**：
  - 稿件版本记录所用学生资料版本和项目知识版本；上下文保留历史，不覆盖。
  - 在 AI 检查和最终确认时增加提示规则：所用资料版本不是最新时标出，交顾问评估；不自动重写。
  - 只要该项目还没递交，学生背景变化（由顾问提交）和项目要求变化（第 11 项每月同步出的差异）都提醒顾问，包括已最终确认的稿件（第三轮已确认）。提醒只要求评估，不自动重写。
  - 判断“没递交”需要知道递交状态，建议读取申请跟进中顾问记录的“已递交申请”，见 [Q-078](../scenarios/first-scenario/questions.md)。
- **影响**：`obj.ps.draft`、`obj.ps.context_packet`、`rel.ps.task_packet`、`cmd.ps.check_english`、`cmd.ps.confirm_final`。
- **批准人**：业务方；跨聚合策略另需工程实现。**验证**：假设“学生更正经历后，旧中文稿被标出”“同一学生无关项目不受影响”。

### 8. 达标判断：由谁写入，避免重复记录

- **现状**：没有命令写入达标情况；未达标后的申请选择在任务属性和独立记录中各存一份；记录该选择的命令在任何达标情况下都能执行。
- **建议**：增加 AI 执行的“对照官网最低条件记录达标情况”（执行后复核）；申请选择只保留独立记录；记录选择限定在未达标时。与第 10 项“客户放弃申请”区分：后者不以未达标为前提。
- **影响**：`obj.ps.task.eligibility`、`obj.ps.task.continuation_decision`、`obj.ps.continuation_decision`、`cmd.ps.record_continuation`、`rule.ps.unmet_remains_unmet`。
- **批准人**：业务方；新命令的执行等级需工程实现与业务方。**验证**：假设“未达标仍继续申请，达标情况保持未达标”。

### 9. 选材理由可追溯

- **现状**：`rule.ps.explain_selection` 条件恒为真，没有实际约束；稿件只记录用了哪些经历，没有记录对应项目的哪个特点。
- **建议**：稿件记录“经历—项目课程或要求—选用理由”的对应；理由属于 AI 分析，标为参考性内容，不当作学生已确认事实。
- **影响**：`obj.ps.draft`、`rel.ps.draft_facts`、`rule.ps.explain_selection`。
- **批准人**：知识编译（参考性）与业务方。**验证**：对验证问题 8“为什么引用这段经历”能指出经历出处、确认情况和对应项目特点。

### 10. 客户放弃申请（用户 2026-11-02 答复）

- **已确认**：递交申请前的任意时间或进度节点，客户都可能表示不再申请该项目。
- **已确认（Q-075）**：放弃时不用记录原因；客户之后又想申请时，恢复原任务。
- **建议**：
  - 增加顾问执行的“记录客户放弃申请”（仅人工），任何状态都可执行，进入“客户已放弃”；任务记住放弃前所处的状态，AI 不再执行该任务的命令，已有稿件和记录保留。
  - 增加顾问执行的“恢复申请”（仅人工），任务回到放弃前的状态继续。放弃期间若学生资料或项目要求有变化，按第 7 项标出需评估的稿件。
  - 原“未达标是否继续”中的放弃选择也走此命令。
- **影响**：`obj.ps.task.lifecycle`、新命令与事件、`role.ps.consultant`。
- **批准人**：工程实现与业务方（状态、命令）。**验证**：假设“中文已确认后客户放弃，AI 不能再生成英文”。

### 11. 官网项目信息每月同步（用户 2026-11-02 答复）

- **已确认**：从学校官网取得的项目信息保存在本地知识库，每月运行一次定时任务同步差异并记录，按申请季区分。
- **已确认（Q-076）**：同步库里全部项目；差异直接生效，但要记录差异变化；差异与学生正在准备申请的项目相关时提醒顾问。
- **建议**：
  - 每月对库里每个项目、每个申请季执行 `cmd.ps.refresh_official_knowledge`；差异直接生效，执行等级由“执行后复核”改为“自动执行”，旧版本及差异记录保留，已被任务使用的版本不覆盖。
  - 元模型的策略目前只能由事件触发，需增加“定时触发”的表达（每月、全部已入库项目）。
  - 增加“官网差异已记录”事件和策略：差异涉及学生正在准备申请的项目时，提醒顾问；“正在准备”指尚未递交且未处于“客户已放弃”的任务，包括已最终确认的任务（第三轮已确认）。
- **影响**：`cmd.ps.refresh_official_knowledge`、`model/meta/model.schema.json` 的策略定义、`policies.yaml`。
- **批准人**：工程实现与业务方（执行等级、策略）。**验证**：假设“官网字数限制在月度同步中变化，旧版本保留，引用旧版本的未确认任务被标出”。

### 改入对照

- **第 5 项**：`obj.ps.draft` 增加 `final_confirmed`（顾问最终确认时标为定稿，重新打开时取消）；`rule.ps.same_student_reference_ps` 要求参考稿是同一学生其他项目的英文定稿。
- **第 6 项**：新增 `obj.ps.direction_draft`，归学生上下文读视图；`obj.ps.draft` 去掉用途字段，只表示项目稿，目标项目必填。
- **第 7 项**：稿件记录所用上下文（`rel.ps.draft_packet`），上下文保留历史（`rel.ps.task_packet_history`），重新组装上下文可在中文待核对时进行；三条策略在学生背景更正、官网差异、网申差异后触发 `cmd.ps.record_change_impact`，为未递交任务（含已最终确认、客户已放弃）记录提醒问题；人工决策点 `hdp.ps.change_impact` 指引顾问评估。
- **第 8 项**：新增 AI 执行的 `cmd.ps.record_eligibility`（执行后复核）；任务上重复的申请选择字段删除；`rule.ps.continuation_only_when_unmet` 限定未达标时才记录继续申请。
- **第 9 项**：新增 `obj.ps.selection_rationale` 及其与经历、课程、要求的关系；`rule.ps.explain_selection` 在中文稿缺少选材理由时标记。
- **第 10 项**：任务增加“客户已放弃”状态及 `cmd.ps.record_withdrawal`、`cmd.ps.restore_application`；元模型增加 `to: previous`，恢复时回到放弃前状态。
- **第 11 项**：`pol.ps.monthly_official_sync` 每月对全部项目同步，`cmd.ps.refresh_official_knowledge` 改为自动执行；新增 `obj.ps.knowledge_change` 记录差异；元模型策略支持定时触发。
- **Q-078**：任务增加“已递交”终止状态及 `cmd.ps.record_submission`（仅人工，只能在顾问已确认后记录）。
- **Q-079**：新增 `cmd.ps.revise_english_wording`（仅人工），英文措辞修订不回到中文。

## 影响清单

- 第二部分另改：`objects.yaml`、`aggregates.yaml`、`roles.yaml`、`rules.yaml`、`policies.yaml`（新增四条策略），元模型增加定时策略与 `to: previous`。
- 已改模型源：`objects.yaml`（确认记录、项目知识、要求记录）、`aggregates.yaml`（中文确认录入、学生上下文与项目知识命令参数）、`roles.yaml`、`rules.yaml`（16 条规则修订、新增 `rule.ps.draft_facts_same_student`）。
- 已改元模型与工具：`model/meta/model.schema.json`、`model/meta/README.md`、`tools/checks/validate_model.py`、投影模板的条件显示。
- 测试：`tests/model/scenarios.yaml`、`tests/model/test_model.py`。
- 投影：`generated/` 由生成器重建。
- 手写实现：无，尚未有业务代码。

## 校验范围

结构校验、绑定解析与假设场景只证明模型表达能得出预期判断，不证明运行时控制层、真实资料检索或网页同步已实现；业务方评审前所有元素保持 `draft`。

<!-- MODEL-REFS:START -->
## 模型关联索引

此段由 `tools/checks/sync_model_refs.py` 根据模型源的 `refs` 同步，仅用于双向定位。

- `agg.ps.program_knowledge`
- `agg.ps.student_context`
- `agg.ps.task`
- `cmd.ps.assemble_context`
- `cmd.ps.confirm_chinese`
- `cmd.ps.confirm_final`
- `cmd.ps.prepare_chinese`
- `cmd.ps.record_change_impact`
- `cmd.ps.record_continuation`
- `cmd.ps.record_eligibility`
- `cmd.ps.record_official_knowledge`
- `cmd.ps.record_portal_feedback`
- `cmd.ps.record_student_context`
- `cmd.ps.record_submission`
- `cmd.ps.record_withdrawal`
- `cmd.ps.refresh_official_knowledge`
- `cmd.ps.refresh_student_context`
- `cmd.ps.restore_application`
- `cmd.ps.revise_chinese`
- `cmd.ps.revise_english_wording`
- `evt.ps.application_restored`
- `evt.ps.application_withdrawn`
- `evt.ps.change_impact_recorded`
- `evt.ps.eligibility_recorded`
- `evt.ps.english_wording_revised`
- `evt.ps.official_knowledge_refreshed`
- `evt.ps.portal_feedback_recorded`
- `evt.ps.student_context_refreshed`
- `evt.ps.submission_recorded`
- `hdp.ps.change_impact`
- `obj.ps.background_fact`
- `obj.ps.confirmation`
- `obj.ps.continuation_decision`
- `obj.ps.direction_draft`
- `obj.ps.draft`
- `obj.ps.issue`
- `obj.ps.knowledge_change`
- `obj.ps.program_knowledge`
- `obj.ps.requirement`
- `obj.ps.selection_rationale`
- `obj.ps.task`
- `pol.ps.monthly_official_sync`
- `pol.ps.official_change_reminder`
- `pol.ps.portal_change_reminder`
- `pol.ps.student_change_reminder`
- `rel.ps.direction_draft_facts`
- `rel.ps.draft_packet`
- `rel.ps.draft_rationales`
- `rel.ps.knowledge_changes`
- `rel.ps.packet_generic_drafts`
- `rel.ps.rationale_courses`
- `rel.ps.rationale_fact`
- `rel.ps.rationale_requirements`
- `rel.ps.student_direction_drafts`
- `rel.ps.task_packet_history`
- `rel.ps.task_rationales`
- `role.ps.agent`
- `role.ps.consultant`
- `rule.ps.confirm_current_chinese`
- `rule.ps.confirm_current_english`
- `rule.ps.continuation_only_when_unmet`
- `rule.ps.draft_facts_same_student`
- `rule.ps.explain_selection`
- `rule.ps.final_known_requirements`
- `rule.ps.knowledge_persisted_before_use`
- `rule.ps.knowledge_scope_matches`
- `rule.ps.length_measurement_unknown`
- `rule.ps.official_source`
- `rule.ps.proposed_details_need_verification`
- `rule.ps.ps_length_limit`
- `rule.ps.same_student_facts`
- `rule.ps.same_student_reference_ps`
- `rule.ps.unknown_is_not_unrestricted`
- `rule.ps.unknown_requirement`
- `rule.ps.unknown_requirements_human_review`
<!-- MODEL-REFS:END -->
