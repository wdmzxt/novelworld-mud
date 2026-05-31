# NovelWorld MUD Design

## Core Principle

NovelWorld MUD turns novels into playable worlds. The project treats a novel not as static text, but as a living world model that players can explore through commands and narrative interaction.

## Design Principles

- AI 是叙事者：AI 负责把世界状态、角色动机与玩家行动组织成自然的叙事反馈。
- 数据库是记忆：数据库保存地点、人物、物品、事件、玩家历史与长期世界状态。
- 规则引擎是裁判：规则引擎判断行动是否成立、状态如何变化、风险与结果如何结算。
- 小说是世界：小说提供世界观、人物关系、地点结构、冲突来源与叙事风格。

## v0.1 Boundary

v0.1 only establishes the local command-line MUD skeleton. It does not use AI, ChromaDB, or SQLite. Those systems are reserved for later milestones.
