#!/usr/bin/env python3
"""从 PNG 文件中读取 chara tEXt/iTXt chunk 并解析为 JSON 对象。

用法：
    python3 read_png_chara.py <png_path> [--out <json_path>] [--key chara]

输出（无 --out 时打印到 stdout）：
    - 解析后的 JSON 对象（json.dumps 紧凑化）
    - 或 V2/V3 顶层字段摘要

支持的 chunk 类型：
    - tEXt（key=chara，value=base64(json) 或 纯 json）
    - iTXt（key=chara，value=base64(json) 或 纯 json，UTF-8）

通用层脚本。所有专题 Skill（角色卡转换_Bara 等）共用。
"""
import argparse
import base64
import json
struct = __import__('struct')
import sys
import zlib


def parse_png_chunks(raw: bytes):
    """解析 PNG，返回 [(ctype_bytes, cdata_bytes), ...]"""
    assert raw[:8] == b'\x89PNG\r\n\x1a\n', 'Not a valid PNG file'
    pos = 8
    chunks = []
    while pos < len(raw):
        if pos + 8 > len(raw):
            break
        length = struct.unpack('>I', raw[pos:pos + 4])[0]
        if pos + 12 + length > len(raw):
            break
        ctype = raw[pos + 4:pos + 8]
        cdata = raw[pos + 8:pos + 8 + length]
        chunks.append((ctype, cdata))
        pos += 12 + length
    return chunks


def decode_chunk_value(ctype: bytes, cdata: bytes) -> str:
    """从 tEXt / iTXt chunk 提取文本值（UTF-8）"""
    if ctype == b'tEXt':
        # keyword \0 text
        _, _, v = cdata.partition(b'\x00')
        return v.decode('utf-8', errors='replace')
    elif ctype == b'iTXt':
        # keyword \0 compression_flag(1) compression_method(1) language \0 translated_keyword \0 text
        idx = cdata.find(b'\x00')
        if idx == -1:
            return ''
        rest = cdata[idx + 1:]
        comp_flag = rest[0]
        comp_method = rest[1]
        # skip language (null-terminated)
        idx2 = rest.find(b'\x00', 2)
        if idx2 == -1:
            return ''
        # skip translated keyword (null-terminated)
        idx3 = rest.find(b'\x00', idx2 + 1)
        if idx3 == -1:
            return ''
        text = rest[idx3 + 1:]
        if comp_flag == 1:
            text = zlib.decompress(text)
        return text.decode('utf-8', errors='replace')
    return ''


def parse_chara_payload(text: str) -> dict:
    """从 chara chunk 文本值解析 JSON（自动尝试 base64）"""
    # 尝试 1：直接 JSON
    try:
        return json.loads(text)
    except (json.JSONDecodeError, ValueError):
        pass
    # 尝试 2：Base64 解码后 JSON
    try:
        decoded = base64.b64decode(text, validate=False)
        return json.loads(decoded)
    except Exception:
        pass
    raise ValueError('chara chunk value is neither JSON nor base64-encoded JSON')


def extract_chara(png_path: str, key: str = 'chara') -> dict | None:
    """提取 PNG 中的 chara JSON 对象。若无对应 chunk 返回 None。"""
    with open(png_path, 'rb') as f:
        raw = f.read()
    chunks = parse_png_chunks(raw)
    for ctype, cdata in chunks:
        if ctype in (b'tEXt', b'iTXt'):
            kw_end = cdata.find(b'\x00')
            if kw_end == -1:
                continue
            keyword = cdata[:kw_end].decode('latin-1', errors='replace')
            if keyword != key:
                continue
            text = decode_chunk_value(ctype, cdata)
            return parse_chara_payload(text)
    return None


def main():
    parser = argparse.ArgumentParser(description='Extract chara JSON from PNG (V2/V3).')
    parser.add_argument('png', help='Path to input PNG file')
    parser.add_argument('--out', default=None, help='Write JSON to this path (pretty-printed)')
    parser.add_argument('--key', default='chara', help='tEXt keyword (default: chara)')
    parser.add_argument('--summary', action='store_true', help='Print top-level fields only')
    args = parser.parse_args()

    try:
        obj = extract_chara(args.png, args.key)
    except FileNotFoundError:
        print(f'ERROR: File not found: {args.png}', file=sys.stderr)
        sys.exit(2)
    except Exception as e:
        print(f'ERROR: {e}', file=sys.stderr)
        sys.exit(1)

    if obj is None:
        print(f'ERROR: No "{args.key}" chunk found in PNG', file=sys.stderr)
        sys.exit(1)

    if args.summary:
        keys = list(obj.keys())
        spec = obj.get('spec') or '(V2)'
        version = obj.get('spec_version') or 'n/a'
        name = ''
        if 'data' in obj and isinstance(obj['data'], dict):
            name = obj['data'].get('name', '')
        elif 'name' in obj:
            name = obj.get('name', '')
        print(f'spec={spec} version={version} keys={keys} name={name}')
        return

    if args.out:
        with open(args.out, 'w', encoding='utf-8') as f:
            json.dump(obj, f, ensure_ascii=False, indent=2)
        print(f'Wrote {args.out}')
    else:
        print(json.dumps(obj, ensure_ascii=False))


if __name__ == '__main__':
    main()