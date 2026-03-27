import os
import sys

# Ensure Agents directory is in sys.path for imports to work
sys.path.insert(0, os.path.dirname(__file__))

from graph_builder import build_graph

graph = build_graph()

print("LangGraph Assistant Started")
print("----------------------------")

while True:

    question = input("\nAsk Question (or type exit): ")

    if question.lower() == "exit":
        break

    result = graph.invoke({"question": question})

    print("\nAnswer:")
    print(result["answer"])