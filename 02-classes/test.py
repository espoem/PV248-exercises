import os
import sys
import scorelib
import re

# regular expressions
RE_YEAR = re.compile(r".*?(\d{4}).*?")
RE_VOICE_RANGE = re.compile(r"(\w+\d?)--?(\w+\d?)")


def readlines(fp):
    try:
        with open(fp, mode="r", encoding="utf-8") as f:
            return f.readlines()
    except IOError:
        print("File can't be opened")


def init_data():
    data = {"composers": [], "voices": []}
    return data


def load(filename):
    with open(filename, "r", encoding="utf-8") as f:
        lines = f.readlines()

    data = init_data()
    prints = []
    for line in lines:
        # print(line, end='')
        line_split = line.split(":")
        if not line_split[0].strip() or line == lines[-1]:
            # create authors objects
            authors = []
            for author in data.get("composers", []):
                authors.append(
                    scorelib.Person(author["name"], author["born"], author["died"])
                )

            # create voices objects
            voices = []
            for voice in data.get("voices", []):
                voices.append(scorelib.Voice(voice["name"], voice["range"]))

            # create composition object
            composition = scorelib.Composition(
                data.get("title"),
                data.get("incipit"),
                data.get("key"),
                data.get("genre"),
                data.get("year"),
                voices,
                authors,
            )

            editors = [scorelib.Person(data.get("editor"))]
            # create edition
            edition = scorelib.Edition(composition, editors, data.get("edition"))

            print(data)
            if data.get("print_id") is not None:
                print_ = scorelib.Print(edition, data["print_id"], data["partiture"])
                prints.append(print_)
            data = init_data()
            continue

        attr_type = line_split[0].lower()
        attr_value = line_split[1].strip() if line_split[1] else ""
        if "print" in attr_type:
            data["print_id"] = int(attr_value)
        elif attr_type == "partiture":
            data["partiture"] = attr_value.lower() == "yes"
        elif attr_type == "composer":
            authors = attr_value.split(";")
            for author in authors:
                split = author.split("(")
                name = split[0].strip()
                born = None
                died = None
                if len(split) > 1:
                    years = RE_YEAR.findall(split[1])
                    if not years:
                        continue
                    born = years[0]
                    if len(years) > 1:
                        died = years[1]
                data["composers"].append({"name": name, "born": born, "died": died})
        elif attr_type == "title":
            data["title"] = attr_value if attr_value else None
        elif attr_type == "genre":
            data["genre"] = attr_value if attr_value else None
        elif attr_type == "key":
            data["key"] = attr_value if attr_value else None
        elif attr_type == "composition year":
            try:
                data["year"] = int(attr_value)
            except:
                data["year"] = None
        elif "voice" in attr_type:
            voice_name = None
            voice_range = None

            if "--" in attr_value:
                voice_split = attr_value.split(",", 1)
                range_match = RE_VOICE_RANGE.match(voice_split[0])
                if not range_match:
                    voice_range = None
                else:
                    voice_range = "{}--{}".format(
                        range_match.group(1), range_match.group(2)
                    )
                voice_name = voice_split[1].strip() if len(voice_split) > 1 else None
            elif attr_value:
                voice_name = attr_value.strip()
            data["voices"].append({"name": voice_name, "range": voice_range})
        elif attr_type == "genre":
            data["genre"] = attr_value if attr_value else None
        elif attr_type == "incipit":
            data["incipit"] = attr_value if attr_value else None
        elif attr_type == "edition":
            data["edition"] = attr_value if attr_value else None
        elif attr_type == "editor":
            data["editor"] = attr_value if attr_value else None

    return prints


if __name__ == "__main__":
    args = sys.argv
    if len(args) < 2:
        print("Wrong number of arguments.")
        print("./test.py FILE_NAME")
        exit(1)

    filepath = args[1]

    prints = load(filepath)
    print(len(prints))
    prints_str = [print_.format() for print_ in prints]

    # with open('./out.txt', 'w', encoding='utf-8') as f:
    #     f.write("\n\n".join(prints_str))
    print("\n\n".join(prints_str))
