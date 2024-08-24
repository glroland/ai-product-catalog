"""customer-chatbot

Chatbot emulating the customer experience for intereacting with a virtual
retail store.
"""
import streamlit as st
from api_utils import invoke_chat_api
from state_utils import get_most_recent_ai_response, is_qualified_customer

if "messages" not in st.session_state:
    st.session_state["messages"] = []
if "last_state" not in st.session_state:
    st.session_state["last_state"] = ""

st.title("💬 Let's GOOOOO!!!! Shoe Store")

st.markdown("""
    <style>
        .reportview-container {
            margin-top: -2em;
        }
        #MainMenu {visibility: hidden;}
        .stDeployButton {display:none;}
        footer {visibility: hidden;}
        #stDecoration {display:none;}
    </style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.subheader("Identified Attributes", divider=True)
    st.markdown(
        """
        - Item 1
        - Item 2
        - Item 3
        """
        )
    st.subheader("Product Recommendations", divider=True)
    st.markdown(
        """
        - Item 1
        - Item 2
        - Item 3
        """
        )

messages = st.container(height=300)

messages.chat_message("assistant").write("Thank you for visiting our store.  How may we help you?")

for msg in st.session_state.messages:
    messages.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input():
    # Gather and log user prompt
    print ("User Input: " + prompt)
    messages.chat_message("user").write(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    print ("st.session_state.messages", st.session_state.messages)

    # Invoke Backend API
    state = invoke_chat_api(prompt, st.session_state["last_state"])
    print("State:", state)
    st.session_state["last_state"] = state

    # Was the customer qualified?
    if not is_qualified_customer(state):
        messages.chat_message("assistant").write(
            "I'm sorry, but this is a shoe store.  Please leave the " + \
                      "premises before I call the police."
        )
    else:
        # Get AI Response to Latest Inquiry
        ai_response = get_most_recent_ai_response(state)
        print ("AI Response Message: " + ai_response)

        # Append AI Response to history
        st.session_state.messages.append({"role": "assistant",
                                        "content": ai_response})
        messages.chat_message("assistant").write(ai_response)
