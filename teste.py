import pandas as pd

# Carregar os dados de inflação
inflation_data = pd.read_csv('Forbes-Richest-Athletes\inflation_data.csv')

# Filtrar os dados para os anos de interesse
inflation_1990 = inflation_data[inflation_data['year'] == 1990]['amount'].values[0]
inflation_2022 = inflation_data[inflation_data['year'] == 2022]['amount'].values[0]

# Calcular o valor ajustado
value_1990 = 1  # Valor em 1990
value_2022 = value_1990 * (inflation_2022 / inflation_1990)
print(f"1 dólar em 1990 é equivalente a {value_2022:.2f} dólares em 2022")
