"""
Quick integration check for LangChain + Ollama
Ensures that LangChain can talk to the configured local Ollama model.
"""
import os
from langchain_core.prompts import PromptTemplate
from langchain_ollama import ChatOllama

model_name = os.getenv("OLLAMA_MODEL", "phi")

print(f"🔍 Checking LangChain ↔ Ollama integration (model={model_name})")

try:
    llm = ChatOllama(model=model_name)
    prompt = PromptTemplate.from_template("Answer briefly: {q}")
    chain = prompt | llm
    response = chain.invoke({"q": "What is LangGraph?"})
    print("✅ SUCCESS:", response.content[:200])
except Exception as e:
    print("❌ LangChain ↔ Ollama integration failed:", e)