""" Default Response API Handler
"""
import logging
from pydantic import BaseModel

DEFAULT_RESPONSE = "Hello!  Welcome to the Virtual AI Storefront!  " + \
                   "Please see the Swagger API for usage guidance."

class DefaultResponse(BaseModel):
    """ Default API Response Type """

    message : str = ""

def default_api_handler() -> DefaultResponse:
    """Provide a simple textual response to the root url to verify the application is working.
    """
    logging.info("default_response")

    response = DefaultResponse()
    response.message = DEFAULT_RESPONSE
    return response
