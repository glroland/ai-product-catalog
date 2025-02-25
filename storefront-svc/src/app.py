""" Virtual Storefront API

Storefront application that provides a chat like experience for customers to find and acquire
new products.
"""
import logging
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from api.chat import chat_api_handler, ChatRequest, ChatResponse
from api.health import health_api_handler
from api.default import default_api_handler, DefaultResponse
import coloredlogs

# Setup Logging
logger = logging.getLogger(__name__)
coloredlogs.install(level="DEBUG")

app = FastAPI()

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """ Additional logging for getting extra detail about certain http binding errors. """
    exc_str = f'{exc}'.replace('\n', ' ').replace('   ', ' ')
    logging.error("Request: %s - Exception: %s" , request, exc_str)
    content = {'status_code': 10422, 'message': exc_str, 'data': None}
    return JSONResponse(content=content, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)

@app.get("/", response_model=DefaultResponse)
def default() -> DefaultResponse:
    """Provide a simple textual response to the root url to verify the application is working.
    """
    return default_api_handler()

@app.post("/chat", response_model=ChatResponse)
def chat(chat_request: ChatRequest):
    """Virtual Store entry point for textual interaction with the customer.

    Keyword arguments:
    chat_request - chat request object
    """
    return chat_api_handler(chat_request)

@app.get("/health", response_model=str)
def health():
    """ Provide a basic response indicating the app is available for consumption. """
    return health_api_handler()
