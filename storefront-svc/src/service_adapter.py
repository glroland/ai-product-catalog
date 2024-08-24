import requests
import os
import logging
from typing import TypedDict, List


logger = logging.getLogger(__name__)


ENV_PRODUCT_SERVICE_ADDRESS = "ENV_PRODUCT_SERVICE_ADDRESS"


class Product(TypedDict):
    """ State structure used throughout the storefront agent process.
    """
    sku: str
    product_name: str
    msrp: int
    cosign_similarity: float


def product_semantic_search(attributes, limit = 3):
    """ Perform a semantic search across products using the provided attributes. 
    
        attributes - attributes to match 
    """
    if len(attributes) == 0:
        msg = "Empty list of attributes passed into semantic search function."
        logger.error(msg)
        raise ValueError(msg)

    service_address = "http://localhost:8080"
    if ENV_PRODUCT_SERVICE_ADDRESS in os.environ:
        service_address = os.environ[ENV_PRODUCT_SERVICE_ADDRESS]
    logger.info("Using Product Service Address: %s", service_address)

    userMessage = attributes

    url = service_address + "/similaritysearch"
    logger.debug("Semantic Search URL: %s with the following data: %s", url, userMessage)
    response = requests.post(url, data={"userMessage": userMessage, "limit": limit})

    if response.status_code != 200:
        msg = "Received Error Response from Products Service: " + str(response.status_code)
        logger.error(msg)
        raise Exception(msg)

    products = response.json()
    print ("Response:", products)


    matchingProducts: List[Product] = []
    for product in products:
        p: Product = {'sku': product["sku"],
                      'product_name': product["productName"],
                      'msrp': product["msrp"] * 100.00,
                      'cosign_similarity': product["cosignSimilarity"]}
        matchingProducts.append(p)

    logger.info("Matching Products: %s", matchingProducts)
    return matchingProducts


def service_adapter_main():
    """ Testing CLI for service adapter. """
    print ()
    print ()
    print ("Entering Adapter Test Mode...")
    print ()

    print ("Storefront>  Enter attributes string to search for....")
    print ()

    option_1 = "Air Jordans, retro look, high tops"
    option_2 = "blue, has straps"
    option_3 = "Baseball cleets, red, boys"

    while True:
        print ("1 - ", option_1)
        print ("2 - ", option_2)
        print ("3 - ", option_3)
        print ()

        user_input = input("Customer>  ")
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break
        if user_input.startswith("1"):
            user_input = option_1
        elif user_input.startswith("2"):
            user_input = option_2
        elif user_input.startswith("3"):
            user_input = option_3

        matchingProducts = product_semantic_search(user_input, 5)
        for p in matchingProducts:
            print ("SKU:", p["sku"], "\tName:", p["product_name"], "\tMSRP:", (p["msrp"] / 100.00), "\tCosign Similarity:", p["cosign_similarity"])

        print ()


if __name__ == "__main__":
    service_adapter_main()
