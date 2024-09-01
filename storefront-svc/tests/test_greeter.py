""" Unit Tests for the Customer Greeter

Verify that the greeter functionality works as intended. 
"""
import logging
import customer_greeter as g

logger = logging.getLogger(__name__)


def test_reject_due_to_unrelated_products():
    """ Attempt to buy something other than shoes at the shoe store """
    logger.debug("test_reject_due_to_unrelated_products()")

    user_input = "What kind of video games do you sell?"

    assert g.qualify_customer_action(user_input) is False


def test_reject_due_to_unrelated_to_retail_store():
    """ Ask question about something completely unrelated to retail """
    logger.debug("test_reject_due_to_unrelated_to_retail_store()")

    user_input = "Who was the first person to walk on the moon?"

    assert g.qualify_customer_action(user_input) is False


def test_accept_interested_in_nike_shoes():
    """ Ensure customer is qualified positively """
    logger.debug("test_accept_interested_in_nike_shoes()")

    user_input = "I need a new pair of tennis shoes for my teenage son starting school next week."

    assert g.qualify_customer_action(user_input) is True
