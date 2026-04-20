import logging
from graph.graph_factory import get_graph
from completeions.graph_query import GraphQueryCompletion
from models.graph_path import GraphPath
from models.graph_query import GraphQuery
from enums.graph_query_type import GraphQueryType
from langchain_core.documents import Document
from typing import Optional
from models.knowledge_subgraph import KnowledgeSubgraph

logger = logging.getLogger(__name__)

def _understand_query(query: str) -> GraphQuery:
    """理解查询字符串"""
    graph = get_graph()
    node_schemas = graph.get_node_schema()
    relation_schemas = graph.get_relation_schema()
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

def _find_entity_relations(graph_query: GraphQuery, session) -> list[GraphPath]:
    """查找实体间关系"""
    return []

def _find_shortest_paths(graph_query: GraphQuery, session) -> list[GraphPath]:
    """查找最短路径"""
    return []

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

    driver = graph.get_driver()

    try:
        with driver.session() as session:
            # 构建多跳遍历查询
            source_entities = graph_query.source_entities
            target_keywords = graph_query.target_entities or []
            max_depth = graph_query.max_depth

            # 根据查询类型选择不同的遍历策略
            if graph_query.query_type == GraphQueryType.MULTI_HOP:
                # 根据是否有目标关键词动态拼接过滤条件
                target_filter_clause = ""
                if target_keywords:
                    target_filter_clause = """
                        AND ANY(kw IN $target_keywords WHERE
                            (target.name IS NOT NULL AND (toString(target.name) CONTAINS kw OR kw CONTAINS toString(target.name))) OR
                            (target.category IS NOT NULL AND (toString(target.category) CONTAINS kw OR kw CONTAINS toString(target.category)))
                        )"""

                cypher_query = f"""
                        // 多跳推理查询
                        UNWIND $source_entities as source_name
                        MATCH (source)
                        WHERE source.name CONTAINS source_name OR source.nodeId = source_name

                        // 执行多跳遍历
                        MATCH path = (source)-[*1..{max_depth}]-(target)
                        WHERE NOT source = target{target_filter_clause}

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
                        LIMIT 20

                        RETURN path, source, target, path_len, rels, path_nodes, relevance
                        """

                params = {
                    "source_entities": source_entities,
                    "relation_types": graph_query.relation_types or []
                }
                if target_keywords:
                    params["target_keywords"] = target_keywords

                result = session.run(cypher_query, params)

                for record in result:
                    path_data = _parse_neo4j_path(record)
                    if path_data:
                        paths.append(path_data)

            elif graph_query.query_type == GraphQueryType.ENTITY_RELATION:
                # 实体间关系查询
                paths.extend(_find_entity_relations(graph_query, session))

            elif graph_query.query_type == GraphQueryType.PATH_FINDING:
                # 最短路径查找
                paths.extend(_find_shortest_paths(graph_query, session))

    except Exception as e:
        logger.error(f"多跳遍历失败: {e}")

    logger.info(f"多跳遍历完成，找到 {len(paths)} 条路径")
    return paths

def _build_path_description(path: GraphPath) -> str:
    """构建路径的自然语言描述"""
    if not path.nodes:
        return "空路径"

    desc_parts = []
    for i, node in enumerate(path.nodes):
        desc_parts.append(node.get("name", f"节点{i}"))
        if i < len(path.relationships):
            rel_type = path.relationships[i].get("type", "相关")
            desc_parts.append(f" --{rel_type}--> ")

    return "".join(desc_parts)

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

    driver = graph.get_driver()

    try:
        with driver.session() as session:
            # 简化的子图提取（不依赖APOC）
            cypher_query = f"""
            // 找到源实体
            UNWIND $source_entities as entity_name
            MATCH (source)
            WHERE source.name CONTAINS entity_name 
               OR source.nodeId = entity_name

            // 获取指定深度的邻居
            MATCH (source)-[r*1..{graph_query.max_depth}]-(neighbor)
            WITH source, collect(DISTINCT neighbor) as neighbors, 
                 collect(DISTINCT r) as relationships
            WHERE size(neighbors) <= $max_nodes

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

            result = session.run(cypher_query, {
                "source_entities": graph_query.source_entities,
                "max_nodes": graph_query.max_nodes
            })

            record = result.single()
            if record:
                return _build_knowledge_subgraph(record)

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

def retrieve_document(query: str, top_k: int = 10):
    """检索知识库"""
    logger.info(f"开始图库检索：{query}")

    #1、查询意图理解
    graph_query = _understand_query(query)
    logger.info(f"图库查询类型: {graph_query.query_type.value}")

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

        # 3. 图结构相关性排序
        documents = _rank_by_graph_relevance(documents, query)
        logger.info(f"图RAG检索完成，返回 {len(documents[:top_k])} 个结果")
        return documents[:top_k]
    except Exception as e:
        logger.error(f"图RAG检索失败: {e}")
        return []
