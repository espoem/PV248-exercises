import sys
import sqlite3
import os
import json

if __name__ == "__main__":
    args = sys.argv
    if len(args) < 2:
        print("Wrong number of arguments.")
        print("./search.py STRING")
        exit(1)

    substring = " ".join(args[1:])

    here = os.path.abspath(os.path.dirname(__file__))
    DB = os.path.join(here, "scorelib.dat")
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    composers = cur.execute(
        """
        SELECT id, name, born, died
        FROM person
        WHERE person.name like ?
        """,
        ("%" + substring + "%",),
    ).fetchall()

    data = {}
    for composer in composers:
        prints = cur.execute(
            """
            SELECT print.id, print.partiture, score.id, edition.id
            FROM (SELECT id FROM person WHERE id=:person_id) as p
            JOIN score_author on p.id = score_author.composer
            JOIN edition on edition.score = score_author.score
            JOIN score on score.id = edition.score
            JOIN print on edition.id = print.edition
            WHERE p.id=:person_id
            """,
            {"person_id": composer[0]},
        ).fetchall()

        prints_data = []
        for print_ in prints:
            print_dict = {}
            print_dict["Print Number"] = print_[0]
            print_dict["Partiture"] = print_[1] == "Y"
            composition_id = print_[2]
            composition = cur.execute(
                """
                SELECT *
                FROM score
                WHERE id=:score_id
                """,
                {"score_id": composition_id},
            ).fetchone()

            edition_id = print_[3]
            edition = cur.execute(
                """
                SELECT *
                FROM edition
                WHERE id=:edition_id
                """,
                {"edition_id": edition_id},
            ).fetchone()

            if composition:
                print_dict["Title"] = composition[1]
                print_dict["Genre"] = composition[2]
                print_dict["Key"] = composition[3]
                print_dict["Incipit"] = composition[4]
                print_dict["Composition Year"] = composition[5]

            if edition:
                print_dict["Edition"] = edition[2]

            composition_composers = cur.execute(
                """
                SELECT *
                FROM person
                JOIN score_author on person.id = score_author.composer
                WHERE score_author.score=:score_id
                """,
                {"score_id": composition_id},
            ).fetchall()

            composers_data = []
            for c in composition_composers:
                c_dict = {"Name": c[3], "Born": c[1], "Died": c[2]}
                composers_data.append(c_dict)
            print_dict["Composer"] = composers_data

            edition_editors = cur.execute(
                """
                SELECT person.*
                FROM person
                JOIN edition_author on person.id = edition_author.editor
                WHERE edition_author.edition=:edition_id
                """,
                {"edition_id": edition_id},
            ).fetchall()

            editors_data = []
            for e in edition_editors:
                e_dict = {"Name": e[3], "Born": e[1], "Died": e[2]}
                editors_data.append(e_dict)
            print_dict["Editor"] = editors_data

            voices = cur.execute(
                """
                SELECT *
                FROM voice
                WHERE score=:score_id
                """,
                {"score_id": composition_id},
            ).fetchall()

            voices_data = {}
            for voice in voices:
                voice_dict = {"Range": voice[3], "Name": voice[4]}
                voices_data[voice[1]] = voice_dict
            print_dict["Voices"] = voices_data

            prints_data.append(print_dict)

            # print(print_dict)
        data[composer[1]] = prints_data

    print(json.dumps(data, ensure_ascii=False, sort_keys=True, indent=4))