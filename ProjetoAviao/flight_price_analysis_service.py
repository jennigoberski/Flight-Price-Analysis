import base64
import io
import joblib

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def plot_to_base64(plot_func):
    """Helper function to convert plot to base64 for embedding in HTML"""
    img = io.BytesIO()
    plot_func()
    plt.savefig(img, format='png')
    img.seek(0)
    return base64.b64encode(img.getvalue()).decode()


class FlightPriceAnalysisService:
    def __init__(self, file_path):
        self.file_path = file_path
        self.data = self.load_data()
        self.model = joblib.load('flight_price_model.pkl')

    def load_data(self):
        data = pd.read_csv(self.file_path)
        if data.isnull().sum().any():
            data = data.dropna()
        return data

    def plot_price_distribution_by_airline(self):
        def plot():
            plt.figure(figsize=(12, 6))
            sns.stripplot(data=self.data, x='airline', y='price', palette="pastel")
            plt.title("Distribuição de preços de passagens por companhia aérea")
            plt.xlabel("Companhia aérea")
            plt.ylabel("Preço da passagem")
            plt.xticks(rotation=45)

        return plot_to_base64(plot)

    def plot_average_price_by_airline(self):
        def plot():
            mean_prices = self.data.groupby('airline')['price'].mean().sort_values()
            plt.figure(figsize=(10, 5))
            sns.barplot(x=mean_prices.index, y=mean_prices.values, palette="coolwarm")
            plt.title("Preço médio da passagem por companhia aérea")
            plt.xlabel("Companhia aérea")
            plt.ylabel("Preço médio da passagem")
            plt.xticks(rotation=45)

        return plot_to_base64(plot)

    def categorize_booking_window(self):
        self.data['Booking_Window'] = self.data['days_left'].apply(
            lambda x: '1-2 Dias Antes do Voo' if x <= 2 else 'Mais de dois dias'
        )

    def plot_price_comparison_by_booking_window(self):
        self.categorize_booking_window()

        def plot():
            plt.figure(figsize=(10, 6))
            sns.boxplot(data=self.data, x='Booking_Window', y='price', palette="Set2")
            plt.title("Comparação de preços de ingressos por janela de reserva")
            plt.xlabel("Janela de reserva")
            plt.ylabel("Preço da passagem")

        return plot_to_base64(plot)

    def plot_average_price_by_booking_window(self):
        self.categorize_booking_window()

        def plot():
            avg_prices = self.data.groupby('Booking_Window')['price'].mean().sort_values()
            plt.figure(figsize=(8, 5))
            sns.barplot(x=avg_prices.index, y=avg_prices.values, palette="Set1")
            plt.title("Preço médio do bilhete por janela de reserva")
            plt.xlabel("Janela de reserva")
            plt.ylabel("Preço médio da passagem")

        return plot_to_base64(plot)

    def plot_price_by_departure_time(self):
        def plot():
            plt.figure(figsize=(12, 6))
            sns.stripplot(data=self.data, x='departure_time', y='price', palette="muted")
            plt.title("Distribuição do preço dos ingressos por horário de partida")
            plt.xlabel("Hora de partida")
            plt.ylabel("Preço da passagem")

        return plot_to_base64(plot)

    def plot_price_by_arrival_time(self):
        def plot():
            plt.figure(figsize=(12, 6))
            sns.stripplot(data=self.data, x='arrival_time', y='price', palette="pastel")
            plt.title("Distribuição do preço dos ingressos por horário de chegada")
            plt.xlabel("Hora de chegada")
            plt.ylabel("Preço da passagem")

        return plot_to_base64(plot)

    def plot_average_price_by_departure_time(self):
        def plot():
            plt.figure(figsize=(10, 5))
            sns.barplot(data=self.data, x='departure_time', y='price', palette="coolwarm", ci=None)
            plt.title("Preço médio do bilhete por horário de partida")
            plt.xlabel("Hora de partida")
            plt.ylabel("Preço médio da passagem")

        return plot_to_base64(plot)

    def plot_average_price_by_arrival_time(self):
        def plot():
            plt.figure(figsize=(10, 5))
            sns.barplot(data=self.data, x='arrival_time', y='price', palette="coolwarm", ci=None)
            plt.title("Preço médio do bilhete por horário de chegada")
            plt.xlabel("Hora de chegada")
            plt.ylabel("Preço médio da passagem")

        return plot_to_base64(plot)

    def plot_price_by_source_destination(self):
        def plot():
            plt.figure(figsize=(15, 8))
            sns.barplot(data=self.data, x='source_city', y='price', hue='destination_city', palette="viridis",
                        alpha=0.7)
            plt.title("Distribuição do Preço do Bilhete por Cidades de Origem e Destino ")
            plt.xlabel("Cidade de Origem")
            plt.ylabel("Preço do Bilhete")
            plt.legend(title="Cidade de Destino", bbox_to_anchor=(1.05, 1), loc='upper left')
            plt.tight_layout()

        return plot_to_base64(plot)

    def plot_average_price_heatmap(self):
        def plot():
            avg_price = self.data.pivot_table(values='price', index='source_city', columns='destination_city',
                                              aggfunc='mean')
            plt.figure(figsize=(10, 8))
            sns.heatmap(avg_price, annot=True, fmt=".0f", cmap="YlGnBu", cbar_kws={'label': 'Preço Médio'})
            plt.title("Preço Médio do Bilhete por Cidades de Origem e Destino")
            plt.xlabel("Cidade de Destino")
            plt.ylabel("Cidade de Origem")

        return plot_to_base64(plot)

    def plot_price_by_class(self):
        def plot():
            plt.figure(figsize=(10, 6))
            sns.boxplot(data=self.data, x='class', y='price', palette='Set2')
            plt.title("Distribuição do Preço do Bilhete por Classe (Econômica vs. Executiva)")
            plt.xlabel("Classe")
            plt.ylabel("Preço do Bilhete")

        return plot_to_base64(plot)

    def plot_average_price_by_class(self):
        def plot():
            plt.figure(figsize=(8, 6))
            sns.barplot(data=self.data, x='class', y='price', palette='Set2', ci=None)
            plt.title("Preço Médio do Bilhete por Classe (Econômica vs. Executiva)")
            plt.xlabel("Classe")
            plt.ylabel("Preço Médio do Bilhete")

        return plot_to_base64(plot)

    def generate_general_insights(self):
        insights = {
            "Airline": "O preço varia de acordo com a companhia aérea, com algumas oferecendo passagens mais caras.",
            "Booking Window": "Passagens compradas 1-2 dias antes do voo tendem a ser mais caras.",
            "Flight Time": "Os preços dos bilhetes variam de acordo com o horário de partida e chegada, com horários "
                           "de pico geralmente mais caros.",
            "Class": "As passagens da classe executiva são mais caras devido aos serviços premium.",
            "Source and Destination": "Os preços dos bilhetes variam entre cidades de origem e destino, com destinos "
                                      "mais populares e distantes geralmente mais caros."
        }
        insights_df = pd.DataFrame.from_dict(insights, orient='index', columns=['Insight'])
        return insights_df

    def predict_price_service(self, data):
        print("Received data:", data)

        input_data = pd.DataFrame([data])

        required_columns = ['airline', 'departure_time', 'arrival_time', 'source_city',
                            'destination_city', 'stops', 'class', 'days_left']

        input_data = input_data[required_columns]

        input_data['stops'] = input_data['stops'].map({'zero': 0, 'one': 1, 'two_or_more': 2})

        input_data['class'] = input_data['class'].map({'Economy': 0, 'Business': 1})

        input_data_transformed = self.model.named_steps['preprocessor'].transform(input_data)

        predicted_log_price = self.model.named_steps['regressor'].predict(input_data_transformed)[0]

        return predicted_log_price

