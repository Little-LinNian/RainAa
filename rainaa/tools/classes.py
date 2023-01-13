from typing import Type


def str_to_class(FatherClass: Type, wanted: str,ignore_high_low: bool) -> Type:
    """将字符串转换为类"""
    subclasses = FatherClass.__subclasses__()
    for subclass in subclasses:
        if ignore_high_low:
            if subclass.__name__.lower() == wanted.lower():
                return subclass
        else:
            if subclass.__name__ == wanted:
                return subclass