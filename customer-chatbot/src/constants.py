""" Constants for the Customer Chatbot Application
"""

# pylint: disable=too-few-public-methods
class SessionStateVariables:
    """ Session State Variable Names """

    CLIENT_ID = "client_id"
    MESSAGES = "messages"
    LAST_STATE = "last_state"
    IDENTIFIED_ATTRIBUTES = "identified_attributes"
    MATCHING_PRODUCTS = "matching_products"
    LAST_RESPONSE = "last_response"

# pylint: disable=too-few-public-methods
class StorefrontResponseVariables:
    """ Storefront Service Response Variable Names """

    IDENTIFIED_ATTRIBUTES = "identified_attributes"
    MATCHING_PRODUCTS = "matching_products"
    AI_RESPONSE = "ai_response"
    QUALIFIED_CUSTOMER_FLAG = "qualified_customer_flag"

# pylint: disable=too-few-public-methods
class AppUserInterfaceElements:
    """ Application UI Elements """

    TITLE = "💬 Let's GOOOOO!!!! Shoe Store"
    ATTRIBUTES_HEADER = "Identified Attributes"
    PRODUCTS_HEADER = "Product Recommendations"
    QUICK_RESPONSES = "Quick Responses"

# pylint: disable=too-few-public-methods
class CannedGreetings:
    """ Preestablished Responses """

    INTRO = "Thank you for visiting our store.  How may we help you?"

# pylint: disable=too-few-public-methods
class QuickResponses:
    """ Quick Responses """

    GENERIC_GREETING_BTN = "Generic Greeting"
    GENERIC_GREETING_PROMPT = "Hello, I am looking for a new pair of shoes."

    SPECIFIC_ASK_BTN = "Specific Ask"
    SPECIFIC_ASK_PROMPT = "I am looking for a new pair of high tops for playing pickup " + \
                    "games of Basketball with my friends.  If you have multiple " + \
                    "options, I would like a retro look and love the color white. " + \
                    "Also, I am a huge Michael Jordan fan!"

    UNRELATED_ASK_BTN = "Unrelated Question"
    UNRELATED_ASK_PROMPT = "What's the weather like today?"

    GENERIC_CLARIFICATION_BTN = "Generic Clarification"
    GENERIC_CLARIFICATION_PROMPT = "I like baseball and the color red."

# pylint: disable=too-few-public-methods
class ProductAttributes:
    """ Product Attributes """

    NAME = "product_name"
    MSRP = "msrp"
    SKU = "sku"
    SIMILARITY = "cosign_similarity"

class MessageAttributes:
    """ LLM APU Message Attributes """

    ROLE = "role"
    USER = "user"
    ASSISTANT = "assistant"
    CONTENT = "content"
