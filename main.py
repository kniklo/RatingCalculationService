import json
#
# # Example usage
# data = [
#     {"presentation": 8, "materials": 9, "knowledge": 7, "communication": 10},
#     {"presentation": 7, "materials": 8, "knowledge": 9, "communication": 9},
#     {"presentation": 9, "materials": 7, "knowledge": 8, "communication": 10}
# ]
#
# weights = {
#     "presentation": 0.25,
#     "materials": 0.25,
#     "knowledge": 0.25,
#     "communication": 0.25
# }
#
# value_range = {
#     "min": 1,
#     "max": 10
# }
#
# net_data = {'data': data, 'weights': weights, 'value_range': value_range}
# json_data = json.dumps(net_data)
# вызывается сервис и передается json
# валидируем json
# work = json.loads(json_data)
# work_data = work['data']
# work_weights = work['weights']
# work_value_range = work['value_range']


# Этап 1: Рассчитать средние оценки по каждому параметру
def calculate_averages(data):
    criteria = data[0].keys()
    averages = {criterion: 0 for criterion in criteria}

    for criterion in criteria:
        averages[criterion] = sum(entry[criterion] for entry in data) / len(data)

    return averages


# Этап 2: Нормализация оценок
def normalize_scores(averages, value_range):
    normalized = {}
    min_val = value_range["min"]
    max_val = value_range["max"]

    for criterion, score in averages.items():
        normalized[criterion] = (score - min_val) / (max_val - min_val)

    return normalized


# Этап 3: Взвешенная сумма нормализованных значений
def calculate_weighted_rating(normalized_scores, weights):
    rating = 0
    for criterion, normalized_score in normalized_scores.items():
        rating += weights[criterion] * normalized_score
    return rating


# Этап 4: Денормализация итогового рейтинга
def denormalize_rating(normalized_rating, value_range):
    min_val = value_range["min"]
    max_val = value_range["max"]
    return normalized_rating * (max_val - min_val) + min_val


# Основной расчет
def calculate_final_rating(data, weights, value_range):
    # Шаг 1: Средние оценки
    averages = calculate_averages(data)

    # Шаг 2: Нормализация
    normalized_scores = normalize_scores(averages, value_range)

    # Шаг 3: Взвешенная сумма
    normalized_rating = calculate_weighted_rating(normalized_scores, weights)

    # Шаг 4: Денормализация
    final_rating = denormalize_rating(normalized_rating, value_range)

    return {
        "averages": averages,
        "normalized_scores": normalized_scores,
        "normalized_rating": normalized_rating,
        "final_rating": final_rating
    }


# # Выполнение расчетов
# result = calculate_final_rating(work_data, work_weights, work_value_range)
#
# # Вывод результата
# print(json.dumps(result, indent=4))
# with open("result.json", "w") as f:
#     json.dump(result, f, indent=4)

# Основная точка входа для веб-сервиса
def process_rating_request(json_data):
    try:
        # Загружаем JSON
        work = json.loads(json_data)
        work_data = work['data']
        work_weights = work['weights']
        work_value_range = work['value_range']

        # Выполняем расчет
        result = calculate_final_rating(work_data, work_weights, work_value_range)
        return result
    except KeyError as e:
        return {"error": f"Missing key in JSON: {e}"}

