"""
Dressmaker - disable Addressables CRC checks in catalog.bin (needed so the
patched localization bundle is accepted by the game).

Usage:
    python patch_catalog.py "D:\\SteamLibrary\\steamapps\\common\\Dressmaker\\Dressmaker_Data\\StreamingAssets\\aa\\catalog.bin"

Writes catalog.bin.uk next to the input. Back up the original, then rename
catalog.bin.uk -> catalog.bin. Only the CRC fields of bundle records are set to 0.
"""
import os
import struct
import sys


def find_records(b):
    """Bundle request-option records: hashId, bundleNameId(=hashId+0x14), crc, size, commonId."""
    recs = []
    for p in range(0, len(b) - 20):
        h, n, crc, size, common = struct.unpack_from("<5I", b, p)
        if n == h + 0x14 and 0 < h < len(b) and 0 < common < len(b) and 0 < size < 500_000_000:
            recs.append((p, crc))
    return recs


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    src = sys.argv[1]
    b = bytearray(open(src, "rb").read())
    recs = find_records(b)
    if not recs:
        print("No bundle records found - is this Dressmaker's catalog.bin?")
        sys.exit(2)
    changed = 0
    for p, crc in recs:
        if crc:
            struct.pack_into("<I", b, p + 8, 0)
            changed += 1
    out = src + ".uk"
    open(out, "wb").write(b)
    print(f"{len(recs)} bundle records found, {changed} CRC values set to 0.\nSaved to:\n{out}")


if __name__ == "__main__":
    main()
