import logging
import os
import sqlite3
import sys

import scorelib

here = os.path.abspath(os.path.dirname(__file__))

logger = logging.getLogger(__name__)
FH = logging.FileHandler(os.path.join(here, "log.txt"), mode="w", encoding="utf-8")
logger.addHandler(FH)
logger.setLevel(logging.DEBUG)


def insert_person(person, persist_people, cursor):
    logger.debug("Insert person %s", person)
    if person.name not in persist_people:
        cursor.execute(
            """
            INSERT INTO person(born, died, name)
            VALUES(?,?,?)
            """,
            (person.born, person.died, person.name),
        )
        person_id = cursor.lastrowid
        persist_people[person.name] = person_id
        return person_id
    else:
        if person.born:
            cursor.execute(
                """
                UPDATE person
                SET born=?
                WHERE name=?
                """,
                (person.born, person.name),
            )
        if person.died:
            cursor.execute(
                """
                UPDATE person
                SET died=?
                WHERE name=?
                """,
                (person.died, person.name),
            )
        return persist_people[person.name]


def insert_voice(voice, voice_number, score_id, cursor):
    cursor.execute(
        """
        INSERT INTO voice (number, score, range, name)
        VALUES (?,?,?,?)
        """,
        (voice_number, score_id, voice.range, voice.name),
    )
    return cursor.lastrowid


def insert_score_author(score_id, composer_id, cursor):
    cursor.execute(
        """
        INSERT INTO score_author(score, composer)
        VALUES (?,?)
        """,
        (score_id, composer_id),
    )
    return cursor.lastrowid


def insert_edition_author(edition_id, editor_id, cursor):
    cursor.execute(
        """
        INSERT INTO edition_author(edition, editor)
        VALUES (?,?)
        """,
        (edition_id, editor_id),
    )
    return cursor.lastrowid


def insert_print(print_, edition_id, cursor):
    if print_.partiture:
        is_partiture = "Y"
    else:
        is_partiture = "N"
    cursor.execute(
        """
        INSERT INTO print(id, partiture, edition)
        VALUES (?,?,?)
        """,
        (print_.print_id, is_partiture, edition_id),
    )
    return cursor.lastrowid


def insert_score(score, persist_scores, cursor):
    if score not in persist_scores:
        cursor.execute(
            """
            INSERT INTO score(name, genre, key, incipit, year)
            VALUES (?,?,?,?,?)
            """,
            (score.name, score.genre, score.key, score.incipit, score.year),
        )
        score_id = cursor.lastrowid
        persist_scores[score] = score_id
        return score_id
    else:
        return persist_scores[score]


def insert_edition(edition, score_id, persist_editions, cursor):
    if edition not in persist_editions:
        cursor.execute(
            """
            INSERT INTO edition(score, name, year)
            VALUES (?,?,?)
            """,
            (score_id, edition.name, None),
        )
        edition_id = cursor.lastrowid
        persist_editions[edition] = edition_id
        return edition_id
    else:
        return persist_editions[edition]


if __name__ == "__main__":
    args = sys.argv
    if len(args) < 3:
        print("Wrong number of arguments.")
        print("./import.py INPUT OUTPUT")
        exit(1)

    data_file = args[1]
    DB = args[2]
    with open(os.path.join(here, "scorelib.sql")) as f:
        sql_script = f.read()
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    try:
        cur.executescript(sql_script)
    except:
        pass
    else:
        conn.commit()

    persisted_scores = {}
    persisted_editions = {}
    persisted_people = {}
    prints = scorelib.load(data_file)
    for print_ in prints:
        edition = print_.edition
        composition = print_.composition()
        score_id = insert_score(composition, persisted_scores, cur)
        edition_id = insert_edition(
            edition, score_id, persisted_editions, cur
        )

        insert_print(print_, edition_id, cur)

        for editor in edition.authors:
            editor_id = insert_person(editor, persisted_people, cur)
            insert_edition_author(edition_id, editor_id, cur)
        for composer in composition.authors:
            composer_id = insert_person(composer, persisted_people, cur)
            insert_score_author(score_id, composer_id, cur)
        for idx, voice in enumerate(composition.voices, 1):
            insert_voice(voice, idx, score_id, cur)

    conn.commit()
    conn.close()
