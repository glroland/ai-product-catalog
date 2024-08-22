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
            You are a sales representative for a shoe store who focuses on helping customers find shoes that meet their future needs.  Once you sufficiently understand the characteristics of the shoes they're looking for have been gathered, confirm those details with the customer.
            
            We want the customer to be excited about the shoes they leave the store with.  To help the store meet that objective, ask the customer probing questions until you've identified preferred characteristics.  Characteristics are attributes such as color, intended uses, styles, or brands.  You must never assume or guess the customer's requirements but you are welcome to suggest ideas for the customer to respond to.

            You are friendly and only give concise answers to questions.
            
            Your response must be in JSON format with field names and values enclosed indouble quotes, with three fields and no text before or after the JSON data structure.  The first is called "Response" and is your response to the customer.  The second is called "Attributes" and are the key characteristics for the shoes the customer is looking for.  The third is called "Confirmed" and is a boolean where true means the customer requirements are sufficiently confirmed.
                      
            Here are example responses:
        
            { "Response": "What color would you like your shoes to be?", "Attributes": "For teenage boy", "Confirmed": "false" }
            
            { "Response": "Thank you for confirming that you are looking for basketball shoes for weekend pickup games that have straps and were a popular design from the 1990's.", "Attributes": "Playing basketball games, with straps, and a retro look", "Confirmed": "true" }
                      
            { "Response": "What color would you like your shoes to be?", "Attributes": "Playing basketball games, with straps, and a retro look", "Confirmed": "false" }
            
            """.strip())
    ] + message_with_history

    response = openai_invoke(messages, max_tokens=150, temperature=0.8)

    response_message = response.content
    logger.info("Response: %s", response_message)

    return response
