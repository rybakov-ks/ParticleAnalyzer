import json
from typing import Dict, List, Tuple, Literal
import pandas as pd
from openai import OpenAI
from huggingface_hub import InferenceClient
from particleanalyzer.core.language_context import LanguageContext
from particleanalyzer.core.languages import translations


class LLMAnalysis:
    def __init__(
        self,
        api_key: str,
        provider: Literal["openrouter", "huggingface"] = "openrouter",
        huggingface_model: str = "fireworks-ai",
        openrouter_model: str = "deepseek/deepseek-chat:free",
    ):
        self.provider = provider
        self.api_key = api_key
        self.stats: Dict[str, Dict[str, float]] = {}

        if provider == "openrouter":
            self.client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=api_key,
            )
            self.model = openrouter_model
        elif provider == "huggingface":
            self.client = InferenceClient(provider=huggingface_model, api_key=api_key)
            self.model = huggingface_model
        else:
            raise ValueError("Неизвестный провайдер. Доступные варианты: 'openrouter', 'huggingface'")

    def load_data(self, df: pd.DataFrame) -> None:
        required_columns = {
            self._get_translation("Параметр"),
            self._get_translation("Среднее"),
            self._get_translation("Медиана"),
            self._get_translation("Максимум"),
            self._get_translation("Минимум"),
            self._get_translation("Среднее"),
        }
        if not required_columns.issubset(df.columns):
            raise ValueError(f"DataFrame должен содержать колонки: {required_columns}")

        self.stats = {
            row[self._get_translation("Параметр")]: {
                self._get_translation("Среднее"): row[self._get_translation("Среднее")],
                self._get_translation("Медиана"): row[self._get_translation("Медиана")],
                self._get_translation("Максимум"): row[self._get_translation("Максимум")],
                self._get_translation("Минимум"): row[self._get_translation("Минимум")],
                self._get_translation("Среднее"): row[self._get_translation("Среднее")],
            }
            for _, row in df.iterrows()
        }

    def analyze(self, df: pd.DataFrame, count_particles: int) -> List[Tuple[None, str]]:
        self.count_particles = count_particles
        if df.empty:
            return [(None, None)]
        self.lang = LanguageContext.get_language()
        self.load_data(df)
        try:
            prompt = self._build_prompt()
            response = self._get_llm_response(prompt)
            return self._format_response(response)
        except Exception as e:
            print(f"LLM analysis failed: {str(e)}")
            return [(None, None)]

    def _build_prompt(self) -> str:
        return f"""
        Ты — эксперт в области материаловедения и сканирующей электронной микроскопии с 10 летним опытом.
        Проведи интерпретацию изображения СЭМ на основе статистических данных о размерных характеристиках частиц.
        В таблице представлены следующие характеристики:
        - Геометрические параметры: площадь, периметр, эквивалентный диаметр, диаметр Ферета (min, max, mean)
        - Морфологические параметры: эксцентриситет
        - Ориентация: максимальный/минимальный угол диаметра Ферета
        - Средняя интенсивность пикселей частиц
        При анализе больше обращай внимание на среднее и медианное значение, а не на максимальное и минимальное значение, так туда могут попасть обрезанные частицы.

        🔍 **Сфокусируйся на следующих аспектах:**
        1. **Размерное распределение** — структура распределения, наличие преобладающих фракций, разброс (SD), соотношение Max/Min.
        Обрати внимания что результаты могут быть представлены как в мкм так и в пикселях.
        2. **Морфология** — эксцентриситет, округлость, вытянутость (Dₘₐₓ / Dₘᵢₙ)
        3. **Ориентация частиц** — есть ли выраженное предпочтение в ориентации.

        📋 **Полная таблица данных:**
        Всего на изображении обнаружено {self.count_particles} частиц. Со следующими характеристиками:
        {json.dumps(self.stats, indent=2)}

        ✍️ **Сформулируй анализ в следующем формате:**

        🔬 **Микроструктурный анализ**:
        - Размер частиц: <анализ по D, SD, разброс, количество частиц>
        - Форма: <анализ по e, аспектному отношению>
        - Ориентация: <анализ распределения углов>

        🧪 **Материаловедческие выводы**:
        - <влияние морфологии и распределения на свойства материала, возможное происхождение>

        💡 **Рекомендации**:
        - <предложения по улучшению технологии, методы контроля качества, возможные причины аномалий>

        Отвечай на следующем языке {self.lang}
        """

    def _get_llm_response(self, prompt: str):
        """Отправка запроса в зависимости от провайдера"""
        if self.provider == "openrouter":
            completion = self.client.chat.completions.create(
                extra_headers={
                    "HTTP-Referer": "https://sem.rybakov-k.ru/",
                    "X-Title": "ParticleAnalyzer",
                },
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
            )
            return completion
        elif self.provider == "huggingface":
            return self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
            )

    def _format_response(self, response) -> List[Tuple[None, str]]:
        """Форматирование ответа для обоих провайдеров"""
        if self.provider == "openrouter":
            analysis = response.choices[0].message.content
        elif self.provider == "huggingface":
            analysis = response.choices[0].message.content
        return [(None, analysis)]

    def _get_translation(self, text):
        return translations.get(self.lang, {}).get(text, text)