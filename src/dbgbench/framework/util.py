def escape_non_ascii_utf8(s):
    escaped = []
    for ch in s:
        if ord(ch) < 128:
            escaped.append(ch)
        else:
            for b in ch.encode("utf-8"):
                escaped.append("\\x{:02X}".format(b))
    return "".join(escaped)


def unescape_hex_utf8(s):
    i = 0
    out_bytes = []
    while i < len(s):
        # Look for a pattern like \xAB
        if (s[i] == '\\'
                and i + 3 < len(s)
                and s[i + 1] == 'x'
                and all(c in '0123456789ABCDEFabcdef' for c in s[i + 2:i + 4])):
            hex_part = s[i + 2:i + 4]
            out_bytes.append(int(hex_part, 16))
            i += 4
        else:
            out_bytes.append(ord(s[i]))
            i += 1
    return bytes(out_bytes).decode('utf-8', errors='replace')