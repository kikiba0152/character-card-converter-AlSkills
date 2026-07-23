#!/usr/bin/env python3
"""对 V3 角色卡 JSON 执行 Bara 专题 §5.3 自检（七项）。

用法：python3 bara_selfcheck.py <json_path>

Bara 专题检查项：[B1] 六大肌群6块齐全 [B2] 每块≥30字符+4维 [B3] 兽人特征覆盖
[B4] 体毛地图5区齐全 [B5] 气味含主味+辅味+场景 [B6] 生殖器含Grower/Shower+数值 [B7] creator_notes≤80字符

退出码：0全部通过；1有失败项。
"""
import argparse, json, re, sys

MUSCLE_GROUPS = ['**胸**：', '**背**：', '**肩**：', '**臂**：', '**腹**：', '**腿**：']
HAIR_AREAS = ['胸部', '腹部', '阴毛', '腿部', '腋毛']
BEAST_TRAITS = ['**耳朵**：', '**尾巴**：', '**獠牙**：', '**Knot**', '**Rut**']
SUCCEEDING_MARKERS = ['**生殖器**：', '**体毛地图**：', '**气味**：', '**汗液**：', '**其他特征**：', '**穿着**：']

def get_description(card):
    if isinstance(card.get('data'), dict):
        return card['data'].get('description', '') or ''
    return card.get('description', '') or ''

def get_creator_notes(card):
    if isinstance(card.get('data'), dict):
        return card['data'].get('creator_notes', '') or ''
    return card.get('creator_notes', '') or ''

def _extract_block(desc, start_marker):
    pos = desc.find(start_marker)
    if pos == -1: return ''
    start = pos + len(start_marker)
    next_pos = [desc.find(m, start) for m in SUCCEEDING_MARKERS]
    next_pos = [p for p in next_pos if p != -1]
    end = min(next_pos) if next_pos else start + 500
    return desc[start:end].strip()

def check_muscles_six(desc):
    missing = [g for g in MUSCLE_GROUPS if g not in desc]
    return (not missing, f'缺失{len(missing)}块' if missing else '6块齐全')

def check_muscle_block_dims(desc):
    fails = []
    for g in MUSCLE_GROUPS:
        block = _extract_block(desc, g)
        if len(block) < 30:
            fails.append(f'{g}长度{len(block)}<30')
            continue
        commas = block.count('，') + block.count('、')
        if commas < 3:
            fails.append(f'{g}分隔{commas}<3')
    return (not fails, '; '.join(fails) if fails else '每块≥30字符+≥3维')

def check_beast_traits(desc):
    has_ear_tail = any(t in desc for t in ['**耳朵**：', '**尾巴**：'])
    has_explicit_none = '**无**' in desc or '非兽人' in desc or '龙族' in desc
    non_beast = ['龙牙', '龙鳞印记', '龙尾', '翅膀']
    has_non_beast = any(m in desc for m in non_beast)
    if has_ear_tail: return (True, '兽人特征已标注')
    if has_non_beast or has_explicit_none: return (True, '非兽人角色')
    return (False, '无耳/尾标注')

def check_body_hair(desc):
    start = desc.find('**体毛地图**：')
    if start == -1: return (False, '体毛地图缺失')
    end = desc.find('**气味**：', start)
    if end == -1: end = len(desc)
    block = desc[start:end]
    missing = [a for a in HAIR_AREAS if f'- {a}' not in block and f'{a}：' not in block]
    return (not missing, f'缺失{missing}' if missing else '5区齐全')

def check_odor(desc):
    pos = desc.find('**气味**：')
    if pos == -1: return (False, '气味缺失')
    end = desc.find('**汗液**：', pos)
    if end == -1: end = desc.find('**其他特征**：', pos)
    if end == -1: end = pos + 500
    block = desc[pos:end]
    main_hits = len([k for k in ['香','味','息','臭'] if k in block])
    aux_hits = len([k for k in ['混','带','夹','底','调'] if k in block])
    has_scenario = bool(re.search(r'(后|时|下|场景)', block))
    ok = main_hits >= 1 and aux_hits >= 1 and has_scenario
    return (ok, f'主{main_hits}/辅{aux_hits}/场景{has_scenario}')

def check_genitalia(desc):
    pos = desc.find('**生殖器**：')
    if pos == -1: return (False, '生殖器缺失')
    end = desc.find('**体毛地图**：', pos)
    if end == -1: end = pos + 800
    block = desc[pos:end]
    has_type = 'Grower' in block or 'Shower' in block
    has_num = bool(re.search(r'\d+\s*cm', block))
    return (has_type and has_num, f'类型{has_type}数值{has_num}')

def check_creator_notes_len(card, limit=80):
    note = get_creator_notes(card)
    return (len(note) <= limit, f'{len(note)}字符(上限{limit})')

def run_selfcheck(card):
    desc = get_description(card)
    results = [
        ('B1', *check_muscles_six(desc)),
        ('B2', *check_muscle_block_dims(desc)),
        ('B3', *check_beast_traits(desc)),
        ('B4', *check_body_hair(desc)),
        ('B5', *check_odor(desc)),
        ('B6', *check_genitalia(desc)),
        ('B7', *check_creator_notes_len(card)),
    ]
    return {'passed': all(ok for _, ok, _ in results), 'results': results}

def main():
    parser = argparse.ArgumentParser(description='Bara self-check')
    parser.add_argument('json_path', nargs='?', default=None)
    parser.add_argument('--stdin', action='store_true')
    args = parser.parse_args()
    if args.stdin:
        card = json.load(sys.stdin)
    else:
        if not args.json_path:
            print('ERROR: provide json_path or --stdin', file=sys.stderr); sys.exit(2)
        with open(args.json_path, 'r', encoding='utf-8') as f:
            card = json.load(f)
    result = run_selfcheck(card)
    print('===== Bara §5.3 自检 =====')
    for code, ok, detail in result['results']:
        print(f'  [{"✅" if ok else "❌"}] {code}  {detail}')
    print()
    if result['passed']:
        print('✅ 全部通过'); sys.exit(0)
    else:
        print('❌ 有失败项'); sys.exit(1)

if __name__ == '__main__':
    main()