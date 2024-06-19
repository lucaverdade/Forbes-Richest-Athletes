import pandas as pd
import streamlit as st
import plotly.express as px
from streamlit_folium import folium_static
import folium
import json

# Configuração da página
st.set_page_config(page_title="Análise dos Salários dos Atletas", layout="wide")

st.title("Análise dos Salários dos Atletas e o Poder de Compra do Dólar")

# Carregar os dados dos atletas
df_atletas = pd.read_csv('Atletas mais bem pagos.csv')
# Carregar os dados do poder de compra do dólar
dollar_df = pd.read_csv('inflation_data.csv')

# Ajustar os nomes das colunas
df_atletas = df_atletas.rename(columns={'Year': 'Ano', 'earnings ($ million)': 'Ganhos'})

# Combinar os esportes
df_atletas['Sport'] = df_atletas['Sport'].replace({
    'NFL': 'American Football',
    'America football': 'American Football',
    'NBA': 'Basketball',
    'soccer': 'Soccer',
    'basketball': 'Basketball',
    'Auto racing': 'Auto Racing',
    'Auto Racing': 'Auto Racing',
    'Auto Racing (Nascar)': 'Auto Racing',
    'auto racing': 'Auto Racing',
    'F1 Motorsports': 'Auto Racing',
    'F1 racing': 'Auto Racing',
    'boxing': 'Boxing',
    'golf': 'Golf',
    'ice hockey': 'Ice Hockey',
    'tennis': 'Tennis',
})

# Ajustar os salários dos atletas com base no valor do dólar
df_atletas['Ano'] = df_atletas['Ano'].astype(int)
dollar_df['year'] = dollar_df['year'].astype(int)

# Criar um dicionário para mapear o valor acumulado para cada ano
inflation_dict = dollar_df.set_index('year')['amount'].to_dict()

# Obter o valor acumulado atual (último valor da coluna 'amount')
current_inflation_value = inflation_dict[max(inflation_dict.keys())]

# Adicionar a inflação acumulada correspondente ao ano de cada registro de atleta
df_atletas['Inflation Amount'] = df_atletas['Ano'].apply(lambda x: inflation_dict.get(x, current_inflation_value))

# Calcular o salário ajustado considerando a inflação acumulada
df_atletas['Salario Ajustado'] = df_atletas['Ganhos'] * (current_inflation_value / df_atletas['Inflation Amount'])

# Carregar os dados do mapa
with open('world-countries.json', 'r', encoding='latin-1') as f:
    data = json.load(f)

# Definir a página inicial
page = st.sidebar.selectbox("Escolha a página", ["Home", "Gráficos", "Análise Ajustada", "Explicações e Análises"], key='page_select')

if page == "Home":
    st.title("🏅 Dashboard de Ganhos de Atletas 🏅")
    st.markdown(
        """
        ### Bem-vindo ao nosso Dashboard de Ganhos de Atletas!
        
        Explore os dados dos atletas mais bem pagos ao longo dos anos e veja como seus ganhos se comparam ao poder de compra do dólar.
        """
    )

    st.image("AtletasRicosAnalise.jpg", use_column_width=True)

    st.title("🏆 Quiz: Descubra os Fatos Sobre os Ganhos dos Atletas! 🏆")
    st.write("Tente adivinhar as respostas para os seguintes fatos sobre os ganhos dos atletas!")

    # Pergunta 1: Qual foi o esporte que mais rendeu dinheiro na história (ajustado)?
    top_esporte_ajustado = df_atletas.groupby('Sport')['Salario Ajustado'].sum().idxmax()
    esportes_opcoes_ajustado = list(df_atletas['Sport'].unique())
    esportes_opcoes_ajustado.remove(top_esporte_ajustado)
    esportes_opcoes_ajustado = [top_esporte_ajustado] + esportes_opcoes_ajustado[:4]
    esportes_opcoes_ajustado = sorted(esportes_opcoes_ajustado)

    resposta_usuario1 = st.radio("Qual foi o esporte que mais rendeu dinheiro na história (ajustado)?", esportes_opcoes_ajustado, key='quiz1')

    if st.button("Verificar Resposta 1"):
        if resposta_usuario1 == top_esporte_ajustado:
            st.success(f"🎉 Correto! {top_esporte_ajustado} foi o esporte que mais rendeu dinheiro na história (ajustado).")
        else:
            st.error(f"❌ Errado! {top_esporte_ajustado} foi o esporte que mais rendeu dinheiro na história (ajustado).")

    # Pergunta 2: Qual a nacionalidade que mais fez dinheiro (ajustado)?
    top_nacionalidade_ajustado = df_atletas.groupby('Nationality')['Salario Ajustado'].sum().idxmax()
    nacionalidades_opcoes_ajustado = list(df_atletas['Nationality'].unique())
    nacionalidades_opcoes_ajustado.remove(top_nacionalidade_ajustado)
    nacionalidades_opcoes_ajustado = [top_nacionalidade_ajustado] + nacionalidades_opcoes_ajustado[:4]
    nacionalidades_opcoes_ajustado = sorted(nacionalidades_opcoes_ajustado)

    resposta_usuario2 = st.radio("Qual a nacionalidade que mais fez dinheiro (ajustado)?", nacionalidades_opcoes_ajustado, key='quiz2')

    if st.button("Verificar Resposta 2"):
        if resposta_usuario2 == top_nacionalidade_ajustado:
            st.success(f"🎉 Correto! {top_nacionalidade_ajustado} foi a nacionalidade que mais fez dinheiro (ajustado).")
        else:
            st.error(f"❌ Errado! {top_nacionalidade_ajustado} foi a nacionalidade que mais fez dinheiro (ajustado).")

    # Pergunta 3: Qual atleta foi o mais bem pago em um determinado ano?
    selected_year = st.selectbox("Escolha o ano", sorted(df_atletas['Ano'].unique()), key='quiz_year_select')
    top_atleta_ano = df_atletas[df_atletas['Ano'] == selected_year].sort_values(by='Salario Ajustado', ascending=False).iloc[0]['Name']
    atletas_opcoes_ano = list(df_atletas[df_atletas['Ano'] == selected_year]['Name'].unique())
    atletas_opcoes_ano.remove(top_atleta_ano)
    atletas_opcoes_ano = [top_atleta_ano] + atletas_opcoes_ano[:4]
    atletas_opcoes_ano = sorted(atletas_opcoes_ano)

    resposta_usuario3 = st.radio(f"Quem foi o atleta mais bem pago em {selected_year}?", atletas_opcoes_ano, key='quiz3')

    if st.button("Verificar Resposta 3"):
        if resposta_usuario3 == top_atleta_ano:
            st.success(f"🎉 Correto! {top_atleta_ano} foi o atleta mais bem pago em {selected_year}.")
        else:
            st.error(f"❌ Errado! {top_atleta_ano} foi o atleta mais bem pago em {selected_year}.")

    # Pergunta 4: Qual esporte teve o maior crescimento em ganhos ao longo dos anos?
    growth_by_sport = df_atletas.groupby('Sport')['Salario Ajustado'].sum().pct_change().fillna(0).idxmax()
    esportes_opcoes_growth = list(df_atletas['Sport'].unique())
    esportes_opcoes_growth.remove(growth_by_sport)
    esportes_opcoes_growth = [growth_by_sport] + esportes_opcoes_growth[:4]
    esportes_opcoes_growth = sorted(esportes_opcoes_growth)

    resposta_usuario4 = st.radio("Qual esporte teve o maior crescimento em ganhos ao longo dos anos?", esportes_opcoes_growth, key='quiz4')

    if st.button("Verificar Resposta 4"):
        if resposta_usuario4 == growth_by_sport:
            st.success(f"🎉 Correto! {growth_by_sport} foi o esporte que teve o maior crescimento em ganhos ao longo dos anos.")
        else:
            st.error(f"❌ Errado! {top_atleta_ano} foi o atleta mais bem pago em {selected_year}.")

elif page == "Gráficos":
    # Filtrar por ano
    selected_years = st.sidebar.multiselect("Escolha o(s) ano(s)", sorted(df_atletas["Ano"].unique()), key='year_select')

    # Filtrar os dados pelos anos selecionados
    filtered_df = df_atletas[df_atletas["Ano"].isin(selected_years)]

    st.title("📊 Visualizações de Ganhos de Atletas 📊")

    # Verificar se pelo menos um ano foi selecionado
    if selected_years:
        col1, col2 = st.columns(2)

        with col1:
            # Gráfico 1: Ganhos totais por ano
            total_earnings_by_year = filtered_df.groupby("Ano")["Ganhos"].sum().reset_index()
            fig1 = px.line(total_earnings_by_year, x="Ano", y="Ganhos", title="Ganhos Totais por Ano",
                          
