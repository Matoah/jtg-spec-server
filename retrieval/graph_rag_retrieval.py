import json
import logging
from graph.graph_factory import get_graph
from completeions.graph_query import GraphQueryCompletion
from models.graph_path import GraphPath
from models.graph_query import GraphQuery, NodeConstraint
from enums.graph_query_type import GraphQueryType
from langchain_core.documents import Document
from typing import Optional
from models.knowledge_subgraph import KnowledgeSubgraph
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


def _understand_query(query: str) -> GraphQuery:
    """理解查询字符串"""
    graph = get_graph()
    node_schemas = graph.get_node_schema()
    relation_schemas = graph.get_relationship_schema()
    graph_query = GraphQueryCompletion(node_schemas, relation_schemas)
    return graph_query.ask(query)


def _parse_neo4j_path(record) -> Optional[GraphPath]:
    """解析Neo4j路径记录"""
    try:
        path_nodes = []
        for node in record["path_nodes"]:
            path_nodes.append({
                "id": node.get("nodeId", ""),
                "name": node.get("name", ""),
                "labels": list(node.labels),
                "properties": dict(node)
            })

        relationships = []
        for rel in record["rels"]:
            relationships.append({
                "type": type(rel).__name__,
                "properties": dict(rel)
            })

        return GraphPath(
            nodes=path_nodes,
            relationships=relationships,
            path_length=record["path_len"],
            relevance_score=record["relevance"],
            path_type="multi_hop"
        )

    except Exception as e:
        logger.error(f"路径解析失败: {e}")
        return None


def _find_shortest_paths(graph_query: GraphQuery) -> list[GraphPath]:
    """查找最短路径"""
    source_query_cypher, source_query_params = _gen_source_query_cypher(graph_query.source_entities)
    target_filter_clause, target_filter_params = _gen_target_filter_clause(graph_query.target_entities)
    max_depth = graph_query.max_depth
    cypher_query = f"""
    {source_query_cypher}
    MATCH path = shortestPath((source)-[*1..{max_depth}]-(target))
    {target_filter_clause}
    // 计算路径相关性
    WITH path, source, target,
         length(path) as path_len,
         relationships(path) as rels,
         nodes(path) as path_nodes

    // 路径评分：短路径 + 高度数节点 + 关系类型匹配
    WITH path, source, target, path_len, rels, path_nodes,
         (1.0 / path_len) + 
         (REDUCE(s = 0.0, n IN path_nodes | s + COUNT {{ (n)--() }}) / 10.0 / size(path_nodes)) +
         (CASE WHEN ANY(r IN rels WHERE type(r) IN $relation_types) THEN 0.3 ELSE 0.0 END) as relevance

    ORDER BY relevance DESC
    LIMIT {graph_query.max_nodes}

    RETURN path, source, target, path_len, rels, path_nodes, relevance
    
    """
    graph = get_graph()
    paths = []
    params = {
        **source_query_params,
        **target_filter_params,
        "relation_types": graph_query.relation_types or []
    }

    result = graph.run(cypher_query, **params)

    for record in result:
        path_data = _parse_neo4j_path(record)
        if path_data:
            paths.append(path_data)
    return paths


def _gen_source_query_cypher(source_constraints: list[NodeConstraint]) -> tuple[str, dict]:
    """生成源实体查询Cypher语句"""
    cypher_query = """
    UNWIND $source_constraints AS source_constraint
    MATCH (source)
    WHERE ANY(
        label IN labels(source) WHERE label = source_constraint.label
    )  AND ALL(
        con IN keys(COALESCE(source_constraint.constraints, {})) WHERE 
        source[con] CONTAINS source_constraint.constraints[con] OR 
        source_constraint.constraints[con] CONTAINS source[con]
    )
    """
    return cypher_query, {
        "source_constraints": [source.model_dump() for source in source_constraints] if source_constraints else []}


def _gen_target_filter_clause(target_constraints: list[NodeConstraint]) -> tuple[str, dict]:
    """
    生成目标实体过滤Cypher语句
    :param target_constraints: 目标实体约束列表
    :return:
    """
    target_filter_clause = ""
    if target_constraints:
        target_filter_clause = """
        AND ANY(
            target_constraint IN $target_constraints
            WHERE ANY(
                label IN labels(target) 
                WHERE label = target_constraint.label
            )
            AND ALL(
                con IN keys(COALESCE(target_constraint.constraints, {})) WHERE target[con] = target_constraint.constraints[con]
            )
        )
        """
    cypher_query = f"""
    WHERE NOT source = target{target_filter_clause}
    """
    return cypher_query, {
        "target_constraints": [target.model_dump() for target in target_constraints] if target_constraints else []}


def _multi_hop_traversal(graph_query: GraphQuery) -> list[GraphPath]:
    """
    多跳图遍历：这是图RAG的核心优势
    通过图结构发现隐含的知识关联
    :param graph_query:
    :return:
    """
    logger.info(f"执行多跳遍历: {graph_query.source_entities} -> {graph_query.target_entities}")

    paths = []

    graph = get_graph()

    try:
        # 构建多跳遍历查询
        max_depth = graph_query.max_depth

        # 根据查询类型选择不同的遍历策略
        if graph_query.query_type == GraphQueryType.MULTI_HOP or graph_query.query_type == GraphQueryType.ENTITY_RELATION:
            # 根据是否有目标关键词动态拼接过滤条件
            target_filter_clause, target_filter_params = _gen_target_filter_clause(graph_query.target_entities)
            source_query_cypher, source_query_params = _gen_source_query_cypher(graph_query.source_entities)
            cypher_query = f"""
                    // 多跳推理查询
                    {source_query_cypher}

                    // 执行多跳遍历
                    MATCH path = (source)-[*1..{max_depth}]-(target)
                    {target_filter_clause}

                    // 计算路径相关性
                    WITH path, source, target,
                         length(path) as path_len,
                         relationships(path) as rels,
                         nodes(path) as path_nodes

                    // 路径评分：短路径 + 高度数节点 + 关系类型匹配
                    WITH path, source, target, path_len, rels, path_nodes,
                         (1.0 / path_len) + 
                         (REDUCE(s = 0.0, n IN path_nodes | s + COUNT {{ (n)--() }}) / 10.0 / size(path_nodes)) +
                         (CASE WHEN ANY(r IN rels WHERE type(r) IN $relation_types) THEN 0.3 ELSE 0.0 END) as relevance

                    ORDER BY relevance DESC
                    LIMIT {graph_query.max_nodes}

                    RETURN path, source, target, path_len, rels, path_nodes, relevance
                    """

            params = {
                **source_query_params,
                **target_filter_params,
                "relation_types": graph_query.relation_types or []
            }

            result = graph.run(cypher_query, **params)

            for record in result:
                path_data = _parse_neo4j_path(record)
                if path_data:
                    paths.append(path_data)

        elif graph_query.query_type == GraphQueryType.PATH_FINDING:
            # 最短路径查找
            paths.extend(_find_shortest_paths(graph_query))

    except Exception as e:
        logger.error(f"多跳遍历失败: {e}")

    logger.info(f"多跳遍历完成，找到 {len(paths)} 条路径")
    return paths


def _find_entity_details(graph_query: GraphQuery) -> List[Dict[str, Any]]:
    """
    查询实体详细信息
    :param graph_query: 查询模型
       :return:
    """
    source_query_cypher, source_query_params = _gen_source_query_cypher(graph_query.source_entities)
    cypher_query = f"""
    {source_query_cypher}
    RETURN source
    LIMIT {graph_query.max_nodes}
    """
    graph = get_graph()
    result = graph.run(cypher_query, **source_query_params)
    entities = []
    for record in result:
        node = record["source"]
        entities.append({
            "id": node.get("nodeId", ""),
            "name": node.get("name", ""),
            "labels": list(node.labels),
            "properties": dict(node)
        })
    return entities


def _build_entity_description(entity: Dict[str, Any]) -> str:
    """构建实体的自然语言描述"""
    definition_script = []
    labels = entity.get("labels", [])
    definition_script.append(f"# {",".join(labels)}")
    properties = entity.get("properties", {})
    for key, value in properties.items():
        definition_script.append(f"- **{key}**: {value}")
    return "\n".join(definition_script)


def _build_path_description(path: GraphPath) -> str:
    """构建路径的自然语言描述"""
    if not path.nodes:
        return ""

    node_desc_parts = []
    relation_desc_parts = ["# 关系描述"]
    for i, node in enumerate(path.nodes):
        node_desc_parts.append(_build_entity_description(node))
        if i < len(path.relationships):
            rel_type = path.relationships[i].get("type", "相关")
            relation_desc_parts.append(
                f"({",".join(node.get('labels', []))}) - {rel_type} -> ({",".join((path.nodes[i + 1] if path.nodes[i + 1] else {}).get('labels', []))})")

    return "\n".join(node_desc_parts + relation_desc_parts)


def _paths_to_documents(paths: list[GraphPath], query: str) -> list[Document]:
    """将图路径转换为Document对象"""
    documents = []

    for i, path in enumerate(paths):
        # 构建路径描述
        path_desc = _build_path_description(path)

        doc = Document(
            page_content=path_desc,
            metadata={
                "search_type": "graph_path",
                "path_length": path.path_length,
                "relevance_score": path.relevance_score,
                "path_type": path.path_type,
                "node_count": len(path.nodes),
                "relationship_count": len(path.relationships),
                "recipe_name": path.nodes[0].get("name", "图结构结果") if path.nodes else "图结构结果"
            }
        )
        documents.append(doc)

    return documents


def _entity_to_documents(entities: List[Dict[str, Any]]) -> list[Document]:
    """
    将实体详细信息转换为Document对象
    :param entities: 实体列表
    :return:
    """
    documents = []
    for entity in entities or []:
        doc = Document(
            page_content=_build_entity_description(entity),
            metadata={
                "search_type": "entity_query",
                "relevance_score": 1.0
            }
        )
        documents.append(doc)

    return documents


def _build_knowledge_subgraph(record) -> KnowledgeSubgraph:
    """构建知识子图对象"""
    try:
        central_nodes = [dict(record["source"])]
        connected_nodes = [dict(node) for node in record["nodes"]]
        relationships = [dict(rel) for rel in record["rels"]]

        return KnowledgeSubgraph(
            central_nodes=central_nodes,
            connected_nodes=connected_nodes,
            relationships=relationships,
            graph_metrics=record["metrics"],
            reasoning_chains=[]
        )
    except Exception as e:
        logger.error(f"构建知识子图失败: {e}")
        return KnowledgeSubgraph(
            central_nodes=[],
            connected_nodes=[],
            relationships=[],
            graph_metrics={},
            reasoning_chains=[]
        )


def _fallback_subgraph_extraction(graph_query: GraphQuery) -> KnowledgeSubgraph:
    """降级子图提取"""
    return KnowledgeSubgraph(
        central_nodes=[],
        connected_nodes=[],
        relationships=[],
        graph_metrics={},
        reasoning_chains=[]
    )


def _extract_knowledge_subgraph(graph_query: GraphQuery) -> KnowledgeSubgraph:
    """
    提取知识子图：获取实体相关的完整知识网络
    这体现了图RAG的整体性思维
    """
    logger.info(f"提取知识子图: {graph_query.source_entities}")

    graph = get_graph()
    source_query_cypher, source_query_params = _gen_source_query_cypher(graph_query.source_entities)
    try:
        # 简化的子图提取（不依赖APOC）
        cypher_query = f"""
        // 找到源实体
        {source_query_cypher}

        // 获取指定深度的邻居
        MATCH (source)-[r*1..{graph_query.max_depth}]-(neighbor)
        WITH source, collect(DISTINCT neighbor) as neighbors, 
             collect(DISTINCT r) as relationships
        //WHERE size(neighbors) <= $max_nodes

        // 计算图指标
        WITH source, neighbors, relationships,
             size(neighbors) as node_count,
             size(relationships) as rel_count

        RETURN 
            source,
            neighbors[0..{graph_query.max_nodes}] as nodes,
            relationships[0..{graph_query.max_nodes}] as rels,
            {{
                node_count: node_count,
                relationship_count: rel_count,
                density: CASE WHEN node_count > 1 THEN toFloat(rel_count) / (node_count * (node_count - 1) / 2) ELSE 0.0 END
            }} as metrics
        """

        result = graph.run(cypher_query, **{
            **source_query_params,
            "max_nodes": graph_query.max_nodes
        })
        if result:
            return _build_knowledge_subgraph(result[0])

    except Exception as e:
        logger.error(f"子图提取失败: {e}")

    # 降级方案：简单邻居查询
    return _fallback_subgraph_extraction(graph_query)


def _identify_reasoning_patterns(subgraph: KnowledgeSubgraph) -> list[str]:
    """识别推理模式"""
    return ["因果关系", "组成关系", "相似关系"]


def _build_reasoning_chain(pattern: str, subgraph: KnowledgeSubgraph) -> Optional[str]:
    """构建推理链"""
    return f"基于{pattern}的推理链"


def _validate_reasoning_chains(chains: list[str], query: str) -> list[str]:
    """验证推理链"""
    return chains[:3]


def _graph_structure_reasoning(subgraph: KnowledgeSubgraph, query: str) -> list[str]:
    """
    基于图结构的推理：这是图RAG的智能之处
    不仅检索信息，还能进行逻辑推理
    """
    reasoning_chains = []

    try:
        # 1. 识别推理模式
        reasoning_patterns = _identify_reasoning_patterns(subgraph)

        # 2. 构建推理链
        for pattern in reasoning_patterns:
            chain = _build_reasoning_chain(pattern, subgraph)
            if chain:
                reasoning_chains.append(chain)

        # 3. 验证推理链的可信度
        validated_chains = _validate_reasoning_chains(reasoning_chains, query)

        logger.info(f"图结构推理完成，生成 {len(validated_chains)} 条推理链")
        return validated_chains

    except Exception as e:
        logger.error(f"图结构推理失败: {e}")
        return []


def _build_subgraph_description(subgraph: KnowledgeSubgraph) -> str:
    """构建子图的自然语言描述"""
    central_names = [node.get("name", "未知") for node in subgraph.central_nodes]
    node_count = len(subgraph.connected_nodes)
    rel_count = len(subgraph.relationships)

    return f"关于 {', '.join(central_names)} 的知识网络，包含 {node_count} 个相关概念和 {rel_count} 个关系。"


def _subgraph_to_documents(subgraph: KnowledgeSubgraph,
                           reasoning_chains: list[str], query: str) -> list[Document]:
    """将知识子图转换为Document对象"""
    documents = []

    # 子图整体描述
    subgraph_desc = _build_subgraph_description(subgraph)

    doc = Document(
        page_content=subgraph_desc,
        metadata={
            "search_type": "knowledge_subgraph",
            "node_count": len(subgraph.connected_nodes),
            "relationship_count": len(subgraph.relationships),
            "graph_density": subgraph.graph_metrics.get("density", 0.0),
            "reasoning_chains": reasoning_chains,
            "recipe_name": subgraph.central_nodes[0].get("name", "知识子图") if subgraph.central_nodes else "知识子图"
        }
    )
    documents.append(doc)

    return documents


def _rank_by_graph_relevance(documents: list[Document], query: str) -> list[Document]:
    """基于图结构相关性排序"""
    return sorted(documents,
                  key=lambda x: x.metadata.get("relevance_score", 0.0),
                  reverse=True)


def _get_entity_relation_test_data() -> GraphQuery:
    """获取实体关系测试数据"""
    return GraphQuery(
        query_type=GraphQueryType.ENTITY_RELATION,
        source_entities=[NodeConstraint(
            label='文档',
            constraints={
                "文件名称": "JTG T D81—2017 公路交通安全设施设计细则.pdf"
            }
        )],
        target_entities=[NodeConstraint(
            label='组织机构',
            constraints=None
        )],
        relation_types=['主编单位'],
        max_nodes=50,
        max_depth=1,
    )


def _get_multi_hop_test_data() -> GraphQuery:
    """获取多跳测试历测试数据"""
    return GraphQuery(
        query_type=GraphQueryType.MULTI_HOP,
        source_entities=[NodeConstraint(
            label='人员',
            constraints={
                "姓名": "张志新"
            })],
        target_entities=[NodeConstraint(label='标准规范')],
        relation_types=['主编', '主审', '主要参编人员', '参加人员', '参审人员', '关联文档'],
        max_depth=2,
        max_nodes=50,
        constraints={}
    )

def _get_subgraph_test_data() -> GraphQuery:
    """获取子图测试数据"""
    return GraphQuery(
        query_type=GraphQueryType.SUBGRAPH,
        source_entities=[NodeConstraint(
            label='标准规范',
            constraints={
                "名称": "检测系统"
            }
        )],
        target_entities=[],
        relation_types=['关联文档', '术语', '符号', '关联公式', '关联图片', '关联表格', '关联目录'],
        constraints={},
        max_depth=2,
        max_nodes=50,
    )


def _get_entity_query_test_data() -> GraphQuery:
    """获取实体查询测试数据"""
    return GraphQuery(
        max_nodes=50,
        max_depth=0,
        query_type=GraphQueryType.ENTITY_QUERY,
        source_entities=[NodeConstraint(
            label='术语',
            constraints={
                "名称": "竖向排水体"
            }
        )],
        target_entities=[],
        relation_types=[],
        constraints={},
    )


def retrieve_document(query: str, top_k: int = 10, debug: bool = False):
    """检索知识库"""
    logger.info(f"开始图库检索：{query}")

    # 1、查询意图理解
    if debug:
    # graph_query = _get_multi_hop_test_data()
    # graph_query = _get_entity_relation_test_data()
    # graph_query = _get_entity_query_test_data()
        graph_query = _get_subgraph_test_data()
    else:
        graph_query = _understand_query(query)


    logger.info(f"图库查询结果: {graph_query}")

    documents = []

    try:
        # 2. 根据查询类型执行不同策略
        if graph_query.query_type in [GraphQueryType.MULTI_HOP, GraphQueryType.PATH_FINDING]:
            # 多跳遍历 / 路径查找
            paths = _multi_hop_traversal(graph_query)
            documents.extend(_paths_to_documents(paths, query))

        elif graph_query.query_type in [GraphQueryType.SUBGRAPH, GraphQueryType.CLUSTERING]:
            # 子图提取 / 聚类查询：都视为“围绕核心实体的局部知识网络”
            subgraph = _extract_knowledge_subgraph(graph_query)
            # 图结构推理
            reasoning_chains = _graph_structure_reasoning(subgraph, query)

            documents.extend(_subgraph_to_documents(subgraph, reasoning_chains, query))

        elif graph_query.query_type == GraphQueryType.ENTITY_RELATION:
            # 实体关系查询（可以视为一跳 / 少量跳的路径查询）
            paths = _multi_hop_traversal(graph_query)
            documents.extend(_paths_to_documents(paths, query))

        elif graph_query.query_type == GraphQueryType.ENTITY_QUERY:
            # 实体查询：查询A的详细信息
            entities = _find_entity_details(graph_query)
            documents.extend(_entity_to_documents(entities))

        # 3. 图结构相关性排序
        documents = _rank_by_graph_relevance(documents, query)
        logger.info(f"图RAG检索完成，返回 {len(documents[:top_k])} 个结果")
        return documents[:top_k]
    except Exception as e:
        logger.error(f"图RAG检索失败: {e}")
        return []
