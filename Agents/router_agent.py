from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)


def route_question(question: str) -> str:
    q = question.lower()

    rag_keywords = [
        "tag", "datasheet", "sow", "specification", "site survey",
        "observation", "observations", "dcs", "esd", "fgs", "whp",
        "cpp", "platform", "wellhead", "instrument", "icss",
        "modbus", "cabinet", "panel", "project", "uad", "ltdp",
        "scope of work", "adequacy", "survey", "pipeline class",
        "pipe class", "control system", "siemens", "yokogawa"
    ]

    if any(keyword in q for keyword in rag_keywords):
        return "rag"

    prompt = f"""
You are a routing agent.

Classify the user's question into one of these two categories only:

- rag = if the question is about uploaded project documents, engineering documents, site surveys, observations, platform systems, control systems, datasheets, specifications, tags, or any project-specific information
- general = if the question is a general knowledge question not dependent on uploaded documents

Return only one word:
rag
or
general

Examples:
Question: What is the pipe class of Tag No. 265BDV230100?
Answer: rag

Question: What are the site survey observations of DCS system of WHP-01?
Answer: rag

Question: What is LangGraph?
Answer: general

Question: Explain Python list comprehension.
Answer: general

Question: What is the scope of UAD LTDP-2?
Answer: rag

Question: {question}
Answer:
"""

    response = llm.invoke(prompt)
    decision = response.content.strip().lower()

    if "rag" in decision:
        return "rag"

    return "general"