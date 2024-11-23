from flask import Flask, request, jsonify, render_template, send_file
from validation import RatingInput
import os
import json
from main import calculate_final_rating

import logging

# --- Настройка логгирования ---
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Файловый обработчик
file_handler = logging.FileHandler(
    os.path.join(os.getcwd(), "app.log")
)
file_handler.setLevel(logging.INFO)

# Консольный обработчик
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Форматирование
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Добавление обработчиков
if not logger.hasHandlers():  # Используем более универсальный метод hasHandlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
RESULT_FOLDER = "results"
RESULT_FILE_NAME = "results/result.json"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)


@app.route('/calculate-rating', methods=['POST'])
def calculate_rating():
    logger.info("Запит на розрахунок рейтингу отримано.")
    try:
        # Валидация JSON через Pydantic
        json_data = request.json
        logger.info(f"Отримані дані: {json_data}")
        validated_data = RatingInput(**json_data)
        logger.info("Дані пройшли валідацію.")

        # Расчет рейтинга
        result = calculate_final_rating(
            data=validated_data.data,
            weights=validated_data.weights,
            value_range=validated_data.value_range
        )
        logger.info(f"Результат обчислень: {result}")

        # Сохранение результата в файл
        result_file_path = os.path.join(RESULT_FOLDER, RESULT_FILE_NAME)
        with open(result_file_path, "w") as f:
            json.dump({"final_rating": result["final_rating"]}, f, indent=4)

        logger.info("Відповідь успішно сформована.")
        return send_file(result_file_path, as_attachment=True)

    except Exception as e:
        logger.error(f"Помилка під час розрахунку: {e}")
        return jsonify({"error": "Виникла помилка під час розрахунку рейтингу.", "details": str(e)}), 400

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        try:
            # Получить загруженный файл
            uploaded_file = request.files.get("file")
            if not uploaded_file:
                logger.error("Файл не завантажено.")
                return render_template("index.html", error="Файл не завантажено.")
            if uploaded_file:
                file_path = os.path.join(UPLOAD_FOLDER, uploaded_file.filename)
                uploaded_file.save(file_path)
                logger.info(f"Файл завантажено: {file_path}")

                # Загрузить JSON и выполнить расчет
                with open(file_path, "r") as f:
                    input_data = json.load(f)

                # Выполнить расчет
                work_data = input_data["data"]
                work_weights = input_data["weights"]
                work_value_range = input_data["value_range"]
                result = calculate_final_rating(work_data, work_weights, work_value_range)

                # Сохранить результат в файл
                result_json = {"final_rating": round(result["final_rating"], 2)}
                result_file_path = os.path.join(RESULT_FOLDER, RESULT_FILE_NAME)
                with open(result_file_path, "w") as f:
                    json.dump(result_json, f, indent=4)

                logger.info(f"Результат розрахунку: {result_json}")
                return render_template(
                    "index.html", result=result_json, download_link=f"/download/{RESULT_FILE_NAME}"
                )
        except Exception as e:
            logger.error(f"Помилка під час обробки файлу: {e}")
            return render_template("index.html", error="Помилка під час обробки файлу.")
    return render_template("index.html")

@app.route("/download/<filename>")
def download_file(filename):
    file_path = os.path.join(RESULT_FOLDER, filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    logger.error(f"Файл не знайдено: {filename}")
    return "Файл не знайдено.", 404

if __name__ == "__main__":
    logger.info("Сервіс розрахунку рейтингу запущено.")
    app.run(debug=True, use_reloader=False)
