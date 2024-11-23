from flask import Flask, request, jsonify, render_template, send_file
from validation import RatingInput
import os
import json
from main import calculate_final_rating

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
RESULT_FOLDER = "results"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)


@app.route('/calculate-rating', methods=['POST'])
def calculate_rating():
    try:
        # Валидация JSON через Pydantic
        json_data = request.json
        validated_data = RatingInput(**json_data)

        # Расчет рейтинга
        result = calculate_final_rating(
            data=validated_data.data,
            weights=validated_data.weights,
            value_range=validated_data.value_range
        )

        # Сохранение результата в файл
        result_file = "result.json"
        with open(result_file, "w") as f:
            json.dump({"final_rating": result["final_rating"]}, f, indent=4)

        # Возврат файла
        return send_file(result_file, as_attachment=True)

    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Получить загруженный файл
        uploaded_file = request.files.get("file")
        if uploaded_file:
            file_path = os.path.join(UPLOAD_FOLDER, uploaded_file.filename)
            uploaded_file.save(file_path)

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
            result_file = os.path.join(RESULT_FOLDER, "result.json")
            with open(result_file, "w") as f:
                json.dump(result_json, f, indent=4)

            # Отобразить результат и дать ссылку на скачивание
            return render_template("index.html", result=result_json, download_link="/download/result.json")

    return render_template("index.html")


@app.route("/download/<filename>")
def download_file(filename):
    file_path = os.path.join(RESULT_FOLDER, filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    return "Файл не найден.", 404


if __name__ == "__main__":
    app.run(debug=True)
