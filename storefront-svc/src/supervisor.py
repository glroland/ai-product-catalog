""" Virtual Store Front Supervisor Agent

Agent that manages the virtual storefront by coordinating responses to customer
inquiries and deferral to other agents.
"""
import logging
import sys
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START, END
from IPython.display import Image
import supervisor_state as ss
from supervisor_actions import qualify_customer
from supervisor_actions import is_customer_qualified
from supervisor_actions import is_sufficient_attributes
from supervisor_actions import clarify_customer_requirements
from supervisor_actions import match_attributes_to_product

logger = logging.getLogger(__name__)

memory = MemorySaver()

def generate_graph_image(graph_app):
    """ Build the storefront agent experience graph
    """
    return Image(graph_app.get_graph(xray=1).draw_mermaid_png())

def build_customer_visit_graph():
    """ Builds the langchain graph representing the virtual storefront experience
        that the customer will traverse while interacting with the agent via textual chat.
    """
    store_builder = StateGraph(ss.CustomerVisitState)

    store_builder.add_node("qualify_customer", qualify_customer)
    store_builder.add_node("clarify_customer_requirements", clarify_customer_requirements)
    store_builder.add_node("match_attributes_to_product", match_attributes_to_product)

    store_builder.add_edge(START, "qualify_customer")

    store_builder.add_conditional_edges("qualify_customer", is_customer_qualified)
    store_builder.add_conditional_edges("clarify_customer_requirements", is_sufficient_attributes)
    store_builder.add_edge("match_attributes_to_product", END)

    return store_builder.compile(checkpointer=memory)

graph = build_customer_visit_graph()

def inquiry_by_customer(user_input, client_id):
    """ Meet new customer node.

        user_input - their initial statement of purpose or question
        client_id - unique identifier of communication
    """
    #graph = build_customer_visit_graph()

    # Validate client id parameter
    if client_id is None or not isinstance(client_id, str) or len(client_id) == 0:
        msg = "client_id is a required field and must be a string"
        logger.error(msg)
        raise ValueError(msg)

    # Continue graph
    config = {"configurable": {"thread_id": client_id}}
    logger.info("Built new customer inquiry graph.  Invoking as Thread ID=%s", client_id)
    final_state = graph.invoke(
                { "messages": [("user", user_input)] },
                config,
                #debug=True
            )

    logger.debug("State resulting from invoke: %s", final_state)
    return final_state


def supervisor_main():
    """ Testing CLI for supervisor agent. """

    # Setup Logging
    logging.basicConfig(level=logging.DEBUG,
        handlers=[
            logging.StreamHandler()
        ])

    print ("Entering Interactive Chat Mode...")
    print ()

    if (len(sys.argv) > 1) and sys.argv[1].lower() == "--show-options":
        show_options = True
        print ("Enabling support for pre-loaded options.")
        print ()
    else:
        show_options = False

    print ("Storefront>  Hello!  Thank you for visiting out shoe store.  How may we help you?")
    print ()

    #graph = build_customer_visit_graph()
    config = {"configurable": {"thread_id": "interactive_chat_mode"}}

    option_1 = "I would like a pair of Air Jordans by Nike that have a retro look and are " + \
               "high tops.  I'm planning to use these for aggressive weekend pickup games " +\
               "with my friends.  I do not have a color preference."
    option_2 = "I'm looking for tennis shoes for my teenage son who is starting high " + \
               "school next week."
    option_3 = "What running shoes do you have?"

    while True:
        if show_options:
            print ("1 - ", option_1)
            print ("2 - ", option_2)
            print ("3 - ", option_3)
            print ()

        user_input = input("Customer>  ")
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break
        if show_options:
            if user_input.startswith("1"):
                user_input = option_1
            elif user_input.startswith("2"):
                user_input = option_2
            elif user_input.startswith("3"):
                user_input = option_3

        print ()

        last_step = None
        for step in graph.stream({"messages": ("user", user_input)}, config, stream_mode="values"):
            last_step = step
        ai_message = last_step["most_recent_ai_response"].content

        print("Storefront>  ", ai_message)
        print ()

        if last_step["matching_products"] is not None and len(last_step["matching_products"]) > 0:
            print()
            print ("Matching Products:")
            print()
            matching_products = last_step["matching_products"]
            for p in matching_products:
                print ("SKU:", p["sku"],
                       "\tName:", p["product_name"],
                       "\tMSRP:", (p["msrp"] / 100.00),
                       "\tCosign Similarity:", p["cosign_similarity"])
            print()


if __name__ == "__main__":
    supervisor_main()
