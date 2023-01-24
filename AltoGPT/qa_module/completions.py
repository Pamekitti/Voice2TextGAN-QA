import openai
from config import completion_gpt3, api
from AltoGPT.qa_module.create_prompt import *

openai.api_key = api.open_ai_api
COMPLETIONS_MODEL = completion_gpt3.id

COMPLETIONS_API_PARAMS = {
    # We use temperature of 0.0 because it gives the most predictable, factual answer.
    "temperature": 0.5,
    "max_tokens": 200,
    "model": COMPLETIONS_MODEL,
}


def answer_query_with_context(
        query: str,
        df: pd.DataFrame,
        document_embeddings: dict[(str, str), np.array],
        show_prompt: bool = False,
        diag: bool = False,
) -> str:
    prompt = construct_prompt(
        query,
        document_embeddings,
        df,
        diag=diag
    )

    if show_prompt:
        print(prompt)

    response = openai.Completion.create(
        prompt=prompt,
        **COMPLETIONS_API_PARAMS
    )

    return response["choices"][0]["text"].strip(" \n")
