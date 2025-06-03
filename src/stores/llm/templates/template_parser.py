import os

class TemplateParser:

    def __init__(self, language: str = None, default_language = 'english'):
        self.current_path = os.path.dirname(os.path.abspath(__file__))
        self.default_language = default_language
        self.language = None

        self.set_language(language)

    def set_language(self, language: str):

        if not language:
            self.language = self.default_language

        language_path = os.path.join(self.current_path, "locales", language)

        if os.path.exists(language_path):
            self.language = language

        else:
            self.language = self.default_language