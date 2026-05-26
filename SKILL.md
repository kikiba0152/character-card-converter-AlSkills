---
name: "角色卡转换"
description: "转换角色卡（含中英检测+自动翻译）"
---

# Skill: 角色卡转Tavo V2格式（中英文双语支持版）

## 概述
本技能用于将任意来源的角色卡（SillyTavern V1/V2、TavernAI、Character.AI JSON等）**统一转换为符合Tavo v0.83.1+严格规范的V2角色卡**。
**新增特性**：自动检测角色卡内容的语言（中文/英文），并对指定的关键字段进行翻译，使输出角色卡适配中文友好型模型。

## 触发条件
用户提供：
- 角色卡JSON文件内容或片段
- 角色卡PNG（内含JSON）
- 或简单描述角色信息（此时需先按标准流程生成V2卡）

## 前置检查
1. **确认输入格式**：是否为有效JSON？是否为V2结构（含`spec: "chara_card_v2"`）？
2. **识别来源**：SillyTavern / TavernAI / Character.AI / 其他
3. **保留核心信息**：name, description, personality, scenario, first_mes, mes_example, alternate_greetings, tags, creator_notes 等

---

## 一、语言检测模块（新增）
在开始转换前，**必须**对角色卡的以下字段进行语言检测：

### 1.1 需要检测的字段
- `data.description`
- `data.personality`
- `data.scenario`
- `data.first_mes`
- `data.tags`（标签数组，逐个检测）

### 1.2 检测规则
1. 取每个字段的前100个字符（或完整内容，取较短者）
2. 用正则表达式 `[\u4e00-\u9fff]` 检测是否包含中文字符
3. 判定标准：
   - **含中文字符** → 判定为「中文/中英混合内容」，**不需要翻译**
   - **不含中文字符** → 判定为「纯英文内容」，**需要翻译为简体中文**

### 1.3 例外处理
- 如果 `first_mes` 中包含角色名称（如 `"Andy"`、`{{user}}` 等占位符），这些不视为英文，不触发翻译需求
- `tags` 字段中如果某个标签已经在中文语境中常见（如 `"BL"`、`"YAOI"`、`"MLM"`），可保留原样

---

## 二、翻译模块（新增）
对于被判定为「纯英文内容」的字段，执行以下翻译规则：

### 2.1 需要翻译的字段
| 字段 | 翻译说明 |
|------|---------|
| `data.description` | 完整翻译为简体中文，保留`{{user}}`占位符原样 |
| `data.personality` | 完整翻译为简体中文，保留`{{user}}`占位符原样 |
| `data.scenario` | 完整翻译为简体中文，保留`{{user}}`占位符原样 |
| `data.first_mes` | 完整翻译为简体中文，保留`{{user}}`占位符和动作格式`*...*`原样 |
| `data.tags` | 将英文标签逐个翻译为中文（常见梗标签如`BL`/`YAOI`/`MLM`可保留） |

### 2.2 翻译质量要求
- 保留角色原本的语气和性格特征（cocky、teasing 等翻译成对应的中文表达）
- 场景描写要自然流畅，不能生硬直译
- 对话部分（`first_mes`中的引号内容）要翻译得像人物自然说出的中文
- 动作描写（`*...*`包裹的内容）翻译后保留星号格式
- `{{user}}` 占位符保持原样，**不得翻译或替换**

### 2.3 翻译风格
- 整体采用**口语化、自然的中文**，适合角色扮演场景
- 保留角色的个性：自信、挑逗感要传达出来
- 不损失细节（身高、外貌、场景设定等）

---

## 三、转换规则（原有，增强版）

### 3.1 结构标准化
确保JSON顶层包含：
```json
{
  "spec": "chara_card_v2",
  "spec_version": "2.0",
  "data": { ... }
}
```

### 3.2 字段补齐与修复
| 字段 | 说明 |
|------|------|
| `name` | 保留原名，无需翻译 |
| `description` | **若检测为英文 → 翻译为中文** |
| `personality` | **若检测为英文 → 翻译为中文** |
| `scenario` | **若检测为英文 → 翻译为中文** |
| `first_mes` | **若检测为英文 → 翻译为中文** |
| `tags` | **若检测为英文 → 逐个翻译为中文** |
| `alternate_greetings` | 若原卡有则保留；没有则设为空数组 |
| `system_prompt` | 保持原样（此为AI指令，通常不翻译） |
| `post_history_instructions` | 保持原样 |
| `creator_notes` | 保持原样 |
| `creator` | 保持原样 |
| `character_version` | 补全为 `"1.0"`（若缺失） |
| `extensions` | 补全为空对象 `{}` |
| `metadata` | 补全标准化metadata |

### 3.3 严格化处理
- 所有字符串类型字段必须是 `string`，不能是 `null` 或其他类型
- 标签必须是字符串数组
- 删除多余空白和异常转义符号
- JSON 序列化时使用 `ensure_ascii=False` 确保中文可读

---

## 四、AI执行流程（零外部依赖）

> **本技能不依赖任何外部脚本文件**，所有提取与转换逻辑由AI通过终端内联执行。

### 4.1 收到用户输入时的标准流程

```
用户上传PNG角色卡
    │
    ▼
Step 1: 终端运行内联脚本，提取PNG数据 + 语言检测
    ├─ 命令: python3 << 'PYEOF'
    │        (完整提取+检测脚本见下方 4.2)
    └─ 输出: 角色名、需翻译字段列表、各字段长度
    │
    ▼
Step 2: AI读取终端输出，对纯英文字段进行翻译
    ├─ description → 翻译为中文，保留{{user}}占位符
    ├─ personality → 翻译为中文
    ├─ scenario   → 翻译为中文
    ├─ first_mes  → 翻译为中文，保留*动作*和引号格式
    └─ tags       → 翻译为中文标签（常见梗标签如BL/YAOI/MLM可保留）
    │
    ▼
Step 3: 构建V2结构并写入文件
    ├─ 文件名: /sdcard/Download/{角色名}_V2_card_CN.json
    ├─ 编码: UTF-8, ensure_ascii=False
    └─ metadata.note = "已进行中文翻译"
```

### 4.2 PNG提取与语言检测（内联脚本模板）

AI在终端中执行提取+检测时，使用以下内联Python脚本：

```python
python3 << 'PYEOF'
import struct, base64, json, re
p = sys.argv[1] if len(sys.argv) > 1 else input("路径: ").strip()
# 提取tEXt/zTXt chunk
with open(p, "rb") as f:
    d = f.read()
pos = 8
raw = None
while pos < len(d):
    l, ct = struct.unpack('>I', d[pos:pos+4])[0], d[pos+4:pos+8].decode()
    cd = d[pos+8:pos+8+l]
    pos += 12 + l
    for pre in [b'chara\x00', b'ccv3\x00', b'text\x00']:
        if ct in ('tEXt','zTXt') and cd.startswith(pre):
            import zlib
            raw = (base64.b64decode if ct=='tEXt' else zlib.decompress)(cd[len(pre):])
            raw = raw.decode('utf-8')
            break
    if raw:
        break
if not raw:
    print("❌ 未找到角色卡数据"); exit(1)
o = json.loads(raw); i = o.get('data', o) if 'spec' in o else o
need = []
for f in ['description','personality','scenario','first_mes']:
    v = i.get(f,'') or ''
    if v.strip() and not re.search(r'[\u4e00-\u9fff]', v[:100]):
        need.append(f)
tags = i.get('tags',[])
if tags and not re.search(r'[\u4e00-\u9fff]', ','.join(tags)[:100]):
    need.append('tags')
print(f"📛 {i.get('name','?')}")
print(f"🔍 需翻译: {','.join(need) if need else '无'}")
for f in ['description','personality','scenario','first_mes']:
    print(f"  {f}: {len(i.get(f,'') or '')} 字")
PYEOF
```

### 4.3 构建V2并输出_CN文件（内联脚本模板）

AI翻译完成后，使用此脚本构建最终文件：

```python
python3 << 'PYEOF'
import json
# AI将翻译后的字段填入此处
TRANSLATIONS = {
    # "description": "翻译后内容",
    # "personality": "翻译后内容",
    # "scenario": "翻译后内容",
    # "first_mes": "翻译后内容",
    # "tags": ["中文标签1", "中文标签2"]
}
DATA = json.loads("""{...}""")  # AI填入翻译前的原始JSON
for k, v in TRANSLATIONS.items():
    if k == 'tags':
        DATA['tags'] = v
    else:
        DATA[k] = v
v2 = {"spec": "chara_card_v2", "spec_version": "2.0", "data": {
    **DATA,
    "character_version": "1.0",
    "alternate_greetings": DATA.get("alternate_greetings", []),
    "extensions": DATA.get("extensions", {}),
    "metadata": {**DATA.get("metadata", {}), "note": "已进行中文翻译",
        "tool": {"name": "Operit Skill Converter", "version": "1.0.0"}}
}}
import re
name = re.sub(r'[^\u4e00-\u9fff\w]', '', DATA.get("name","Unknown")).strip() or "Unknown"
out = f"/sdcard/Download/{name}_V2_card_CN.json"
with open(out, "w", encoding="utf-8") as f:
    json.dump(v2, f, ensure_ascii=False, indent=2)
print(f"✅ {out}")
PYEOF
```

## 五、输出格式
- **英文原版卡**：`/sdcard/Download/{角色名}_V2_card.json`
- **中文翻译版卡**：`/sdcard/Download/{角色名}_V2_card_CN.json`（若检测为英文并翻译后，在原文件名后添加`_CN`）
- **中/中英混合版卡**：`/sdcard/Download/{角色名}_V2_card.json`（无需翻译，保持原文件名）
- 编码：UTF-8，`ensure_ascii=False`
- 缩进：2 spaces

## 六、注意事项
1. 中文翻译要保留原角色卡的感情色彩，不能机械翻译
2. 如果用户提供的是中文描述或中文角色卡，不要重复翻译
3. 翻译后的 `first_mes` 必须仍然是可用的开场白格式
4. 遇到不确定的翻译时，优先保留原术语 + 中文注释
5. 翻译完所有字段后，在最终输出中注明「已进行中文翻译」
