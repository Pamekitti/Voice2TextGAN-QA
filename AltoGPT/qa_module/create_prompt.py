import tiktoken
import numpy as np
import pandas as pd
from AltoGPT.qa_module.embeddings import get_embedding


"""
2) Find the most similar document embeddings to the question embedding.

So we have split our document library into sections, and encoded them by creating embedding vectors that 
represent each chunk. Next we will use these embeddings to answer our users' questions.

At the time of question-answering, to answer the user's query we compute the query embedding of the question and 
use it to find the most similar document sections. Since this is a small example, we store and search the 
embeddings locally. If you have a larger dataset, consider using a vector search engine like 
[Pinecone](https://www.pinecone.io/) or [Weaviate](https://github.com/semi-technologies/weaviate) to power the search.
"""


def vector_similarity(x: list[float], y: list[float]):
    """
    Returns the similarity between two vectors.

    Because OpenAI Embeddings are normalized to length 1, the cosine similarity is the same as the dot product.
    """
    return np.dot(np.array(x), np.array(y))


def order_document_sections_by_query_similarity(query: str, contexts: dict[(str, str), np.array]) -> list[
    (float, (str, str))]:
    """
    Find the query embedding for the supplied query, and compare it against all of the pre-calculated document embeddings
    to find the most relevant sections.

    Return the list of document sections, sorted by relevance in descending order.
    """
    query_embedding = get_embedding(query)

    document_similarities = sorted([
        (vector_similarity(query_embedding, doc_embedding), doc_index) for doc_index, doc_embedding in contexts.items()
    ], reverse=True)

    return document_similarities


"""
# 3) Add the most relevant document sections to the query prompt.

Once we've calculated the most relevant pieces of context, we construct a prompt by simply prepending them 
to the supplied query. It is helpful to use a query separator to help the model distinguish between separate 
pieces of text.
"""


MAX_SECTION_LEN = 500
SEPARATOR = "\n* "
ENCODING = "cl100k_base"  # encoding for text-embedding-ada-002

encoding = tiktoken.get_encoding(ENCODING)
separator_len = len(encoding.encode(SEPARATOR))


def construct_prompt(question: str, context_embeddings: dict, df: pd.DataFrame, diag=True) -> str:
    """
    Fetch relevant
    """
    most_relevant_document_sections = order_document_sections_by_query_similarity(question, context_embeddings)

    chosen_sections = []
    chosen_sections_len = 0
    chosen_sections_indexes = []

    for _, section_index in most_relevant_document_sections:
        # Add contexts until we run out of space.
        document_section = df.loc[section_index]

        chosen_sections_len += document_section.tokens + separator_len
        if chosen_sections_len > MAX_SECTION_LEN:
            break

        chosen_sections.append(SEPARATOR + document_section.content.replace("\n", " "))
        chosen_sections_indexes.append(str(section_index))

    # Useful diagnostic information
    if diag:
        print(f"Selected {len(chosen_sections)} document sections:")
        print("\n".join(chosen_sections_indexes))

    # header = """Answer the question as truthfully as possible using the provided context, and if the answer is not contained within the text below, say "I don't know."\n\nContext:\n"""
    header = """Answer the question."\n\nContext:\n"""

    return header + "".join(chosen_sections) + "\n\n Q: " + question + "\n A:"