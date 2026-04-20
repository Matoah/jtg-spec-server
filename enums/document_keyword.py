from enum import Enum


class DocumentKeyword(str, Enum):
    """
    文档关键词
    """

    BRIDGE = "桥梁",

    TUNNEL = "隧道",

    SUBGRADE = "路基",

    PAVEMENT = "路面",

    SEISMIC = "抗震",

    CONSTRUCTION = "施工",

    DESIGN = "设计",

    MAINTENANCE = "养护",
