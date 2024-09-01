"""storefront-svc

Virtual Storefront API
"""
import os
import logging
import json
import uvicorn
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from supervisor import inquiry_by_customer

logger = logging.getLogger(__name__)

DEFAULT_RESPONSE = "Hello!  Welcome to the Virtual AI Storefront!  " + \
                   "Please see the Swagger API for usage guidance."

UNRELATED_RESPONSE = "I'm sorry but this is a shoe store.  " + \
                     "We are unable to help you with that question." + \
                     "However, we would love to sell you a new pair of shoes!"

IM_SPEECHLESS_RESPONSE = "Whoah!  You stumped the AI!  Not sure how you got here!"

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

    return {"message": DEFAULT_RESPONSE}

class ChatRequest(BaseModel):
    """ Chat Request Input Structure """
    user_message: str
    client_id: str

@app.post("/chat")
def chat(chat_request: ChatRequest):
    """Virtual Store entry point for textual interaction with the customer.

    Keyword arguments:
    user_message -- user message
    prior_state -- chat message history, if a conversation is occuring
    """
    user_message = chat_request.user_message
    client_id = chat_request.client_id
    logging.info("chat() User_Message: %s   Client_ID: %s", user_message, client_id)

    # Invoke LangGraph Agent
    state = inquiry_by_customer(user_message, client_id)
    logger.info("Resulting State After Invoke: %s", state)

    # Create qualification flag
    qualified_customer_flag = bool("YES" == state["qualified_customer"])

    # Prepare attributes response
    if state["attributes_confirmed"] is None:
        attributes_confirmed_flag = False
    else:
        attributes_confirmed_flag = state["attributes_confirmed"]
    product_attributes = state["product_attributes"]

    # Prepare default AI Response - allows ai to override logic by design
    if state["most_recent_ai_response"] is None:
        if qualified_customer_flag is True:
            ai_response = IM_SPEECHLESS_RESPONSE
        else:
            ai_response = UNRELATED_RESPONSE
            product_attributes = ""
    else:
        json_str_response = state["most_recent_ai_response"].content
        json_response = json.loads(json_str_response)
        ai_response = json_response["Response"]
        product_attributes = json_response["Attributes"]

    matching_products = ""
    if state["matching_products"] is not None:
        matching_products = state["matching_products"]

    # Map State to Response Object
    response = {
        "ai_response": f"{ai_response}",
        "qualified_customer_flag": qualified_customer_flag,
        "attributes_confirmed_flag": attributes_confirmed_flag,
        "identified_attributes": f"{product_attributes}",
        "matching_products": f"{matching_products}"
    }
    logger.info("Response to Chat Request <<< %s >>>", response)
    return response

@app.get("/health")
def health_check():
    """ Provide a basic response indicating the app is available for consumption. """
    return "OK"

if __name__ == "__main__":
    main()
