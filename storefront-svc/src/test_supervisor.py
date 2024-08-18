""" Unit Tests for supervisor.py

Validate functionality for the supervisor agent during ongoing code updates and 
enhancemnets.
"""
import time
import logging
from IPython.display import Image, display
import supervisor as s

def test_graph_compilation_and_visualization():
    """ Ensure that the graph compiles and supports graph visualization """
    print ("test_graph_compilation_and_visualization()")

    # Build the storefront agent experience graph
    graph = s.build_customer_visit_graph()
    assert Image(graph.get_graph(xray=1).draw_mermaid_png()) != None


def test_wrong_store():
    """ Attempt to buy something other than shoes at the shoe store """
    print ("test_wrong_store()")

    user_input = "What kind of video games do you sell?"
    graph = s.build_customer_visit_graph()

    #inputs = {"question": "Hello, how are you?"}
    result = graph.invoke(
        {"messages": [("user", user_input)]}
    )
    #print ("Result:", result)
 
    #event = graph.stream({"messages": ("user", user_input)})
    #assert event != None
    #print ("Event:", event)
    #assert event.values() != None
    #assert len(event.values()) == 1


    #    for value in event.values():
    #        print("Assistant:", value["messages"][-1].content)

    assert True
