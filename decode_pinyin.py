"""
I edited the code from here
https://stackoverflow.com/questions/8200349/convert-numbered-pinyin-to-pinyin-with-tone-marks
"""
import re

PinyinToneMark = {
    0: "aoeiuv\u00fc",
    1: "\u0101\u014d\u0113\u012b\u016b\u01d6\u01d6",
    2: "\u00e1\u00f3\u00e9\u00ed\u00fa\u01d8\u01d8",
    3: "\u01ce\u01d2\u011b\u01d0\u01d4\u01da\u01da",
    4: "\u00e0\u00f2\u00e8\u00ec\u00f9\u01dc\u01dc",
}

def decode_pinyin(s):
    s = s.lower()
    word = ""
    char = ""
    for c in s:
        if c >= 'a' and c <= 'z':
            char += c
        elif c == ':':
            assert char[-1] == 'u'
            char = char[:-1] + "\u00fc"
        elif c >= '0' and c <= '5':
            tone = int(c) % 5
            if tone != 0:
                m = re.search("[aoeiuv\u00fc]+", char)
                if m is None:
                    char += c
                elif len(m.group(0)) == 1:
                    char = char[:m.start(0)] + PinyinToneMark[tone][PinyinToneMark[0].index(m.group(0))] + char[m.end(0):]
                else:
                    if 'a' in char:
                        char = char.replace("a", PinyinToneMark[tone][0])
                    elif 'o' in char:
                        char = char.replace("o", PinyinToneMark[tone][1])
                    elif 'e' in char:
                        char = char.replace("e", PinyinToneMark[tone][2])
                    elif char.endswith("ui"):
                        char = char.replace("i", PinyinToneMark[tone][3])
                    elif char.endswith("iu"):
                        char = char.replace("u", PinyinToneMark[tone][4])
                    else:
                        char += "!"
            word += char
            char = ""
        else:
            word += char
            char = ""
            word += c
    word += char
    return word