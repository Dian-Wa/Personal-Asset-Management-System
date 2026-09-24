import struct, zlib, math

def make_png(path, size):
    # RGBA pixel buffer
    buf = bytearray([0, 0, 0, 0]) * (size * size)

    def setpx(x, y, rgba):
        if x < 0 or y < 0 or x >= size or y >= size:
            return
        i = (y * size + x) * 4
        buf[i:i+4] = bytes(rgba)

    def in_rounded_rect(x, y, l, t, r, b, rad):
        # r,b are exclusive-1 boundaries
        if x < l or x > r or y < t or y > b:
            return False
        # corner regions
        if x < l + rad and y < t + rad:
            return (x - (l + rad)) ** 2 + (y - (t + rad)) ** 2 <= rad * rad
        if x > r - rad and y < t + rad:
            return (x - (r - rad)) ** 2 + (y - (t + rad)) ** 2 <= rad * rad
        if x < l + rad and y > b - rad:
            return (x - (l + rad)) ** 2 + (y - (b - rad)) ** 2 <= rad * rad
        if x > r - rad and y > b - rad:
            return (x - (r - rad)) ** 2 + (y - (b - rad)) ** 2 <= rad * rad
        return True

    bg = (168, 181, 160, 255)        # #A8B5A0
    white = (255, 255, 255, 255)
    dark = (138, 154, 130, 255)      # #8A9A82

    bg_rad = int(size * 0.22)
    # background (rounded square, full canvas)
    for y in range(size):
        for x in range(size):
            if in_rounded_rect(x, y, 0, 0, size - 1, size - 1, bg_rad):
                setpx(x, y, bg)

    # white box
    m = int(size * 0.26)
    box_rad = int(size * 0.10)
    for y in range(size):
        for x in range(size):
            if in_rounded_rect(x, y, m, m, size - m - 1, size - m - 1, box_rad):
                setpx(x, y, white)

    # lid line (darker green) near top of box
    lid_y = int(size * 0.44)
    line_w = max(2, int(size * 0.035))
    lx0 = m + int(size * 0.07)
    lx1 = size - m - int(size * 0.07)
    for y in range(lid_y - line_w // 2, lid_y + line_w // 2 + 1):
        for x in range(lx0, lx1 + 1):
            setpx(x, y, dark)

    # ---- encode PNG ----
    raw = bytearray()
    for y in range(size):
        raw.append(0)  # filter type 0
        start = y * size * 4
        raw.extend(buf[start:start + size * 4])

    def chunk(tag, data):
        c = struct.pack(">I", len(data)) + tag + data
        c += struct.pack(">I", zlib.crc32(tag + data) & 0xffffffff)
        return c

    sig = b"\x89PNG\r\n\x1a\n"
    ihdr = struct.pack(">IIBBBBB", size, size, 8, 6, 0, 0, 0)  # 8-bit RGBA
    idat = zlib.compress(bytes(raw), 9)
    png = sig + chunk(b"IHDR", ihdr) + chunk(b"IDAT", idat) + chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)
    print("wrote", path, size, "x", size)

make_png("icon-192.png", 192)
make_png("icon-512.png", 512)
