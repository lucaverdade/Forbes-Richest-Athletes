from pyspark.sql import SparkSession
from pyspark.sql.functions import col
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Inicializando SparkSession
spark = SparkSession.builder.appName("AtletasMaisBemPagos").getOrCreate()

# Carregando os dados (substitua 'dados_atletas.csv' pelo seu arquivo de dados)
dados_atletas = spark.read.csv('Atletas mais bem pagos.csv', header=True, inferSchema=True)
