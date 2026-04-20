from pydantic import BaseModel, Field, field_validator

from enums.document_category import DocumentCategory
from enums.document_keyword import DocumentKeyword
from enums.document_subcategory import DocumentSubcategory
from enums.document_type import DocumentType
from enums.document_stage import DocumentStage
from utils.enum_util import is_enum_value


def validate_enum_values(value: str | list[str], enum_cls) -> list[str]:
    v = [value] if not isinstance(value, list) else value
    return [item for item in v if is_enum_value(item, enum_cls)]


class DocFilter(BaseModel):
    """
    文档筛选条件
    """
    category: list[DocumentCategory] = Field(default_factory=list, description="文档分类")

    @field_validator("category", mode="before")
    @classmethod
    def category_validator(cls, v):
        return validate_enum_values(v, DocumentCategory)

    subcategory: list[DocumentSubcategory] = Field(default_factory=list, description="文档子分类")

    @field_validator("subcategory", mode="before")
    @classmethod
    def subcategory_validator(cls, v):
        return validate_enum_values(v, DocumentSubcategory)

    type: list[DocumentType] = Field(default_factory=list, description="文档类型")

    @field_validator("type", mode="before")
    @classmethod
    def type_validator(cls, v):
        return validate_enum_values(v, DocumentType)

    stage: list[DocumentStage] = Field(default_factory=list, description="文档阶段")

    @field_validator("stage", mode="before")
    @classmethod
    def stage_validator(cls, v):
        return validate_enum_values(v, DocumentStage)

    keyword: list[DocumentKeyword] = Field(default_factory=list, description="文档关键词")

    @field_validator("keyword", mode="before")
    @classmethod
    def keyword_validator(cls, v):
        return validate_enum_values(v, DocumentKeyword)

    name: str = Field(default="", description="文档名称")


class SpecFilter(BaseModel):
    """
    标准规范筛选条件
    """

    name: str = Field(default="", description="标准规范名称")

    code: str = Field(default="", description="标准规范编码")


class DocumentFilter(BaseModel):
    """
    文档筛选条件
    """

    doc_filter: DocFilter = Field(description="文档筛选条件")

    spec_filter: SpecFilter = Field(description="标准规范筛选条件")


if __name__ == "__main__":
    params = {
        "doc_filter": {
            "category": [
                "勘察"
            ],
            "subcategory": [
                "通用"
            ],
            "type": [],
            "state": [],
            "keyword": [
                "盐渍土",
                "勘察"
            ],
            "name": ""
        },
        "spec_filter": {
            "name": "",
            "code": ""
        }
    }
    document_filter = DocumentFilter(**params)
    print(document_filter)
