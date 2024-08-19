""" Customer Greeter Agent

Analyzes a new customer inquiry to determine if its a qualified opportunity or not.
"""
import httpx
import logging
from langchain_openai import ChatOpenAI
from openai import APIConnectionError
from langchain_core.messages import HumanMessage, SystemMessage
from openai_client import openai_invoke

logger = logging.getLogger(__name__)

def qualify_customer_action(userMessage):
    """ Qualify whether a new customer walking into the virtual store is interested in
        shoes.

        userMessage - user message
    """
    logger.info("qualify_customer_action()")

    logger.info("User Message = " + userMessage)

    messages = [
        SystemMessage(content="You are a retail store manager for a Nike shoe store. " +
                              "You are friendly and only give concise answers to questions. " +
                              "Do not answer questions unrelated to selling shoes. " +
                              "Politely turn away any customers not interested in shoes." +
                              "Simply respond with only ACCEPT if the customer's questions should " +
                              "be answered and only REJECT if the customer should be turned away."),
        HumanMessage(content=userMessage),
    ]

    response = openai_invoke(messages, max_tokens=10, temperature=0)
    responseMessage = response.content

    logger.info("Response: " + responseMessage)
    if "ACCEPT" in responseMessage.upper():
        return True
    elif "REJECT" in responseMessage.upper():
        return False

    msg = "Unexpected response from LLM: " + responseMessage
    logger.fatal(msg)
    raise msg

