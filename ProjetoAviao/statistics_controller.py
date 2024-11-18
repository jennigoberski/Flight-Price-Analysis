import locale

import pandas as pd
from flask import Flask, render_template, jsonify, request, redirect, flash, url_for
from flight_price_analysis_service import FlightPriceAnalysisService
import os

app = Flask(__name__)

locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
app.secret_key = 'secret_key'


UPLOAD_FOLDER = 'archive'
ALLOWED_EXTENSIONS = {'csv'}
REQUIRED_COLUMNS = [
    'airline', 'departure_time', 'arrival_time', 'source_city',
    'destination_city', 'stops', 'class', 'days_left'
]

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
file_path = os.path.join(UPLOAD_FOLDER, 'dataset.csv')


def format_currency(value):
    return locale.currency(value, grouping=True)


def allowed_file(filename):
    """Check if the uploaded file has the allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


app.jinja_env.filters['format_currency'] = format_currency

analysis_service = FlightPriceAnalysisService(file_path)

GRAPHIC_PATH = 'static/graphics'
os.makedirs(GRAPHIC_PATH, exist_ok=True)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/statistics/question1', methods=['GET'])
def question1():
    plot_1 = analysis_service.plot_price_distribution_by_airline()
    plot_2 = analysis_service.plot_average_price_by_airline()
    conclusion = "O preço varia de acordo com a companhia aérea, com algumas oferecendo passagens mais caras do que outras."

    return jsonify(
        plot_url_1=plot_1,
        plot_url_2=plot_2,
        conclusion=conclusion
    )


@app.route('/statistics/question2', methods=['GET'])
def question2():
    plot_3 = analysis_service.plot_price_comparison_by_booking_window()
    plot_4 = analysis_service.plot_average_price_by_booking_window()
    conclusion = "O preço das passagens varia conforme a janela de reserva, com preços mais altos sendo encontrados em janelas mais próximas à data de partida."

    return jsonify(
        plot_url_3=plot_3,
        plot_url_4=plot_4,
        conclusion=conclusion
    )


@app.route('/statistics/question3', methods=['GET'])
def statistics_question3():
    plot5 = analysis_service.plot_price_by_departure_time()
    plot6 = analysis_service.plot_average_price_by_departure_time()
    plot7 = analysis_service.plot_price_by_arrival_time()
    plot8 = analysis_service.plot_average_price_by_arrival_time()

    return jsonify({
        'plot_url_5': plot5,
        'plot_url_6': plot6,
        'plot_url_7': plot7,
        'plot_url_8': plot8,
        'conclusion': "O preço das passagens está intimamente relacionado tanto com a hora de partida quanto com a hora de chegada. Variações significativas podem ser observadas com base nesses horários."
    })


@app.route('/statistics/question4', methods=['GET'])
def question4():
    plot_9 = analysis_service.plot_price_by_source_destination()
    plot_10 = analysis_service.plot_average_price_heatmap()

    return jsonify({
        'plot_url_9': plot_9,
        'plot_url_10': plot_10,
        'conclusion': "A análise mostra como os preços variam de acordo com a cidade de origem e destino, tanto em termos de distribuição quanto de preço médio."
    })


@app.route('/statistics/question5', methods=['GET'])
def get_question5_data():
    plot_url_11 = analysis_service.plot_price_by_class()
    plot_url_12 = analysis_service.plot_average_price_by_class()

    return jsonify({
        'plot_url_11': plot_url_11,
        'plot_url_12': plot_url_12,
        'conclusion': "A análise mostra a variação do preço dos bilhetes entre as classes econômica e executiva. Os gráficos indicam que os preços na classe executiva são consideravelmente mais altos que na classe econômica."
    })


@app.route('/statistics/summary', methods=['GET'])
def summary():
    insights_df = analysis_service.generate_general_insights()
    insights_json = insights_df.to_dict(orient='index')

    return jsonify(insights_json)


@app.route('/sobre')
def sobre():
    return render_template('sobre.html')


@app.route('/estatisticas')
def estatisticas():
    return render_template('estatisticas.html')


@app.route('/upload-page')
def upload():
    return render_template('upload.html')


@app.route('/simulacao')
def simulacao():
    df = pd.read_csv(file_path)

    airlines = df['airline'].unique().tolist()
    departure_times = df['departure_time'].unique().tolist()
    arrival_times = df['arrival_time'].unique().tolist()
    stops = df['stops'].unique().tolist()
    cities = df['source_city'].unique().tolist()
    classes = df['class'].unique().tolist()

    return render_template('simulacao.html', airlines=airlines, departure_times=departure_times,
                           arrival_times=arrival_times, stops=stops, cities=cities, classes=classes)


@app.route('/predict_price', methods=['POST'])
def predict_price():
    form_data = {
        "airline": request.form.get("airline"),
        "departure_time": request.form.get("departure_time"),
        "arrival_time": request.form.get("arrival_time"),
        "source_city": request.form.get("source_city"),
        "destination_city": request.form.get("destination_city"),
        "stops": request.form.get("stops"),
        "class": request.form.get("class"),
        "days_left": int(request.form.get("days_left"))
    }

    predicted_price = analysis_service.predict_price_service(form_data)
    formatted_price = locale.currency(predicted_price, grouping=True)
    return jsonify({'predicted_price': formatted_price})


@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part in the request')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('Nenhum arquivo selecionado!')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            temp_path = os.path.join(UPLOAD_FOLDER, 'temp_dataset.csv')
            file.save(temp_path)
            try:
                df = pd.read_csv(temp_path)
                if all(column in df.columns for column in REQUIRED_COLUMNS):
                    os.rename(temp_path, file_path)
                    flash('Upload realizado com sucesso!', 'success')
                    return redirect(url_for('upload_file'))
                else:
                    flash(
                        f"Dataset não tem as colunas necessárias: {', '.join(REQUIRED_COLUMNS)}",
                        'error'
                    )
            except Exception as e:
                flash(f"Um erro ocorreu na leitura do dataset: {e}", 'error')
            finally:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
        else:
            flash('Por favor, utilize somente arquivos .csv.', 'error')
    return render_template('upload.html')


if __name__ == '__main__':
    app.run(debug=True)
