import os
import sys

# Ensure Agents directory is in sys.path for imports to work
sys.path.insert(0, os.path.dirname(__file__))

from graph_builder import build_graph

graph = build_graph()

question = input("Ask your question: ")

result = graph.invoke({
    "question": question
})

print("\nFinal Answer:\n")
print(result["answer"])