from graph.graph import Graph

SINGLETON_INSTANCE: Graph | None = None

def get_graph():
    """获取单例实例"""
    global SINGLETON_INSTANCE
    if SINGLETON_INSTANCE is None:
        SINGLETON_INSTANCE = Graph()
    return SINGLETON_INSTANCE