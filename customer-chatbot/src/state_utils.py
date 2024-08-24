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

        return ai_response

    ai_response_str = ai_response_json["Response"]
    logger.debug("AI Message Response: %s", ai_response_str)
    return ai_response_str
