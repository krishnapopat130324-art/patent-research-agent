from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage

# Connect to your local Ollama model
llm = ChatOllama(model="llama3.2:1b")

# Test the connection
message = HumanMessage(content="What is a patent? Explain in one short sentence.")
response = llm.invoke([message])

print(f"[Response] --> {response.content}")