"""storefront-svc

Virtual Storefront API
"""
import os
import uuid
import logging
import uvicorn
from fastapi import FastAPI
from supervisor import build_customer_visit_graph

logger = logging.getLogger(__name__)

app = FastAPI()

def main():
    """Main Method
    """
    logging.basicConfig(filename='storefront-svc.log', level=logging.INFO)

    port = 8080
    if "PORT" in os.environ:
        port = int(os.environ["PORT"])
    print ("Starting Virtual Storefront on Port", port)
    logging.info("Starting Virtual Storefront on Port %s", port)

    uvicorn.run(app, host="0.0.0.0", port=port)

@app.get("/")
def default_response():
    """Provide a simple textual response to the root url to verify the application is working.
    """
    logging.info("default_response")

    msg = "Hello!  Welcome to the Virtual AI Storefront!  " + \
          "Please see the Swagger API for usage guidance."
    return {"message": msg}

@app.post("/chat")
def chat(user_message: str = "Hello", prior_state = None):
    """Virtual Store entry point for textual interaction with the customer.

    Keyword arguments:
    user_message -- user message
    prior_state -- chat message history, if a conversation is occuring
    """
    logging.info("chat() User_Message: %s   Prior_State: %s", user_message, prior_state)
    print("Chat()   User_Message:", user_message, "Prior_State:", prior_state)

    graph = build_customer_visit_graph()
    config = {"configurable": {"thread_id": str(uuid.uuid4())}}

    state = graph.invoke({"messages": ("user", user_message)}, config)

    logger.debug("Resulting State After Invoke: %s", state)
    print ("Resulting State After Invoke>>> ", state)

    return state

@app.get("/health")
def health_check():
    """ Provide a basic response indicating the app is available for consumption. """
    return "OK"

if __name__ == "__main__":
    main()
