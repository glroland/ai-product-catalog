""" Sales Rep Agent

Agent specializing in taking a qualified customer through the journey of finding
shoes they want to buy.
"""
import httpx
import logging
from langchain_openai import ChatOpenAI
from openai import APIConnectionError
from langchain_core.messages import HumanMessage, SystemMessage

logger = logging.getLogger(__name__)

def clarify_customer_requirements_action(userMessage):
    """ Try to determine what characteristics the customer is looking for with their purchase.

        userMessage - user message
    """
    logger.info("clarify_customer_requirements_action()")

    logger.info("User Message = " + userMessage)

    messages = [
        SystemMessage(content="You are a sales representative for a shoe store who focuses on " +
                              "identifying 3 preferred characteristics that a potential " +
                              "customer is looking for with their next purchase of shoes. " + 
                              "You are friendly and only give concise answers to questions. " +
                              "The preferred shoe characteristics must be gathered or directly " +
                              "inferred from the customer.  " + 
                              "Never assume or guess the customer's requirements. " +
                              "Respond first as a bulleted list with what preferred shoe characteristics the " +
                              "customer has communicated as being important for their next purchase. " +
                              "If 3 characteristics have been gathered, confirm with the customer that " +
                              "this list is correct. " +
                              "If more information is needed, ask the customer questions about their " +
                              "style preferences, usage conditions, and expectations for their next set " +
                              "of shoes."),
        HumanMessage(content=userMessage),
    ]

    try:
        llm = ChatOpenAI(model_name="llama3.1",
                     base_url="http://ocpbmwork:11434/v1",
                     api_key="nokey",
                     timeout = httpx.Timeout(timeout=30),
                     http_client=httpx.Client(verify=False),
                     max_tokens=200,
                     temperature=0.5)

        response = llm.invoke(messages)
    except APIConnectionError as e:
        msg = "Unable to connect to OpenAI Server: " + e
        logger.fatal(msg)
        raise msg

    responseMessage = response.content
    logger.info("Response: " + responseMessage)
    return response
