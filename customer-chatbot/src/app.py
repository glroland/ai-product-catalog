"""Customer Chatbot

Chatbot emulating the customer experience for intereacting with a virtual
retail store.
"""
import logging
import uuid
import streamlit as st
from api_gateway import invoke_chat_api
from utils import list_of_strings_to_markdown
from constants import SessionStateVariables
from constants import StorefrontResponseVariables
from constants import AppUserInterfaceElements
from constants import QuickResponses
from constants import CannedGreetings
from constants import ProductAttributes
from constants import MessageAttributes

logger = logging.getLogger(__name__)

logging.basicConfig(level=logging.DEBUG,
    handlers=[
        # no need from a docker container - logging.FileHandler("customer-chatbot.log"),
        logging.StreamHandler()
    ])

# Initialize Streamlit State
if SessionStateVariables.CLIENT_ID not in st.session_state:
    st.session_state[SessionStateVariables.CLIENT_ID] = str(uuid.uuid4())
if SessionStateVariables.MESSAGES not in st.session_state:
    st.session_state[SessionStateVariables.MESSAGES] = []
if SessionStateVariables.LAST_STATE not in st.session_state:
    st.session_state[SessionStateVariables.LAST_STATE] = ""
if SessionStateVariables.IDENTIFIED_ATTRIBUTES not in st.session_state:
    st.session_state[SessionStateVariables.IDENTIFIED_ATTRIBUTES] = ""
if SessionStateVariables.MATCHING_PRODUCTS not in st.session_state:
    st.session_state[SessionStateVariables.MATCHING_PRODUCTS] = ""

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
    response = invoke_chat_api(prompt, st.session_state[SessionStateVariables.CLIENT_ID])
    logger.info("Response: %s", response)
    st.session_state[SessionStateVariables.LAST_RESPONSE] = response

    # Was the customer qualified?
    if not response[StorefrontResponseVariables.QUALIFIED_CUSTOMER_FLAG]:
        logger.info("Customer not qualified. Resetting state...")

        # Reset the state
        st.session_state[SessionStateVariables.MESSAGES] = []
        st.session_state[SessionStateVariables.LAST_STATE] = ""
        st.session_state[SessionStateVariables.IDENTIFIED_ATTRIBUTES] = ""
        st.session_state[SessionStateVariables.MATCHING_PRODUCTS] = ""

    else:
        # Get AI Product Attributes
        st.session_state[SessionStateVariables.IDENTIFIED_ATTRIBUTES] = \
                    response[StorefrontResponseVariables.IDENTIFIED_ATTRIBUTES]
        logger.info ("AI Product Attributes Type<%s> - %s",
                     type(st.session_state[SessionStateVariables.IDENTIFIED_ATTRIBUTES]),
                     st.session_state[SessionStateVariables.IDENTIFIED_ATTRIBUTES])

        # Get Matching Products
        st.session_state[SessionStateVariables.MATCHING_PRODUCTS] = \
                    response[StorefrontResponseVariables.MATCHING_PRODUCTS]
        logger.info ("Matching Products Type<%s> - %s",
                     type(st.session_state[SessionStateVariables.MATCHING_PRODUCTS]),
                     st.session_state[SessionStateVariables.MATCHING_PRODUCTS])

    # Get AI Response to Latest Inquiry
    ai_response = response[StorefrontResponseVariables.AI_RESPONSE]
    logger.info ("AI Response Message: %s", ai_response)

    # Append AI Response to history
    st.session_state.messages.append({MessageAttributes.ROLE: MessageAttributes.ASSISTANT,
                                    MessageAttributes.CONTENT: ai_response})
    messages.chat_message(MessageAttributes.ASSISTANT).write(ai_response)

# Initialize High Level Page Structure
st.title(AppUserInterfaceElements.TITLE)
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
    # Additional Details - Attributes
    st.subheader(AppUserInterfaceElements.ATTRIBUTES_HEADER, divider=True)
    st.markdown(list_of_strings_to_markdown(
        st.session_state[SessionStateVariables.IDENTIFIED_ATTRIBUTES]
    ))

    # Additional Details - Matched Products
    st.subheader(AppUserInterfaceElements.PRODUCTS_HEADER, divider=True)
    if st.session_state[SessionStateVariables.MATCHING_PRODUCTS] is not None:
        for product in st.session_state[SessionStateVariables.MATCHING_PRODUCTS]:
            cosign_similarity = round(product[ProductAttributes.SIMILARITY] * 100)
            label = product[ProductAttributes.NAME] # + f" ({cosign_similarity}%)"
            with st.popover(label=label, use_container_width=True):
                msrp = product[ProductAttributes.MSRP]
                st.markdown(f"MSRP ${msrp}")
                st.markdown("SKU #" + product[ProductAttributes.SKU])
                st.markdown(f"Similarity - {cosign_similarity}%")

    # Quick Response Buttons
    st.subheader(AppUserInterfaceElements.QUICK_RESPONSES, divider=True)
    st.button(QuickResponses.GENERIC_GREETING_BTN,
              on_click=process_user_message,
              use_container_width=True,
              args=(QuickResponses.GENERIC_GREETING_PROMPT, ))
    st.button(QuickResponses.SPECIFIC_ASK_BTN,
              on_click=process_user_message,
              use_container_width=True,
              args=(QuickResponses.SPECIFIC_ASK_PROMPT, ))
    st.button(QuickResponses.UNRELATED_ASK_BTN,
              on_click=process_user_message,
              use_container_width=True,
              args=(QuickResponses.UNRELATED_ASK_PROMPT, ))
    st.button(QuickResponses.GENERIC_CLARIFICATION_BTN,
              on_click=process_user_message,
              use_container_width=True,
              args=(QuickResponses.GENERIC_CLARIFICATION_PROMPT, ))

# Initialize Chat Box
messages = st.container(height=300)
messages.chat_message(MessageAttributes.ASSISTANT).write(CannedGreetings.INTRO)
for msg in st.session_state.messages:
    messages.chat_message(msg[MessageAttributes.ROLE]).write(msg[MessageAttributes.CONTENT])

# Gather and log user prompt
if user_input := st.chat_input():
    process_user_message(user_input)
