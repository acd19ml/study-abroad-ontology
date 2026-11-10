# 留学申请咨询服务：业务需求与本体

仓库：[`study-abroad-ontology`](https://github.com/acd19ml/study-abroad-ontology)。

整理个人留学申请咨询服务的业务需求，并在此基础上建立业务本体，最终让 AI 依据业务知识受限地推理、回答和操作。框架依据[业务世界模型驱动的 Agent 友好开发实践标准](业务世界模型驱动的%20Agent%20友好开发实践标准.html)。

## 入口

**[产品需求文档](docs/requirements/product-requirements-v0.1.md)是全部需求的聚合，阅读需求只看这一份。**

## 工作顺序

先定一个大一统的标准再装入业务信息，难以验证；现在改为用金标测试集驱动（见 `docs/sources/practice-direction-2026-11-05.md`）：

1. 梳理需求：需求文档 v0.1 已完成。
2. 构建金标测试集：按[构建标准](evals/golden/README.md)整理用例路径清单和题目；第一批 45 道待确认标准答案。**当前步骤。**
3. 分析如何定义业务本体模型标准：价值流、业务能力、业务流、业务活动、业务对象、业务实体等，以及它们之间的关系。
4. 根据金标的消费效果，决定用什么形态承载和消费业务知识。
5. 回头调整，再验证。

实践中发现的白皮书问题记入[实践标准修订记录](docs/standard/revisions.md)，采纳后成批写入白皮书。

## 目录

| 路径 | 内容 |
|---|---|
| `docs/requirements/` | 产品需求文档（需求聚合体） |
| `docs/sources/` | 事实源：用户陈述的整理记录、合同条文索引 |
| `docs/standard/revisions.md` | 实践标准（白皮书）的修订记录 |
| `evals/golden/` | 金标测试集：构建标准、用例路径清单、开发集题目 |
| `docs/scenarios/first-scenario/questions.md` | 历次访谈的问题与结论；PRD 中 `Q-nnn` 的出处 |
| `external-docs/` | 外部参考材料，不是本项目的事实源 |

早期的业务发现整理稿、模型 v0.1、HTML 浏览页、问答评测集及其工具，已在需求整理后删除，存档于 Git 标签 `archive/pre-prd`，不作为依据。
