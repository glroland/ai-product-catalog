""" Similarity Search Functionality

Searches the product database for similarity
"""
import os
import logging
from typing import TypedDict, List
import psycopg
from embedding_utils import create_embedding

logger = logging.getLogger(__name__)

ENV_PRODUCT_DB_CONN_STRING = "PRODUCT_DB_CONN_STRING"

DEVTEST_CONNECTION_STRING = "host=localhost port=5432 " \
                            "dbname=ai_product_catalog " + \
                            "user=ai_product_catalog password=ai_product_catalog123 " + \
                            "connect_timeout=30"

class Product(TypedDict):
    """ State structure used throughout the storefront agent process.
    """
    sku: str
    product_name: str
    msrp: float
    cosign_similarity: float

def get_connection_string():
    """ Gets the DB Connection String from config or via defaults """
    connection_string = DEVTEST_CONNECTION_STRING
    if ENV_PRODUCT_DB_CONN_STRING in os.environ:
        connection_string = os.environ[ENV_PRODUCT_DB_CONN_STRING]

    logger.info("Product DB Connection String: %s", connection_string)
    return connection_string

def product_semantic_search(attributes, limit = 3):
    """ Perform a semantic search across products using the provided attributes. 
    
        attributes - attributes to match 
    """
    if len(attributes) == 0:
        msg = "Empty list of attributes passed into semantic search function."
        logger.error(msg)
        raise ValueError(msg)

    sql = """
            SELECT products.product_id,
                   sku, 
                   products.brand_id as brand_id, 
                   product_name, 
                   product_desc, 
                   size, 
                   msrp, 
                   products.category_id as category_id, 
                   embedding <-> CAST(%s as vector) as distance, 
                   1 - (embedding <=> CAST(%s as vector)) as cosign_similarity, 
                   (embedding <#> CAST(%s as vector)) * -1 AS inner_product 
                   FROM products, categories, brands, product_embeddings 
                   WHERE products.category_id = categories.category_id 
                   AND products.brand_id = brands.brand_id 
                   AND product_embeddings.product_id = products.product_id
                   ORDER BY embedding <-> CAST(%s as vector)
                   LIMIT %s
    """

    embedding = create_embedding(attributes)
    values = [ embedding, embedding, embedding, embedding, limit ]

    rows = []
    # pylint: disable=E1129
    with psycopg.connect(get_connection_string()) as db_connection:
        with db_connection.cursor() as c:
            c.execute(sql, values)
            rows = c.fetchall()

    logger.debug("# of similar results returned from query: %s", len(rows))

    matching_products: List[Product] = []
    for row in rows:
        p: Product = {'sku': row[1],
                      'product_name': row[3],
                      'msrp': row[6],
                      'cosign_similarity': row[9]}
        matching_products.append(p)

    logger.info("Matching Products: %s", matching_products)
    return matching_products
