from enum import Enum


class DocumentStage(str, Enum):
    """
    文档生命周期阶段
    """

    DESIGN = "设计阶段",

    CONSTRUCTION = "施工阶段",

    MAINTENANCE = "养护阶段",

    ALL = "全生命周期"
