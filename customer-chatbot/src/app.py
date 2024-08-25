"""customer-chatbot

Chatbot emulating the customer experience for intereacting with a virtual
retail store.
"""
import logging
import streamlit as st
from api_utils import invoke_chat_api
from state_utils import get_most_recent_ai_response
from state_utils import get_most_recent_ai_attributes
from state_utils import is_qualified_customer
from state_utils import comma_seperated_to_markdown
from state_utils import get_matching_products

logging.basicConfig(level=logging.DEBUG,
    handlers=[
        logging.FileHandler("customer-chatbot.log"),
        logging.StreamHandler()
    ])

# Initialize Streamlit State
if "messages" not in st.session_state:
    st.session_state["messages"] = []
if "last_state" not in st.session_state:
    st.session_state["last_state"] = ""
if "identified_attributes" not in st.session_state:
    st.session_state["identified_attributes"] = ""
if "recommended_products" not in st.session_state:
    st.session_state["recommended_products"] = ""

# Process a text response
def process_user_message(prompt):
    """ Submit User Message
    
    prompt - user message
    """
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
            "I'm sorry but this is a shoe store.  We are unable to help you with that question." +
            "However, we would love to sell you a new pair of shoes!"
        )

        # Reset the state
        st.session_state["messages"] = []
        st.session_state["last_state"] = ""
        st.session_state["identified_attributes"] = ""
        st.session_state["recommended_products"] = ""

    else:
        # Get AI Response to Latest Inquiry
        ai_response = get_most_recent_ai_response(state)
        print ("AI Response Message: " + ai_response)

        # Get AI Product Attributes
        st.session_state["identified_attributes"] = get_most_recent_ai_attributes(state)
        if st.session_state["identified_attributes"] is not None:
            print ("AI Product Attributes: ", st.session_state["identified_attributes"])

        # Get Matching Products
        st.session_state["recommended_products"] = get_matching_products(state)
        if st.session_state["recommended_products"] is not None:
            print ("Matching Products: " + st.session_state["recommended_products"])

        # Append AI Response to history
        st.session_state.messages.append({"role": "assistant",
                                        "content": ai_response})
        messages.chat_message("assistant").write(ai_response)

# Initialize High Level Page Structure
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

# Build Side Bar
with st.sidebar:
    # Additional Details
    st.subheader("Identified Attributes", divider=True)
    st.markdown(comma_seperated_to_markdown(st.session_state["identified_attributes"]))
    st.subheader("Product Recommendations", divider=True)
    st.markdown(comma_seperated_to_markdown(st.session_state["recommended_products"]))

    # Quick Response Buttons
    st.subheader("Quick Responses", divider=True)
    st.button("Generic Greeting", on_click=process_user_message, use_container_width=True,
              args=("Hello, I am looking for a new pair of shoes.", ))
    st.button("Specific Ask", on_click=process_user_message, use_container_width=True,
              args=("I am looking for a new pair of high tops for playing pickup " +
                    "games of Basketball with my friends.  If you have multiple " +
                    "options, I would like a retro look and love the color white. " +
                    "Also, I am a huge Michael Jordan fan!", ))
    st.button("Unrelated Question", on_click=process_user_message, use_container_width=True,
              args=("What's the weather like today?", ))
    st.button("Generic Clarification", on_click=process_user_message, use_container_width=True,
              args=("I like baseball and the color red.", ))

# Initialize Chat Box
messages = st.container(height=300)
messages.chat_message("assistant").write("Thank you for visiting our store.  How may we help you?")
for msg in st.session_state.messages:
    messages.chat_message(msg["role"]).write(msg["content"])

# Gather and log user prompt
if user_input := st.chat_input():
    process_user_message(user_input)
