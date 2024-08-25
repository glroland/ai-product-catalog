""" Unit Tests for supervisor.py

Validate functionality for the supervisor agent during ongoing code updates and 
enhancemnets.
"""
import logging
from IPython.display import Image
import supervisor as s

logger = logging.getLogger(__name__)

def test_graph_compilation_and_visualization():
    """ Ensure that the graph compiles and supports graph visualization """
    print ("test_graph_compilation_and_visualization()")

    # Build the storefront agent experience graph
    graph = s.build_customer_visit_graph()
    assert graph is not None
    assert Image(graph.get_graph(xray=1).draw_mermaid_png()) is not None


def test_reject_due_to_unrelated_products():
    """ Attempt to buy something other than shoes at the shoe store """
    logger.debug("test_reject_due_to_unrelated_products()")

    user_input = "What kind of video games do you sell?"

    final_state = s.inquiry_by_new_customer(user_input,
                                            "test_reject_due_to_unrelated_products")
    assert final_state is not None

    logger.info ("Final State: %s", final_state)
    assert final_state["qualified_customer"] == "NO"


def test_reject_due_to_unrelated_to_retail_store():
    """ Ask question about something completely unrelated to retail """
    logger.debug("test_reject_due_to_unrelated_to_retail_store()")

    user_input = "Who was the first person to walk on the moon?"

    final_state = s.inquiry_by_new_customer(user_input,
                                            "test_reject_due_to_unrelated_to_retail_store")
    assert final_state is not None

    logger.info ("Final State: %s", final_state)
    assert final_state["qualified_customer"] == "NO"


def test_accept_interested_in_nike_shoes():
    """ Ensure customer is qualified positively """
    logger.debug("test_accept_interested_in_nike_shoes()")

    user_input = "I need a new pair of tennis shoes for my teenage son starting school next week."

    final_state = s.inquiry_by_new_customer(user_input, "test_accept_interested_in_nike_shoes")
    assert final_state is not None

    logger.info ("Final State: %s", final_state)
    assert final_state["qualified_customer"] == "YES"
    assert len(final_state["messages"]) == 2
