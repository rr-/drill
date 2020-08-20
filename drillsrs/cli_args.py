import enum


class ArgEnum(enum.Enum):
    def __str__(self):
        return self.name.lower()

    def __repr__(self):
        return str(self)

    @classmethod
    def parse(cls, arg):
        try:
            return cls[arg]
        except KeyError:
            raise ValueError


class Mode(ArgEnum):
    direct = "direct"
    reversed = "reversed"
    mixed = "mixed"
