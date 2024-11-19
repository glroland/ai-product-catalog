""" Utility Functions 
"""
import logging
from pydantic import BaseModel

logger = logging.getLogger(__name__)

def to_json_string(i : BaseModel):
    """ Create a JSON string for the provided pydantic model.
    
        i - model
    """
    return i.model_dump_json(indent=2)

def get_state_value(state, variable_name, default_value):
    """ Gets the provided variable from the state object, along with all
        the error handling needed given that state data could be all over
        the place.
        
        state - some type of dict
        variable_name - key
        default_value - default value
    """
    if variable_name is None or len(variable_name) == 0:
        msg = "A Null or empty variable_name was passed into get_state_value!"
        logger.error(msg)
        raise ValueError(msg)

    if state is None:
        logger.warning("get_state_value() was provided a NULL state value.  Returning default.")
        return default_value

    if variable_name not in state:
        logger.debug("Key not in state, using default.   Key=%s", variable_name)
        return default_value

    return state[variable_name]

def get_state_strlist(state, variable_name):
    """ For the given variable in state, get the results as a list of strings.
    
        state - state/dict
        variable_name - key
    """
    value = get_state_value(state, variable_name, None)
    if value is None:
        logger.debug("None was returned from get_state_value(), returning empty list")
        return []

    if isinstance(value, str):
        logger.debug("Value was string, returning a split str array based on commas.  %s", value)
        return value.split(",")

    if isinstance(value, list):
        logger.debug("Value was a list.  Validating that its only strings.")
        for item in value:
            if not isinstance(item, str):
                msg = f"Encountered list item that was not a string!  Value={item}"
                logger.error(msg)
                raise ValueError(msg)
        return value

    msg = f"Unknown Value Type!  Type={type(value)}"
    logger.error(msg)
    raise ValueError(msg)
