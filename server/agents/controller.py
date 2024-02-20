from langchain import hub
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
load_dotenv()

new_prompt = """You are a helpful assistant.
Respond in the language of the user.
Your output will be transcribed to speech and played to the user. So, when responding:
1. Use plain, conversational language.
2. Avoid markdown, special characters, or symbols.
3. Expand abbreviations and acronyms into their full spoken form. For example, use 'miles per hour' instead of 'mph'.
4. If technical terms or jargon are unavoidable, provide a brief spoken explanation.
5. Articulate numbers as they would be spoken. For example, use 'two point two' instead of '2.2'.
6. Avoid complex punctuation. Use simple sentence structures conducive to spoken language.

Remember, your goal is to provide responses that are clear, concise, and easily understood when spoken aloud.
"""

class Controller:
    def __init__(self):
        """tools should be list of functions"""
        tools = [
            
        ]

        prompt = hub.pull("hwchase17/openai-tools-agent")
        prompt.messages[0].prompt.template = new_prompt
        model = ChatOpenAI(model="gpt-4-turbo-preview", temperature=0, streaming=True)
        agent = create_openai_tools_agent(
            model.with_config({"tags": ["agent_llm"]}), tools, prompt
        )
        self.executor = AgentExecutor(agent=agent, tools=tools).with_config(
            {"run_name": "Assistant"}
        )
        self.history = []

    def text_to_speech(self, status):
        """Not implemented yet, will convert text to speech and play it to the user"""
        pass

    async def invoke(self, message):
        output = ""
        full_message = "History: \n\n"
        for index, i in enumerate(self.history):
            if index % 2 == 0:
                full_message += f"User: {i}\n"
            else:
                full_message += f"Assistant: {i}\n"
        full_message += f"User: {message}\n"
        async for event in self.executor.astream_events(
            {"input": full_message, "history": self.history},
            version="v1",
        ):
            kind = event["event"]
            if kind == "on_chat_model_stream":
                content = event["data"]["chunk"].content
                if content:
                    yield content
            elif kind == "on_chain_end":
                if event["name"] == "Terry":
                    output = event["data"].get("output")["output"]
        print(f"Controller: invoke: message: {message}, output: {output}")
        self.history.append([message, output])
        
        