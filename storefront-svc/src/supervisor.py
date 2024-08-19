""" Virtual Store Front Supervisor Agent

Agent that manages the virtual storefront by coordinating responses to customer
inquiries and deferral to other agents.
"""
import logging
import uuid
import sys
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
    most_recent_ai_response: str
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
    logger.debug("clarify_customer_requirements")

    logger.debug("State=" + str(state))
    userMessage = state["messages"][0].content.strip()
    logger.info("User Message = " + userMessage)

    response = clarify_customer_requirements_action(userMessage)
    state["messages"].append(response)
    state["most_recent_ai_response"] = response

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


if __name__ == "__main__":
    print ("Entering Interactive Chat Mode...")
    print ()

    show_options = False
    if (len(sys.argv) > 1) and sys.argv[1].lower() == "--show-options":
        show_options = True
        print ("Enabling support for pre-loaded options.")
        print ()

    print ("Storefront>  Hello!  Thank you for visiting out shoe store.  How may we help you?")
    print ()

    graph = build_customer_visit_graph()
    config = {"configurable": {"thread_id": "interactive_chat_mode"}}

    option1 = "I'm looking for tennis shoes for my teenage son who is starting high school next week."
    option2 = "Do you have any collectable Jordan basketball shoes?"
    option3 = "What running shoes do you have?"

    while True:
        if show_options:
            print ("1 - ", option1)
            print ("2 - ", option2)
            print ("3 - ", option3)
            print ()

        user_input = input("Customer>  ")
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break
        if show_options:
            if (user_input.startswith("1")):
                user_input = option1
            elif user_input.startswith("2"):
                user_input = option2
            elif user_input.startswith("3"):
                user_input = option3

        print ()

        last_step = None
        for step in graph.stream({"messages": ("user", user_input)}, config, stream_mode="values"):
            last_step = step
        aiMessage = last_step["most_recent_ai_response"].content
        
        print("Storefront>  ", aiMessage)
        print ()
