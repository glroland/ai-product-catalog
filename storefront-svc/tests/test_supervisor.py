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
