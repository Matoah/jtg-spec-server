from enum import Enum

class DocumentSubcategory(str, Enum):
    """
    文档子分类
    """

    BRIDGE = "桥梁",

    TUNNEL = "隧道",

    SUBGRADE = "路基",

    PAVEMENT = "路面",

    TRAFFIC_ENGINEERING = "交通工程",

    GENERAL = "通用"
