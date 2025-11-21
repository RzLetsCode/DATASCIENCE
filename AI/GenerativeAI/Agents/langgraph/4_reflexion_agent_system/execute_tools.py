import json
from typing import List, Dict, Any
from langchain_core.messages import AIMessage, ToolMessage

# Example: import your search tool here
from langchain_community.tools import TavilySearchResults

tavily_search_tool = TavilySearchResults(max_results=5)

def execute_tool_search_queries(state: Dict[str, Any]) -> Dict[str, Any]:
    messages = state.get("messages", [])
    # Defensive: ensure messages is a list and not empty
    if not isinstance(messages, list) or not messages:
        return {"messages": messages}

    last_ai_message = messages[-1]
    if not hasattr(last_ai_message, "tool_calls") or not getattr(last_ai_message, "tool_calls", []):
        return {"messages": messages}

    tool_messages = []
    for tool_call in last_ai_message.tool_calls:
        if tool_call.get("name") in ["AnswerQuestion", "ReviseAnswer"]:
            call_id = tool_call.get("id", "")
            search_queries = tool_call.get("args", {}).get("search_queries", [])
            result_map: Dict[str, Any] = {}
            for query in search_queries:
                try:
                    result_map[query] = tavily_search_tool.invoke(query)
                except Exception as e:
                    result_map[query] = {"error": str(e)}
            tool_messages.append(
                ToolMessage(
                    content=json.dumps(result_map),
                    tool_call_id=call_id
                )
            )
    # *** Always append to existing messages, never replace ***
    return {"messages": messages + tool_messages}



# # --------- Example Usage ---------
# if __name__ == "__main__":
#     # Example test state mimicking a conversation with tool calls.
#     test_state = [
#         HumanMessage(content="Write about how small business can leverage AI to grow"),
#         AIMessage(
#             content="",
#             tool_calls=[
#                 {
#                     "name": "AnswerQuestion",
#                     "args": {
#                         'answer': '',
#                         'search_queries': [
#                             'AI tools for small business',
#                             'AI in small business marketing',
#                             'AI automation for small business'
#                         ],
#                         'reflection': {
#                             'missing': '',
#                             'superfluous': ''
#                         }
#                     },
#                     "id": "call_KpYHichFFEmLitHFvFhKy1Ra",
#                 }
#             ],
#         )
#     ]

#     # Run tool execution and display results.
#     results = execute_tool_search_queries(test_state)
#     print("Raw results:", results)
#     if results:
#         parsed_content = json.loads(results[0].content)
#         print("Parsed content:", parsed_content)
