""" Utility module for making client invocations to OpenAI compliant server.

Connect to OpenAI servers consistently from the product catalog application without
replicating the openai configuration everywhere.
"""
import logging
import os
import json
import httpx
from langchain_openai import ChatOpenAI
from openai import APIConnectionError
from graph.tools import tools_list, invoke_tools

logger = logging.getLogger(__name__)

ENV_OPENAI_BASEURL="OPENAI_BASEURL"
ENV_OPENAI_MODEL="OPENAI_MODEL"
ENV_OPENAI_APIKEY="OPENAI_APIKEY"

def openai_invoke_require_valid_json(messages,
                                     max_tokens=100,
                                     temperature=0.8,
                                     json_mode=False,
                                     enable_tools=False,
                                     max_retries=5):
    """ Invoke an OpenAI completion inquiry but require a well formed JSON response.
        This method will retry until one is retrieved or the limit is reached.
    
        messages - message and history
        max_tokens - maximum number of tokens in response
        temperature - temperature for llm invocation
        json_mode - enable json mode
        enable_tools - whether or not to enable tools support
        max_retries - maximum number of retries
    """
    counter = 1
    while counter <= max_retries:
        logger.info("Invokink OpenAI API - Iteration #%s", counter)
        response_obj = openai_invoke(messages, max_tokens, temperature, json_mode, enable_tools)
        response_str = response_obj.content
        print()
        print(f"RESPONSE: {response_obj}")
        print()
        try:
            json.loads(response_str)
            return response_obj
        except json.JSONDecodeError as e:
            logger.warning("LLM did not return valid JSON.  Retrying!  Res=%s E=%s",
                           response_str, e)

        counter += 1

    # A valid response was not returned
    msg = "LLM NEVER returned valid JSON"
    logger.fatal(msg)
    raise ValueError(msg)

def openai_invoke(messages, max_tokens=100, temperature=0.8, json_mode = False, enable_tools = False):
    """ Invoke an OpenAI completion inquiry.
    
        messages - message and history
        max_tokens - maximum number of tokens in response
        temperature - temperature for llm invocation
        json_mode - enable json mode
    """
    logger.debug("openai_invoke() - %s", messages)

    url = "http://envision.home.glroland.com:11434/v1"
    if ENV_OPENAI_BASEURL in os.environ:
        url = os.environ[ENV_OPENAI_BASEURL]
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

        llm_with_tools = actionable_llm
        if enable_tools:
            llm_with_tools = actionable_llm.bind_tools(tools_list, parallel_tool_calls=False)

        response = llm_with_tools.invoke(messages)

        new_messages = invoke_tools(response, messages)
        if new_messages:
            logger.info("LLM invoked tools and ask is being reinvoked with new content")
            response = llm_with_tools.invoke(new_messages)

        if response.tool_calls:
            logger.warning("After invoking tools, LLM still has outstanding tool calls")

    except APIConnectionError as e:
        msg = "Unable to connect to OpenAI Server: " + str(e)
        logger.fatal(msg)
        raise e

    return response
