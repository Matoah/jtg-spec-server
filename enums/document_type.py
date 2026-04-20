from enum import Enum


class DocumentType(str, Enum):
    """
    文档类型
    """

    STANDARD = "标准",

    SPECIFICATION = "规范",

    GUIDELINE = "细则",

    PROCEDURE = "规程",

    GUIDE = "导则",

    METHOD = "办法",

    QUOTA = "定额",

    GUIDANCE = "指南",

    DRAWING = "通用图",
