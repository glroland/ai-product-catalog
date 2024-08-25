""" Utility Functions for LangGraph State

Utility functions that help access and manipulate the LangGraph State
that is returned from the invocation service.
"""
import logging
import json

logger = logging.getLogger(__name__)

def is_qualified_customer(response_json):
    """ Determine if LLM believes the customer is a qualified customer.
    
    Returns true if qualified
    """
    val = response_json["qualified_customer"]
    if not isinstance(val, str):
        msg = "Unable to determine if the customer is qualified due to unexpected response from LLM"
        logger.error(msg)
        raise ValueError(msg)
    logger.debug("Customer Qualified value from LLM: %s", val)

    if val == "YES":
        return True

    return False


def get_most_recent_ai_response(response_json):
    """ Get the Most Recent AI Response from the Provided State
    
    response_json - last state
    """
    ai_response = response_json["most_recent_ai_response"]["content"]
    logger.debug("Most Recent AI Response: %s", ai_response)
    print("Most Recent AI Response: " + str(ai_response))

    try:
        ai_response_json = json.loads(ai_response)
    except json.decoder.JSONDecodeError as e:
        msg = "Cannot decode AI Response: " + ai_response
        print(msg, e)
        logger.error(msg, e)

        return "DECODE_ERROR - " + str(ai_response)

    ai_response_str = ai_response_json["Response"]
    logger.debug("AI Message Response: %s", ai_response_str)
    return ai_response_str


def get_most_recent_ai_attributes(response_json):
    """ Get the Most Recent AI recommended attributes from the Provided State
    
    response_json - last state
    """
    ai_response = response_json["most_recent_ai_response"]["content"]
    logger.debug("Most Recent AI Response: %s", ai_response)
    print("Most Recent AI Response: " + str(ai_response))

    try:
        ai_response_json = json.loads(ai_response)
    except json.decoder.JSONDecodeError as e:
        msg = "Cannot decode AI Response: " + ai_response
        print(msg, e)
        logger.error(msg, e)
        return "DECODE_ERROR"

    ai_attributes = ai_response_json["Attributes"]
    logger.debug("AI Attributes: %s", ai_attributes)
    return ai_attributes


def get_matching_products(response_json):
    """ Get matching products from the last LLM response.
    
    response_json - state
    """
    matching_products = ""
    if "matching_products" in response_json:
        matching_products = response_json["matching_products"]
    if matching_products is None:
        matching_products = ""
    logger.debug("Matching Products: %s", matching_products)
    return matching_products


def comma_seperated_to_markdown(value):
    """ Convert a comman delimitted list of strings to a markdown list of items.
    
    value - comma delimitted list or list of strings
    """
    markdown = ""
    if value is not None:
        if isinstance(value, list):
            for v in value:
                markdown = markdown + "- " + v + "\n"
        elif isinstance(value, str):
            if len(value) > 0:
                value_list = value.split(",")
                for value in value_list:
                    markdown = markdown + "- " + value + "\n"        
        else:
            markdown = "UNKNOWN TYPE - " + str(value)
    return markdown
