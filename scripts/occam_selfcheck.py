#!/usr/bin/env python3
"""对 V3 角色卡 JSON 执行奥卡姆 §0 元铁律自检。

用法：
    python3 occam_selfcheck.py <json_path>
    python3 occam_selfcheck.py --stdin  < 从 stdin 读 JSON

通用层检查（适用于所有角色卡）：
    [G1] 字段内含判定术语？→ 删
    [G2] 字段内含 AI 痕迹？→ 删
    [G3] 字段内含"推断为 X 因为..."？→ 仅留结论
    [G4] 字段内含来源注释？→ 仅 metadata
    [G5] 每一句都对角色扮演有贡献？→ 否则删
    [G6] creator_notes ≤ 80 字符

专题维度检查（如适用）：
    [T1] Bara 角色：六大肌群 6 块齐全（写入 description）
    [T2] 兽人角色：耳/尾/Knot/Rut 维度全覆盖

通用层只跑 [G*]。专题 [T*] 由各专题 Skill 的 selfcheck 脚本扩展。
退出码：0 全部通过；1 有失败项。
"""
import argparse
import json
import re
import sys


# 元铁律禁词（奥卡姆剃刀）
FORBIDDEN_TERMS = [
    '判定依据', '三维投票', '公式验证',
    'L1推断', 'L2推断', 'L3推断',
    '由 AI', '由Operit', 'AI处理', 'AI痕迹',
    '修订要点', '处理中', '已修订', '已更新',
    '原卡来自', '原卡混杂',
]


def get_description(card: dict) -> str:
    """兼容 V2 与 V3"""
    if isinstance(card.get('data'), dict):
        return card['data'].get('description', '') or ''
    return card.get('description', '') or ''


def get_creator_notes(card: dict) -> str:
    if isinstance(card.get('data'), dict):
        return card['data'].get('creator_notes', '') or ''
    return card.get('creator_notes', '') or ''


def check_forbidden_terms(card: dict) -> list[str]:
    """[G1-G4] 检查禁词"""
    hits = []
    desc = get_description(card)
    note = get_creator_notes(card)
    for term in FORBIDDEN_TERMS:
        if term in desc or term in note:
            hits.append(term)
    return hits


def check_creator_notes_length(card: dict, limit: int = 80) -> int:
    """[G6] creator_notes 字符数"""
    return len(get_creator_notes(card))


def check_value_centric(card: dict) -> list[str]:
    """[G3/G5] 简化启发式：检查 description 中是否存在 '推断为 X 因为 Y' 模式"""
    desc = get_description(card)
    bad_patterns = [
        r'推断为[^,，。.;；\n]{0,30}因为',
        r'因为[^,，。.;；\n]{0,30}所以',
    ]
    hits = []
    for p in bad_patterns:
        m = re.search(p, desc)
        if m:
            hits.append(m.group(0))
    return hits


def run_selfcheck(card: dict) -> dict:
    """执行通用自检。返回 {passed: bool, results: [(code, ok, detail), ...]}"""
    results = []

    # [G1-G4] 禁词检查
    hits = check_forbidden_terms(card)
    results.append(('G1-G4', not hits, f'禁词命中: {hits}' if hits else '无禁词'))

    # [G3/G5] 推断链检查
    infer_hits = check_value_centric(card)
    results.append(('G3/G5', not infer_hits,
                    f'推断链命中: {infer_hits}' if infer_hits else '无推断链外溢'))

    # [G6] creator_notes 长度
    note_len = check_creator_notes_length(card)
    results.append(('G6', note_len <= 80,
                    f'creator_notes {note_len} 字符 (上限 80)'))

    # spec/version 完整性
    spec = card.get('spec', '')
    spec_version = card.get('spec_version', '')
    results.append(('V3-spec', spec == 'chara_card_v3',
                    f'spec={spec!r}'))
    results.append(('V3-version', spec_version == '3.0',
                    f'spec_version={spec_version!r}'))

    passed = all(ok for _, ok, _ in results)
    return {'passed': passed, 'results': results}


def main():
    parser = argparse.ArgumentParser(description='Occam §0 self-check for V3 character card.')
    parser.add_argument('json_path', nargs='?', default=None)
    parser.add_argument('--stdin', action='store_true')
    args = parser.parse_args()

    if args.stdin:
        card = json.load(sys.stdin)
    else:
        if not args.json_path:
            print('ERROR: provide json_path or --stdin', file=sys.stderr)
            sys.exit(2)
        try:
            with open(args.json_path, 'r', encoding='utf-8') as f:
                card = json.load(f)
        except FileNotFoundError:
            print(f'ERROR: not found: {args.json_path}', file=sys.stderr)
            sys.exit(2)
        except json.JSONDecodeError as e:
            print(f'ERROR: invalid JSON: {e}', file=sys.stderr)
            sys.exit(1)

    result = run_selfcheck(card)

    print('===== Occam §0 自检 =====')
    for code, ok, detail in result['results']:
        mark = '✅' if ok else '❌'
        print(f'  [{mark}] {code}  {detail}')
    print()

    if result['passed']:
        print('✅ 全部通过 — 角色卡符合元铁律')
        sys.exit(0)
    else:
        print('❌ 有失败项 — 输出前需修复')
        sys.exit(1)


if __name__ == '__main__':
    main()