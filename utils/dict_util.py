def is_empty_value(value):
    """判断一个值是否为空"""
    if value is None:
        return True
    if isinstance(value, (str, list, tuple, dict, set)):
        return len(value) == 0
    return False

def is_all_empty(d):
    return all(is_empty_value(value) for value in d.values())