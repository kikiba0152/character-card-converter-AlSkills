# 角色卡转换 Skill v2.0.0

Operit 平台的 Skill，将任意来源的角色卡**统一转换为完整的 V3 角色卡**，含智能拆分补齐。

## ✨ 功能特性

- 🌐 **多语种检测与翻译**：自动检测非中文内容（英文/西班牙语/日语等），翻译为简体中文
- 🧠 **智能字段拆分**：自动识别 description/personality/scenario 中的冗余内容，拆分到正确的功能字段
- ✨ **智能补齐**：对缺失字段（system_prompt、post_history_instructions、tags、mes_example 等）自动推演生成
- 💬 **mes_example 推演**：基于角色设定自动生成 5 段对话示例
- 🖼️ **PNG 角色卡支持**：Base64 自动解码 + 回嵌
- 📐 **V3 格式输出**：15 个完整字段，兼容 Tavo v0.87+

## 📥 输入格式

| 类型 | 说明 |
|------|------|
| PNG 角色卡 | SillyTavern 导出，chara 支持明文/Base64 |
| JSON 文件 | `.json` 后缀 |
| 纯 JSON 文本 | 对话中直接粘贴 |

## 📤 输出格式

| 输入 | 输出 |
|------|------|
| PNG | `{角色名}_V3_restructured.png`（回嵌）或 `.json` |
| JSON | `{角色名}_V3_restructured.json` |

## 🔄 执行流程（6步）

```
Step 0: 格式判断
Step 1: 终端提取 + 语言检测
Step 2: AI翻译非中文内容
Step 3: 智能拆分（去冗余）
Step 4: 智能补齐（推演缺失字段）
Step 5: 构建V3 JSON输出
Step 6: [可选] PNG回嵌
```

## 🆕 更新日志

### v2.0.0 (2026-06-14)
- 🧠 智能字段拆分模块
- ✨ 智能补齐模块（system_prompt/post_history_instructions/tags/mes_example 自动推演）
- 🌐 语言检测扩展为通用非中文检测
- 📋 字段补齐从 3 个扩展到 10+ 个
- 🔧 重写执行流程为 6 步完整管线

### v1.1.0 (2026-06-12)
- Base64 解码、占比阈值、V3 格式、PNG 回嵌修复

### v1.0.0 (2026-05-26)
- 初始版本

## 📄 许可证

MIT License