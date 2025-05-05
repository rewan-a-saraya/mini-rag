from ..LLMInterface import LLMInterface
from src.stores.llm import LLMInterface
from openai import OpenAI

class OpenAIProvider(LLMInterface):

    def __init__(self, api_key: str, api_url:str = None,
                       default_input_max_characters: int=1000,
                       default_generation_max_output_characters: int=1000,
                       default_generation_temperature: float=0.1 ):

        self.api_key = api_key
        self.api_url = api_url

        self.default_input_max_characters = default_input_max_characters
        self.default_generation_max_output_characters = default_generation_max_output_characters
        self.default_generation_temperature = default_generation_temperature

