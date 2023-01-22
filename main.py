from AltoGPT.completions import answer_query_with_context
from AltoGPT.embeddings import compute_doc_embeddings, preprocess_for_embeddings
import pickle

df = preprocess_for_embeddings()

EMBEDDING_REQUIRED = False
if EMBEDDING_REQUIRED:
    # Compute document embeddings
    document_embeddings = compute_doc_embeddings(df)
    # Save document embeddings
    with open('AltoGPT/assets/embedded-data/document_embeddings.pickle', 'wb') as handle:
        pickle.dump(document_embeddings, handle, protocol=pickle.HIGHEST_PROTOCOL)

else:
    with open('AltoGPT/assets/embedded-data/document_embeddings.pickle', 'rb') as handle:
        document_embeddings = pickle.load(handle)

"""
the Completions API is used to answer the user's query.
"""

query = "In pump system, head and flow rate is reverse proportional?"
answer = answer_query_with_context(query, df, document_embeddings, diag=False)
print(f"\nQ: {query}\nA: {answer}")