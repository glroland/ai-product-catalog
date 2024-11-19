""" Chat API Handler

Handles the API for Storefront Chat interface
"""
import json
import logging
from json.decoder import JSONDecodeError
from pydantic import BaseModel
from associates.supervisor import inquiry_by_customer
from utils.data import to_json_string, get_state_value, get_state_strlist

logger = logging.getLogger(__name__)

UNRELATED_RESPONSE = "I'm sorry but this is a shoe store.  " + \
                     "We are unable to help you with that question." + \
                     "However, we would love to sell you a new pair of shoes!"

IM_SPEECHLESS_RESPONSE = "Whoah!  You stumped the AI!  Not sure how you got here!"

ERROR_RESPONSE = "ERROR: My AI brain is very fried right now.  Please try again!"

class ChatRequest(BaseModel):
    """ Chat Request Input Structure """
    client_id : str
    user_message : str

    def __str__(self) -> str:
        return to_json_string(self)

class ChatResponse(BaseModel):
    """ Chat Request Output Structure """
    ai_response : str | None = None
    qualified_customer_flag : bool = False
    identified_attributes : list[str] = []
    matching_products: list[str] = []

    def __str__(self) -> str:
        return to_json_string(self)

def chat_api_handler(chat_request: ChatRequest) -> ChatResponse:
    """Virtual Store entry point for textual interaction with the customer.

    Keyword arguments:
    chat_request - chat request object
    """
    # Invoke LangGraph Agent
    logger.info("chat_api_handler() chat_request: %s", chat_request)
    state = inquiry_by_customer(chat_request.user_message, chat_request.client_id)
    logger.info("Resulting State After Invoke: %s", state)

    # Build Response
    response = ChatResponse()
    is_qualified = bool("YES" == get_state_value(state, "qualified_customer", False))
    response.qualified_customer_flag = is_qualified
    attributes = get_state_strlist(state, "product_attributes")
    if attributes is not None:
        response.identified_attributes = attributes
    products = get_state_value(state, "matching_products", [])
    if products is not None:
        response.matching_products = products

    # Get the AI Response, if existent
    most_recent_response = get_state_value(state, "most_recent_ai_response", None)
    json_str_response = ""
    if most_recent_response is not None and most_recent_response.content is not None:
        json_str_response = most_recent_response.content

    # Build AI Response
    if len(json_str_response) == 0:
        # Empty Response
        if response.qualified_customer_flag:
            response.ai_response = IM_SPEECHLESS_RESPONSE
        else:
            response.ai_response = UNRELATED_RESPONSE
            response.identified_attributes.clear()
            response.matching_products.clear()
    else:
        # Textual Response
        response.identified_attributes.clear()
        try:
            json_response = json.loads(json_str_response)
            response.ai_response = get_state_value(json_response, "Response", ERROR_RESPONSE)
            response.identified_attributes = get_state_strlist(json_response, "Attributes")
        except JSONDecodeError as e:
            logger.error("Unable to parse JSON response!  JsonStr=%s  Exception=%s",
                         json_str_response, e)
            response.ai_response = json_str_response

    # Return Response
    logger.info("Response to Chat Request <<< %s >>>", response)
    return response
