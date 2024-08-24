"""API Utilities

Utility functions related to connecting with the backend services supporting
the chatbot.
"""
import os
import logging
import requests

logger = logging.getLogger(__name__)

ENV_AI_BACKEND_ENDPOINT = "AI_BACKEND_ENDPOINT"

DEFAULT_TIMEOUT = 30

def get_ai_backend_endpoint():
    """ Gets the default or configured backend endpoint URL.
    
    Returns URL
    """
    url = "http://localhost:8080"
    if ENV_AI_BACKEND_ENDPOINT in os.environ:
        url = os.environ[ENV_AI_BACKEND_ENDPOINT]

    logger.info("AI Backend Endpoint: %s", url)
    return url

def invoke_chat_api(user_message, prior_state = None):
    """ Invokes the backend chat API.
    
    user_message - user message (clean string)
    prior_state - ongoing message state for langgraph
    """
    chat_url = get_ai_backend_endpoint() + "/chat"
    chat_params = {
        "user_message": user_message,
        "prior_state": prior_state
    }
    response = requests.post(chat_url,
                        params=chat_params,
                        timeout=DEFAULT_TIMEOUT)

    if response.status_code != 200:
        msg = "Received Error Response from Backend Service: " + str(response.status_code)
        logger.error(msg)
        raise ConnectionError(msg)

    response_json = response.json()
    logger.info ("Response JSON: %s", response_json)
    print ("Response JSON: " + str(response_json))

    return response_json
