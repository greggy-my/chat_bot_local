from transformers import pipeline
from langchain.llms import Ollama
from langchain.callbacks.manager import CallbackManager, AsyncCallbackManagerForLLMRun
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
import requests
import subprocess
import json
import httpx
import json
import asyncio
import re
import time


def timing_decorator(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"{func.__name__} took {elapsed_time:.6f} seconds to execute.")
        return result

    return wrapper


def async_timing_decorator(func):
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        result = await func(*args, **kwargs)
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"{func.__name__} took {elapsed_time:.6f} seconds to execute.")
        return result

    return wrapper


def embed_text(text: list[str]) -> list[list]:
    embedding_function = pipeline("feature-extraction", model="ai-forever/sbert_large_nlu_ru")
    embeddings = embedding_function(text)
    embeddings_parsed = [item[0][0] for item in embeddings]
    return embeddings_parsed


def validate_response(response: requests.Response):
    if isinstance(response, httpx.Response):
        if response.status_code == 200:
            print("HTTP response is valid.")
            return True
        else:
            print(f"Invalid HTTP response. Status Code: {response.status_code}\n {response.text}")
            return False
    else:
        print("Invalid response. Expected an instance of requests.Response.")
        return False


class Models:
    def __init__(self):
        self.models_urls = {"get": {"list": "http://localhost:11434/api/tags"},
                            "post": {"generate": "http://localhost:11434/api/generate"}}
        self.__initiate_connection()

    @staticmethod
    def __initiate_connection() -> None:
        bash_command = "ollama serve"
        try:
            subprocess.run(bash_command, shell=True, check=True)
            print("Ollama is serving.")
        except subprocess.CalledProcessError as e:
            print(f"Error during ollama initialisation: {e}")

    async def get_list_models(self) -> None:
        async with httpx.AsyncClient() as client:
            response = await client.get(url=self.models_urls["get"]["list"])
            if validate_response(response=response):
                all_models = [model["name"] for model in json.loads(response.text)["models"]]
                print(all_models)

    async def generate_response(self, model: str, prompt: str) -> str:
        async with httpx.AsyncClient() as client:
            json_data = json.dumps({"model": model, "prompt": prompt, "stream": False})
            response = await client.post(url=self.models_urls["post"]["generate"],
                                         data=json_data, timeout=30)
            if validate_response(response=response):
                model_answer = json.loads(response.text)["response"]
                return model_answer


# @async_timing_decorator
# async def a_main():
#     models = Models()
#
#     # await models.get_list_models()
#
#     model_answer_1 = await models.generate_response(model="llama2:latest", prompt="Как твои дела?")
#     print(model_answer_1)
#     model_answer_2 = await models.generate_response(model="llama2:latest", prompt="Как твои дела?")
#     print(model_answer_2)
#     model_answer_3 = await models.generate_response(model="llama2:latest", prompt="Как твои дела?")
#     print(model_answer_3)
#     model_answer_4 = await models.generate_response(model="llama2:latest", prompt="Как твои дела?")
#     print(model_answer_4)
#
# asyncio.run(a_main())


@timing_decorator
def run_in_line():
    data = {
        "model": "llama2:latest",
        "prompt": "Как твои дела?",
        "stream": False
    }
    response = requests.post("http://localhost:11434/api/generate", data=json.dumps(data))
    model_answer_1 = json.loads(response.text)["response"]
    print(model_answer_1)

    response = requests.post("http://localhost:11434/api/generate", data=json.dumps(data))
    model_answer_2 = json.loads(response.text)["response"]
    print(model_answer_2)

    response = requests.post("http://localhost:11434/api/generate", data=json.dumps(data))
    model_answer_3 = json.loads(response.text)["response"]
    print(model_answer_3)

    response = requests.post("http://localhost:11434/api/generate", data=json.dumps(data))
    model_answer_4 = json.loads(response.text)["response"]
    print(model_answer_4)


run_in_line()

