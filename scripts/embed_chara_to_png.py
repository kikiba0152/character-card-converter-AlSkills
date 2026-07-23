#!/usr/bin/env python3
"""把角色卡 JSON 写回 PNG 作为 chara tEXt chunk。

用法：
    python3 embed_chara_to_png.py <src_png> <out_png> <json_path>
    python3 embed_chara_to_png.py <src_png> <out_png> --stdin  < 从 stdin 读 JSON

行为：
    1. 读取源 PNG 字节流
    2. 解析所有 chunk，丢弃旧 chara tEXt/iTXt 与旧 IEND
    3. 在新 IEND 前插入新 chara tEXt chunk（keyword=chara, text=base64(json)）
    4. 重写 PNG，按 CRC 校验写入
    5. 校验最终文件（chara tEXt 唯一 + IEND 唯一）

通用层脚本。所有专题 Skill（角色卡转换_Bara 等）共用。
"""
import argparse
import base64
import json
struct = __import__('struct')
import sys
import zlib


def parse_png_chunks(raw: bytes):
    """解析 PNG，返回 [(ctype_bytes, cdata_bytes), ...]（不含 length/CRC）"""
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


def chunk_keyword(cdata: bytes) -> str | None:
    """tEXt / iTXt chunk 数据的 keyword（None 表示非文本 chunk）"""
    idx = cdata.find(b'\x00')
    if idx == -1:
        return None
    return cdata[:idx].decode('latin-1', errors='replace')


def embed_chara(src_png: str, out_png: str, json_obj: dict, key: str = 'chara') -> dict:
    """把 json_obj 嵌入 src_png，写到 out_png。返回统计信息。"""
    with open(src_png, 'rb') as f:
        raw = f.read()

    sig = raw[:8]
    chunks = parse_png_chunks(raw)

    # 过滤：丢弃旧 chara tEXt/iTXt、丢弃旧 IEND（统一重写）
    kept = []
    dropped_chara = 0
    for ctype, cdata in chunks:
        if ctype in (b'tEXt', b'iTXt'):
            kw = chunk_keyword(cdata)
            if kw == key:
                dropped_chara += 1
                continue
        if ctype == b'IEND':
            continue
        kept.append((ctype, cdata))

    # 紧凑化 JSON
    compact = json.dumps(json_obj, ensure_ascii=False, separators=(',', ':'))
    b64 = base64.b64encode(compact.encode('utf-8')).decode('ascii')
    tEXt_payload = key.encode('ascii') + b'\x00' + b64.encode('ascii')

    # 重写 PNG：sig + kept + 新 chara tEXt + 新 IEND
    with open(out_png, 'wb') as f:
        f.write(sig)
        for ctype, cdata in kept:
            f.write(struct.pack('>I', len(cdata)))
            f.write(ctype)
            f.write(cdata)
            f.write(struct.pack('>I', zlib.crc32(ctype + cdata) & 0xffffffff))
        f.write(struct.pack('>I', len(tEXt_payload)))
        f.write(b'tEXt')
        f.write(tEXt_payload)
        f.write(struct.pack('>I', zlib.crc32(b'tEXt' + tEXt_payload) & 0xffffffff))
        f.write(struct.pack('>I', 0))
        f.write(b'IEND')
        f.write(struct.pack('>I', zlib.crc32(b'IEND') & 0xffffffff))

    # 校验最终文件
    with open(out_png, 'rb') as f:
        new_raw = f.read()
    new_chunks = parse_png_chunks(new_raw)
    chara_count = 0
    iend_count = 0
    for ctype, cdata in new_chunks:
        if ctype in (b'tEXt', b'iTXt'):
            kw = chunk_keyword(cdata)
            if kw == key:
                chara_count += 1
        elif ctype == b'IEND':
            iend_count += 1

    return {
        'src_size': len(raw),
        'out_size': len(new_raw),
        'kept_chunks': len(kept),
        'dropped_chara': dropped_chara,
        'chara_count': chara_count,
        'iend_count': iend_count,
        'json_chars': len(compact),
        'b64_chars': len(b64),
    }


def main():
    parser = argparse.ArgumentParser(description='Embed chara JSON into PNG as tEXt chunk.')
    parser.add_argument('src', help='Source PNG path')
    parser.add_argument('out', help='Output PNG path (will be overwritten)')
    parser.add_argument('json_path', nargs='?', default=None, help='JSON file to embed (or --stdin)')
    parser.add_argument('--stdin', action='store_true', help='Read JSON from stdin')
    parser.add_argument('--key', default='chara', help='tEXt keyword (default: chara)')
    args = parser.parse_args()

    if args.stdin:
        try:
            json_obj = json.load(sys.stdin)
        except json.JSONDecodeError as e:
            print(f'ERROR: Invalid JSON from stdin: {e}', file=sys.stderr)
            sys.exit(1)
    elif args.json_path:
        try:
            with open(args.json_path, 'r', encoding='utf-8') as f:
                json_obj = json.load(f)
        except FileNotFoundError:
            print(f'ERROR: JSON file not found: {args.json_path}', file=sys.stderr)
            sys.exit(2)
        except json.JSONDecodeError as e:
            print(f'ERROR: Invalid JSON: {e}', file=sys.stderr)
            sys.exit(1)
    else:
        print('ERROR: provide JSON path or --stdin', file=sys.stderr)
        sys.exit(2)

    try:
        stats = embed_chara(args.src, args.out, json_obj, args.key)
    except Exception as e:
        print(f'ERROR: {e}', file=sys.stderr)
        sys.exit(1)

    # 自检
    ok = (stats['chara_count'] == 1 and stats['iend_count'] == 1)
    status = '✅ OK' if ok else '❌ INVALID'
    print(f'{status}  chara={stats["chara_count"]} IEND={stats["iend_count"]}')
    print(f'src {stats["src_size"]} B -> out {stats["out_size"]} B (Δ +{stats["out_size"] - stats["src_size"]} B)')
    print(f'kept {stats["kept_chunks"]} chunks, dropped {stats["dropped_chara"]} old chara')
    print(f'JSON {stats["json_chars"]} chars / Base64 {stats["b64_chars"]} chars')

    if not ok:
        sys.exit(1)


if __name__ == '__main__':
    main()