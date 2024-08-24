"""customer-chatbot

Chatbot emulating the customer experience for intereacting with a virtual
retail store.
"""
import streamlit as st
from api_utils import invoke_chat_api
from state_utils import get_most_recent_ai_response
from state_utils import get_most_recent_ai_attributes
from state_utils import is_qualified_customer
from state_utils import comma_seperated_to_markdown
from state_utils import get_matching_products

# Initialize Streamlit State
if "messages" not in st.session_state:
    st.session_state["messages"] = []
if "last_state" not in st.session_state:
    st.session_state["last_state"] = ""
if "identified_attributes" not in st.session_state:
    st.session_state["identified_attributes"] = ""
if "recommended_products" not in st.session_state:
    st.session_state["recommended_products"] = ""

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

# Initialize Chat Box
messages = st.container(height=300)
messages.chat_message("assistant").write("Thank you for visiting our store.  How may we help you?")
for msg in st.session_state.messages:
    messages.chat_message(msg["role"]).write(msg["content"])

# Gather and log user prompt
if prompt := st.chat_input():
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

        # Reset the state
        st.session_state["messages"] = []
        st.session_state["last_state"] = ""

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
