""" Virtual Store Front Supervisor Agent

Agent that manages the virtual storefront by coordinating responses to customer
inquiries and deferral to other agents.
"""
import httpx
import logging
from operator import add
from typing import List, TypedDict, Optional, Annotated, Dict
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from openai import APIConnectionError
from IPython.display import Image, display
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage, SystemMessage

logger = logging.getLogger(__name__)

class CustomerInteractionLogEntry(TypedDict):
    """ Data structure representing a single customer interaction and its results.
    """
    timestamp:float
    question:str
    answer:str


class CustomerVisitState(TypedDict):
    """ State structure used throughout the storefront agent process.
    """
    messages: Annotated[list, add_messages]
    qualified_customer: str
    #customer_interactions: List[CustomerInteractionLogEntry]


def qualify_customer(state):
    """ Qualify whether a new customer walking into the virtual store is interested in
        shoes.

        state - langchain graph state
    """
    logger.info("qualify_customer()")

    logger.debug("State=" + str(state))
    userMessage = state["messages"][0].content.strip()
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
        state["qualified_customer"] = "YES"
    elif "REJECT" in responseMessage.upper():
        state["qualified_customer"] = "NO"
    else:
        msg = "Unexpected response from LLM: " + responseMessage
        logger.fatal(msg)
        raise msg

    return state


def build_customer_visit_graph():
    """ Builds the langchain graph representing the virtual storefront experience
        that the customer will traverse while interacting with the agent via textual chat.
    """
    store_builder = StateGraph(CustomerVisitState)

    store_builder.add_node("qualify_customer", qualify_customer)
    store_builder.add_edge(START, "qualify_customer")
    store_builder.add_edge("qualify_customer", END)

    graph = store_builder.compile()

    return graph

def generate_graph_image(graph):
    # Build the storefront agent experience graph
    return Image(graph.get_graph(xray=1).draw_mermaid_png())

def inquiry_by_new_customer(user_input):
    graph = build_customer_visit_graph()

    final_state = graph.invoke(
                { "messages": [("user", user_input)] }, 
                #debug=True
            )
    
    return final_state
