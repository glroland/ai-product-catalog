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

def is_not_empty_str(s):
    """ Analyzes the variable to ensure it is a non-empty string.
    
        s - string
    """
    if s is None or not isinstance(s, str) or len(s) == 0 or len(s.trim()) == 0:
        return False
    return True

def is_key_similar(primary, secondary):
    """ Analyzes the provided keys and determines if they are similar or a match.
    
        primary - first key
        secondary - second key
    """
    # validate input parameters
    if not is_not_empty_str(primary):
        msg = "is_key_similar() Primary string is invalid or empty!"
        logger.error(msg)
        raise ValueError(msg)
    if not is_not_empty_str(secondary):
        msg = "is_key_similar() Secondary string is invalid or empty!"
        logger.error(msg)
        raise ValueError(msg)

    # trim values and standardize case
    p = primary.trim().lower()
    s = secondary.trim().lower()

    return p == s

def find_approximate_key_for_state(state, variable_name):
    """ Searches the list of keys already in state to find an approximate
        match.  The problem this is solving ties to how LLMs do not always
        obey guidance, so this attempts to find something that is similar.
        
        Initial matches seek to ignore case and whitespace.
        
        state - some type of dict
        variable_name - key
    """
    # validate input
    if state is None or not isinstance(state, dict):
        msg = f"find_approximate_key_for_state() State is null or invalid! T={type(state)}"
        logger.error(msg)
        raise ValueError(msg)

    # get keys
    keys = state.keys()
    if len(keys) == 0:
        logger.warning("find_approximate_key_for_state() No keys in state! Using default.")
        return variable_name

    # work through each key
    for key in keys:
        if is_key_similar(variable_name, key):
            return key

    # No match found, keeping default
    logger.warning("Key not found in state.  Using default...  Key=%s  State=%s",
                   variable_name, state)
    return variable_name

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
        logger.info("Key not in state, using default.   Key=%s  State=%s", variable_name, state)
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
