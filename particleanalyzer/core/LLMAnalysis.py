import json
from typing import Dict, List, Tuple
import pandas as pd
from huggingface_hub import InferenceClient
from particleanalyzer.core.language_context import LanguageContext
from particleanalyzer.core.languages import translations


class LLMAnalysis:
    def __init__(self, api_key: str):
        self.client = InferenceClient(provider="fireworks-ai", api_key=api_key)
        self.stats: Dict[str, Dict[str, float]] = {}

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
                self._get_translation("Максимум"): row[
                    self._get_translation("Максимум")
                ],
                self._get_translation("Минимум"): row[self._get_translation("Минимум")],
                self._get_translation("Среднее"): row[self._get_translation("Среднее")],
            }
            for _, row in df.iterrows()
        }

    def analyze(self, df: pd.DataFrame) -> List[Tuple[None, str]]:
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
        Ты — эксперт в области материаловедения и сканирующей электронной микроскопии.
        Проведи интерпретацию результатов сегментационного анализа частиц на основе статистических данных.
        В таблице представлены характеристики, полученные методами компьютерного зрения:
        - Геометрические параметры: площадь, периметр, эквивалентный диаметр, диаметр Ферета (min, max, mean)
        - Морфологические параметры: эксцентриситет
        - Ориентация: максимальный угол диаметра Ферета
        При анализе больше обращай внимание на среднее и медианное значение, а не на максимальное и минимальное значение, так туда могут попасть обрезанные частицы.

        🔍 **Сфокусируйся на следующих аспектах:**
        1. **Размерное распределение** — структура распределения, наличие преобладающих фракций, разброс (SD), соотношение Max/Min.
        Обрати внимания что результаты могут быть представлены как в мкм так и в пикселях.
        2. **Морфология** — эксцентриситет, округлость, вытянутость (Dₘₐₓ / Dₘᵢₙ)
        3. **Ориентация частиц** — есть ли выраженное предпочтение в ориентации.

        📋 **Полная таблица данных:**
        {json.dumps(self.stats, indent=2)}

        ✍️ **Сформулируй анализ в следующем формате:**

        🔬 **Микроструктурный анализ**:
        - Размер частиц: <анализ по D, SD, разброс>
        - Форма: <анализ по e, аспектному отношению>
        - Ориентация: <анализ распределения углов>

        🧪 **Материаловедческие выводы**:
        - <влияние морфологии и распределения на свойства материала, возможное происхождение>

        💡 **Рекомендации**:
        - <предложения по улучшению технологии, методы контроля качества, возможные причины аномалий>

        Отвечай на следующем языке {self.lang}
        """

    def _get_llm_response(self, prompt: str):
        """Запрос к языковой модели"""
        return self.client.chat.completions.create(
            model="deepseek-ai/DeepSeek-V3",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,  # Контроль случайности ответов
        )

    def _format_response(self, response) -> List[Tuple[None, str]]:
        analysis = response.choices[0].message.content
        return [(None, analysis)]

    def _get_translation(self, text):
        return translations.get(self.lang, {}).get(text, text)
