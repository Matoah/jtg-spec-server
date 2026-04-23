from graph.graph_factory import get_graph

class TermService:

    @classmethod
    def query(cls, args):
        term_str = args.get("terms","")
        terms = term_str.split(",")
        terms = [term.strip() for term in terms if term.strip()]
        if not terms:
            return {"success": False,"message": "没有提供查询的术语！"}
        cypher_script = """
        MATCH (d:文档)-[:术语]->(s:术语)
        WHERE s.名称 IN $term_names
        OR s.英文名称 IN $term_names
        return s.名称 as 名称, s.英文名称 as 英文名称, s.定义 as 定义, d.文件名称 as 来源文档
        """
        graph = get_graph()
        result = graph.run(cypher_script, term_names=terms)
        if not result:
            return {"success": False,"message": "没有查询到术语！"}
        else:
            script = []
            for item in result:
                script.append(f"名称: {item.get('名称')}")
                script.append(f"英文名称: {item.get('英文名称')}")
                script.append(f"定义: {item.get('定义')}")
                script.append(f"来源文档: {item.get('来源文档')}")
            return {"success": True, "data": "\n".join(script)}
