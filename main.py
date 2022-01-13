import argparse
import json
import re
import zipfile
from decode_pinyin import decode_pinyin

OUTPUT_FOLDER = "CC-CEDICT.zip"
TERM_BANK_SIZE = 4000


def parser():
    """Parses cmd argument. Returns the dictionary file object."""
    parser = argparse.ArgumentParser("main.py", description="Converts CC-CEDICT file to a Yomichan-compatible dictionary format")
    parser.add_argument("dictpath", type=argparse.FileType("r", encoding="utf-8"))
    dict_file = parser.parse_args().dictpath
    return dict_file


def create_index(dict_file):
    for line in dict_file:
        if line.startswith("#! date="):
            date = re.search(r"(\d{4})-(\d{2})-(\d{2})", line)[0]
            break
    index = { "title": "CC-CEDICT",
              "format": 3,
              "revision": f"cc_cedict_{date}",
              "sequenced": True }
    return index


def termbank_creator(dict_file):
    def to_pinyin(match):
        return decode_pinyin(match.group())

    def split_CL(match):
        text = match.group()

        # Mark split with newline
        text = text.removesuffix("/") + "\n"

        # Sometimes there's not a space after comma
        # First, delete space to avoid double spaces
        text = text.replace(", ", ",")
        # Then add the space
        text = text.replace(",", ", ")

        # Also add spaces to colons
        text = text.replace(":", ": ")
        return text

    index = 1

    def create_termbank():
        nonlocal index

        termbank = []
        # line = "課 课 [ke4] /subject/course/CL:門|门[men2]/class/lesson/CL:堂[tang2],節|节[jie2]/to levy/tax/form of divination/"
        for line in dict_file:
            if len(termbank) >= TERM_BANK_SIZE:
                return termbank
            pinyin = re.sub(r"\[.+?\]", to_pinyin, line.strip())
            chars, pronunciation, meaning = re.split(r" \[|\] ", pinyin, 2)
            matches = chars.split()
            if matches[0] == matches[1]:
                del matches[1]

            # The meaning part starts and ends with slashes
            meaning = meaning.removeprefix("/").removesuffix("/")
            # Different word starts after the counter
            meaning = re.sub(r"\/CL:.+?\/", split_CL, meaning)
            meaning = meaning.replace("/", "; ")
            meanings = meaning.split("\n")
            entries = [[match, pronunciation, "", "", 2, meanings, index, ""] for match in matches]
            termbank.extend(entries)
            index += 1
        return termbank

    return create_termbank


def create_termbanks(dict_file):
    index = 1
    create_termbank = termbank_creator(dict_file)
    while True:
        term_bank = create_termbank()
        if not term_bank:
            break
        yield term_bank
        index += 1


def format_obj(obj):
    return json.dumps(obj, ensure_ascii=False, separators=(',', ':'))


def main():
    dict_file = parser()

    with zipfile.ZipFile(OUTPUT_FOLDER, "w") as zipf:
        zipf.writestr("index.json", format_obj(create_index(dict_file)))
        # Skip last comment line in dict_file
        next(dict_file)
        for i, term_bank in enumerate(create_termbanks(dict_file)):
            zipf.writestr(f"term_bank_{i+1}.json", format_obj(term_bank))

    print("Done")


if __name__ == "__main__":
    main()
