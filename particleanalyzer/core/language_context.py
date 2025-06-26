class LanguageContext:
    _current_lang = "ru"

    @classmethod
    def set_language(cls, lang):
        cls._current_lang = lang

    @classmethod
    def get_language(cls):
        return cls._current_lang
