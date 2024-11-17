""" Chat API Handler

Handles the API for Storefront Chat interface
"""
import json
import logging
from json.decoder import JSONDecodeError
from pydantic import BaseModel
from supervisor import inquiry_by_customer

logger = logging.getLogger(__name__)

UNRELATED_RESPONSE = "I'm sorry but this is a shoe store.  " + \
                     "We are unable to help you with that question." + \
                     "However, we would love to sell you a new pair of shoes!"

IM_SPEECHLESS_RESPONSE = "Whoah!  You stumped the AI!  Not sure how you got here!"

class ChatRequest(BaseModel):
    """ Chat Request Input Structure """
    user_message: str
    client_id: str

def chat_api_handler(chat_request: ChatRequest):
    """Virtual Store entry point for textual interaction with the customer.

    Keyword arguments:
    chat_request - chat request object
    """
    user_message = chat_request.user_message
    client_id = chat_request.client_id
    logging.info("chat() User_Message: %s   Client_ID: %s", user_message, client_id)

    # Invoke LangGraph Agent
    state = inquiry_by_customer(user_message, client_id)
    logger.info("Resulting State After Invoke: %s", state)

    # Create qualification flag
    qualified_customer_flag = bool("YES" == state["qualified_customer"])

    # Prepare attributes response
    product_attributes = ""
    if "product_attributes" in state:
        product_attributes = state["product_attributes"]

    # Prepare default AI Response - allows ai to override logic by design
    if state["most_recent_ai_response"] is None:
        if qualified_customer_flag is True:
            ai_response = IM_SPEECHLESS_RESPONSE
        else:
            ai_response = UNRELATED_RESPONSE
            product_attributes = ""
    else:
        json_str_response = state["most_recent_ai_response"].content
        product_attributes = None
        try:
            json_response = json.loads(json_str_response)
            ai_response = json_response["Response"]
            if "Attributes" in json_response:
                product_attributes = json_response["Attributes"]
        except JSONDecodeError as e:
            logger.error("Unable to parse JSON response!  JsonStr=%s  Exception=%s",
                         json_str_response, e)
            ai_response = json_str_response

    # Process matching products data
    matching_products = ""
    if "matching_products" in state and state["matching_products"] is not None:
        matching_products = state["matching_products"]
    else:
        logging.info("No matching products.  Defaulting to empty string")
    logging.info("Matching Products: %s", matching_products)

    # Map State to Response Object
    logger.info("AI Response - %s", ai_response)
    response = {
        "ai_response": f"{ai_response}",
        "qualified_customer_flag": qualified_customer_flag,
        "identified_attributes": product_attributes,
        "matching_products": matching_products
    }
    logger.info("Response to Chat Request <<< %s >>>", response)
    return response
