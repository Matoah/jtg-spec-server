from graph.graph_factory import get_graph

class SymbolService:

    @classmethod
    def query(cls, args):
        """查询符号"""
        symbol_str = args.get("symbols", "")
        symbols = symbol_str.split(",")
        symbols = [symbol.strip() for symbol in symbols if symbol.strip()]
        if not symbols:
            return {"success": False, "message": "没有提供查询的符号！"}
        cypher_script = """
                MATCH (d:文档)-[:符号]->(s:符号)
                WHERE s.符号 IN $symbol_names
                OR s.名称 IN $symbol_names
                return s.符号 as 符号, s.名称 as 名称, d.文件名称 as 来源文档
                """
        graph = get_graph()
        result = graph.run(cypher_script, symbol_names=symbols)
        if not result:
            return {"success": False, "message": "没有查询到符号！"}
        else:
            script = []
            for item in result:
                script.append(f"符号: {item.get('符号')}")
                script.append(f"定义: {item.get('名称')}")
                script.append(f"来源文档: {item.get('来源文档')}")
            return {"success": True, "data": "\n".join(script)}

