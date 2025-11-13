from typing import List
from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph import StateGraph, END
from chains import generation_chain, reflection_chain

# Load environment variables (OPENAI_API_KEY etc.)
load_dotenv()

# Define the state schema for the graph
class ChatState(BaseModel):
    messages: List[BaseMessage]


REFLECT = "reflect"
GENERATE = "generate"

# Initialize the StateGraph with the state schema
graph = StateGraph(ChatState)

# Node function for generation
# Accepts current state, returns partial state update

def generate_node(state: ChatState):
    output = generation_chain.invoke({"messages": state.messages})
    # Append new AI message to messages
    return {"messages": state.messages + [output]}


# Node function for reflection

def reflect_node(state: ChatState):
    response = reflection_chain.invoke({"messages": state.messages})
    # Append new HumanMessage with reflection content
    return {"messages": state.messages + [HumanMessage(content=response.content)]}


# Add nodes to graph
graph.add_node(GENERATE, generate_node)
graph.add_node(REFLECT, reflect_node)
graph.set_entry_point(GENERATE)

# Conditional edge to decide whether to continue reflecting/generating

def should_continue(state: ChatState):
    if len(state.messages) > 6:
        return END
    return REFLECT


graph.add_conditional_edges(GENERATE, should_continue)
graph.add_edge(REFLECT, GENERATE)

# Compile app
app = graph.compile()

# Visualize the graph
print(app.get_graph().draw_mermaid())
app.get_graph().print_ascii()

# Create initial state with starting human message
init_state = ChatState(messages=[HumanMessage(content="AI Agents taking over content creation")])

# Invoke the graph with initial state
response = app.invoke(init_state)

# Print the final response object
print(response)
