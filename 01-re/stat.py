import os
import re
import sys
from collections import Counter
from operator import itemgetter

# regular expressions
RE_YEAR = re.compile(r".*?(\d{4}|\d{2}th).*?")

# options
CMD_COMPOSER = "composer"
CMD_CENTURY = "century"

CMD_OPTIONS = [CMD_COMPOSER, CMD_CENTURY]


def readlines(fp):
    try:
        with open(fp, mode="r", encoding="utf-8") as f:
            return f.readlines()
    except IOError:
        print("File can't be opened")


def extract_data(file_path, opt):
    results = []

    for line in readlines(file_path):
        line_split = line.split(":")
        if len(line_split) < 2 or not line_split[1].strip():
            continue

        attr_type = line_split[0].lower()
        if opt == CMD_COMPOSER and attr_type == "composer":
            composers_split = line_split[1].split(";")
            for composer in composers_split:
                results.append(composer.split("(", 1)[0].strip())
        elif opt == CMD_CENTURY and attr_type == "composition year":
            comp_year = line_split[1].strip()
            year_match = RE_YEAR.search(comp_year)
            if not year_match:
                continue
            year = year_match.groups()[0]
            century = int(year[:2])
            if year[2:] != "00" and year[2:] != "th":
                century += 1
            results.append(century)

    return results


if __name__ == "__main__":
    args = sys.argv
    if len(args) != 3:
        print("Wrong number of arguments")
        print("./stat.py FILE_PATH CMD")
        exit(1)

    file = os.path.abspath(args[1])
    cmd = args[2]
    if not os.path.isfile(file):
        print("Wrong path to the file")
        exit(1)
    if cmd not in CMD_OPTIONS:
        print("Available commands are", CMD_OPTIONS)
        exit(1)

    data = extract_data(file, cmd)
    counter = Counter(data)

    if cmd == CMD_COMPOSER:
        for k, v in sorted(counter.items(), key=itemgetter(0)):
            print("{}: {}".format(k, v))
    elif cmd == CMD_CENTURY:
        for k, v in sorted(counter.items(), key=itemgetter(0)):
            print("{}th century: {}".format(k, v))
