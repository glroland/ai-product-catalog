""" Customer Greeter Agent

Analyzes a new customer inquiry to determine if its a qualified opportunity or not.
"""
import logging
from langchain_core.messages import HumanMessage, SystemMessage
from utils.openai_client import openai_invoke

logger = logging.getLogger(__name__)

def qualify_customer_action(user_message):
    """ Qualify whether a new customer walking into the virtual store is interested in
        shoes.

        userMessage - user message
    """
    logger.info("qualify_customer_action()")

    logger.info("User Message = %s", user_message)

    messages = [
        SystemMessage(content=
            """
            You are a retail store manager for a Nike shoe store.
            You are friendly and only give concise answers to questions.
            Do not answer questions unrelated to selling shoes.
            Politely turn away any customers not interested in shoes.
            Simply respond with only ACCEPT if the customer's questions
            should be answered and only REJECT if the customer should
            be turned away.
            """.strip()
        ),
        HumanMessage(content=user_message),
    ]

    response = openai_invoke(messages, max_tokens=10, temperature=0)
    response_message = response.content

    logger.info("Response: %s", response_message)
    if "ACCEPT" in response_message.upper():
        return True
    if "REJECT" in response_message.upper():
        return False

    msg = "Unexpected response from LLM: " + response_message
    logger.fatal(msg)
    raise msg
