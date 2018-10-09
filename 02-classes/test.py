import os
import sys
import scorelib

def readlines(fp):
    try:
        with open(fp, mode="r", encoding="utf-8") as f:
            return f.readlines()
    except IOError:
        print("File can't be opened")


if __name__ == "__main__":
    args = sys.argv
    if len(args) < 2:
        print("Wrong number of arguments.")
        print("./test.py FILE_NAME")
        exit(1)

    filepath = args[1]

    prints = scorelib.load(filepath)
    prints_str = [print_.format() for print_ in prints]

    # with open('./out.txt', 'w', encoding='utf-8') as f:
    #     f.write("\n\n".join(prints_str))
    print("\n\n".join(prints_str))
