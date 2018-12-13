import os
import re

# regular expressions
RE_YEAR = re.compile(r".*?(\d{4}).*?")
RE_VOICE_RANGE = re.compile(r"(\w+\d?)--?(\w+\d?)")

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
                    Person(author["name"], author["born"], author["died"])
                )

            # create voices objects
            voices = []
            for voice in data.get("voices", []):
                voices.append(Voice(voice["name"], voice["range"]))

            # create composition object
            composition = Composition(
                data.get("title"),
                data.get("incipit"),
                data.get("key"),
                data.get("genre"),
                data.get("year"),
                voices,
                authors,
            )

            # editors = [Person(data.get("editor"))]
            editors = [Person(editor, None, None) for editor in data.get("editors", [])]
            # create edition
            edition = Edition(composition, editors, data.get("edition"))

            if data.get("print_id") is not None:
                print_ = Print(edition, data["print_id"], data["partiture"])
                prints.append(print_)
                # print(print_)
            data = init_data()
            continue

        if line_split:
            attr_type = line_split[0].lower()
            attr_value = line_split[1].strip() if len(line_split) > 1 else ""
        else:
            attr_type = ""
            attr_value = ""
        if "print" in attr_type:
            data["print_id"] = int(attr_value)
        elif attr_type == "partiture":
            data["partiture"] = attr_value.lower() == "yes"
        elif attr_type == "composer":
            authors = attr_value.split(";")
            for author in authors:
                split = author.split("(")
                name = split[0].strip()
                if name:
                    born = None
                    died = None
                    if len(split) > 1:
                        years = RE_YEAR.findall(split[1])
                        if not years:
                            continue
                        born = int(years[0])
                        if len(years) > 1:
                            died = int(years[1])
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
            regex = re.compile(r"\w\.,")
            match = regex.search(attr_value)
            if match:
                editors = attr_value.split(".,")
                editors = [editor.strip(" .")+"." for editor in editors]
                data["editors"] = editors
            else:
                data["editors"] = [attr_value] if attr_value else []
            # data["editor"] = attr_value if attr_value else None

    return prints


class Print:
    def __init__(self, edition, print_id: int, partiture: bool):
        self.edition = edition
        self.print_id = print_id
        self.partiture = partiture

    def format(self):
        LINES = {
            "print_id": "Print Number: {}".format(self.print_id),
            "composers": "Composer: {}".format(
                self._composers_line_value(self.composition())
            ),
            "title": "Title: {}".format(self.composition().name or ""),
            "genre": "Genre: {}".format(self.composition().genre or ""),
            "key": "Key: {}".format(self.composition().key or ""),
            "composition_year": "Composition Year: {}".format(
                self.composition().year or ""
            ),
            "publication_year": "Publication Year: ",
            "edition": "Edition: {}".format(self.edition.name or ""),
            "editors": "Editor: {}".format(
                self._editors_line_value(self.edition) or ""
            ),
            "voices": "\n".join(self._voices_lines(self.composition().voices)),
            "partiture": "Partiture: {}".format("yes" if self.partiture else "no"),
            "incipit": "Incipit: {}".format(self.composition().incipit or ""),
        }
        return "\n".join(LINES.values())

    def composition(self):
        return self.edition.composition

    def _composers_line_value(self, composition):
        composers = composition.authors
        msg = ""
        for composer in composers:
            if composer.name:
                msg += composer.name
                if composer.born or composer.died:
                    msg += " ({}--{})".format(composer.born or "", composer.died or "")
        return msg

    def _voices_lines(self, voices):
        parts = []
        for idx, voice in enumerate(voices, 1):
            range_ = voice.range
            name = voice.name
            vals = []
            if range_:
                vals.append(range_)
            if name:
                vals.append(name)
            msg = "Voice {number}: ".format(number=idx) + ", ".join(vals)
            parts.append(msg)
        return parts

    def _editors_line_value(self, edition):
        return ", ".join([editor.name for editor in edition.authors if editor.name])

    def __repr__(self):
        return "<Print: id={id}, edition={edition}, partiture={partiture}".format(id=self.print_id, edition=self.edition, partiture=self.partiture)


class Edition:
    def __init__(self, composition=None, authors=None, name=None):
        self.composition = composition
        self.authors = authors or []
        self.name = name

    def __repr__(self):
        return "<Edition: composition={}, authors={}, name={}>".format(
            self.composition, self.authors, self.name
        )


class Composition:
    def __init__(
        self,
        name=None,
        incipit=None,
        key=None,
        genre=None,
        year=None,
        voices=None,
        authors=None,
    ):
        self.name = name
        self.incipit = incipit
        self.key = key
        self.genre = genre
        self.year = year
        self.voices = voices or []
        self.authors = authors or []

    def __repr__(self):
        return "<Composition: name={}, incipit={}, key={}, genre={}, year={}, voices={}, authors={}>".format(
            self.name,
            self.incipit,
            self.key,
            self.genre,
            self.year,
            self.voices,
            self.authors,
        )


class Voice:
    def __init__(self, name=None, _range=None):
        self.name = name
        self.range = _range

    def __repr__(self):
        return "<Voice: name={}, range={}>".format(self.name, self.range)


class Person:
    def __init__(self, name=None, born=None, died=None):
        self.name = name
        self.born = born
        self.died = died

    def __repr__(self):
        return "<Person: name={}; born={}; died={}>".format(
            self.name, self.born, self.died
        )
