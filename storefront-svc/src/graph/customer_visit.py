""" Customer Visit Graph

Orchestration of a virtual storefront that coordinates responses to customer
inquiries and deferral to other agents.
"""
import logging
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from IPython.display import Image
from graph.customer_visit_state import CustomerVisitState
from graph.customer_visit_actions import qualify_customer
from graph.customer_visit_actions import is_customer_qualified
from graph.customer_visit_actions import is_sufficient_attributes
from graph.customer_visit_actions import clarify_customer_requirements
from graph.customer_visit_actions import match_attributes_to_product

logger = logging.getLogger(__name__)

def generate_graph_image(graph_app):
    """ Build the storefront agent experience graph
    """
    return Image(graph_app.get_graph(xray=1).draw_mermaid_png())

def build_customer_visit_graph(checkpointer):
    """ Builds the langchain graph representing the virtual storefront experience
        that the customer will traverse while interacting with the agent via textual chat.
    """
    store_builder = StateGraph(CustomerVisitState)

    store_builder.add_node("qualify_customer", qualify_customer)
    store_builder.add_node("clarify_customer_requirements", clarify_customer_requirements)
    store_builder.add_node("match_attributes_to_product", match_attributes_to_product)

    store_builder.add_edge(START, "qualify_customer")

    store_builder.add_conditional_edges("qualify_customer", is_customer_qualified)
    store_builder.add_conditional_edges("clarify_customer_requirements", is_sufficient_attributes)
    store_builder.add_edge("match_attributes_to_product", END)

    graph =  store_builder.compile(checkpointer=checkpointer)

    ascii = graph.get_graph().draw_ascii()
    logger.debug("Customer Visit Graph: %s", ascii)
    print(ascii)

    return graph

graph_memory = MemorySaver()

customer_visit_graph = build_customer_visit_graph(graph_memory)

def invoke_customer_visit_graph(graph_input, client_id, debug=False):
    """ Meet new customer node.

        graph_input - their initial statement of purpose or question
        client_id - unique identifier of communication
        debug - whether to enable debug output
    """
    # Continue graph
    config = {"configurable": {"thread_id": client_id}}
    logger.info("Built new customer inquiry graph.  Invoking as Thread ID=%s", client_id)
    final_state = customer_visit_graph.invoke(
                graph_input,
                config,
                debug=debug
            )

    logger.debug("State resulting from invoke: %s", final_state)
    return final_state
