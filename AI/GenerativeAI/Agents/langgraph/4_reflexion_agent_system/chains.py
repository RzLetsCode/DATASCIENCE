import datetime
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers.openai_tools import PydanticToolsParser, JsonOutputToolsParser
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
# Import your schema tools
from schema import AnswerQuestion, ReviseAnswer
load_dotenv()
# --- Setup Parsers ---
answer_parser = PydanticToolsParser(tools=[AnswerQuestion])
json_parser = JsonOutputToolsParser(return_id=True)

# --- Prompt Templates ---
BASE_SYSTEM_PROMPT = """You are expert AI researcher.
Current time: {time}

1. {first_instruction}
2. Reflect and critique your answer. Be severe to maximize improvement.
3. After the reflection, **list 1-3 search queries separately** for researching improvements. Do not include them inside the reflection.
"""

REVISE_INSTRUCTIONS = """Revise your previous answer using the new information.
    - Use the previous critique to add important information.
    - MUST include numerical citations to ensure verifiability.
    - Add a "References" section (not counted towards word limit) in this form:
        - [1] [https://example.com](https://example.com)
        - [2] [https://example.com](https://example.com)
    - Remove superfluous information and keep the answer <=250 words.
"""

# --- Create Chat Prompt Templates ---
def get_actor_prompt_template(first_instruction: str):
    """Creates an actor prompt template with a given instruction."""
    return ChatPromptTemplate.from_messages([
        ("system", BASE_SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="messages"),
        ("system", "Answer the user's question above using the required format."),
    ]).partial(
        time=lambda: datetime.datetime.now().isoformat(),
        first_instruction=first_instruction
    )

first_responder_prompt_template = get_actor_prompt_template("Provide a detailed ~250 word answer")
revisor_prompt_template = get_actor_prompt_template(REVISE_INSTRUCTIONS)

# --- Initialize Model ---
llm = ChatOpenAI(model="gpt-4o-mini")

# --- Composable Chains ---
first_responder_chain = first_responder_prompt_template | llm.bind_tools(
    tools=[AnswerQuestion], tool_choice='AnswerQuestion'
)
revisor_chain = revisor_prompt_template | llm.bind_tools(
    tools=[ReviseAnswer], tool_choice="ReviseAnswer"
)

#--- Example Usage ---
response = first_responder_chain.invoke({
    "messages": [HumanMessage("AI Agents taking over content creation")]
})
print(response)
