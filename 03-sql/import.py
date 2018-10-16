import os
import sqlite3
from scorelib import Person
import scorelib

def insert_person(person: Person, connection):
    cur = connection.cursor()
    cur.execute("SELECT * FROM person WHERE name=?", (person.name,))
    person_found = cur.fetchone()

    if person_found:
        if (person_found[1] and person_found[2]) or not (person.born and person.died):
            return person_found[0]
        born = person_found[1] if not person_found[1] else person.born
        died = person_found[2] if not person_found[2] else person.died
        sql = f"UPDATE person SET born=?, died=? WHERE name=?"
        cur.execute(sql, (born, died, person.name,))
        connection.commit()
        return person_found[0]

    sql = "INSERT INTO person(born, died, name) VALUES (?,?,?)"
    cur.execute(sql, (person.born, person.died, person.name,))
    connection.commit()
    return cur.lastrowid

def insert_voice(voice, voice_number, score_id, connection):
    cur = connection.cursor()
    # cur.execute("SELECT * FROM voice WHERE score=? AND number=? AND name=?", (score_id, voice_number, voice.name,))
    # voice_found = cur.fetchone()
    # if voice_found:
    #     return voice_found[0]

    cur.execute("INSERT OR IGNORE INTO voice VALUES(NULL, ?, ?, ?, ?)", (voice_number, score_id, voice.range, voice.name))
    connection.commit()
    # return cur.lastrowid


def insert_edition(edition, score_id, connection):
    cur = connection.cursor()
    cur.execute("SELECT * FROM edition WHERE score=? AND name=?", (score_id, edition.name))
    edition_found = cur.fetchone()
    if edition_found:
        return edition_found[0]

    cur.execute("INSERT INTO edition VALUES(NULL, ?,?,NULL)", (score_id, edition.name,))
    connection.commit()
    return cur.lastrowid

def insert_score(score, connection):
    cur = connection.cursor()
    cur.execute('SELECT * FROM score WHERE name=?', (score.name,))
    score_found = cur.fetchone()
    if score_found:
        if (score.genre and not score_found[1]) or (score.key and not score_found[2]) or (score.incipit and not score_found[3]) or (score.year and not score_found[4]):
            genre = score_found[1] or score.genre
            key = score_found[2] or score.key
            incipit = score_found[3] or score.incipit
            year = score_found[4] or score.year
            cur.execute("UPDATE score SET genre=?, key=?, incipit=?, year=? WHERE name=?", (genre, key, incipit, year, score.name,))
            conn.commit()
        return score_found[0]

    cur.execute('INSERT INTO score(name,genre,key,incipit,year) VALUES(?,?,?,?,?)', (score.name, score.genre, score.key, score.incipit, score.year,))
    connection.commit()
    return cur.lastrowid

def insert_score_author(score_id, composer_id, connection):
    cur = connection.cursor()
    cur.execute("INSERT OR IGNORE INTO score_author VALUES(NULL,?,?)", (score_id, composer_id))
    connection.commit()

def insert_edition_author(edition_id, editor_id, connection):
    cur = connection.cursor()
    cur.execute("INSERT OR IGNORE INTO edition_author VALUES(NULL,?,?)", (edition_id, editor_id,))
    connection.commit()

def insert_print(print_, edition_id, connection):
    cur = connection.cursor()
    if print_.partiture:
        pmsg = 'Y'
    else:
        pmsg = 'N'
    cur.execute("INSERT OR IGNORE INTO print VALUES(?,?,?)", (print_.print_id, pmsg, edition_id))
    connection.commit()

if __name__ == "__main__":
    DB = "scorelib.dat"
    here = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(here, 'scorelib.sql')) as f:
        sql_script = f.read()
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    try:
        cur.executescript(sql_script)
    except:
        pass
    else:
        conn.commit()

    prints = scorelib.load(os.path.join(here, 'scorelib.txt'))
    size = len(prints)
    c = 1
    for print_ in prints:
        print("Print", c)
        c += 1
        edition = print_.edition
        composition = print_.composition()
        score_id = insert_score(composition, conn)
        edition_id = insert_edition(edition, score_id, conn)
        insert_print(print_, edition_id, conn)
        for editor in edition.authors:
            editor_id = insert_person(editor, conn)
            insert_edition_author(edition_id, editor_id, conn)
        for composer in composition.authors:
            composer_id = insert_person(composer, conn)
            insert_score_author(score_id, composer_id, conn)
        for idx, voice in enumerate(composition.voices,1):
            insert_voice(voice, idx, score_id, conn)

    conn.close()