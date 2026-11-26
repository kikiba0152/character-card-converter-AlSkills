# 角色卡转换_Bara v2.0.0-standalone

> **独立运行**的 Bara 特化版 V3 角色卡转换器。自带完整脚本，**不依赖** `角色卡转换` 主 Skill。

在通用 V3 框架上叠加高颗粒度的 Bara 审美与兽人机制，输出 **JSON 骨架 + Markdown 内容**。

---

## 独立性说明

v2.0.0 起本 Skill 从主 Skill 解耦：

| 项目 | 说明 |
|------|------|
| 脚本 | PNG 读写、奥卡姆自检、Bara 专项自检全部在本目录 `scripts/` 内，跨目录相对引用已全部移除 |
| 规则 | 不再继承主 Skill 的「无证据留白 / 题材中立」约束 |
| 运行 | 即使删除 `角色卡转换` 目录，本 Skill 仍可完整工作 |

### 优先级裁决

```text
用户明确要求 > 本 Skill §0 奥卡姆元铁律 > 原卡显式硬设定 > Bara 维度补齐 > 通用留白
```

- **Bara 维度补齐属于领域增强，不视为臆造**：原卡缺失六大肌群、体毛、气味、Knot / Rut 等维度时按规范补齐，不留白。
- **不得覆盖原卡显式硬设定**：明确写的性向、物种（非兽人）、年龄、明确禁区、明确尺寸数值，一律尊重原文。
- 冲突时以「不破坏原卡角色一致性」为最终判据。

---

## 安装

1. 把本目录整体放到 `/sdcard/Download/Operit/skills/角色卡转换_Bara/`
2. 确认目录内存在 `SKILL.md`
3. 在 Operit 的 Skill 列表中开启

> 与主 Skill 可同时存在，互不干扰。

---

## 目录结构

```text
角色卡转换_Bara/
├── SKILL.md                            # 主文档
├── SKILL_description_enhancer.md       # 通用 Description 增强（连带模块）
├── SKILL_description_enhancer_Bara.md  # Bara 版 Description 增强
├── SKILL_description_skeleton.md       # 骨架说明
├── examples/
│   └── skeleton_template.json          # V3 输出骨架
├── assets/
│   └── Skill.md                        # 历史参考
└── scripts/
    ├── read_png_chara.py               # PNG 内嵌 chara 提取
    ├── embed_chara_to_png.py           # JSON 回嵌 PNG 并校验
    ├── occam_selfcheck.py              # §0 元铁律自检
    └── bara_selfcheck.py               # Bara 专题自检（肌群/兽人/体毛/标签）
```

---

## 转换维度

| 维度 | 规范 |
|------|------|
| **六大肌群** | 胸 / 背 / 肩 / 臂 / 腹 / 腿，顺序固定，每块 ≥ 30 字符且含形态·体积·肌理·可视线索 4 维；按体型（精壮 / 健美 / 熊系 / 瘦肌肉 / 脂包肌）适配强度 |
| **体毛地图** | 胸 / 腹 / 阴部 / 腿 / 腋 5 区全覆盖，按设定写浓密或稀疏，不强行统一 |
| **气味与汗液** | 主味 + 辅味 + 场景变化（运动后 / 情绪波动 / 亲密场景） |
| **兽人特征** | 耳（毛色·内绒毛·情绪联动）、尾（毛量·起始位置·情绪联动）、獠牙（如有）、Knot（位置·大小·充血·锁结时长）、Rut（触发·表现·渴求度·事后脱力） |
| **生殖器三级推断** | L1 有数值套公式；L2/L3 走三维投票（物种 / 性格 / 措辞时态）+ 体型基准与修正因子。**平局四级裁决**：犬科→Grower；人类+外露→Shower；人类+内敛→Grower；原卡强调尺寸恒定→Shower |
| **标签体系** | 10–18 个中文标签，覆盖体型 / 体毛 / 汗液气味 / 肌肉偏好 / 兽人 / 性癖 / 关系动态 |

> 所有推断过程仅存于内部，成品只写结果——禁止出现「L1/L2/L3」「投票」「公式」等字样。

---

## 自检与 PNG 回嵌

```bash
# 元铁律自检
python3 scripts/occam_selfcheck.py <json_path>

# Bara 专题自检（6 块肌群 / 兽人维度 / 体毛 5 区 / 气味 / 生殖器 / 标签数）
python3 scripts/bara_selfcheck.py <json_path>

# 如需回嵌 PNG
python3 scripts/embed_chara_to_png.py <src_png> <out_png> <json_path>
```

`bara_selfcheck.py` 检查项：B1 六块齐全、B2 每块长度、B3 兽人特征、B4 体毛 5 区、B5 气味三要素、B6 生殖器类型 + 数值、B7 creator_notes 长度。

输出建议：

```json
{
  "spec": "chara_card_v3",
  "spec_version": "3.0",
  "data": { "name": "", "description": "", "personality": "", "scenario": "",
            "first_mes": "", "mes_example": "", "creator_notes": "",
            "system_prompt": "", "post_history_instructions": "",
            "alternate_greetings": [], "tags": [], "creator": "",
            "character_version": "", "extensions": {} }
}
```

---

## 分支说明

| 分支 | 内容 |
|------|------|
| `main` | 通用版 `角色卡转换`（题材中立底座） |
| `skill/bara` | 本 Skill，独立维护的 Bara 特化版 |

---

## 版本

| 版本 | 变更 |
|:---:|------|
| **v2.0.0-standalone** | **从主 Skill 解耦**：移除全部跨目录相对引用，脚本自闭环；确立专题补齐优先级；修正 1:1:1 平局兜底为四级裁决；明确字段拆分"先保原意"边界 |
| v1.4.0 | 新增六大肌群描写规范、兽人特征规范、自检清单；新增 `bara_selfcheck.py` |
| v1.3.0 | 奥卡姆设为元铁律；章节重排为 〇→八 |
| v1.2.0 | 生殖器三级推断体系 |
| v1.1.0 | 生殖器数据驱动判定 |

---

## 许可

见 [LICENSE](LICENSE)。
