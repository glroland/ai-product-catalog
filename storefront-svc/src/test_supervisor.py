""" Unit Tests for supervisor.py

Validate functionality for the supervisor agent during ongoing code updates and 
enhancemnets.
"""
import time
from IPython.display import Image, display
import supervisor as s

def test_wrong_store():
    """ Attempt to buy something other than shoes at the shoe store """
    print ("test_wrong_store()")

    # script customer interactions
    interaction_1 = s.CustomerInteractionLogEntry(
            timestamp = time.time(),
            question = "",
            answer = None)

    # Build the storefront agent experience graph
    graph = s.build_customer_visit_graph()
    assert Image(graph.get_graph(xray=1).draw_mermaid_png()) != None
