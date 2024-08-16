"""customer-greeter-agent

AI agent acting as a customer greeter in a retail store
"""
import uvicorn
from fastapi import FastAPI

app = FastAPI()

def main():
    """Main Method
    """
    port = 8080
    if "PORT" in os.environ:
        port = int(os.environ["PORT"])
    print ("Starting Customer Greeter Agent on Port", port)
    uvicorn.run(app, host="0.0.0.0", port=port)

@app.get("/")
def default_response():
    """Provide a simple textual response to the root url to verify the application is working.
    """
    return {"message": "Hello!  Tell me who you are via /hello?name=NameGoesHere"}

@app.get("/hello")
def hello(name: str = ""):
    """Provide a basic response that propagates a query string parameter.

    Keyword arguments:
    name -- name in which to respond to with greeting
    """
    return {"message": f"Hello {name}"}


if __name__ == "__main__":
    main()
