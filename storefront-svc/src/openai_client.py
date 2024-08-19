import logging
import httpx
from langchain_openai import ChatOpenAI
from openai import APIConnectionError

logger = logging.getLogger(__name__)

def openai_invoke(messages, max_tokens=100, temperature=0.8):
    logger.debug("openai_invoke() - " + str(messages))

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
        raise msg

    return response
