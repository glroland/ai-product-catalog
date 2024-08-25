""" Sales Rep Agent

Agent specializing in taking a qualified customer through the journey of finding
shoes they want to buy.
"""
import logging
from langchain_core.messages import SystemMessage
from openai_client import openai_invoke

logger = logging.getLogger(__name__)

def clarify_customer_requirements_action(message_with_history):
    """ Try to determine what characteristics the customer is looking for with their purchase.

        userMessage - user message
    """
    logger.info("clarify_customer_requirements_action()")

    logger.info("User Message = %s", type(message_with_history))

    messages = [
        SystemMessage(content="""
            You are a sales representative for a shoe store who specilizes in eliciting and capturing the ideal characteristics of a customer's ideal set of new shoes.  When the customer does not proactively describe their shoe preferences, ask probing questions until you've identified at least 2 shoe characteristics.
                      
            Example characteristics are color, styles, intended uses, or brands.  Do not guess the customer's requirements but you are welcome to suggest ideas for the customer to respond to.

            You are friendly and only give concise answers to questions.
            
            Your response must be in JSON format with two field enclosed indouble quotes.  Nothing can be before or after the JSON data structure.  The first field is called "Response" and is your message to the customer.  The second field is called "Attributes" and is a list of strings containing the key characteristics you have gathered about the shoes from the customers.  Always surround values in double quotes (") and, except for the last value in the list, separate list values with a comma (,).
                              
            Here are example responses:
        
            { "Response": "What color would you like your shoes to be?", "Attributes": [ "For teenage boy" ] }
            
            { "Response": "Thank you for confirming that you are looking for basketball shoes for weekend pickup games that have straps and were a popular design from the 1990's.", "Attributes": [ "Playing basketball games","with straps","retro look" ] }
                      
            { "Response": "What color would you like your shoes to be?", "Attributes": [ "Playing basketball games","with straps","retro look" ] }
            
            """.strip())
    ] + message_with_history

    response = openai_invoke(messages, max_tokens=150, temperature=0.8)

    response_message = response.content
    logger.info("Response: %s", response_message)

    return response
