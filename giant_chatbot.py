import streamlit as st
import os
from dotenv import load_dotenv
from jamaibase import JamAI, protocol as p

load_dotenv()
project_id = os.getenv('PROJECT_ID')
api_key = os.getenv('API_KEY')

# Header
st.header("Giant Shopping Assistant")

# feed input into LLM, stream the output
def ask_question(user_input):
    jamai = JamAI(api_key=api_key, project_id=project_id)
    completion = jamai.add_table_rows(
        "chat",
        p.RowAddRequest(
            table_id="test1",
            data=[dict(User=user_input)],
            stream=True,
        ),
    )
    full_response = ""
    for chunk in completion:
        if chunk.output_column_name != "AI":
            continue
        if isinstance(chunk, p.GenTableStreamReferences):
            pass
        else:
            full_response += chunk.text
            yield full_response

# Initialize chat history if not present
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


if len(st.session_state.chat_history) == 0:  # If the conversation hasn't started yet
    initial_message = """
    👋 Hi there! Welcome to Giant Online.
    I’m your shopping assistant — here to help you quickly find and order your groceries.

    You can type or say things like:
    - “I need eggs and chocolate ice cream”      
    - “Show me this week’s deals”      
    - “Order the same as last time”

    How can I assist you today?
    """
    st.session_state.chat_history.append({"role": "assistant", "content": initial_message})
    
# Display chat history
chat_container = st.container()
with chat_container:
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# Get user input
user_query = st.chat_input("Ask me something!")

# Process user input and generate response
if user_query:
    # Append user message to chat history
    st.session_state.chat_history.append({"role": "user", "content": user_query})

    # Re-render chat to show user input at the bottom
    with chat_container:
        with st.chat_message("user"):
            st.markdown(user_query)

    with chat_container:
        with st.chat_message("assistant"):
            message_placeholder = st.empty()  # Placeholder for assistant's message
            full_response = ""
            # Simulate a typing effect
            for response in ask_question(user_query):  # Get the assistant's response
                message_placeholder.markdown(response + "▌")  # Display the typing effect (cursor)
                full_response = response
            # Finalize response without the cursor
            message_placeholder.markdown(full_response)

        # Append the assistant's final response to the chat history
        st.session_state.chat_history.append({"role": "assistant", "content": full_response})
        
        
    