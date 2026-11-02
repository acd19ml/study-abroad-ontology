# PS 场景业务发现稿 v0.1

- 整理日期：2026-11-02。
- 场景：为指定学生准备指定项目的 PS，范围与负责人已经用户确认。
- 用途：将既有访谈收束为可整体审阅的业务表达，为后续正式本体模型提供依据。
- 状态：2026-11-02 用户对整体审阅回复“没问题”，认可本稿业务含义、流程、关系、规则和主要例外。事件工作名称与对象拆分尚未转为正式模型语法、稳定 ID 或聚合定义，不据此声称已完成正式模型校验。
- 阶段记录：阶段 0 的指标、基线及阈值仍待收口；本稿整理已有业务发现素材，不宣称阶段 0 或阶段 1 已通过。
- 详细任务资料见 [PS 任务说明](../../discovery/ps-task-context.md)，场景边界见[画布](canvas.md)。

## 1. 这份模型将要支撑什么

顾问指定学生和目标项目后，AI 应沿业务关系找到任务所需的项目课程、要求、学生背景、既有稿件和写作规则，准备项目 PS，并能解释采用哪些资料和规则。

模型需要明确资料属于谁、适用哪个项目、哪些内容已经确认、哪些知识应如何取得，以及后续动作的前提。具体检索、官网读取、写作和工具执行效果在具备实现后验证。

本稿先验证这些业务含义是否正确；可以用假设情景推演，无需真实学生资料。

## 2. 主流程：从任务发起到顾问确认

以下业务流程已获本轮整体认可；节点与事件名称是业务描述，尚未成为已实现的执行顺序或正式系统事件。

1. **顾问发起项目 PS 任务。** 明确学生、目标项目及申请季，产出类型为项目稿。形成“项目 PS 准备任务已提出”的业务事实。
2. **AI 识别并取得任务依赖。** 取得该学生相关背景、素材、确认内容、方向初稿与其他项目已审核 PS；取得目标项目课程、写作要求和本任务适用的业务规则。项目资料先查库，缺少则查学校官网，结构化记录后使用。形成“任务资料及具体缺口已列明”的结果。
3. **AI 处理可自行查证的问题。** 资料矛盾先核对时间、版本与含义；要求仍缺失或个人事实无法确认时，保留原话、出处及具体问题交顾问判断。继续不受影响的内容。
4. **AI 按项目准备中文稿，顾问编辑。** 结合学生经历与项目要求选材、组织内容。已确认事实可复用，新增拟写的经历细节仍标明待核对。形成“项目中文核对稿已准备”的结果。
5. **顾问协调学生核对中文。** 学生核对本人经历和本项目稿件内容，顾问整理反馈并修改；确认对应实际内容和版本。形成“该项目中文稿已确认”的业务事实。
6. **AI 根据已确认中文生成英文并检查。** 核对项目要求、背景事实、中英文对应和适用版本。发现经历需更改时，先改中文并按既有核对流程处理，再生成对应英文。形成英文稿及检查结果。
7. **顾问作最终确认。** AI 一并提供关键要求及出处、采用的学生背景依据、检查结果和具体待决问题；顾问判断稿件是否可用或还需修改。该结果不自动等同于网申已递交或其他项目已确认。

正常闭环外的补充、修改和重新核对由下列例外及已确认规则约束；正式状态转换在阶段 2 再编写并校验。

## 3. 必须能表达的对象与关系

以下业务含义已获整体认可，用于检查模型是否能承载已确认需求；正式元素拆分仍须后续建模，不表示一项对应一张表或一个聚合。

- **申请人、经历事实和背景素材**：事实属于某位学生，素材提供原话或依据；事实有无核对与素材是否存在附件分别理解。
- **目标项目及适用申请范围**：项目关联课程、材料要求、最低申请条件和截止等知识，使用时定位适用范围。
- **要求知识与来源**：项目要求关联学校官方出处及适用范围；没找到限制和官方明确无限制分别记录。
- **PS 准备任务**：关联学生、目标项目和所需产出，沿关系取得依赖，不要求顾问逐次拼接上下文。
- **通用初稿与项目稿**：通用初稿关联学生及申请方向，项目稿关联具体目标项目；项目稿可在没有通用初稿时直接准备。
- **参考稿与可复用内容**：同一学生其他项目已审核 PS 可以参考，已确认事实可复用；其他项目稿件的审核不会自动确认当前项目最终表达。
- **中文稿、英文稿与确认记录**：确认关联实际稿件内容，英文对应已确认中文；旧稿与更改后的稿件分别理解。
- **检查结果与待决问题**：关联实际稿件、所用要求和背景依据，说明完成了什么、缺什么，以及具体需要谁判断。

事实、学校要求、分析建议和写作表达具有不同业务含义。AI 的选材推理可引用事实与项目知识，但推理本身不自动成为学生已经确认的事实。

## 4. 已确认规则及出处索引

这里的序号仅用于本稿审阅，不是正式模型元素 ID。

1. 项目要求先查数据库；缺少时查学校官网，结构化记录后使用。项目课程信息同样可查官网后入库。依据：S1 的 R16、S3 的用户成功标准。
2. 同一学生的已确认事实可复用；针对项目的表达与最终稿仍分别确认。依据：S1 的 R19。
3. 通用初稿按方向准备，最终稿逐项目定制；通用初稿不是项目稿的必经步骤。依据：S1 的 R22、R23。
4. 学生核对中文，确认后由 AI 生成英文；经历更改先改中文，再生成英文；AI 辅助检查，顾问最后确认。依据：S2 的中文稿与英文生成确认、S1 的 R18。
5. 顾问拟出的经历细节需要学生核对；未核对内容与已确认事实分开。缺少工作附件可继续追问和拟稿核对。依据：S2 的经历细节核对记录。
6. 缺要求时先完成不受影响的内容，列出具体待核对项；未知限制不等于没有限制。依据：S1 的 R18。
7. 学生资料有差异时，先检查时间、版本和含义；仍不能解释时保留原话与差异交顾问判断。依据：S1 的 R18。
8. 背景变化影响该学生及相关项目；共用项目要求变化影响全部适用学生。受影响表示需要评估，不等于自动重写。依据：S1 的 R17。
9. 未达官网最低条件的事实与是否继续申请的选择分别保留，由顾问和客户人工决定；AI 不自动取消，也不因继续申请改记为达标。依据：S1 的 R20、R21。
10. 最终确认材料附关键要求与出处、背景依据、检查结果及具体待决问题。依据：S1 的 R18。
11. 同一学生其他项目已审核 PS 是 AI 应主动检索的上下文；本场景不要求顾问反复找稿或复制。依据：S3 的用户成功标准。
12. 本场景止于 PS 准备和顾问确认，不含网申递交、自动联系客户或学校。依据：S3 的 Q1 采用及已确认场景范围。

### 来源

- **S1**：[建模目标与历轮确认](../../sources/modeling-objective-2026-10-31.md)。
- **S2**：[背景资料、中文核对与英文生成确认](../../sources/business-brief-2026-10-31-intake.md)。
- **S3**：[阶段 0 场景选择与用户纠正](../../sources/stage-0-2026-11-02.md)。
- 通用写作组织方法见 [PS 任务说明第 4 节](../../discovery/ps-task-context.md)，当前仍为参考草案，不增加为本稿的已确认硬规则。

## 5. 主要例外及预期业务处理

- **官网仍找不到某项要求**：记录未知及查找依据，继续其他内容，交顾问在手动申请系统操作时补充；未知项不判为已经满足。
- **同一经历在不同资料中不一致**：先核对时间、版本和含义，不能解释则列出原话与差异。事实核对前不悄悄选一个版本当真。
- **目标项目没有可参考通用初稿**：直接依据学生事实和项目要求准备项目稿。
- **其他项目有已审核 PS**：取相关事实和表达作参考，仍对目标项目的表达和最终稿单独确认。
- **学生补充或更正经历**：评估本人相关稿件及依据；涉及英文对应的经历更改时回到中文修订、核对流程。
- **项目修改题目、长度等要求**：评估该要求适用的任务、稿件与检查依据；不直接覆盖历史确认记录或自动重写全部内容。
- **学生条件未达标但仍希望申请**：保留原因和人工选择，当前任务如何继续遵循顾问与客户的决定。
- **顾问需要决定或学生需要核对**：交付具体问题、依据和受影响内容，其他可继续部分继续准备。

上述条目来自既有规则，用于核对主要异常是否覆盖；不声称已经覆盖所有未来情形。

## 6. 模型验证怎样从本稿开始

完整的八个问题见 [PS 任务说明第 6 节](../../discovery/ps-task-context.md)。对每个问题依次核对：

1. 本稿是否提供了所需概念、关系和判断规则，以及来源；缺什么就记录为待补内容。
2. 后续正式模型是否为这些关系和规则提供了明确表达，回答能否指出模型依据。
3. 用明确标注的假设资料走查预期判断，例如“两个项目审核情况不同”“要求未知”“经历已更正”；真实客户信息不是前置条件。

业务表达已获得用户整体认可。按用户最新指令，现已建立[模型源 v0.1 草案](../../../model/README.md)及结构校验器；新增聚合、状态、命令和契约仍待评审，不能据此宣称阶段 2 已通过。阶段 5 再检查实际系统行为。

## 7. 整体审阅记录

- **流程是否符合实际**：主流程是否覆盖准备、中文核对、英文生成、检查与最终确认，是否遗漏主要回退或例外。
- **业务含义是否准确**：学生事实、素材、参考稿、项目表达、确认范围及依赖关系是否分清，是否有顾问不认可的强制步骤。
- **规则与例外是否完整**：上述规则是否忠实于用户确认，主要例外的处理是否符合顾问做法。

用户对上述三方面回复“没问题”，本稿业务含义整体认可。Agent 负责后续模型表达及校验；正式载体、稳定 ID、语法、聚合划分与模型验证结果不由本次认可自动确认。

阶段 0 的指标、基线和阈值继续在[画布](canvas.md)及 [Q-071](questions.md)中明示待对齐；本稿不通过增加真实资料要求来填补这些缺口，也不自动推进正式阶段。

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
- `hdp.ps.background_conflict`
- `hdp.ps.continue_unmet`
- `hdp.ps.length_measurement`
- `hdp.ps.missing_requirements`
- `obj.ps.applicant`
- `obj.ps.background_fact`
- `obj.ps.background_material`
- `obj.ps.check_report`
- `obj.ps.confirmation`
- `obj.ps.context_packet`
- `obj.ps.continuation_decision`
- `obj.ps.course`
- `obj.ps.draft`
- `obj.ps.issue`
- `obj.ps.program`
- `obj.ps.program_knowledge`
- `obj.ps.requirement`
- `obj.ps.student_context`
- `obj.ps.task`
- `rel.ps.check_version`
- `rel.ps.confirmation_version`
- `rel.ps.draft_facts`
- `rel.ps.knowledge_courses`
- `rel.ps.knowledge_program`
- `rel.ps.knowledge_requirements`
- `rel.ps.packet_approved_ps`
- `rel.ps.packet_courses`
- `rel.ps.packet_facts`
- `rel.ps.packet_materials`
- `rel.ps.packet_requirements`
- `rel.ps.student_applicant`
- `rel.ps.student_facts`
- `rel.ps.student_materials`
- `rel.ps.task_checks`
- `rel.ps.task_confirmations`
- `rel.ps.task_decisions`
- `rel.ps.task_drafts`
- `rel.ps.task_issues`
- `rel.ps.task_packet`
- `rel.ps.task_program`
- `rel.ps.task_student`
- `role.ps.agent`
- `role.ps.consultant`
- `role.ps.student`
- `rule.ps.confirm_current_english`
- `rule.ps.current_version_checked`
- `rule.ps.explain_selection`
- `rule.ps.final_known_requirements`
- `rule.ps.knowledge_scope_matches`
- `rule.ps.length_measurement_unknown`
- `rule.ps.ps_length_limit`
<!-- MODEL-REFS:END -->
