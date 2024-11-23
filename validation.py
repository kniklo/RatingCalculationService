from pydantic import BaseModel, Field, model_validator
from typing import List, Dict

class RatingInput(BaseModel):
    data: List[Dict[str, float]] = Field(..., description="Список оценок клиентов за параметры.")
    weights: Dict[str, float] = Field(..., description="Весовые коэффициенты параметров.")
    value_range: Dict[str, float] = Field(..., description="Диапазон значений параметров (min, max).")

    @model_validator(mode="after")
    def validate_weights(self):
        # Проверка суммы весовых коэффициентов
        if not abs(sum(self.weights.values()) - 1) < 1e-6:
            raise ValueError("Сумма весовых коэффициентов должна быть равна 1.")
        return self

    @model_validator(mode="after")
    def validate_value_range(self):
        # Проверка диапазона значений
        if self.value_range["min"] >= self.value_range["max"]:
            raise ValueError("Минимальное значение должно быть меньше максимального.")
        return self
