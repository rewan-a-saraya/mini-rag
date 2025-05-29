from abc import ABC

from ..LLMInterface import LLMInterface
from src.stores.llm.LLMEnums import CoHereEnums
import cohere
import logging

class CoHereProvider(LLMInterface, ABC):

    def __init__(self, api_key: str,
                 default_input_max_characters: int = 1000,
                 default_generation_max_output_tokens: int = 1000,
                 default_generation_temperature: float = 0.1):

        self.api_key = api_key

        self.default_input_max_characters = default_input_max_characters
        self.default_generation_max_output_tokens = default_generation_max_output_tokens
        self.default_generation_temperature = default_generation_temperature

        self.generation_model_id = None

        self.embedding_model_id = None
        self.embedding_size = None

        self.client = cohere.Client(api_key= self.api_key)

        self.logger = logging.getLogger(__name__)

        def set_generation_model(self, model_id: str):
            self.generation_model_id = model_id

        def set_embedding_model(self, model_id: str, embedding_size: int):
            self.embedding_model_id = model_id
            self.embedding_size = embedding_size

        def process_text(self, text: str):
            return text[: self.default_input_max_characters].strip()

