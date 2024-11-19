""" Virtual Store Front Supervisor Agent

Agent that manages the virtual storefront by coordinating responses to customer
inquiries and deferral to other agents.
"""
import logging
from graph.customer_visit import invoke_customer_visit_graph

logger = logging.getLogger(__name__)

def inquiry_by_customer(user_input, client_id):
    """ Meet new customer node.

        user_input - their initial statement of purpose or question
        client_id - unique identifier of communication
    """
    # Validate client id parameter
    if client_id is None or not isinstance(client_id, str) or len(client_id) == 0:
        msg = "client_id is a required field and must be a string"
        logger.error(msg)
        raise ValueError(msg)

    # Continue graph
    graph_input = { "messages": [("user", user_input)] }
    graph_state = invoke_customer_visit_graph(graph_input, client_id)
    return graph_state
