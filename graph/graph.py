from collections import defaultdict

from py2neo import Graph as Py2NeoGraph
from configs import spec_server_config

# ====== 配置 ======
IGNORE_PROPS = {"_id", "id", "created_at", "updated_at"}
REL_SAMPLE_LIMIT = 50   # 每种关系最多采样数量
GLOBAL_REL_LIMIT = 500  # 全局最大关系采样


class Graph:

    def __init__(self):
        """初始化图"""
        self._graph = Py2NeoGraph(
            spec_server_config.NEO4J_URI,
            name=spec_server_config.NEO4J_DATABASE,
            auth=(spec_server_config.NEO4J_USERNAME, spec_server_config.NEO4J_PASSWORD),
        )
        self._node_schemas = None
        self._relationships = None

    def run(self, cypher_query: str, **kwargs):
        """执行Cypher查询"""
        return self._graph.run(cypher_query, **kwargs).data()

    def get_driver(self):
        """获取Neo4j驱动"""
        return self._graph

    def clear_schema(self):
        """清除schema缓存"""
        self._node_schemas = None
        self._relationships = None

    def get_node_schema(self) -> list[str]:
        """获取节点schema"""
        if self._node_schemas is None:
            self._node_schemas = self._format_nodes(self._get_nodes())
        return self._node_schemas

    def get_relationship_schema(self) -> list[str]:
        """获取关系schema"""
        if self._relationships is None:
            self._relationships = self._format_relationships(self._get_relationships())
        return self._relationships

    def _get_nodes(self):
        """获取所有节点类型"""
        cypher_query = """
        CALL db.schema.nodeTypeProperties()
        YIELD nodeType, propertyName, propertyTypes
        RETURN nodeType, propertyName, propertyTypes
        """
        nodes_raw = self.run(cypher_query=cypher_query)
        nodes = defaultdict(dict)
        for row in nodes_raw:
            label = row["nodeType"].replace(":", "")
            prop = row["propertyName"]
            if prop in IGNORE_PROPS:
                continue
            types = row["propertyTypes"]
            prop_type = types[0] if types else "ANY"
            nodes[label][prop] = prop_type
        return nodes

    def _get_relationships(self):
        """获取所有关系类型"""
        # --- 获取所有关系类型 ---
        cypher_query = """
        CALL db.relationshipTypes() YIELD relationshipType RETURN relationshipType
        """
        rel_types = [r["relationshipType"] for r in self._graph.run(cypher_query)]
        relationships = set()
        # --- 按关系类型逐个采样 ---
        for rel_type in rel_types:
            query = f"""
            MATCH (a)-[r:`{rel_type}`]->(b)
            RETURN DISTINCT labels(a) AS from_labels,
                            labels(b) AS to_labels
            LIMIT {REL_SAMPLE_LIMIT}
            """

            results = self.run(query)

            for row in results:
                from_labels = row["from_labels"]
                to_labels = row["to_labels"]

                if not from_labels or not to_labels:
                    continue

                from_label = from_labels[0]
                to_label = to_labels[0]

                relationships.add((from_label, rel_type, to_label))

        # --- 兜底：补充“无数据关系类型” ---
        # 防止某些关系没有数据被漏掉
        for rel_type in rel_types:
            if not any(r[1] == rel_type for r in relationships):
                relationships.add(("Unknown", rel_type, "Unknown"))

        return relationships

    @staticmethod
    def _format_nodes(nodes_dict):
        lines = []
        for label in sorted(nodes_dict.keys()):
            props = nodes_dict[label]
            if props:
                props_str = ", ".join(
                    f"{k}: {v}" for k, v in sorted(props.items())
                )
            else:
                props_str = ""
            lines.append(f"{label} {{{props_str}}}")
        return lines

    @staticmethod
    def _format_relationships(rels):
        lines = []
        for from_label, rel_type, to_label in sorted(rels):
            lines.append(f"({from_label})-[:{rel_type}]->({to_label})")
        return lines