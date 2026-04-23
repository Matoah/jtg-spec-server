from dataclasses import dataclass

from langchain_openai import OpenAI
from langgraph.graph import StateGraph, START


@dataclass
class MyState:
    topic: str
    joke: str = ""


model = OpenAI(
            openAIApiKey="sk-87d83a248503468ab8204d749d97e2b2",
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
            model="qwen3.5-plus",
            max_tokens=4096,
            temperature=0.1,
            streaming=True,
            extra_body={
                "chat_template_kwargs": {
                    "enable_thinking": True
                }
            }
        )

def call_model(state: MyState):
    """Call the LLM to generate a joke about a topic"""
    # Note that message events are emitted even when the LLM is run using .invoke rather than .stream
    model_response = model.stream(
        [
            {"role": "user", "content": f"讲一个关于{state.topic}的笑话"}
        ]
    )
    for chunk in model_response:
        print(chunk.content, end="", flush=True)
    return {"joke": model_response.content}

graph = (
    StateGraph(MyState)
    .add_node(call_model)
    .add_edge(START, "call_model")
    .compile()
)

# The "messages" stream mode streams LLM tokens with metadata
# Use version="v2" for a unified StreamPart format
# for chunk in graph.stream(
#     {"topic": "ice cream"},
#     stream_mode="messages",
#     version="v2",
# ):
#     if chunk["type"] == "messages":
#         message_chunk, metadata = chunk["data"]
#         if message_chunk.content:
#             print(message_chunk.content, end="|", flush=True)

model_response = model.stream(
        [
            {"role": "user", "content": f"讲一个关于冰淇淋的笑话"}
        ]
    )
for chunk in model_response:
    print(chunk.text, end="", flush=True)