---
name: "角色卡转换"
version: "2.1.0"
description: "转换角色卡（含多语种检测+翻译、智能字段拆分补齐、昵称自动生成、PNG回嵌，V3格式输出）"
---

# Skill: 角色卡转换（智能拆分补齐版，V3格式输出）

## 概述
本技能用于将任意来源的角色卡**统一转换为符合Tavo v0.87+严格规范的完整V3角色卡**。
**核心特性**：
- 自动检测非中文内容并翻译为简体中文
- **智能拆分**：将 description/personality/scenario 中的冗余内容拆分到正确的功能字段
- **Description增强**：检查 description 外貌+身份子项完整性，缺失项自动补齐（详见 `SKILL_description_enhancer.md`）
- **智能补齐**：对缺失字段（system_prompt、post_history_instructions、tags、creator、creator_notes、mes_example、nickname）自动推演生成
- **昵称自动生成**：从角色名提取翻译后的全名作为昵称（不拆分多个）
- 支持PNG Base64自动解码与回嵌

## 触发条件
用户提供：角色卡PNG / JSON文件 / 纯JSON文本

---

## 前置检查

### 0.1 输入格式判断（最高优先级）

| 输入类型 | 判断依据 | 处理路径 |
|---------|---------|---------|
| **PNG角色卡** | `.png`后缀，含`chara`/`ccv3`/`text` chunk | 提取→Base64解码→翻译→拆分补齐→回嵌 |
| **JSON角色卡** | `.json`后缀或以`{`开头 | 读取→翻译→拆分补齐→输出JSON |

### 0.2 Base64检测
提取chara原始数据后：不以`{`或`[`开头 → Base64解码后再解析。

---

## 一、语言检测与翻译模块

### 1.1 检测规则
对所有文本字段，用正则 `[\u4e00-\u9fff]` 统计中文字符占比（去空白后）：
- **中文占比 ≥ 5%** → 已是中文，**不翻译**
- **中文占比 < 5%** → 视为非中文（英文/西班牙语/日语等），**翻译为简体中文**

### 1.2 翻译字段
`description`、`personality`、`scenario`、`first_mes`、`tags`、`system_prompt`（如有内容）、`post_history_instructions`（如有内容）。

### 1.3 翻译要求
- 保留`{{user}}`、`{{char}}`占位符原样
- 保留`*...*`动作格式和`"..."`对话格式
- 口语化、自然的中文，保留角色个性
- 不损失任何细节

---

## 二、智能字段拆分模块（核心新增）

> **原则：有内容则不动，只翻译；无内容则从其他字段拆分填充。拆分只移动内容到能发挥其作用的字段。**

### 2.1 各字段的功能定义

| 字段 | 应存放内容 | 不应存放内容 |
|------|-----------|-------------|
| `description` | **外貌描写 + 基础身份**（身高体重、面容、体型、生殖器、体毛、气味、职业年龄国籍） | 性格、世界观、RP规则 |
| `personality` | **性格特质 + 行为模式**（战场/私下/对{{user}}的态度、缺陷、优势、习惯、代表性台词） | 外貌、世界观设定 |
| `scenario` | **世界观 + 当前场景上下文**（时代背景、角色定位、与{{user}}的关系历史、当前场景描述） | 外貌细节、RP指令 |
| `first_mes` | **开场白**（角色第一句话，含动作描写） | — |
| `system_prompt` | **角色扮演规则**（说话风格、行为准则、禁止事项） | 世界观、外貌 |
| `post_history_instructions` | **对话后指令**（回复格式、长度控制、风格约束） | — |
| `mes_example` | **对话示例**（`<START>{{char}}: ...<END>` 格式，5段左右） | — |
| `tags` | **标签数组**（从内容提取的关键词） | — |
| `creator` | **创建者**（从metadata提取或标记来源） | — |
| `creator_notes` | **创建者备注**（记录转换过程） | — |
| `nickname` | **昵称**（角色翻译后的全名，不拆分多个，不用分号分隔） | — |

### 2.2 拆分规则

AI读取翻译后的全部内容，按以下优先级判断：

```
Step A: 检查 description 是否混入了性格/世界观/RP规则
  ├─ 有 → 提取性格部分 → 合并到 personality（如personality为空则填充，有则保留原样）
  ├─ 有 → 提取世界观部分 → 合并到 scenario
  └─ 有 → 提取RP规则 → 合并到 system_prompt

Step B: 检查 personality 是否混入了外貌/世界观/RP规则
  ├─ 有 → 提取外貌 → 合并到 description
  ├─ 有 → 提取RP规则 → 合并到 system_prompt
  └─ 有 → 提取图片链接/HTML → 清理或保留在末尾

Step C: 检查 scenario 是否混入了外貌/性格/RP规则
  ├─ 有 → 提取性格 → 合并到 personality
  └─ 有 → 提取RP规则 → 合并到 system_prompt

Step D: 精简各字段
  ├─ description → 仅保留外貌+身份，删除性格/世界观/RP相关内容
  ├─ personality → 仅保留性格+行为模式，删除外貌描写
  └─ scenario → 仅保留世界观+场景，删除外貌细节
```

### 2.3 拆分后的字段状态

| 字段 | 拆分后内容 |
|------|-----------|
| `description` | 精简为：外貌（身高体重皮肤面容躯干四肢生殖器体毛气味）+ 身份概述（名/龄/籍/职） |
| `personality` | 精简为：性格特质 + 行为模式 + 缺陷 + 优势 + 习惯 + 代表性台词 |
| `scenario` | 精简为：世界观 + 角色定位 + 当前场景 + 与{{user}}关系 |

---

## 三、智能补齐模块（核心新增）

> **原则：字段有内容（非空字符串/非null/非空数组）则不动；无内容则自动推演生成。**

### 3.1 补齐决策表

| 字段 | 条件 | 动作 |
|------|------|------|
| `system_prompt` | 为空/null | 从 personality + first_mes 推演生成 |
| `post_history_instructions` | 为空/null | 从 system_prompt + personality 推演生成 |
| `tags` | 为空/null/空数组 | 从全部内容提取关键词生成（8-15个标签） |
| `creator` | 为空/null | 从 metadata.tool.name 提取，或标记 "Unknown" |
| `creator_notes` | 为空/null | 记录转换过程（来源、翻译语言、拆分操作） |
| `mes_example` | 为空字符串 | 从 personality + scenario + first_mes 推演5段对话 |
| `nickname` | 为空/null | 从 name 字段提取翻译后的角色全名（如「凯尔」），不拆分多个，不用分号分隔 |
| `character_version` | 缺失 | 补为 `"1.0"` |
| `alternate_greetings` | 缺失 | 补为空数组 `[]` |
| `extensions` | 缺失 | 保留原有或补为 `{}` |

### 3.2 mes_example 推演规则

基于角色卡的 personality + scenario + first_mes，AI推演5段对话示例：

- **格式**：`<START>\n{{char}}: *动作描写*\n对话内容\n<END>`
- **覆盖场景**：
  1. 日常互动（展示角色的日常关怀/习惯）
  2. 角色特色场景（展示角色的独特面，如甜品/束缚/战斗等）
  3. 脆弱时刻（展示角色的不安/创伤）
  4. 核心场景（复现 scenario 中的关键场景）
  5. 温馨收尾（展示角色笨拙的温柔）
- **风格约束**：严格遵循角色的说话方式、语气、用词习惯
- **不替{{user}}说话**：每段只有{{char}}的发言

### 3.3 system_prompt 推演规则

```
## 角色扮演规则
你正在扮演 {角色名}，{一句话身份}。

### 说话风格
- {从personality提取的说话特点}
- 不替{{user}}说话或做决定。

### 行为准则
- {从personality提取的关键行为模式}
- {禁止事项}
```

### 3.4 post_history_instructions 推演规则

```
## 对话后指令
- 保持角色一致性：{核心特质}
- 回复长度根据角色性格推断：阳光开朗型偏长（3-5段），温柔含蓄型适中（2-3段），沉默寡言型偏短（1-2段）
- 动作描写用 *...* 包裹，对话用 "..." 包裹。
- {从内容提取的风格约束}
- 不要替{{user}}做决定或说话。
```

---

## 四、转换规则

### 4.1 V3结构
```json
{
  "spec": "chara_card_v3",
  "spec_version": "3.0",
  "data": { ... }
}
```

### 4.2 完整字段清单（16个核心字段）
`name`, `description`, `personality`, `scenario`, `first_mes`, `mes_example`, `system_prompt`, `post_history_instructions`, `tags`, `creator`, `creator_notes`, `nickname`, `character_version`, `alternate_greetings`, `extensions`, `metadata`

### 4.3 严格化
- 所有字符串字段不能为null，空则用`""`
- tags必须是字符串数组
- `ensure_ascii=False`，UTF-8编码

---

## 五、PNG回嵌模块

### 5.1 回嵌规则
保留原PNG头像（IHDR+IDAT），替换chara chunk为中文V3 JSON。

### 5.2 回嵌脚本（直接定位法）

```python
python3 << 'PYEOF'
import struct, base64, json, zlib

src_png = "原PNG路径"
out_png = "输出PNG路径"
chara_json = {...}  # AI填入完整V3 JSON

with open(src_png, "rb") as f:
    d = f.read()

chara_kw = d.find(b'chara\x00')
chunk_len_start = chara_kw - 8
before = d[:chunk_len_start]

enc = base64.b64encode(json.dumps(chara_json, ensure_ascii=False).encode('utf-8'))
chunk_data = b'chara\x00' + enc
chunk_len = len(chunk_data)
crc = struct.pack('>I', zlib.crc32(b'tEXt' + chunk_data) & 0xffffffff)
new_chara = struct.pack('>I', chunk_len) + b'tEXt' + chunk_data + crc

iend_crc = struct.pack('>I', zlib.crc32(b'IEND') & 0xffffffff)
iend = struct.pack('>I', 0) + b'IEND' + iend_crc

with open(out_png, "wb") as f:
    f.write(before + new_chara + iend)

print(f"✅ 回嵌完成: {out_png}")
PYEOF
```

---

## 六、AI执行流程

### 6.1 完整流程（优化版）

> **核心优化**：Step 2-4 合并为单步，AI 一次性完成翻译+拆分+补齐+昵称生成，直接输出完整 JSON，减少中间文件读写。

```
用户上传角色卡
    │
    ▼
Step 0: 格式判断（PNG/JSON）
    │
    ▼
Step 1: 终端提取 + 语言检测（super_admin:terminal 执行 Python）
    ├─ PNG: 提取 chara chunk → Base64解码 → 解析JSON
    ├─ JSON: 直接读取
    ├─ 输出: 角色名、各字段中文占比、缺失字段列表
    └─ 保存原始JSON到 /tmp/chara_raw.json
    │
    ▼
Step 2: AI一次性完成翻译+拆分+补齐+昵称（合并原Step 2/3/3.5/4）
    ├─ 读取 /tmp/chara_raw.json
    ├─ 对非中文字段翻译为简体中文
    ├─ 清理 HTML 标签（<p>、<strong>、<em>、<img> 等）→ 转为 Markdown
    ├─ 智能拆分：description/personality/scenario 去冗余，内容归位
    ├─ Description增强：检查外貌17项+性爱风格4项+身份5项，缺失补齐
    ├─ 补齐 system_prompt / post_history_instructions / tags / mes_example
    ├─ 生成 nickname：从 name 提取翻译后的角色全名（不拆分多个）
    ├─ 补齐 creator / creator_notes / character_version / alternate_greetings / extensions
    └─ 通过 cat heredoc 写入 /tmp/restructured_data.json
    │
    ▼
Step 3: Python 构建 V3 JSON 并输出
    ├─ 读取 /tmp/restructured_data.json
    ├─ 包装为 {spec, spec_version, data} 结构
    ├─ 输出 JSON → /sdcard/Download/Operit/charactercard/{角色名}_V3_restructured.json
    └─ 确保 JSON 合法（末尾 } 闭合，字符串内 " 转义）
    │
    ▼
[仅PNG输入] Step 4: PNG 回嵌
    ├─ 保留原 PNG 头像（IHDR+IDAT）
    ├─ 替换 chara chunk 为中文 V3 JSON
    └─ 输出 → /sdcard/Download/Operit/charactercard/{角色名}_V3_restructured.png
```

### 6.2 关键注意事项

1. **使用 super_admin:terminal 而非 code_runner**：PNG 文件较大时 code_runner 易超时卡死，terminal 更稳定，建议 timeoutMs=30000
2. **JSON 完整性检查**：输出前必须验证 JSON 合法——常见问题：末尾缺 `}`、字符串内裸双引号未转义
3. **HTML 清理**：JanitorAI 来源的 personality 常含 `<p>`、`<strong>`、`<img>` 等标签，必须转为纯 Markdown
4. **nickname 格式**：仅保留翻译后的角色全名，如 `凯尔`，不用分号分隔多个

### 6.2 提取与检测脚本（Step 1用）

```python
python3 << 'PYEOF'
import struct, base64, json, re

p = "PNG路径"
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
    print("ERROR: no chara"); exit(1)

raw_stripped = raw.strip()
if raw_stripped[0] not in ('{', '['):
    raw = base64.b64decode(raw_stripped).decode('utf-8')
    print("BASE64_DECODED")

o = json.loads(raw)
i = o.get('data', o) if 'spec' in o else o

need = []
for f in ['description','personality','scenario','first_mes']:
    v = i.get(f,'') or ''
    if v.strip():
        cn = len(re.findall(r'[\u4e00-\u9fff]', v))
        total = len(re.sub(r'[\s\n\t]', '', v))
        if cn / max(total, 1) < 0.05:
            need.append(f)

tags = i.get('tags',[])
if tags:
    tag_str = ','.join(tags)
    cn = len(re.findall(r'[\u4e00-\u9fff]', tag_str))
    total = len(re.sub(r'[\s\n\t]', '', tag_str))
    if total > 0 and cn / total < 0.05:
        need.append('tags')

print(f"NAME: {i.get('name','?')}")
print(f"NEED_TRANSLATE: {','.join(need) if need else 'NONE'}")
for f in ['description','personality','scenario','first_mes']:
    print(f"LEN_{f}: {len(i.get(f,'') or '')}")

# 检查缺失字段
for k in ['system_prompt','post_history_instructions','tags','creator','creator_notes','mes_example']:
    v = i.get(k, 'KEY_MISSING')
    if v == 'KEY_MISSING':
        print(f"MISSING: {k}")
    elif isinstance(v, str) and v == '':
        print(f"EMPTY: {k}")
    elif v is None:
        print(f"NULL: {k}")
    elif isinstance(v, list) and len(v) == 0:
        print(f"EMPTY_LIST: {k}")

with open("/tmp/chara_raw.json", "w", encoding="utf-8") as f:
    json.dump(o, f, ensure_ascii=False, indent=2)
print("SAVED: /tmp/chara_raw.json")
PYEOF
```

### 6.3 构建输出脚本（Step 5用）

AI完成翻译+拆分+补齐后，将完整数据写入临时JSON文件，再用Python构建V3：

```python
python3 -c "
import json, re

with open('/tmp/restructured_data.json', 'r', encoding='utf-8') as f:
    DATA = json.load(f)

v3 = {
    'spec': 'chara_card_v3',
    'spec_version': '3.0',
    'data': DATA
}

name_raw = DATA.get('name', 'Unknown')
cleaned = re.sub(r'[^\u4e00-\u9fff\w\d_]', '_', name_raw)
cleaned = re.sub(r'_+', '_', cleaned).strip('_') or 'Unknown'

out = f'/sdcard/Download/Operit/charactercard/{cleaned}_V3_restructured.json'
with open(out, 'w', encoding='utf-8') as f:
    json.dump(v3, f, ensure_ascii=False, indent=2)

print(f'OK: {out}')
print(f'Fields: {len(DATA)}')
"
```

---

## 七、输出格式

| 输入 | 输出 |
|------|------|
| PNG | `/sdcard/Download/Operit/charactercard/{角色名}_V3_restructured.png`（回嵌）+ `.json` |
| JSON | `/sdcard/Download/Operit/charactercard/{角色名}_V3_restructured.json` |

文件名规则：保留中文字符、字母、数字、下划线，其余替换为下划线。

---

## 八、版本历史

| 版本 | 日期 | 变更内容 |
|------|------|---------|
| **v2.1.0** | 2026-06-21 | 🏷️ 新增 nickname 字段自动生成（分号分隔多昵称）；⚡ 合并 Step 2-4 为单步，减少中间文件；📁 输出路径改为 charactercard/；🔧 指定 super_admin:terminal 执行脚本避免超时；🧹 新增 HTML 标签清理规则 |
| **v2.0.0** | 2026-06-14 | 🧠 新增智能字段拆分模块（description/personality/scenario去冗余）；✨ 新增智能补齐模块（system_prompt/post_history_instructions/tags/mes_example自动推演）；🌐 语言检测扩展为通用非中文检测；📋 字段补齐从3个扩展到10+个；🔧 重写执行流程为6步完整管线 |
| v1.1.0 | 2026-06-12 | Base64解码、占比阈值、V3格式、PNG回嵌修复 |
| v1.0.0 | 2026-05-26 | 初始版本 |

---

## 九、注意事项
1. **有则不动**：字段已有内容（非空）则只翻译，不拆分不覆盖
2. **拆分只移动**：从冗余字段提取内容到空字段，不凭空创造角色信息
3. **mes_example严格遵循角色设定**：不OOC，不替{{user}}说话
4. 翻译保留感情色彩，口语化自然
5. `{{user}}`和`{{char}}`占位符永不翻译
6. V3格式必须`chara_card_v3`+`spec_version: 3.0`
7. PNG回嵌保留原头像
8. 输出文件编码UTF-8，`ensure_ascii=False`