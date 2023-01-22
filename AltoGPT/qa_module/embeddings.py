import openai
import pandas as pd
import numpy as np
from numpy import ndarray
import tiktoken

from config import completion_gpt3, embeddings_ada2

COMPLETIONS_MODEL = completion_gpt3.id
EMBEDDING_MODEL = embeddings_ada2.id

# Preprocess knowledge base in CSV format
def read_csv(path):
    df = pd.read_csv(path)
    df = df.set_index(["title", "heading"])
    return df


def preprocess_for_embeddings():
    csv_path = [
        "AltoGPT/assets/csq-data/csq_knowledge_base.csv",
        "AltoGPT/assets/csq-data/chiller_knowledge_base.csv",
    ]

    df = pd.concat([read_csv(path) for path in csv_path])
    df['tokens'] = df.content.str.replace(',', '').str.split().str.len()
    return df


"""
1) Preprocess the document library

We preprocess the document sections by creating an embedding vector for each section. An embedding is a 
vector of numbers that helps us understand how semantically similar or different the texts are. The closer 
two embeddings are to each other, the more similar are their contents. See the [documentation on OpenAI 
embeddings](https://beta.openai.com/docs/guides/embeddings) for more information.

This indexing stage can be executed offline and only runs once to precompute the indexes for the dataset 
so that each piece of content can be retrieved later. Since this is a small example, we will store and 
search the embeddings locally. If you have a larger dataset, consider using a vector search engine like 
[Pinecone](https://www.pinecone.io/) or [Weaviate](https://github.com/semi-technologies/weaviate) to power 
the search.

For the purposes of this tutorial we chose to use Curie embeddings, which are 4096-dimensional embeddings 
at a very good price and performance point. Since we will be using these embeddings for retrieval, we’ll 
use the "search" embeddings (see the [documentation](https://beta.openai.com/docs/guides/embeddings)).
"""


def get_embedding(text: str, model: str = EMBEDDING_MODEL) -> list[float]:
    result = openai.Embedding.create(
        model=model,
        input=text
    )
    return result["data"][0]["embedding"]


def compute_doc_embeddings(df: pd.DataFrame) -> dict[tuple[str, str], list[float]]:
    """
    Create an embedding for each row in the dataframe using the OpenAI Embeddings API.

    Return a dictionary that maps between each embedding vector and the index of the row that it corresponds to.
    """
    return {
        idx: get_embedding(r.content) for idx, r in df.iterrows()
    }


def load_embeddings(fname: str) -> dict[tuple[str, str], list[float]]:
    """
    Read the document embeddings and their keys from a CSV.

    fname is the path to a CSV with exactly these named columns:
        "title", "heading", "0", "1", ... up to the length of the embedding vectors.

    You may use
    document_embeddings = load_embeddings("fine-tuned_qa/olympics-data/olympics_sections_document_embeddings.csv")
    """

    df = pd.read_csv(fname, header=0)
    max_dim = max([int(c) for c in df.columns if c != "title" and c != "heading"])
    return {
        (r.title, r.heading): [r[str(i)] for i in range(max_dim + 1)] for _, r in df.iterrows()
    }




