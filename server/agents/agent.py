from langchain import hub
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_openai import ChatOpenAI


class Agent:
    def __init__(self, tools):
        """tools should be list of functions"""
        prompt = hub.pull("hwchase17/openai-tools-agent")
        llm = ChatOpenAI(model="gpt-4-turbo-preview", temperature=0)
        agent = create_openai_tools_agent(llm, tools, prompt)
        self.executor = AgentExecutor(agent=agent, tools=tools)

    def invoke(self, message):
        response = self.executor.invoke(
            {
                "input": message,
            }
        )

        return response["output"]
