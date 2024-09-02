""" Embedding Utility Functions

Helper functions for token encoding
"""
import logging
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

SENTENCE_TRANSFORMER_MODEL = "sentence-transformers/all-mpnet-base-v2"

def get_model():
    """ Gets the Encoding Model """
    logging.info("Loading Sentence Transformer Model: %s", SENTENCE_TRANSFORMER_MODEL)
    model = SentenceTransformer(SENTENCE_TRANSFORMER_MODEL)
    return model

def create_embedding(text):
    """ Creates an embedding for the specified text.
    
        text - text
    """
    model = get_model()
    embedding_raw = model.encode([text])

    if len(embedding_raw) > 1:
        logger.error ("Embedding has more dimensions than expected!  Data likely being lost.  %s",
                embedding_raw.shape)

    embedding = embedding_raw[0].tolist()
    logger.info ("CREATED Embedding for ....  Text<%s> Embedding<%s>", text, embedding)
    return embedding
