""" Customer Visit LangGraph State

Attributes that are carried from node to node within the graph.
"""
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
from utils.semantic_search import Product

class CustomerVisitState(TypedDict):
    """ State structure used throughout the storefront agent process.
    """
    messages: Annotated[list, add_messages]
    qualified_customer: str
    most_recent_ai_response: str
    product_attributes: str
    matching_products: list[Product]
