""" Virtual Store Front Supervisor Agent

Agent that manages the virtual storefront by coordinating responses to customer
inquiries and deferral to other agents.
"""
import logging
from operator import add
from typing import List, TypedDict, Optional, Annotated, Dict
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START, END
from IPython.display import Image, display
from langgraph.graph.message import add_messages
from qualify_customer import qualify_customer_action

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

    if qualify_customer_action(userMessage):
        state["qualified_customer"] = "YES"
    else:        
        state["qualified_customer"] = "NO"

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
