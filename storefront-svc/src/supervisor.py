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

class CustomerInteractionLogEntry(TypedDict):
    """ Data structure representing a single customer interaction and its results.
    """
    timestamp:float
    question:str
    answer:str


class CustomerVisitState(TypedDict):
    """ State structure used throughout the storefront agent process.
    """
    #messages: Annotated[list, add]
    #customer_interactions: List[CustomerInteractionLogEntry]
    #question: Optional[str] = None
    #response: Optional[str] = None
    messages: Annotated[list, add_messages]


def greet_customer(state):
    """ Greet a new customer walking into the virtual store.

        state - langchain graph state
    """
    print ("greet_customer()")

    try:
        llm = ChatOpenAI(model_name="llama3.1",
                     base_url="http://ocpbmwork:11434/v1",
                     api_key="nokey",
                     timeout = httpx.Timeout(timeout=30),
                     http_client=httpx.Client(verify=False),
                     max_tokens=100,
                     temperature=0.2)

        response = llm.invoke("Who's the current president of USA?")
        responseMessage = response.content
        logging.getLogger(__name__).info("Response: " + responseMessage)

    except APIConnectionError as e:
        raise ("Unable to connect to OpenAI Server: " + e)

    #question = state.get('question', '').strip()
    #response = llm.invoke(
    #        {
    #            "input": question,
    #        }
    #    )
    #print("LLM Interaction:  UserMessage=", question, "Response=", response)
    #return {"response": [response]}


def build_customer_visit_graph():
    """ Builds the langchain graph representing the virtual storefront experience
        that the customer will traverse while interacting with the agent via textual chat.
    """
    store_builder = StateGraph(CustomerVisitState)

    store_builder.add_node("greet_customer", greet_customer)
    store_builder.add_edge(START, "greet_customer")
    store_builder.add_edge("greet_customer", END)

    graph = store_builder.compile()

    return graph

def generate_graph_image(graph):
    # Build the storefront agent experience graph
    return Image(graph.get_graph(xray=1).draw_mermaid_png())
