""" Sales Rep Agent

Agent specializing in taking a qualified customer through the journey of finding
shoes they want to buy.
"""
import logging
from langchain_core.messages import HumanMessage, SystemMessage
from openai_client import openai_invoke

logger = logging.getLogger(__name__)

def clarify_customer_requirements_action(user_message):
    """ Try to determine what characteristics the customer is looking for with their purchase.

        userMessage - user message
    """
    logger.info("clarify_customer_requirements_action()")

    logger.info("User Message = " + user_message)

    messages = [
        SystemMessage(content="""
            You are a sales representative for a shoe store who focuses on identifying 3 preferred characteristics that a potential customer is looking for with 
            their next purchase of shoes.
            Characteristics are attributes such as color, unique ways of usage (such as hiking, specific sports, etc).
            You are friendly and only give concise answers to questions.
            The preferred shoe characteristics must be gathered or directly inferred from the customer.
            Never assume or guess the customer's requirements.
            Respond first as a bulleted list with what preferred shoe characteristics the customer has communicated as being important for their next purchase.
            If 3 characteristics have been gathered, confirm with the customer that this list is correct.
            If more information is needed, ask the customer questions about their style preferences, usage conditions, and expectations for their next set of shoes.
            """.strip()),
        HumanMessage(content=user_message),
    ]

    response = openai_invoke(messages, max_tokens=150, temperature=0.8)

    response_message = response.content
    logger.info("Response: " + response_message)

    return response
