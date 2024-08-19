""" Utility module for making client invocations to OpenAI compliant server.

Connect to OpenAI servers consistently from the product catalog application without
replicating the openai configuration everywhere.
"""
import logging
import httpx
from langchain_openai import ChatOpenAI
from openai import APIConnectionError

logger = logging.getLogger(__name__)

def openai_invoke(messages, max_tokens=100, temperature=0.8):
    """ Invoke an OpenAI completion inquiry.
    
        messages - message and history
        max_tokens - maximum number of tokens in response
        temperature - temperature for llm invocation
    """
    logger.debug("openai_invoke() - %s", messages)

    try:
        llm = ChatOpenAI(model_name="llama3.1",
                        base_url="http://ocpbmwork:11434/v1",
                        api_key="nokey",
                        timeout = httpx.Timeout(timeout=30),
                        http_client=httpx.Client(verify=False),
                        max_tokens=max_tokens,
                        temperature=temperature)

        response = llm.invoke(messages)
    except APIConnectionError as e:
        msg = "Unable to connect to OpenAI Server: " + e
        logger.fatal(msg)
        raise msg from e

    return response
