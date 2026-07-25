from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel


load_dotenv()


class ResponseModel(BaseModel):
    topic: str
    summary: str
    sources: list[str]
    tools_used: list[str]


claude_llm = ChatAnthropic(model="claude-haiku-4-5")

parser = PydanticOutputParser(pydantic_object=ResponseModel)

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
            You are an Instagram content creator.
            Create a short 30-second script with hooks.

            Respond in this format and include no other text:
            {format_instructions}
            """,
        ),
        ("placeholder", "{chat_history}"),
        ("human", "{query}"),
        ("placeholder", "{agent_scratchpad}"),
    ]
).partial(format_instructions=parser.get_format_instructions())

agent = create_tool_calling_agent(
    llm=claude_llm,
    prompt=prompt,
    tools=[],
)

agent_executor = AgentExecutor(
    agent=agent,
    tools=[],
    verbose=True,
)

raw_response = agent_executor.invoke({"query": "Explain React"})

# ChatAnthropic returns the final answer as a list of content blocks.
output_text = raw_response["output"][0]["text"]
nice_response = parser.parse(output_text)

print(nice_response)
