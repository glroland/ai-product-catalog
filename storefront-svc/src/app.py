"""storefront-svc

Virtual Storefront API
"""
import os
import uuid
import logging
import uvicorn
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from supervisor import build_customer_visit_graph

logger = logging.getLogger(__name__)

app = FastAPI()

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """ Additional logging for getting extra detail about certain http binding errors. """
    exc_str = f'{exc}'.replace('\n', ' ').replace('   ', ' ')
    logging.error("Request: %s - Exception: %s" , request, exc_str)
    content = {'status_code': 10422, 'message': exc_str, 'data': None}
    return JSONResponse(content=content, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)

def main():
    """Main Method
    """

    # Setup Logging
    logging.basicConfig(level=logging.DEBUG,
        handlers=[
            # no need from a docker container - logging.FileHandler("storefront-svc.log"),
            logging.StreamHandler()
        ])

    # Setup Port
    port = 8080
    if "PORT" in os.environ:
        port = int(os.environ["PORT"])
    logging.info("Starting Virtual Storefront on Port %s", port)

    # Start Server
    uvicorn.run(app, host="0.0.0.0", port=port)

@app.get("/")
def default_response():
    """Provide a simple textual response to the root url to verify the application is working.
    """
    logging.info("default_response")

    msg = "Hello!  Welcome to the Virtual AI Storefront!  " + \
          "Please see the Swagger API for usage guidance."
    return {"message": msg}

class ChatRequest(BaseModel):
    """ Chat Request Input Structure """
    user_message: str
    prior_state: str

@app.post("/chat")
def chat(chat_request: ChatRequest):
    """Virtual Store entry point for textual interaction with the customer.

    Keyword arguments:
    user_message -- user message
    prior_state -- chat message history, if a conversation is occuring
    """
    user_message = chat_request.user_message
    prior_state = chat_request.prior_state
    logging.info("chat() User_Message: %s   Prior_State: %s", user_message, prior_state)

    # Invoke LangGraph Agent
    graph = build_customer_visit_graph()
    config = {"configurable": {"thread_id": str(uuid.uuid4())}}
    state = graph.invoke({"messages": ("user", user_message)}, config)

    logger.info("Resulting State After Invoke: %s", state)
    return state

@app.get("/health")
def health_check():
    """ Provide a basic response indicating the app is available for consumption. """
    return "OK"

if __name__ == "__main__":
    main()
