import sys
import sqlite3
import os
import json

if __name__ == "__main__":
    args = sys.argv
    if len(args) < 2:
        print("Wrong number of arguments.")
        print("./getprint.py PRINT_ID")
        exit(1)

    print_id = args[1]

    here = os.path.abspath(os.path.dirname(__file__))
    conn = sqlite3.connect(os.path.join(here, "scorelib.dat"))
    cur = conn.cursor()

    composers = cur.execute(
        """SELECT person.name, person.born, person.died
        FROM (SELECT id, edition FROM print where print.id=?) AS print
        JOIN edition ON print.edition = edition.id
        JOIN score_author ON edition.score = score_author.score
        JOIN person ON person.id = score_author.composer""",
        (print_id,),
    )

    results = []
    for composer in composers:
        data = {"name": composer[0], "born": composer[1], "died": composer[2]}
        results.append(data)

    print(json.dumps(results, ensure_ascii=False, sort_keys=True, indent=4))
    conn.close()
