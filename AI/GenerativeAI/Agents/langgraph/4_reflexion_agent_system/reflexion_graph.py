from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, ToolMessage
from chains import first_responder_chain, revisor_chain
from execute_tools import execute_tool_search_queries

MAX_ITERATIONS = 2


def chain_wrapper(chain_fn):
    def wrapped(state):
        messages = state.get("messages", [])
        # Chain result is usually a message object (sometimes list or dict)
        result = chain_fn.invoke({"messages": messages})
        if isinstance(result, list):
            return {"messages": messages + result}
        elif isinstance(result, dict) and "messages" in result:
            return {"messages": messages + result["messages"]}
        elif hasattr(result, "content"):
            return {"messages": messages + [result]}
        else:
            return {"messages": messages}
    return wrapped


# Create the graph
graph = StateGraph(dict)
graph.add_node("draft", chain_wrapper(first_responder_chain))
graph.add_node("execute_tools", execute_tool_search_queries)
graph.add_node("revisor", chain_wrapper(revisor_chain))

# Connect nodes
graph.add_edge("draft", "execute_tools")
graph.add_edge("execute_tools", "revisor")


def tool_iteration_limiter(state):
    messages = state.get("messages", [])
    count_tool_visits = sum(isinstance(msg, ToolMessage) for msg in messages)
    print("--- Iteration limiter debug ---")
    print(f"messages: {messages}")
    print(f"ToolMessages count: {count_tool_visits}")
    if count_tool_visits > MAX_ITERATIONS:
        print("Returning END")
        return END
    print("Returning execute_tools")
    return "execute_tools"


graph.add_conditional_edges("revisor", tool_iteration_limiter)
graph.set_entry_point("draft")

app = graph.compile()
print(app.get_graph().draw_mermaid())

# Example usage
if __name__ == "__main__":
    initial_state = {
        "messages": [HumanMessage(content="Write about how small business can leverage AI to grow")]
    }
    response = app.invoke(initial_state)
    final_messages = response.get("messages", [])
    tool_messages = [msg for msg in final_messages if isinstance(msg, ToolMessage)]
    if tool_messages:
        import json
        results_dict = json.loads(tool_messages[-1].content)
        print(results_dict)
    print(response, "response")
