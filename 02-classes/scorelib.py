import os


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
