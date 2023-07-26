import openai
import numpy as np

openai.api_key = "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"

DEFAULT_OPENAI_MODEL = "gpt-3.5-turbo"


def openai_embedding(input_text):
    """
    Generates an embedding for a given input text using the OpenAI Embedding API
    The model used for the embedding is text-embedding-ada-002.

    TODO: Add retries, in case they're necessary in the future, by using requests.
    """

    embedding = openai.Embedding.create(
        input=input_text, model="text-embedding-ada-002"
    )["data"][0]["embedding"]
    return embedding



def openai_response(message_content):
    """Generates a response for a given user's message using the OpenAI ChatCompletion API
    The model used for generating the response is gpt-3.5-turbo."""

    messages_to_send = [{"role": "user", "content": message_content}]
    response = openai.ChatCompletion.create(model=DEFAULT_OPENAI_MODEL,
                                            messages=messages_to_send)
    response_text = response["choices"][0]["message"]["content"]
    return response_text


def openai_response_multiple_messages(messages):
    """Similar to openai_response, but it allows for multiple messages to be sent in a conversation format to the OpenAI API."""

    response = openai.ChatCompletion.create(model=DEFAULT_OPENAI_MODEL,
                                            messages=messages)
    response_text = response["choices"][0]["message"]["content"]
    return response_text



def cosine_similarity(a, b):
    """Calculates the cosine similarity between two vectors (of the same length). It is used to compute the similarity between two embeddings."""
    return np.dot(a, b)/(np.linalg.norm(a)*np.linalg.norm(b))