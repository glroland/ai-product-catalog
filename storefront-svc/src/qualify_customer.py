""" Customer Qualification Action

Analyzes a new customer inquiry to determine if its a qualified opportunity or not.
"""
import httpx
import logging
from langchain_openai import ChatOpenAI
from openai import APIConnectionError
from langchain_core.messages import HumanMessage, SystemMessage

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

    try:
        llm = ChatOpenAI(model_name="llama3.1",
                     base_url="http://ocpbmwork:11434/v1",
                     api_key="nokey",
                     timeout = httpx.Timeout(timeout=30),
                     http_client=httpx.Client(verify=False),
                     max_tokens=10,
                     temperature=0)

        response = llm.invoke(messages)
    except APIConnectionError as e:
        msg = "Unable to connect to OpenAI Server: " + e
        logger.fatal(msg)
        raise msg

    responseMessage = response.content
    logger.info("Response: " + responseMessage)
    if "ACCEPT" in responseMessage.upper():
        return True
    elif "REJECT" in responseMessage.upper():
        return False

    msg = "Unexpected response from LLM: " + responseMessage
    logger.fatal(msg)
    raise msg
