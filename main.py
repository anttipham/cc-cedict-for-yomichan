import argparse
from dataclasses import dataclass
from io import TextIOWrapper
import json
import re
import zipfile
from decode_pinyin import decode_pinyin

OUTPUT_FOLDER = "CC-CEDICT.zip"
TERM_BANK_SIZE = 4000


@dataclass
class Args:
    dict_file: TextIOWrapper
    is_seperate: bool
    is_number: bool


def parse_file() -> Args:
    """Parses cmd argument. Returns the dictionary file object."""
    parser = argparse.ArgumentParser("main.py", description="Converts CC-CEDICT file to a Yomichan-compatible dictionary format")
    parser.add_argument("dictpath",
                        type=argparse.FileType("r", encoding="utf-8"))
    parser.add_argument("--seperate",
                        action="store_true",
                        help="Use new bullet points as the seperator instead of commas")
    parser.add_argument("--pinyin-numbers",
                        action="store_true",
                        help="Use tone numbers, for example 课 [ke4] instead of 课 [kè]")
    args = parser.parse_args()
    return Args(args.dictpath, args.seperate, args.pinyin_numbers)


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


def termbank_creator(args: Args):
    def to_pinyin(match):
        return decode_pinyin(match.group())

    def format_CL(match):
        text = match.group()
        # Sometimes there's not a space after comma
        # First, delete space to avoid double spaces
        text = text.replace(", ", ",")
        # Then add the space
        text = text.replace(",", ", ")
        # Also add spaces to colons
        text = text.replace(":", ": ")
        return text

    def split_CL(match):
        text = format_CL(match)
        text = " (" + text.removeprefix("/").removesuffix("/") + ")\n"
        return text

    index = 1

    def create_termbank():
        nonlocal index

        termbank = []
        # line = "課 课 [ke4] /subject/course/CL:門|门[men2]/class/lesson/CL:堂[tang2],節|节[jie2]/to levy/tax/form of divination/"
        for line in args.dict_file:
            if len(termbank) >= TERM_BANK_SIZE:
                return termbank

            if args.is_number:
                pinyin = re.sub(r"\[.+?\]", lambda match: match.group().lower(), line.strip())
            else:
                pinyin = re.sub(r"\[.+?\]", to_pinyin, line.strip())

            chars, pronunciation, meaning = re.split(r" \[|\] ", pinyin, 2)
            matches = chars.split()
            if matches[0] == matches[1]:
                del matches[1]

            # The meaning part starts and ends with slashes
            meaning = meaning.removeprefix("/").removesuffix("/")

            if args.is_seperate:
                # Format counter
                meaning = re.sub(r"\/CL:.+?\/", format_CL, meaning)
                meaning = meaning.replace("/", "\n")
            else:
                # Different word starts after the counter
                meaning = re.sub(r"\/CL:.+?\/", split_CL, meaning)
                meaning = meaning.replace("/", ", ")
            meanings = meaning.split("\n")
            entries = [[match, pronunciation, "", "", 2, meanings, index, ""] for match in matches]
            termbank.extend(entries)
            index += 1
        return termbank

    return create_termbank


def create_termbanks(args: Args):
    index = 1
    create_termbank = termbank_creator(args)
    while True:
        term_bank = create_termbank()
        if not term_bank:
            break
        yield term_bank
        index += 1


def format_obj(obj):
    return json.dumps(obj, ensure_ascii=False, separators=(',', ':'))


def main():
    args = parse_file()

    with zipfile.ZipFile(OUTPUT_FOLDER, "w") as zipf:
        zipf.writestr("index.json", format_obj(create_index(args.dict_file)))
        # Skip last comment line in dict_file
        next(args.dict_file)
        for i, term_bank in enumerate(create_termbanks(args)):
            zipf.writestr(f"term_bank_{i+1}.json", format_obj(term_bank))

    print("Done")


if __name__ == "__main__":
    main()
