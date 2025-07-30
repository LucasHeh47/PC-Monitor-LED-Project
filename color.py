import json
from pathlib import Path

class ColorValue:
    def __init__(self, name, rgb):
        self.name = name.upper()
        self.value = tuple(rgb)

    @property
    def r(self): return self.value[0]
    @property
    def g(self): return self.value[1]
    @property
    def b(self): return self.value[2]

    def __iter__(self):
        return iter(self.value)

    def __getitem__(self, index):
        return self.value[index]

    def __repr__(self):
        return f"ColorValue(name='{self.name}', value={self.value})"


class Color:
    _predefined = {
        name: ColorValue(name, rgb) for name, rgb in {
            "RED":     (255, 0, 0),
            "GREEN":   (0, 255, 0),
            "BLUE":    (0, 0, 255),
            "WHITE":   (255, 255, 255),
            "BLACK":   (0, 0, 0),
            "YELLOW":  (255, 255, 0),
            "CYAN":    (0, 255, 255),
            "MAGENTA": (255, 0, 255),
            "ORANGE":  (255, 80, 0),
            "PURPLE":  (128, 0, 128),
            "VIOLET":  (128, 0, 255),
            "PINK":    (255, 105, 180),
            "TEAL":    (0, 128, 128),
        }.items()
    }

    _custom = {}
    _file_path = Path("custom_colors.json")

    @classmethod
    def load_custom_colors(cls):
        if cls._file_path.exists():
            with open(cls._file_path, "r") as f:
                data = json.load(f)
                cls._custom = {
                    k.upper(): ColorValue(k.upper(), tuple(v))
                    for k, v in data.items()
                }

    @classmethod
    def save_custom_colors(cls):
        with open(cls._file_path, "w") as f:
            json.dump({k: v.value for k, v in cls._custom.items()}, f)

    @classmethod
    def add_custom_color(cls, name: str, r: int, g: int, b: int):
        cls._custom[name.upper()] = ColorValue(name, (r, g, b))
        cls.save_custom_colors()

    @classmethod
    def get(cls, name: str):
        name = name.upper()
        if name in cls._predefined:
            return cls._predefined[name]
        elif name in cls._custom:
            return cls._custom[name]
        else:
            raise KeyError(f"Color '{name}' not found")

    @classmethod
    def all(cls):
        return {**cls._predefined, **cls._custom}

    @classmethod
    def has(cls, name):
        return name.upper() in cls._predefined or name.upper() in cls._custom

    @classmethod
    def __class_getitem__(cls, name):
        return cls.get(name)
