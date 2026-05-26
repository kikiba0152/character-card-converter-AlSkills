# Skill: 角色卡转Tavo V2格式

## 概述
本技能用于将任意来源的角色卡（SillyTavern V1/V2、TavernAI、Character.AI JSON等）**统一转换为符合Tavo v0.83.1+严格规范的V2角色卡**。Tavo对JSON校验极其严格，必须修复字段类型、转义字符、字段顺序等常见问题。

## 触发条件
用户提供：
- 角色卡JSON文件内容或片段
- 角色卡PNG（内含JSON）
- 或简单描述角色信息（此时需先按标准流程生成V2卡）

## 前置检查
1. **确认输入格式**：是否为有效JSON？是否为V2结构（含`spec: "chara_card_v2"`）？
2. **识别来源**：SillyTavern / TavernAI / Character.AI / 其他
3. **保留核心信息**：name, description, personality, scenario, first_mes, mes_example, alternate_greetings, tags, creator_notes 等

## 转换规则（必须逐条应用）

### 1. 结构标准化
确保JSON顶层包含：
```json
{
  "spec": "chara_card_v2",
  "spec_version": "2.0",
  "data": { ... }
}