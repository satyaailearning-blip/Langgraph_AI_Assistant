import streamlit as st
from graph_builder import build_graph

st.set_page_config(
    page_title="LangGraph AI Assistant",
    page_icon="🤖",
    layout="wide"
)

st.title("LangGraph AI Assistant")
st.write("Ask questions from your uploaded project documents.")

# Build graph once
if "graph" not in st.session_state:
    st.session_state.graph = build_graph()

# Chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input
user_question = st.chat_input("Type your question here...")

if user_question:
    # Show user message
    st.session_state.messages.append({"role": "user", "content": user_question})
    with st.chat_message("user"):
        st.markdown(user_question)

    # Run LangGraph
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            result = st.session_state.graph.invoke({
                "question": user_question
            })

            answer = result["answer"]
            st.markdown(answer)

    # Save assistant response
    st.session_state.messages.append({"role": "assistant", "content": answer})