from completeions.base import JsonCompletionLLM
from enums.document_category import DocumentCategory
from enums.document_keyword import DocumentKeyword
from enums.document_subcategory import DocumentSubcategory
from models.document_filter import DocumentFilter
from enums.document_type import DocumentType
from enums.document_stage import DocumentStage
from completeions.prompt_factory import get_prompt, PromptType


class DocumentFilterCompletion(JsonCompletionLLM[DocumentFilter]):

    def __init__(self):
        super().__init__()


    def _get_json_schema(self):
        return DocumentFilter

    def _build_system_prompt(self):
        """
        构建系统提示
        """
        prompt_content = get_prompt(PromptType.DOCUMENT_FILTER)
        return prompt_content.format(
            stage="\n".join(["  - " + stage.value for stage in DocumentStage]),
            category="\n".join(["  - " + cy.value for cy in DocumentCategory]),
            subcategory="\n".join(["  - " + sc.value for sc in DocumentSubcategory]),
            type="\n".join(["  - " + dt.value for dt in DocumentType]),
            keyword="\n".join(["  - " + kw.value for kw in DocumentKeyword]),
        )
