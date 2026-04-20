from typing import Any

def is_enum_value(value: Any, enum_cls) -> bool:
    """
    检查值是否是枚举类的值
    :param value: 值
    :param enum_cls: 枚举类
    :return:
    """
    try:
        enum_cls(value)  # 尝试用 value 创建枚举成员
        return True
    except ValueError:
        return False