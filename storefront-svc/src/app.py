"""storefront-svc

Virtual Storefront API
"""
import os
import uvicorn
from fastapi import FastAPI

app = FastAPI()

def main():
    """Main Method
    """
    port = 8080
    if "PORT" in os.environ:
        port = int(os.environ["PORT"])
    print ("Starting Virtual Storefront on Port", port)
    uvicorn.run(app, host="0.0.0.0", port=port)

@app.get("/")
def default_response():
    """Provide a simple textual response to the root url to verify the application is working.
    """
    msg = "Hello!  Welcome to the Virtual AI Storefront!  " + \
          "Please see the Swagger API for usage guidance."
    return {"message": msg}

@app.post("/")
def chat(user_message: str, msg_history = None):
    """Virtual Store entry point for textual interaction with the customer.

    Keyword arguments:
    user_message -- user message
    msg_history -- chat message history, if a conversation is occuring
    """
    return {"message": "Hello: " + user_message + msg_history}

if __name__ == "__main__":
    main()
