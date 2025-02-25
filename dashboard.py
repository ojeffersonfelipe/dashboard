import streamlit as st
import pandas as pd
import gspread
import plotly.express as px
import json
import os
from oauth2client.service_account import ServiceAccountCredentials

# Configurar layout do Streamlit
st.set_page_config(page_title="Dashboard de Tarefas", layout="wide")

st.title("📊 Dashboard de Tarefas - Google Sheets")

# 🔹 Ler as credenciais da variável de ambiente
json_credenciais = st.secrets["GOOGLE_SHEETS_CREDENTIALS"]
creds_dict = json.loads(json_credenciais)  # Converter a string JSON para dicionário

# Configurar autenticação com Google Sheets
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, SCOPE)
client = gspread.authorize(creds)

# 🔹 Conectar ao Google Sheets
SHEET_NAME = "Planejamento"  # Altere para o nome real
sheet = client.open(SHEET_NAME).sheet1  # Primeiro aba da planilha

# 🔹 Ler os dados
data = sheet.get_all_records()
df = pd.DataFrame(data)

# 🔹 Converter colunas de data
df["Data de Início"] = pd.to_datetime(df["Data de Início"])
df["Data de Término"] = pd.to_datetime(df["Data de Término"])
df["Duração"] = (df["Data de Término"] - df["Data de Início"]).dt.days

# 🔹 KPIs
col1, col2, col3, col4 = st.columns(4)
col1.metric("📌 Total de Tarefas", len(df))
col2.metric("✅ Concluídas", df[df["Status"] == "Concluído"].shape[0])
col3.metric("🕒 Em andamento", df[df["Status"] == "Em andamento"].shape[0])
col4.metric("📋 A Fazer", df[df["Status"] == "A fazer"].shape[0])

# 🔹 Gráfico de Gantt (Linha do Tempo das Tarefas)
fig_gantt = px.timeline(df, x_start="Data de Início", x_end="Data de Término",
                        y="Tarefa Principal", color="Status",
                        title="📅 Linha do Tempo das Tarefas")
fig_gantt.update_yaxes(categoryorder="total ascending")

# 🔹 Gráfico de Horas Estimadas
fig_horas = px.bar(df, x="Horas Estimadas", y="Tarefa Principal", color="Responsável",
                   title="⏳ Horas Estimadas por Tarefa", orientation="h")

# 🔹 Exibir gráficos lado a lado
col1, col2 = st.columns(2)
col1.plotly_chart(fig_gantt, use_container_width=True)
col2.plotly_chart(fig_horas, use_container_width=True)

# 🔹 Tabela de Tarefas
st.subheader("📋 Tabela de Tarefas")
st.dataframe(df)
