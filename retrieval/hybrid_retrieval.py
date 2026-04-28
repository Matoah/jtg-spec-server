from completeions.document_filter import DocumentFilterCompletion
from graph.graph_factory import get_graph
from models.document_filter import DocumentFilter
from utils.dict_util import is_all_empty
from utils.dify_util import retrieve_document as retrieve_dify_document
from langchain_core.documents import Document

def _build_where_clause(condition: DocumentFilter) -> tuple[str, dict]:
    """
    构建Cypher查询的WHERE子句
    :param condition: 文档筛选条件
    :return: WHERE子句和参数字典
    """
    conditions = []
    params = {}

    doc = condition.doc_filter
    std = condition.spec_filter

    if doc:
        if doc.category:
            conditions.append("d.分类 IN $categories")
            params["categories"] = [item.value for item in doc.category]

        if doc.subcategory:
            conditions.append("d.子分类 IN $subcategories")
            params["subcategories"] = [item.value for item in doc.subcategory]

        if doc.type:
            conditions.append("d.类型 IN $types")
            params["types"] = [item.value for item in doc.type]

        if doc.stage:
            conditions.append("d.生命周期阶段 IN $stages")
            params["stages"] = [item.value for item in doc.stage]

        if doc.keyword:
            conditions.append(
                "ANY(k IN $keywords WHERE d.关键字 CONTAINS k)"
            )
            params["keywords"] = [item.value for item in doc.keyword]

        if doc.name:
            conditions.append("d.文件名称 CONTAINS $doc_names")
            params["doc_names"] = doc.name

    if std:
        if std.name:
            conditions.append("s.名称 CONTAINS $std_name")
            params["std_name"] = std.name

        if std.code:
            conditions.append("s.编号 = $std_code")
            params["std_code"] = std.code

    where_clause = ""
    if conditions:
        where_clause = "WHERE " + " AND ".join(conditions)

    return where_clause, params

def _get_document_list(query: str)-> list[str]:
    """
    根据查询条件获取文档列表
    :param query: 查询条件
    :return: 文档名称列表
    """
    document_filter = DocumentFilterCompletion()
    condition = document_filter.ask(query)
    if is_all_empty(condition.model_dump()):
        return []
    else:
        where_clause, params = _build_where_clause(condition)

        cypher = f"""
            MATCH (s:标准规范)-[:关联文档]->(d:文档)
            {where_clause}
            RETURN d.文件名称 as name
            LIMIT 50
            """

        graph = get_graph()

        result = graph.run(cypher, **params)
        return [record["name"] for record in result]

def get_document_md5_list(document_filter: DocumentFilter) -> list[str]:
    """
    根据文档筛选条件，获取文档md5列表
    :param document_filter: 文档筛选条件
    :return: 文档md5列表
    """
    if is_all_empty(document_filter.model_dump()):
        return []
    else:
        where_clause, params = _build_where_clause(document_filter)
        cypher = f"""
                    MATCH (s:标准规范)-[:关联文档]->(d:文档)
                    {where_clause}
                    RETURN d.文件唯一标识 as md5
                    LIMIT 20
                    """

        graph = get_graph()

        result = graph.run(cypher, **params)
        return [record["md5"] for record in result]

def retrieve_document(query: str, top_k: int = 5) -> list[Document]:
    """检索知识库"""
    document_list = _get_document_list(query)
    result: list[dict] = retrieve_dify_document(query, top_k * 3 if document_list else top_k)
    original_result = result
    if document_list:
        result = [doc for doc in result if doc.get("segment",{}).get("document",{}).get("name","") in document_list]

    if original_result and not result:
        # 知识检索有内容，但根据文档筛选后为空，则先判定为文档列表不正确，忽略
        result = original_result
    documents: list[Document] = []
    for doc in result:
        segment = doc.get("segment",{})
        if not segment or not segment.get("enabled", True):
            continue
        document_name = segment.get("document").get("name","")
        documents.append(Document(
            page_content="\n".join([segment.get('content', ""), f"来源文件：{document_name}"]),
            metadata={
                "search_type": "hybrid",
                "document_name": document_name,
                "score": doc.get("score",0),
                "tokens": doc.get("tokens",0),
            }
        ))
    return documents[:top_k]


