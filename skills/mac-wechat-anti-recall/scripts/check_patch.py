#!/usr/bin/env python3
"""核对 WeChatTweak 的字节补丁是否真的写进了微信里。

原理：config.json 给每个微信 build 一组 (binary, arch, addr, asm)，
`wechattweak patch` 就是把 asm 字节写到 addr 所在的 segment 偏移处。
本脚本反向操作：算出同样的文件偏移，读出当前字节，与 asm 比对。

用法：
    python3 check_patch.py 268851
    python3 check_patch.py 268851 --app /Applications/微信1.app --config ~/tools/WeChatTweak/config.json

参数里的版本号 = /Applications/WeChat.app/Contents/Info.plist 的 CFBundleVersion。
"""
import argparse
import json
import os
import struct
import sys

FAT_MAGIC = 0xCAFEBABE
FAT_CIGAM = 0xBEBAFECA
MH_MAGIC_64 = 0xFEEDFACF
LC_SEGMENT_64 = 0x19
CPU_BY_NAME = {"arm64": 16777228, "x86_64": 16777223}
CPU_NAMES = {v: k for k, v in CPU_BY_NAME.items()}


def slices(path):
    """返回 [(cputype, slice_offset)]，兼容 fat 与 thin"""
    with open(path, "rb") as f:
        head = f.read(8)
        if len(head) < 8:
            return []
        magic = struct.unpack(">I", head[:4])[0]
        if magic in (FAT_MAGIC, FAT_CIGAM):
            endian = ">" if magic == FAT_MAGIC else "<"
            f.seek(4)
            nfat = struct.unpack(endian + "I", f.read(4))[0]
            out = []
            for _ in range(nfat):
                raw = f.read(20)
                if len(raw) < 20:
                    break
                cputype = struct.unpack(endian + "I", raw[0:4])[0]
                offset = struct.unpack(endian + "I", raw[8:12])[0]
                out.append((cputype, offset))
            return out
        cputype = struct.unpack("<I", head[4:8])[0]
        return [(cputype, 0)]


def find_offset(path, slice_offset, target_va):
    """走 load command，找包含 target_va 的 segment，返回文件偏移"""
    with open(path, "rb") as f:
        f.seek(slice_offset)
        hdr = f.read(32)
        if len(hdr) < 32 or struct.unpack("<I", hdr[0:4])[0] != MH_MAGIC_64:
            return None
        ncmds = struct.unpack("<I", hdr[16:20])[0]
        lc_off = slice_offset + 32
        for _ in range(ncmds):
            f.seek(lc_off)
            head = f.read(8)
            if len(head) < 8:
                return None
            cmd, cmdsize = struct.unpack("<II", head)
            if cmd == LC_SEGMENT_64:
                seg = f.read(64)
                if len(seg) >= 40:
                    vmaddr, vmsize, fileoff = struct.unpack("<QQQ", seg[16:40])
                    if vmaddr <= target_va < vmaddr + vmsize:
                        return slice_offset + fileoff + (target_va - vmaddr)
            lc_off += cmdsize
    return None


def to_bytes(asm):
    if isinstance(asm, list):
        return bytes(asm)
    s = str(asm).strip().replace(" ", "").replace("0x", "")
    try:
        return bytes.fromhex(s)
    except ValueError:
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("version", help="微信 CFBundleVersion，如 268851")
    ap.add_argument("--app", default="/Applications/WeChat.app")
    ap.add_argument("--config", default="~/tools/WeChatTweak/config.json")
    args = ap.parse_args()

    config_path = os.path.expanduser(args.config)
    if not os.path.isfile(config_path):
        print(f"找不到 config：{config_path}")
        return 2

    cfg = json.load(open(config_path))
    entries = cfg if isinstance(cfg, list) else cfg.get("versions", [])
    match = [c for c in entries if str(c.get("version")) == str(args.version)]
    if not match:
        print(f"config 里没有 version={args.version}（该 build 不受支持）")
        return 1

    ok_count = bad_count = 0
    for conf in match:
        print(f"=== config version={conf['version']} ===")
        for t in conf.get("targets", []):
            binary = t.get("binary") or "Contents/MacOS/WeChat"
            label = t.get("identifier", "?")
            path = os.path.join(args.app, binary)
            if not os.path.isfile(path):
                print(f"  缺少目标文件：{path}")
                bad_count += 1
                continue
            print(f"\n--- {label}  →  {binary}")
            for e in t.get("entries", []):
                arch = e.get("arch")
                cpu = arch.get("cpu") if isinstance(arch, dict) else CPU_BY_NAME.get(str(arch))
                addr = e.get("addr")
                if isinstance(addr, str):
                    addr = int(addr, 16)
                want = to_bytes(e.get("asm"))
                if want is None:
                    print(f"  [解析不了 asm] {e.get('asm')!r}")
                    bad_count += 1
                    continue

                hit = None
                for scpu, soff in slices(path):
                    if scpu != cpu:
                        continue
                    off = find_offset(path, soff, addr)
                    if off is not None:
                        with open(path, "rb") as f:
                            f.seek(off)
                            hit = (CPU_NAMES.get(cpu, str(cpu)), addr, off, f.read(len(want)))
                if hit is None:
                    print(f"  [{CPU_NAMES.get(cpu, cpu)}] addr={hex(addr)} → 不在任何 segment 内")
                    bad_count += 1
                    continue
                name, addr, off, have = hit
                good = have == want
                ok_count += good
                bad_count += not good
                print(f"  [{name}] addr={hex(addr)} fileoff={hex(off)} "
                      f"期望={want.hex()} 实际={have.hex()}  {'✅ 补丁在' if good else '❌ 补丁不在!'}")

    print(f"\n小结：✅ {ok_count} 处 / ❌ {bad_count} 处")
    if ok_count and not bad_count:
        print("字节层面已确认打上；功能是否生效仍需一次真实撤回事件验证。")
    return 0 if not bad_count else 1


if __name__ == "__main__":
    sys.exit(main())
