""" Generic Utility Functions

Utility functions that help access and manipulate responses from the storefront services.
"""
import logging
import json

logger = logging.getLogger(__name__)

def list_of_strings_to_markdown(value):
    """ Convert a comman delimitted list of strings to a markdown list of items.
    
    value - comma delimitted list or list of strings
    """
    logger.info("Converting object to markdown Type<%s> Value=%s", type(value), value)

    markdown = ""
    if value is not None:
        if isinstance(value, list):
            for value_entry in value:
                markdown = markdown + "- " + value_entry + "\n"
        elif isinstance(value, str):
            if len(value) > 0:
                value_list = value.split(",")
                for value_entry in value_list:
                    markdown = markdown + "- " + value_entry + "\n"
        else:
            markdown = "UNKNOWN/UNEXPECTED TYPE - " + str(value)
    return markdown

def object_to_markdown(field, value):
    """ Convert a comman delimitted list of strings to a markdown list of items.
    
    field - field name to extract
    value - comma delimitted list or list of strings
    """
    logger.info("Converting object to markdown Type<%s> Value=%s", type(value), value)

    markdown = ""
    if value is not None and len(value) > 0:
        if isinstance(value, list):
            for value_entry in value:
                markdown = markdown + "- " + value_entry[field] + "\n"
        else:
            markdown = "UNKNOWN/UNEXPECTED TYPE - " + str(value)
    return markdown
