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
    'Nascar': 'Auto Racing',
    'basketball': 'Basketball',
    'Auto racing': 'Auto Racing',
    'Auto Racing': 'Auto Racing',
    'Auto Racing (Nascar)': 'Auto Racing',
    'auto racing': 'Auto Racing',
    'boxing': 'Boxing',
    'golf': 'Golf',
    'F1 Motorsports': 'Auto Racing',
    'F1 racing': 'Auto Racing',
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

    # Pergunta 2: Qual a nacionalidade que mais fez dinheiro?
    top_nacionalidade_ajustado = df_atletas.groupby('Nationality')['Salario Ajustado'].sum().idxmax()
    nacionalidades_opcoes_ajustado = list(df_atletas['Nationality'].unique())
    nacionalidades_opcoes_ajustado.remove(top_nacionalidade_ajustado)
    nacionalidades_opcoes_ajustado = [top_nacionalidade_ajustado] + nacionalidades_opcoes_ajustado[:4]
    nacionalidades_opcoes_ajustado = sorted(nacionalidades_opcoes_ajustado)

    resposta_usuario2 = st.radio("Qual a nacionalidade que mais fez dinheiro?", nacionalidades_opcoes_ajustado, key='quiz2')

    if st.button("Verificar Resposta 2"):
        if resposta_usuario2 == top_nacionalidade_ajustado:
            st.success(f"🎉 Correto! {top_nacionalidade_ajustado} foi a nacionalidade que mais fez dinheiro.")
        else:
            st.error(f"❌ Errado! {top_nacionalidade_ajustado} foi a nacionalidade que mais fez dinheiro.")

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
                           labels={"Ano": "Ano", "Ganhos": "Ganhos ($ milhões)"},
                                                      template="plotly_dark", color_discrete_sequence=["#FF6347"])
            st.write("**Ganhos Totais por Ano:** Este gráfico mostra a tendência dos ganhos totais de atletas ao longo dos anos. (Selecione mais de um ano para ver a tendência)")
            st.plotly_chart(fig1, use_container_width=True)

        with col2:
            # Gráfico 2: Ganhos totais por esporte
            total_earnings_by_sport = filtered_df.groupby("Sport")["Ganhos"].sum().reset_index()
            fig2 = px.bar(total_earnings_by_sport, x="Sport", y="Ganhos", title="Ganhos Totais por Esporte",
                          labels={"Sport": "Esporte", "Ganhos": "Ganhos ($ milhões)"},
                          template="plotly_dark", color_discrete_sequence=["#FF6347"])
            st.write("**Ganhos Totais por Esporte:** Este gráfico mostra os ganhos totais de atletas em cada modalidade esportiva.")
            st.plotly_chart(fig2, use_container_width=True)

        col3, col4 = st.columns(2)

        with col3:
            # Gráfico 3: Ganhos por atleta no ano
            fig3 = px.bar(filtered_df, x="Name", y="Ganhos", title="Ganhos por Atleta no Ano",
                          labels={"Name": "Atleta", "Ganhos": "Ganhos ($ milhões)"},
                          template="plotly_dark", color_discrete_sequence=["#FF6347"])
            st.write("**Ganhos por Atleta no Ano:** Este gráfico mostra os ganhos de cada atleta no ano selecionado.")
            st.plotly_chart(fig3, use_container_width=True)

        with col4:
            # Gráfico 4: Mapa de distribuição de ganhos por nacionalidade
            st.subheader("Distribuição de Ganhos por Nacionalidade")

            # Calcular os ganhos totais por nacionalidade
            total_earnings_by_country = filtered_df.groupby("Nationality")["Ganhos"].sum().reset_index()

            # Criar o mapa com folium
            m = folium.Map(location=[0, 0], zoom_start=2)

            # Adicionar o choropleth layer ao mapa com cores personalizadas
            folium.Choropleth(
                geo_data=data,
                name="choropleth",
                data=total_earnings_by_country,
                columns=["Nationality", "Ganhos"],
                key_on="feature.properties.name",
                fill_color="YlOrRd",
                fill_opacity=0.7,
                line_opacity=0.2,
                legend_name="Ganhos ($ milhões)",
            ).add_to(m)

            # Exibir o mapa
            folium_static(m)

    else:
        st.write("Por favor, selecione pelo menos um ano.")

elif page == "Análise Ajustada":
    # Selecionar os atletas
    atletas_selecionados = st.sidebar.multiselect(
        "Selecione os Atletas",
        options=df_atletas['Name'].unique(),
        default=list(df_atletas.groupby('Name')['Salario Ajustado'].sum().nlargest(20).index),
        key='atletas_select'
    )

    # Selecionar o intervalo de anos
    anos = st.sidebar.slider(
        'Selecione o Intervalo de Anos',
        min_value=int(df_atletas['Ano'].min()),
        max_value=int(df_atletas['Ano'].max()),
        value=(int(df_atletas['Ano'].min()), int(df_atletas['Ano'].max())),
        key='anos_select'
    )

    # Filtrar os dados
    df_filtrado = df_atletas[(df_atletas['Name'].isin(atletas_selecionados)) & (df_atletas['Ano'] >= anos[0]) & (df_atletas['Ano'] <= anos[1])]

    st.title("📈 Análise Ajustada dos Ganhos dos Atletas 📈")

   

    # Gráfico 2: Salário Ajustado dos Top 10 Atletas
    top_10_atletas = df_filtrado.groupby('Name')['Salario Ajustado'].sum().nlargest(10).reset_index()
    fig2 = px.bar(top_10_atletas, x='Name', y='Salario Ajustado', title='Ganhos totais dos atletas corrigidos para o ano Selecionado',
                  labels={"Name": "Atleta", "Salario Ajustado": "Salário Ajustado ($ milhões)"},
                  template="plotly_dark", color_discrete_sequence=px.colors.qualitative.Pastel)
    st.plotly_chart(fig2, use_container_width=True)

    # Gráfico 2: Ganhos por Ano
    fig2 = px.bar(df_atletas, x='Ano', y='Salario Ajustado', color='Name', title='Ganhos por Ano',
                labels={"Ano": "Ano", "Salario Ajustado": "Salário Ajustado ($ milhões)", "Name": "Atleta"},
                template="plotly_dark", color_discrete_sequence=px.colors.qualitative.Pastel)
    st.plotly_chart(fig2, use_container_width=True)
 

elif page == "Explicações e Análises":
    st.title("📚 Explicações e Análises 📚")
    st.markdown("""
        ## Dados Utilizados

        ### Atletas Mais Bem Pagos
        Os dados dos atletas mais bem pagos foram obtidos a partir de um conjunto de dados que lista os ganhos anuais de vários atletas ao longo dos anos. Este conjunto de dados inclui informações como o nome do atleta, nacionalidade, esporte, ano e ganhos em milhões de dólares.

        ### Poder de Compra do Dólar
        O segundo conjunto de dados utilizado é o valor do poder de compra do dólar ao longo dos anos. Este conjunto de dados inclui informações sobre o valor do dólar, poder de compra e taxa de inflação para cada ano.

        ## Processamento dos Dados

        ### Ajuste dos Ganhos dos Atletas
        Para ajustar os ganhos dos atletas ao longo dos anos, consideramos o poder de compra do dólar. Calculamos o salário ajustado multiplicando os ganhos pelo valor atual do dólar dividido pelo valor do dólar no ano correspondente.

        ```python
        df_atletas['Salario Ajustado'] = df_atletas['Ganhos'] * (current_inflation_value / df_atletas['Inflation Amount'])
        ```

        ## Análises Realizadas

        ### Ganhos Totais por Ano
        Esta análise mostra a tendência dos ganhos totais de atletas ao longo dos anos. Isso nos ajuda a entender como a popularidade e o pagamento de atletas mudaram com o tempo.

        ### Ganhos Totais por Esporte
        Aqui, visualizamos quais esportes geraram mais receita ao longo dos anos, tanto em valores não ajustados quanto ajustados pela inflação. Isso nos ajuda a identificar quais esportes são mais lucrativos.

        ### Distribuição de Ganhos por Nacionalidade
        Esta análise nos permite ver quais nacionalidades dominam em termos de ganhos totais dos atletas. Isso pode indicar quais países investem mais em esportes específicos.

        ### Salário Ajustado ao Longo dos Anos
        Analisamos como os ganhos dos principais atletas mudaram ao longo dos anos quando ajustados pela inflação. Isso nos dá uma visão mais precisa do crescimento real dos ganhos dos atletas.

        ## Visualizações

        ### Gráficos e Mapas
        Utilizamos uma combinação de gráficos de linha, barras e mapas para visualizar os dados. Os gráficos de linha mostram as tendências ao longo do tempo, enquanto os gráficos de barras comparam diferentes categorias, como esportes e nacionalidades. Os mapas ajudam a visualizar a distribuição geográfica dos ganhos.

        ## Conclusão

        Este dashboard oferece uma visão abrangente dos ganhos dos atletas ao longo dos anos, ajustando os valores para refletir o poder de compra atual do dólar. Isso permite uma comparação mais justa e precisa dos ganhos dos atletas em diferentes épocas.

        ## Próximos Passos

        - **Melhorar a Precisão**: Utilizar dados mais detalhados de inflação para ajustes mais precisos.
        - **Análises Adicionais**: Incluir mais perguntas no quiz e explorar outros aspectos dos dados, como a relação entre ganhos e popularidade dos esportes ao longo do tempo.
        """)

   

