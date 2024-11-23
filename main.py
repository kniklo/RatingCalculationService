import json
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Этап 1: Рассчитать средние оценки по каждому параметру
def calculate_averages(data):
    logging.info("Starting calculation of averages...")
    criteria = data[0].keys()
    averages = {criterion: 0 for criterion in criteria}

    for criterion in criteria:
        averages[criterion] = sum(entry[criterion] for entry in data) / len(data)
        logging.info(f"Average for {criterion}: {averages[criterion]}")

    logging.info(f"Calculated averages: {averages}")
    return averages


# Этап 2: Нормализация оценок
def normalize_scores(averages, value_range):
    logging.info("Starting normalization of scores...")
    normalized = {}
    min_val = value_range["min"]
    max_val = value_range["max"]

    for criterion, score in averages.items():
        normalized[criterion] = (score - min_val) / (max_val - min_val)
        logging.info(f"Normalized score for {criterion}: {normalized[criterion]}")

    logging.info(f"Normalized scores: {normalized}")
    return normalized


# Этап 3: Взвешенная сумма нормализованных значений
def calculate_weighted_rating(normalized_scores, weights):
    logging.info("Starting weighted rating calculation...")
    rating = 0
    for criterion, normalized_score in normalized_scores.items():
        rating += weights[criterion] * normalized_score

    logging.info(f"Calculated weighted rating (normalized): {rating}")
    return rating


# Этап 4: Денормализация итогового рейтинга
def denormalize_rating(normalized_rating, value_range):
    logging.info("Starting denormalization of the final rating...")
    min_val = value_range["min"]
    max_val = value_range["max"]
    denormalized_rating = normalized_rating * (max_val - min_val) + min_val
    logging.info(f"Denormalized final rating: {denormalized_rating}")
    return denormalized_rating


# Основной расчет
def calculate_final_rating(data, weights, value_range):
    logging.info("Starting final rating calculation...")

    # Шаг 1: Средние оценки
    averages = calculate_averages(data)

    # Шаг 2: Нормализация
    normalized_scores = normalize_scores(averages, value_range)

    # Шаг 3: Взвешенная сумма
    normalized_rating = calculate_weighted_rating(normalized_scores, weights)

    # Шаг 4: Денормализация
    final_rating = denormalize_rating(normalized_rating, value_range)

    logging.info("Final rating calculation completed.")
    return {
        "averages": averages,
        "normalized_scores": normalized_scores,
        "normalized_rating": normalized_rating,
        "final_rating": final_rating
    }

def process_rating_request(json_data):
    try:
        logging.info("Processing rating request...")
        # Загружаем JSON
        work = json.loads(json_data)
        work_data = work['data']
        work_weights = work['weights']
        work_value_range = work['value_range']

        # Выполняем расчет
        result = calculate_final_rating(work_data, work_weights, work_value_range)
        logging.info("Rating request processed successfully.")
        return result
    except KeyError as e:
        logging.error(f"Missing key in JSON: {e}")
        return {"error": f"Missing key in JSON: {e}"}
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        return {"error": str(e)}

