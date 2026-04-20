from enum import Enum


class DocumentCategory(str, Enum):
    """
    文档分类
    """

    DESIGN = "设计",

    CONSTRUCTION = "施工",

    MAINTENANCE = "养护",

    TESTING = "试验检测",

    COST = "造价",

    INFORMATION = "信息化",

    SURVEY = "勘察",

    QUALITY_AND_SAFETY = "质量安全",

    GENERAL = "综合",
