from langchain_core.runnables import RunnableConfig
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from workflow.state.workflow_state import WorkflowState
from workflow.operations.welcome import welcome
from workflow.operations.gateway import gateway
from workflow.operations.query_analysis import query_analysis
from workflow.operations.hybrid_traditional_search import hybrid_traditional_search
from workflow.operations.graph_rag_search import graph_rag_search
from workflow.operations.combined_search import combined_search
from workflow.operations.completion_generator import completion_generator
from pathlib import Path

builder = StateGraph(state_schema=WorkflowState)
builder.add_node(welcome)
builder.add_node(gateway)
builder.add_node(hybrid_traditional_search)
builder.add_node(query_analysis)
builder.add_node(graph_rag_search)
builder.add_node(combined_search)
builder.add_node(completion_generator)


builder.add_edge(START, "welcome")
builder.add_edge("welcome", "gateway")

builder.add_conditional_edges("gateway", lambda x: x.audit_status.value, {
    "pass": "query_analysis",
    "reject": END,
})

builder.add_conditional_edges("query_analysis", lambda x: x.search_strategy.value, {
    "hybrid_traditional": "hybrid_traditional_search",
    "graph_rag": "graph_rag_search",
    "combined": "combined_search",
})

builder.add_edge("hybrid_traditional_search", "completion_generator")
builder.add_edge("graph_rag_search", "completion_generator")
builder.add_edge("combined_search", "completion_generator")
builder.add_edge("completion_generator", END)

checkpointer = InMemorySaver()
app = builder.compile(checkpointer=checkpointer)

graph_image_path = Path(__file__).parent / "graph.png"
graph_image_path.write_bytes(app.get_graph().draw_mermaid_png())

import random
import string


def _random_md5():
    """
    生成随机的MD5字符串
    """
    return ''.join(random.choices(string.hexdigits.lower(), k=32))


def invoke_workflow(query: str):
    """
    执行工作流
    :param query:
    :return:
    """
    config: RunnableConfig = {
        "configurable": {"thread_id": _random_md5()}
    }
    state = WorkflowState(query=query)
    result = app.invoke(state, config=config)
    return result.get("content", "")


async def invoke_workflow_async(query: str):
    """
    异步执行工作流
    :param query:
    :return:
    """
    config: RunnableConfig = {
        "configurable": {"thread_id": _random_md5()}
    }
    state = WorkflowState(query=query, streaming=True)
    for event in app.stream(state, config=config, stream_mode="updates", version="v2"):
        if event["type"] == "updates":
            for node_name, state in event["data"].items():
                yield state.get("content", "")
