""" Virtual Store Front Supervisor Agent

Agent that manages the virtual storefront by coordinating responses to customer
inquiries and deferral to other agents.
"""
import logging
import json
import uuid
import sys
from typing import TypedDict, Annotated, Literal
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from IPython.display import Image
from customer_greeter import qualify_customer_action
from sales_rep import clarify_customer_requirements_action
from service_adapter import product_semantic_search, Product

logger = logging.getLogger(__name__)

memory = MemorySaver()

class CustomerVisitState(TypedDict):
    """ State structure used throughout the storefront agent process.
    """
    messages: Annotated[list, add_messages]
    qualified_customer: str
    most_recent_ai_response: str
    product_attributes: str
    attributes_confirmed: str
    matching_products: list[Product]


def qualify_customer(state):
    """ Qualify whether a new customer walking into the virtual store is interested in
        shoes.

        state - langchain graph state
    """
    logger.info("qualify_customer()")

    logger.debug("State=%s", state)
    user_message = state["messages"][0].content.strip()
    logger.info("User Message = %s", user_message)

    if qualify_customer_action(user_message):
        state["qualified_customer"] = "YES"
    else:
        state["qualified_customer"] = "NO"

    return state


def is_customer_qualified(state: CustomerVisitState) -> \
                Literal["check_attributes", END]:
    """ Determine whether the graph should proceed to clarify customer requirements or end.

        state - langgraph state
    """
    if state["qualified_customer"] != "YES":
        return END

    return "check_attributes"

def check_attributes(state: CustomerVisitState):
    """ Qualified customer and now check to see if attributes are complete and confirmed. 
    
        state - langgraph state
    """
    print ("State>", state)
    logger.info("State> %s", state)

    if isinstance(state["attributes_confirmed"], bool) and state["attributes_confirmed"]:
        if len(state["product_attributes"].strip()) == 0:
            state["attributes_confirmed"] = False

    return state

def is_attributes_confirmed(state: CustomerVisitState) -> \
        Literal["clarify_customer_requirements", "match_attributes_to_product"]:
    """ Determine whether the graph should continue to clarify customer requirements or 
        proceed onto matching possible products to their requests.

        state - langgraph state
    """
    if isinstance(state["attributes_confirmed"], bool) and state["attributes_confirmed"]:
        return "match_attributes_to_product"

    return "clarify_customer_requirements"


# pylint disable=W0718
def clarify_customer_requirements(state):
    """ Attempt to clarify customer purchasing needs node.

        state - langgraph state
    """
    logger.debug("clarify_customer_requirements")

    logger.debug("State=%s", state)
    user_message = state["messages"][0].content.strip()
    logger.info("User Message = %s", user_message)

    logger.debug ("Message History and Latest User Message prior to LLM>>  %s", state["messages"])

    if state["matching_products"] is not None:
        state["matching_products"].clear()

    response = clarify_customer_requirements_action(state["messages"])
    state["messages"].append(response)
    state["most_recent_ai_response"] = response

    try:
        response_json = json.loads(response.content)
        state["product_attributes"] = response_json["Attributes"]
    except Exception as e:
        logger.error("LLM produced unexpected response.  Exception=%s Response=%s",
                     e, response.content)
        state["product_attributes"] = ""
        state["attributes_confirmed"] = ""
        if state["matching_products"] is not None:
            state["matching_products"].clear()

        print()

    if is_sufficient_attributes(state["product_attributes"]):
        state["attributes_confirmed"] = True
    else:
        state["attributes_confirmed"] = False

    return state


def is_sufficient_attributes(attributes):
    """ Check attributes to see if there is sufficient quanitity and quality to
        proceed.

        attributes - delimited string containing attribute data
    """
    if not isinstance(attributes, str) or len(attributes) == 0:
        return False

    alist = attributes.split(",")

    if len(alist) >= 2:
        return True

    return False


def match_attributes_to_product(state):
    """ Take the shoe attributes gathered from the customer and attempt to
        match available products to them.  """
    logger.debug("match_attributes_to_product")

    if state["attributes_confirmed"] is not True:
        return state

    attributes = state["product_attributes"]
    logger.debug("Matching Attributes to Products via Semantic Search: %s", attributes)

    products = product_semantic_search(attributes, 3)
    logger.info("Matched Products!  Attributes=%s  Matching_Products=%s", attributes, products)
    state["matching_products"] = products

    return state


def build_customer_visit_graph():
    """ Builds the langchain graph representing the virtual storefront experience
        that the customer will traverse while interacting with the agent via textual chat.
    """
    store_builder = StateGraph(CustomerVisitState)

    store_builder.add_node("qualify_customer", qualify_customer)
    store_builder.add_node("check_attributes", check_attributes)
    store_builder.add_node("clarify_customer_requirements", clarify_customer_requirements)
    store_builder.add_node("match_attributes_to_product", match_attributes_to_product)
    store_builder.add_edge(START, "qualify_customer")
    store_builder.add_edge("clarify_customer_requirements", "match_attributes_to_product")
    store_builder.add_conditional_edges("qualify_customer", is_customer_qualified)
    store_builder.add_conditional_edges("check_attributes", is_attributes_confirmed)
    store_builder.add_edge("match_attributes_to_product", END)

    return store_builder.compile(checkpointer=memory)


def generate_graph_image(graph_app):
    """ Build the storefront agent experience graph
    """
    return Image(graph_app.get_graph(xray=1).draw_mermaid_png())


def inquiry_by_new_customer(user_input, client_id=str(uuid.uuid4())):
    """ Meet new customer node.

        user_input - their initial statement of purpose or question
        client_id - unique identifier of communication
    """
    graph = build_customer_visit_graph()

    config = {"configurable": {"thread_id": client_id}}
    logger.info("Built new customer inquiry graph.  Invoking as Thread ID=%s", client_id)
    final_state = graph.invoke(
                { "messages": [("user", user_input)] },
                config,
                #debug=True
            )

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

    graph = build_customer_visit_graph()
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
