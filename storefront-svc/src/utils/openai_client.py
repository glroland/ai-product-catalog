""" Utility module for making client invocations to OpenAI compliant server.

Connect to OpenAI servers consistently from the product catalog application without
replicating the openai configuration everywhere.
"""
import logging
import os
import httpx
from langchain_openai import ChatOpenAI
from openai import APIConnectionError

logger = logging.getLogger(__name__)

ENV_OPENAI_BASEURL="OPENAI_BASEURL"
ENV_OPENAI_MODEL="OPENAI_MODEL"
ENV_OPENAI_APIKEY="OPENAI_APIKEY"

def openai_invoke(messages, max_tokens=100, temperature=0.8, json_mode = False):
    """ Invoke an OpenAI completion inquiry.
    
        messages - message and history
        max_tokens - maximum number of tokens in response
        temperature - temperature for llm invocation
    """
    logger.debug("openai_invoke() - %s", messages)

    url = "http://ocpwork.home.glroland.com:11434/v1"
    if ENV_OPENAI_BASEURL in os.environ:
        url = os.environ[ENV_OPENAI_BASEURL]
    # TODO - make the defaults managed by make versus hard coded
    model = "llama3.2"
    if ENV_OPENAI_MODEL in os.environ:
        model = os.environ[ENV_OPENAI_MODEL]
    apikey = "nokey"
    if ENV_OPENAI_APIKEY in os.environ:
        apikey = os.environ[ENV_OPENAI_APIKEY]
        logging.debug("Overriding API Key with configured value")
    logger.info("OpenAI Base URL (%s) and Model (%s)", url, model)

    try:
        llm = ChatOpenAI(model_name=model,
                        base_url=url,
                        api_key=apikey,
                        timeout = httpx.Timeout(timeout=30),
                        http_client=httpx.Client(verify=False),
                        max_tokens=max_tokens,
                        temperature=temperature)

        actionable_llm = llm
        if json_mode is True:
            actionable_llm = llm.bind(response_format={"type": "json_object"})

        response = actionable_llm.invoke(messages)
    except APIConnectionError as e:
        msg = "Unable to connect to OpenAI Server: " + str(e)
        logger.fatal(msg)
        raise e

    return response
