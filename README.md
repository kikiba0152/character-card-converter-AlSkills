# 角色卡转换 Skill v2.5.0

> 将任意来源（PNG 内嵌 / SillyTavern 导出 / JSON）的角色卡统一转换为符合 Tavo v0.87+ 规范的完整 **V3 中文角色卡**。

一个 **题材中立** 的通用转换底座：只做「结构统一 + 字段归位 + 翻译 + 留白」，不注入任何带题材立场的增强。

---

## 特性

| 能力 | 说明 |
|------|------|
| **奥卡姆元铁律** | 成品只保留对角色扮演有直接贡献的内容；判定依据、版本号、AI 痕迹一律不入卡 |
| **性别中性原则** | 不假设 / 不强加 / 不刻板化 / 不替换，无证据即留白 |
| **证据型补齐** | 仅从当前原卡其他字段归位或概括；补齐禁区明确（不编造数值、不发明身份、不预设身体） |
| **格式覆盖** | PNG（`tEXt` / `iTXt`，含无换行 Base64）、JSON、V1 / V2 / V3 升级 |
| **多语种** | 中 / 英 / 日 / 韩检测后翻译，专有名词保留，格式与术语一致 |
| **智能字段拆分** | 按显式标题与语义段落归位；归属不明则暂留原字段，避免误拆 |
| **PNG 回嵌** | 脚本化处理，自动清旧 `chara` chunk 并校验 `IHDR` / `IDAT` / `IEND` |

---

## 安装

1. 把本目录整体放到 `/sdcard/Download/Operit/skills/角色卡转换/`
2. 确认该目录内存在 `SKILL.md`
3. 在 Operit 的 Skill 列表中开启

> 目录名可以改，但必须保证 `<skills>/角色卡转换/SKILL.md` 这个层级关系。

---

## 目录结构

```text
角色卡转换/
├── SKILL.md                      # 主文档（frontmatter + 全部规则）
├── SKILL_description_enhancer.md # 连带模块：Description 通用增强
├── assets/
│   └── Skill.md                  # 历史参考（Tavo V2 版说明）
└── scripts/
    ├── read_png_chara.py         # 提取 PNG 内嵌 chara JSON
    ├── embed_chara_to_png.py     # JSON 写回 PNG 并校验
    └── occam_selfcheck.py        # §0 元铁律自检
```

---

## 执行流程

```text
1. 接收输入（附件 / 文本）
2. 判定格式（PNG / JSON / V1 / V2 / V3）
3. 提取数据          → scripts/read_png_chara.py
4. 检测语言
5. 翻译（如需）
6. 字段拆分
7. 字段补齐（仅证据型）
8. 标准化为 V3
9. 奥卡姆自检        → scripts/occam_selfcheck.py
10. 输出 JSON
11. PNG 回嵌（如原为 PNG）→ scripts/embed_chara_to_png.py
12. 最终校验（脚本内自动完成）
```

**禁止事项**：不要在终端里手写 PNG chunk 处理代码，一律调用脚本。

---

## 脚本用法

```bash
# 提取 PNG 内嵌角色卡
python3 scripts/read_png_chara.py <png> [--out <json>] [--summary]

# 自检（§0 元铁律）
python3 scripts/occam_selfcheck.py <json_path>

# 回嵌到 PNG
python3 scripts/embed_chara_to_png.py <src_png> <out_png> <json_path>
python3 scripts/embed_chara_to_png.py <src_png> <out_png> --stdin < new_card.json
```

退出码 `0` = 成功，非 `0` = PNG 非法或自检未通过。

---

## 与专题 Skill 的关系

主 Skill **只承担通用转换**。任何带题材立场的增强（Bara 兽人维度、肌肉描写强化、机甲扩展等）必须由专题 Skill 显式承担：

- **`角色卡转换_Bara` → 已独立**，维护在 `skill/bara` 分支（v2.0.0-standalone），自带完整脚本，**不再依赖本目录**。
- 主目录下的 `SKILL_description_enhancer.md` 为连带模块，受 §1.0.1 / §1.0.2 约束。

---

## 版本

| 版本 | 变更 |
|:---:|------|
| **v2.5.0** | 通用化重构：性别中性、证据型补齐、专题边界、Description 通用增强；输出改为"结构统一、内容自适应"。文档修订：§十 重复的「5. 零奥卡姆违规」条目已合并（纯编号修复，无行为变更） |
| v2.4.0 | 沉淀辅助脚本（read_png_chara / embed_chara_to_png / occam_selfcheck）至 `scripts/`；§七 / §八 改为引用脚本；禁止手写 PNG chunk 代码 |
| v2.3.2-occam | 奥卡姆元铁律统辖；结构精简；删除冗余范本 |
| v2.3.1 | 智能字段拆分模块 |
| v2.3.0 | 多语种检测翻译 |
| v2.2.0 | V1 / V2 升级支持 |
| v2.1.0 | PNG 回嵌 |
| v2.0.0 | V3 标准输出 |

---

## 许可

见 [LICENSE](LICENSE)。
