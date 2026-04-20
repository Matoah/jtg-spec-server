from enum import Enum


class AuditStatus(str, Enum):
    """审核状态"""
    DEFAULT = "default"
    PASS = "pass"
    REJECT = "reject"
