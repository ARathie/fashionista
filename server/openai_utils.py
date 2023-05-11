import openai
import numpy as np

openai.api_key = "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"

DEFAULT_OPENAI_MODEL = "gpt-3.5-turbo-0301"

def openai_embedding(input_text):
    """
    Sends request to OpenAI API to generate an embedding for the user's message.

    TODO: Add retries, in case they're necessary in the future, by using requests.
    """

    embedding = openai.Embedding.create(
        input=input_text, model="text-embedding-ada-002"
    )["data"][0]["embedding"]
    return embedding


def openai_response(message_content):
    messages_to_send = [{"role": "user", "content": message_content}]
    response = openai.ChatCompletion.create(model=DEFAULT_OPENAI_MODEL,
                                            messages=messages_to_send)
    response_text = response["choices"][0]["message"]["content"]
    return response_text


def openai_response_multiple_messages(messages):
    response = openai.ChatCompletion.create(model=DEFAULT_OPENAI_MODEL,
                                            messages=messages)
    response_text = response["choices"][0]["message"]["content"]
    return response_text


def cosine_similarity(a, b):
    """Returns the cosine distance between two vectors of the same length."""
    return np.dot(a, b)/(np.linalg.norm(a)*np.linalg.norm(b))