from typing import Type, TypeVar

T = TypeVar("T")


def str_to_class(FatherClass: Type[T], wanted: str, ignore_high_low: bool) -> Type[T]:
    """将字符串转换为类"""
    subclasses = FatherClass.__subclasses__()
    for subclass in subclasses:
        if ignore_high_low:
            if subclass.__name__.lower() == wanted.lower():
                return subclass
        elif subclass.__name__ == wanted:
            return subclass
