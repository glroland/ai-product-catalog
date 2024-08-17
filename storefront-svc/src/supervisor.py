""" Virtual Store Front Supervisor Agent

Agent that manages the virtual storefront by coordinating responses to customer
inquiries and deferral to other agents.
"""
from operator import add
from typing import List, TypedDict, Optional, Annotated, Dict
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START, END
from IPython.display import Image, display


class CustomerInteractionLogEntry(TypedDict):
    """ Data structure representing a single customer interaction and its results.
    """
    timestamp:float
    question:str
    answer:str


class CustomerVisitState(TypedDict):
    """ State structure used throughout the storefront agent process.
    """
    raw_logs: Annotated[List[Dict], add]
    customer_interactions: List[CustomerInteractionLogEntry]


def greet_customer(state):
    """ Greet a new customer walking into the virtual store.

        state - langchain graph state
    """
    print ("greet_customer()")


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
