"""Customer Chatbot

Chatbot emulating the customer experience for intereacting with a virtual
retail store.
"""
import logging
import uuid
import streamlit as st
from api_gateway import invoke_chat_api
from utils import comma_seperated_to_markdown

logger = logging.getLogger(__name__)

logging.basicConfig(level=logging.DEBUG,
    handlers=[
        # no need from a docker container - logging.FileHandler("customer-chatbot.log"),
        logging.StreamHandler()
    ])

# Initialize Streamlit State
if "client_id" not in st.session_state:
    st.session_state["client_id"] = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state["messages"] = []
if "last_state" not in st.session_state:
    st.session_state["last_state"] = ""
if "identified_attributes" not in st.session_state:
    st.session_state["identified_attributes"] = ""
if "matching_products" not in st.session_state:
    st.session_state["matching_products"] = ""

# Process a text response
def process_user_message(prompt):
    """ Submit User Message
    
    prompt - user message
    """
    logger.info ("User Input: %s", prompt)
    messages.chat_message("user").write(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    logger.info ("st.session_state.messages - %s", st.session_state.messages)

    # Invoke Backend API
    response = invoke_chat_api(prompt, st.session_state["client_id"])
    logger.info("Response: %s", response)
    st.session_state["last_response"] = response

    # Was the customer qualified?
    if not response["qualified_customer_flag"]:
        logger.info("Customer not qualified. Resetting state...")

        # Reset the state
        st.session_state["messages"] = []
        st.session_state["last_state"] = ""
        st.session_state["identified_attributes"] = ""
        st.session_state["matching_products"] = ""

    else:
        # Get AI Product Attributes
        st.session_state["identified_attributes"] = response["identified_attributes"]
        logger.info ("AI Product Attributes Type<%s> - %",
                     type(st.session_state["identified_attributes"]),
                     st.session_state["identified_attributes"])

        # Get Matching Products
        st.session_state["matching_products"] = response["matching_products"]
        logger.info ("Matching Products Type<%s> - %s",
                     type(st.session_state["matching_products"]),
                     st.session_state["matching_products"])

    # Get AI Response to Latest Inquiry
    ai_response = response["ai_response"]
    logger.info ("AI Response Message: %s", ai_response)

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
    st.markdown(comma_seperated_to_markdown(st.session_state["matching_products"]))

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
