# 角色卡转换 Skill v2.1.0

Operit 平台的 Skill，将任意来源的角色卡**统一转换为完整的 V3 角色卡**，含智能拆分补齐。

## ✨ 功能特性

- 🌐 **多语种检测与翻译**：自动检测非中文内容（英文/西班牙语/日语等），翻译为简体中文
- 🧠 **智能字段拆分**：自动识别 description/personality/scenario 中的冗余内容，拆分到正确的功能字段
- ✨ **智能补齐**：对缺失字段（system_prompt、post_history_instructions、tags、mes_example、nickname 等）自动推演生成
- 🏷️ **昵称自动生成**：从角色名提取中文名/外文名/简称，分号分隔，方便对话中称呼
- 💬 **mes_example 推演**：基于角色设定自动生成 5 段对话示例
- 🧹 **HTML 清理**：自动清理 JanitorAI 等来源的富文本标签，转为纯 Markdown
- 🖼️ **PNG 角色卡支持**：Base64 自动解码 + 回嵌
- 📐 **V3 格式输出**：16 个完整字段，兼容 Tavo v0.87+

## 📥 输入格式

| 类型 | 说明 |
|------|------|
| PNG 角色卡 | SillyTavern 导出，chara 支持明文/Base64 |
| JSON 文件 | `.json` 后缀 |
| 纯 JSON 文本 | 对话中直接粘贴 |

## 📤 输出格式

| 输入 | 输出 |
|------|------|
| PNG | `charactercard/{角色名}_V3_restructured.png`（回嵌）+ `.json` |
| JSON | `charactercard/{角色名}_V3_restructured.json` |

## 🔄 执行流程（4步优化版）

```
Step 0: 格式判断
Step 1: 终端提取 + 语言检测（super_admin:terminal）
Step 2: AI一次性完成翻译+拆分+补齐+昵称（合并原4步）
Step 3: Python 构建 V3 JSON 并输出
Step 4: [仅PNG] PNG 回嵌
```

## 🆕 更新日志

### v2.1.0 (2026-06-21)
- 🏷️ 新增 nickname 字段自动生成（分号分隔多昵称）
- ⚡ 合并 Step 2-4 为单步，减少中间文件读写
- 📁 输出路径改为 charactercard/
- 🔧 指定 super_admin:terminal 执行脚本避免超时
- 🧹 新增 HTML 标签清理规则

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