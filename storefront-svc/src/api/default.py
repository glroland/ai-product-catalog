""" Default Response API Handler
"""
import logging

DEFAULT_RESPONSE = "Hello!  Welcome to the Virtual AI Storefront!  " + \
                   "Please see the Swagger API for usage guidance."

def default_api_handler():
    """Provide a simple textual response to the root url to verify the application is working.
    """
    logging.info("default_response")

    return {"message": DEFAULT_RESPONSE}
