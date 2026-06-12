---
name: "角色卡转换"
version: "1.1.0"
description: "转换角色卡（含中英检测+自动翻译，支持PNG Base64自动解码，V3格式输出）"
---

# Skill: 角色卡转换（中英文双语支持版，V3格式输出）

## 概述
本技能用于将任意来源的角色卡（SillyTavern V1/V2/V3、TavernAI、Character.AI JSON等）**统一转换为符合Tavo v0.87+严格规范的V3角色卡**。
**核心特性**：自动检测角色卡内容的语言（中文/英文），对纯英文内容翻译为简体中文，输出V3格式PNG角色卡。

## 触发条件
用户提供：
- 角色卡JSON文件内容或片段
- 角色卡PNG（内含JSON，支持Base64编码）
- 或简单描述角色信息（此时需先按标准流程生成V3卡）

## 前置检查

### 0.1 输入格式判断（最高优先级）
AI收到用户上传的角色卡时，**首先**判断输入格式，决定后续处理路径：

| 输入类型 | 判断依据 | 处理路径 |
|---------|---------|---------|
| **PNG角色卡** | 文件后缀为 `.png`，且PNG中包含`chara`/`ccv3`/`text`元数据chunk | PNG路径：提取→**Base64检测与解码**→检测→翻译→**回嵌** |
| **JSON角色卡** | 文件后缀为 `.json`，或内容以 `{` 开头 | JSON路径：读取→检测→翻译→输出JSON |
| **纯JSON文本** | 用户直接在消息中粘贴JSON内容 | JSON路径：解析→检测→翻译→输出JSON |

**PNG路径关键补充**：提取chara字段的原始数据后，**必须先检测是否为Base64编码**：
- 若原始字符串以 `{` 或 `[` 开头 → 明文JSON，直接解析
- 若原始字符串不以 `{` 或 `[` 开头 → 尝试Base64解码后再解析JSON
- 常见情况：SillyTavern导出的PNG角色卡，chara字段存储的是**Base64编码的JSON字符串**，需先`base64.b64decode()`再`json.loads()`

### 0.2 内容确认
1. **确认输入格式**：是否为有效JSON？
2. **识别来源**：SillyTavern / TavernAI / Character.AI / 其他
3. **保留核心信息**：name, description, personality, scenario, first_mes, mes_example, alternate_greetings, tags, creator_notes 等

---

## 一、语言检测模块

在开始转换前，**必须**对角色卡的以下字段进行语言检测：

### 1.1 需要检测的字段
- `description`
- `personality`
- `scenario`
- `first_mes`
- `tags`（标签数组，逐个检测）

### 1.2 检测规则（含中文占比阈值）
1. 取每个字段的完整内容
2. 用正则表达式 `[\u4e00-\u9fff]` 统计中文字符数量
3. 计算中文字符占字段总字符数（去空白）的比例
4. 判定标准：
   - **中文占比 ≥ 5%** → 判定为「中文/中英混合内容」，**不需要翻译**
   - **中文占比 < 5%** → 判定为「纯英文内容」（可能含角色名等零星中文），**需要翻译为简体中文**
5. **重要**：不能仅凭"是否包含中文字符"判断——角色名（如"徐元"）可能出现在英文description中，占比极低（<1%），应视为英文内容翻译

### 1.3 例外处理
- 如果 `first_mes` 中包含角色名称（如 `"Andy"`、`{{user}}` 等占位符），这些不视为英文，不触发翻译需求
- `tags` 字段中如果某个标签已经在中文语境中常见（如 `"BL"`、`"YAOI"`、`"MLM"`），可保留原样

---

## 二、翻译模块

对于被判定为「纯英文内容」的字段，执行以下翻译规则：

### 2.1 需要翻译的字段
| 字段 | 翻译说明 |
|------|---------|
| `description` | 完整翻译为简体中文，保留`{{user}}`占位符原样 |
| `personality` | 完整翻译为简体中文，保留`{{user}}`占位符原样 |
| `scenario` | 完整翻译为简体中文，保留`{{user}}`占位符原样 |
| `first_mes` | 完整翻译为简体中文，保留`{{user}}`占位符和动作格式`*...*`原样 |
| `tags` | 将英文标签逐个翻译为中文（常见梗标签如`BL`/`YAOI`/`MLM`可保留） |

### 2.2 翻译质量要求
- 保留角色原本的语气和性格特征
- 场景描写要自然流畅，不能生硬直译
- 对话部分要翻译得像人物自然说出的中文
- 动作描写（`*...*`包裹的内容）翻译后保留星号格式
- `{{user}}` 占位符保持原样，**不得翻译或替换**

### 2.3 翻译风格
- 整体采用**口语化、自然的中文**，适合角色扮演场景
- 保留角色的个性：自信、挑逗感要传达出来
- 不损失细节（身高、外貌、场景设定等）

---

## 三、转换规则

### 3.1 结构标准化（V3格式）
**输出必须使用V3格式**（Tavo v0.87+兼容）：
```json
{
  "spec": "chara_card_v3",
  "spec_version": "3.0",
  "data": { ... }
}
```
> **关键发现**：v0.87仅识别`chara_card_v3`+`spec_version: 3.0`格式。扁平结构或V2格式会导致"未检测到PNG元数据"错误。

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
- 所有字符串类型字段必须是 `string`，不能是 `` 或其他类型
- 标签必须是字符串数组
- 删除多余空白和异常转义符号
- JSON 序列化时使用 `ensure_ascii=False` 确保中文可读

---

## 四、PNG回嵌模块

> 输入格式判断已移至「前置检查 → 0.1 输入格式判断」，此处仅保留PNG回嵌相关逻辑。

### 4.1 PNG回嵌规则
当输入为PNG角色卡时，最终输出的中文版角色卡**回嵌到原PNG的头像图像中**，生成带有原头像的PNG格式角色卡：

1. **保留原PNG头像图像**（IHDR + IDAT chunk 保持不变）
2. **替换/添加chara数据**：在IDAT之后、IEND之前，写入`tEXt` chunk，key为`chara`，value为base64编码的中文V3 JSON数据
3. **输出文件名**：遵循原有命名规则，后缀为 `.png`（如`{清理后角色名}_V2_card_CN.png`）

### 4.2 PNG回嵌（内联脚本模板，已验证通过）
AI使用以下内联Python脚本将V3中文JSON数据回嵌到PNG中。
**核心原则**：直接定位原chara chunk的起始位置，取其之前的所有数据 + 新chara chunk + 标准IEND，避免遍历chunk导致的偏移bug。

```python
python3 << 'PYEOF'
import struct, base64, json, zlib

src_png = "输入的原PNG路径"           # AI替换为实际路径
out_png = "输出的中文PNG路径"          # AI替换为实际路径
chara_json = {...}                    # AI填入完整的V3中文JSON对象

with open(src_png, "rb") as f:
    d = f.read()

# 直接定位原chara chunk的length字段位置
chara_kw = d.find(b'chara\x00')
chunk_len_start = chara_kw - 8       # length(4) + type(4) = 8字节在key之前
before = d[:chunk_len_start]          # chara之前的所有数据（header + IHDR + IDAT）

# 构建新chara chunk
enc = base64.b64encode(json.dumps(chara_json, ensure_ascii=False).encode('utf-8'))
chunk_data = b'chara\x00' + enc
chunk_len = len(chunk_data)
crc = struct.pack('>I', zlib.crc32(b'tEXt' + chunk_data) & 0xffffffff)
new_chara = struct.pack('>I', chunk_len) + b'tEXt' + chunk_data + crc

# 构建标准IEND（12字节）
iend_crc = struct.pack('>I', zlib.crc32(b'IEND') & 0xffffffff)
iend = struct.pack('>I', 0) + b'IEND' + iend_crc

# 拼接：before + 新chara + IEND（IEND之后不拼任何数据）
with open(out_png, "wb") as f:
    f.write(before + new_chara + iend)

print(f"✅ 回嵌完成: {out_png}")
PYEOF
```

> **踩坑记录**：旧版回嵌脚本使用遍历chunk+拼接方式，导致IEND被截断4字节、tEXt key变成`a`而非`chara`。直接定位法彻底解决此问题。

---

## 五、AI执行流程（零外部依赖，含格式判断）

> **本技能不依赖任何外部脚本文件**，所有提取与转换逻辑由AI通过终端内联执行。

### 5.1 完整执行流程

```
用户上传角色卡
    │
    ▼
Step 0: 格式判断（见前置检查0.1）
    ├─ .png → PNG路径（走完整提取→翻译→回嵌流程）
    └─ .json / 纯JSON文本 → JSON路径（走读取→翻译→输出JSON流程）
    │
    ▼
[PNG路径]
Step 1: 终端运行内联脚本，提取PNG角色卡数据 + 语言检测
    ├─ 命令: python3 << 'PYEOF'（提取+检测脚本见5.2）
    └─ 输出: 角色名、需翻译字段列表、各字段长度
    │
Step 2: AI读取终端输出，对纯英文字段进行翻译
    ├─ description → 翻译为中文
    ├─ personality → 翻译为中文
    ├─ scenario   → 翻译为中文
    ├─ first_mes  → 翻译为中文（保留*动作*和引号格式）
    └─ tags       → 翻译为中文标签
    │
Step 3: 构建V3结构（脚本见5.3），生成中间JSON
    ├─ 输出: /sdcard/Download/{清理后角色名}_V2_card_CN.json（中间文件）
    └─ metadata.note = "已进行中文翻译"
    │
Step 4: 回嵌到PNG
    ├─ 命令: python3 << 'PYEOF'（PNG回嵌脚本见4.2）
    ├─ 输入: 原PNG路径 + 中文V3 JSON
    └─ 输出: /sdcard/Download/{清理后角色名}_V2_card_CN.png ✅
    │
    ▼
[JSON路径]
Step 1: 读取JSON + 语言检测
    ├─ JSON文件 → 解析为数据结构
    └─ 检测各字段：检测规则同第一章
    │
Step 2: AI对纯英文字段进行翻译（同PNG路径Step 2）
    │
Step 3: 构建V3结构并写入文件（脚本见5.3）
    ├─ 文件: /sdcard/Download/{清理后角色名}_V2_card_CN.json ✅
    ├─ 编码: UTF-8, ensure_ascii=False
    └─ metadata.note = "已进行中文翻译"
```

### 5.2 PNG提取与语言检测（内联脚本模板）

AI在终端中执行提取+检测时，使用以下内联Python脚本：

```python
python3 << 'PYEOF'
import struct, base64, json, re, sys
p = sys.argv[1] if len(sys.argv) > 1 else input("路径: ").strip()
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
# === Base64自动检测与解码 ===
raw_stripped = raw.strip()
if raw_stripped[0] not in ('{', '['):
    try:
        raw = base64.b64decode(raw_stripped).decode('utf-8')
        print("🔓 检测到Base64编码，已自动解码")
    except Exception:
        print("❌ 数据不是有效JSON也不是Base64编码"); exit(1)
o = json.loads(raw); i = o.get('data', o) if 'spec' in o else o
# === 语言检测（含中文占比阈值） ===
need = []
for f in ['description','personality','scenario','first_mes']:
    v = i.get(f,'') or ''
    if v.strip():
        cn = len(re.findall(r'[\u4e00-\u9fff]', v))
        total = len(re.sub(r'[\s\n\t]', '', v))
        ratio = cn / max(total, 1)
        if ratio < 0.05:  # 中文占比<5%视为英文
            need.append(f)
tags = i.get('tags',[])
if tags:
    tag_str = ','.join(tags)
    cn = len(re.findall(r'[\u4e00-\u9fff]', tag_str))
    total = len(re.sub(r'[\s\n\t]', '', tag_str))
    if total > 0 and cn / total < 0.05:
        need.append('tags')
print(f"📛 {i.get('name','?')}")
print(f"🔍 需翻译: {','.join(need) if need else '无'}")
for f in ['description','personality','scenario','first_mes']:
    print(f"  {f}: {len(i.get(f,'') or '')} 字")
PYEOF
```

### 5.3 构建V3并输出（内联脚本模板）

AI翻译完成后，使用此脚本构建最终文件：

```python
python3 << 'PYEOF'
import json, re
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
v3 = {"spec": "chara_card_v3", "spec_version": "3.0", "data": {
    **DATA,
    "character_version": "1.0",
    "alternate_greetings": DATA.get("alternate_greetings", []),
    "extensions": DATA.get("extensions", {}),
    "metadata": {**DATA.get("metadata", {}), "note": "已进行中文翻译",
        "tool": {"name": "Operit Skill Converter", "version": "1.1.0"}}
}}
name_raw = DATA.get("name","Unknown")
cleaned = re.sub(r'[^\u4e00-\u9fff\w\d_]', '_', name_raw)
cleaned = re.sub(r'_+', '_', cleaned).strip('_') or 'Unknown'
out = f"/sdcard/Download/{cleaned}_V2_card_CN.json"
with open(out, "w", encoding="utf-8") as f:
    json.dump(v3, f, ensure_ascii=False, indent=2)
print(f"✅ {out}")
PYEOF
```

## 六、输出格式

### 6.1 PNG输入（含角色卡数据的PNG）
- **输出类型**：PNG（保留原头像图像，替换角色卡数据）
- **文件名**：`/sdcard/Download/{清理后角色名}_V2_card_CN.png`
- **回嵌方式**：在PNG的IDAT chunk之后、IEND之前写入`tEXt` chunk（key=`chara`，value为base64编码的中文V3 JSON）

### 6.2 JSON输入（纯文本JSON文件）
- **英文原版卡**（无需翻译）：`/sdcard/Download/{清理后角色名}_V2_card.json`
- **中文翻译版卡**（需翻译）：`/sdcard/Download/{清理后角色名}_V2_card_CN.json`
- **中/中英混合版卡**（无需翻译）：`/sdcard/Download/{清理后角色名}_V2_card.json`
- 编码：UTF-8，`ensure_ascii=False`
- 缩进：2 spaces

### 6.3 通用规则
- 文件名中的`{清理后角色名}`：保留中文字符、字母、数字、下划线，其余字符替换为下划线，多余下划线合并
- 若检测为纯英文并翻译后，文件名添加`_CN`后缀
- 若检测为中文/中英混合，不添加`_CN`后缀

## 七、版本历史

| 版本 | 日期 | 变更内容 |
|------|------|---------|
| **v1.1.0** | 2026-06-12 | 🔓 新增PNG Base64自动检测与解码；📋 输入格式判断提升至前置检查最高优先级；🔧 语言检测改为中文占比阈值（<5%视为英文）；📐 输出格式升级为V3（`chara_card_v3`）；🩹 修复PNG回嵌IEND截断bug（直接定位法） |
| **v1.0.0** | 2026-05-26 | 🎉 初始版本：中英检测 + 自动翻译 + PNG回嵌 |

## 八、注意事项
1. 中文翻译要保留原角色卡的感情色彩，不能机械翻译
2. 如果用户提供的是中文描述或中文角色卡，不要重复翻译
3. 翻译后的 `first_mes` 必须仍然是可用的开场白格式
4. 遇到不确定的翻译时，优先保留原术语 + 中文注释
5. 翻译完所有字段后，在最终输出中注明「已进行中文翻译」
6. PNG回嵌时务必保留原头像图像数据（IHDR + IDAT chunks），仅替换chara数据
7. PNG输出时清理文件名中的特殊符号，确保文件名合法
8. **输出必须使用V3格式**（`chara_card_v3` + `spec_version: 3.0`），否则v0.87无法识别
9. **语言检测使用占比阈值**（<5%视为英文），避免角色名等零星中文导致整段英文被跳过
