import logging
from langchain_core.messages import ToolMessage
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode

logger = logging.getLogger(__name__)

@tool
def get_product_price(sku: str = None) -> float:
    """ Get the price of a product by SKU. """
    logger.info("LLM TOOL INVOKED >>> get_product_price(%s)", sku)

    return 999.99

tools_list = [get_product_price]

# define a tool_node with the available tools
tool_node = ToolNode(tools_list)

def invoke_tools(llm_response, messages):
    """ Invoke outstanding tools as requested by the LLM.
    
        llm_response - LLM response
        messages - message list
    """
    if not llm_response.tool_calls:
        return None

    for tool_call in llm_response.tool_calls:
        selected_tool = {"getproductprice": get_product_price,
                         "get_product_price": get_product_price} [tool_call["name"].lower()]
        tool_output = selected_tool.invoke(tool_call["args"])
        messages.append(ToolMessage(tool_output, tool_call_id=tool_call["id"]))
    
    return messages
