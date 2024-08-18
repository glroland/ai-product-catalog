""" Virtual Store Front Supervisor Agent

Agent that manages the virtual storefront by coordinating responses to customer
inquiries and deferral to other agents.
"""
import logging
import uuid
from operator import add
from typing import List, TypedDict, Optional, Annotated, Literal, TypedDict
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START, END
from IPython.display import Image, display
from langgraph.graph.message import add_messages
from customer_greeter import qualify_customer_action
from sales_rep import clarify_customer_requirements_action

logger = logging.getLogger(__name__)

memory = MemorySaver()

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


def should_continue(state: CustomerVisitState) -> Literal["clarify_customer_requirements", END]:
    if state["qualified_customer"] != "YES":
        return END
    
    return "clarify_customer_requirements"


def clarify_customer_requirements(state):
    logger.debug("State=" + str(state))
    userMessage = state["messages"][0].content.strip()
    logger.info("User Message = " + userMessage)

    response = clarify_customer_requirements_action(userMessage)
    state["messages"].append(response)
    return state


def build_customer_visit_graph():
    """ Builds the langchain graph representing the virtual storefront experience
        that the customer will traverse while interacting with the agent via textual chat.
    """
    store_builder = StateGraph(CustomerVisitState)

    store_builder.add_node("qualify_customer", qualify_customer)
    store_builder.add_node("clarify_customer_requirements", clarify_customer_requirements)
    store_builder.add_edge(START, "qualify_customer")
    store_builder.add_conditional_edges("qualify_customer", should_continue)
    #store_builder.add_edge("qualify_customer", END)

    graph = store_builder.compile(checkpointer=memory)

    return graph

def generate_graph_image(graph):
    # Build the storefront agent experience graph
    return Image(graph.get_graph(xray=1).draw_mermaid_png())

def inquiry_by_new_customer(user_input, client_id=str(uuid.uuid4())):
    graph = build_customer_visit_graph()

    config = {"configurable": {"thread_id": client_id}}
    logger.info("Built new customer inquiry graph.  Invoking as Thread ID=" + client_id)
    final_state = graph.invoke(
                { "messages": [("user", user_input)] }, 
                config,
                #debug=True
            )
    
    return final_state
