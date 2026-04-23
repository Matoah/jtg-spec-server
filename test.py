# from dotenv import load_dotenv
# from workflow.index import invoke_workflow_async
#
# load_dotenv()
#
# if __name__ == "__main__":
#     import asyncio
#
#     async def run_workflow():
#         async for chunk in invoke_workflow_async("砂砾垫层是什么意思?"):
#             print(chunk, end="")
#
#     asyncio.run(run_workflow())
import json
from enums.document_stage import DocumentStage
from enums.document_subcategory import DocumentSubcategory
from enums.document_type import DocumentType
from enums.document_keyword import DocumentKeyword

from enums.document_category import DocumentCategory


content = "\"{   \\\"is_related\\\": true,   \\\"reject_message\\\": \\\"\\\" }\"\n"

def main(data: str) -> dict:
    json_data = json.loads(data)
    return {
        "is_related": "true" if json_data.get("is_related", False) else "false",
        "reject_message": json_data.get("reject_message", "")
    }

stage="\n".join(["  - " + stage.value for stage in DocumentStage])
category="\n".join(["  - " + cy.value for cy in DocumentCategory])
subcategory="\n".join(["  - " + sc.value for sc in DocumentSubcategory])
type="\n".join(["  - " + dt.value for dt in DocumentType])
keyword="\n".join(["  - " + kw.value for kw in DocumentKeyword])
print("生命周期："+"-"*20)
print(stage)
print("分类："+"-"*20)
print(category)
print("子分类："+"-"*20)
print(subcategory)
print("类型："+"-"*20)
print(type)
print("关键词："+"-"*20)
print(keyword)
