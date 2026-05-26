# 🎭 Character Card Converter · 角色卡转换

> **An Operit Skill** — Convert character cards from various formats to V2 standard, with automatic language detection & translation.
>
> **Operit 技能** — 将任意格式的角色卡统一转换为 V2 标准格式，支持自动语言检测与翻译。

<p align="center">
  <img src="https://img.shields.io/badge/Operit-Skill-8A2BE2?style=flat-square" alt="Operit Skill"/>
  <img src="https://img.shields.io/badge/Status-Ready-00C853?style=flat-square" alt="Ready"/>
  <img src="https://img.shields.io/badge/License-MIT-yellow?style=flat-square" alt="MIT License"/>
  <img src="https://img.shields.io/badge/Format-V2_Tavern-FF6F00?style=flat-square" alt="V2 Tavern"/>
</p>

---

## 📖 Overview · 概述

**Character Card Converter** is an Operit skill designed to unify character cards from different sources — **SillyTavern V1/V2, TavernAI, Character.AI JSON**, and more — into the **Tavo v0.83.1+ V2 character card specification**.

**角色卡转换** 是一个 Operit 技能，用于将来自 **SillyTavern V1/V2、TavernAI、Character.AI JSON** 等多种来源的角色卡，统一转换为 **Tavo v0.83.1+ V2 角色卡** 格式。

### ✨ What's New

A brand-new **language detection & translation module** automatically identifies English content and translates it into Simplified Chinese, making your character cards ready for Chinese-friendly models.

全新的 **语言检测与翻译模块** 自动识别英文内容并翻译为简体中文，让你的角色卡完美适配中文友好型模型。

---

## 🚀 Features · 功能特点

### Core · 核心功能

| Feature | Description |
|---------|-------------|
| 🔄 **Format Conversion** · 格式转换 | Convert between SillyTavern V1/V2, TavernAI, Character.AI JSON → Tavo V2 |
| 🔍 **Language Detection** · 语言检测 | Auto-detect Chinese / English in key fields (`description`, `personality`, `scenario`, `first_mes`, `tags`) |
| 🌐 **Auto Translation** · 自动翻译 | English → Simplified Chinese translation with natural, roleplay-friendly tone |
| 🎭 **Personality Preservation** · 性格保留 | Maintain character tone, quirks, and speech patterns during translation |
| 🏷️ **Tag Translation** · 标签翻译 | Individual tag translation with common terms preserved (`BL`, `YAOI`, `MLM`, etc.) |

### Supported Input Formats · 支持的输入格式

- ✅ **SillyTavern V1** (legacy format)
- ✅ **SillyTavern V2** (`chara_card_v2` spec)
- ✅ **TavernAI** (`.png` with embedded JSON)
- ✅ **Character.AI** (exported JSON)
- ✅ **Raw JSON** / **Any V2-compatible** structure
- ✅ **Simple text description** (basic character info)

---

## 📦 Installation · 安装

### Prerequisites · 前置要求

- [Operit Ai](https://github.com/AAswordman/Operit) installed
- Network access for translation API calls

### Steps · 步骤

1. **Clone the repository**
   ```bash
   git clone https://github.com/kikiba0152/character-card-converter-AlSkills.git
   ```

2. **Import into Operit**
   - Open Operit → **Skills** → **Import Skill**
   - Select the `SKILL.md` file from this repository
   - Or follow platform-specific instructions for skill import

3. **Activate the skill**
   - Go to your skill list and enable **Character Card Converter**
   - You're ready to go! 🎉

---

## 🔧 Usage · 使用方法

### Via Operit Chat

Simply provide your character card in any of these ways:

```
用户: 帮我转换这个角色卡：{"spec":"chara_card_v2","data":{...}}
用户: 这里有一个 Character.AI 的 JSON，转成 V2 格式
用户: <attached a character card PNG file>
```

The skill will automatically:

1. **Detect** the input format
2. **Analyze** key fields for language (Chinese / English)
3. **Translate** English content to Simplified Chinese (if needed)
4. **Convert** to the standard Tavo V2 format
5. **Return** the complete, translated character card

### Quick Examples · 快速示例

#### Input (English · 英文输入)
```json
{
  "name": "Andy",
  "description": "A confident bartender with a mysterious smile",
  "first_mes": "Well, well, look what the cat dragged in. What'll it be, darling?"
}
```

#### Output (Translated · 翻译输出)
```json
{
  "spec": "chara_card_v2",
  "data": {
    "name": "Andy",
    "description": "一位带着神秘微笑的自信调酒师",
    "personality": "",
    "first_mes": "哎呀哎呀，看看是谁来了。想喝点什么，亲爱的？"
  }
}
```

---

## 🧩 Key Modules · 核心模块

### 1. Language Detection · 语言检测

Scans **5 key fields** (`description`, `personality`, `scenario`, `first_mes`, `tags`) using regex `[\u4e00-\u9fff]` to determine language.

- **Contains Chinese** → No translation needed
- **No Chinese** → Mark for translation

### 2. Translation Engine · 翻译引擎

Transforms English content into **natural, roleplay-friendly Chinese**:
- ✅ Preserves `{{user}}` placeholders
- ✅ Keeps action markers `*...*` intact
- ✅ Retains character personality (cocky, teasing, flirty — all translated with appropriate tone)
- ❌ No literal/robotic translations

### 3. Format Conversion · 格式转换

Standardizes any input into the `chara_card_v2` spec with proper field mapping.

---

## 📄 License · 许可证

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

本项目基于 **MIT 许可证** 开源 — 详见 [LICENSE](LICENSE) 文件。

```
MIT License

See the [LICENSE](LICENSE) file for full text.
```

---

## 🙌 Contributing · 贡献

Feel free to open issues or submit PRs if you have suggestions or improvements! 

欢迎提交 Issue 或 PR，一起让这个技能变得更好！

---

<p align="center">
  Made with ❤️ for the <a href="https://github.com/AAswordman/Operit">Operit</a> Community
</p>
<p align="center">
  为 <a href="https://github.com/AAswordman/Operit">Operit</a> 社区制作
</p>
