import pandas as pd
import dash
from dash import dash_table, html
import dash_bootstrap_components as dbc
from datetime import datetime
import os

# === CONFIGURAÇÃO DO GOOGLE SHEETS ===
spreadsheet_id = "13Yqhezy8VIknbs0083sCwsIgqw5VIJrqCTM8_Ry_de0"
sheet_name = "DEMONSTRATIVO"
csv_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"

# === LEITURA DOS DADOS ===
df_demo = pd.read_csv(csv_url)

# === RENOMEAR E AJUSTAR COLUNAS ===
df_demo = df_demo.rename(columns={
    'NOME DO CLIENTE': 'Cliente',
    'DATA NF': 'Data Nota',
    'DATA PGTO': 'Data Pagamento',
    'PLANO': 'Plano de Saúde',
    'SITUAÇÃO': 'Situação'
})

# CONVERSÕES
df_demo['Data Nota'] = pd.to_datetime(df_demo['Data Nota'], errors='coerce', dayfirst=True)
df_demo['Data Pagamento'] = pd.to_datetime(df_demo['Data Pagamento'], errors='coerce', dayfirst=True)

# DATAS ATUAIS
hoje = datetime.today()
mes_atual = hoje.month
ano_atual = hoje.year

# === FILTRAR NOTAS DO MÊS ATUAL ===
df_notas_mes = df_demo[
    (df_demo['Data Nota'].dt.month == mes_atual) &
    (df_demo['Data Nota'].dt.year == ano_atual)
].copy()

# PEGAR A ÚLTIMA NOTA DE CADA CLIENTE NO MÊS
ultima_nota_mes = df_notas_mes.sort_values('Data Nota').drop_duplicates('Cliente', keep='last')

# OBTER O ÚLTIMO PAGAMENTO DO MÊS PARA CADA CLIENTE
df_pagamentos_mes = df_demo[
    (df_demo['Data Pagamento'].notna()) &
    (df_demo['Data Pagamento'].dt.month == mes_atual) &
    (df_demo['Data Pagamento'].dt.year == ano_atual)
].copy()

ultimo_pagamento = df_pagamentos_mes.sort_values('Data Pagamento').drop_duplicates('Cliente', keep='last')[['Cliente', 'Data Pagamento']]

# JUNTAR AS DUAS TABELAS
df = pd.merge(ultima_nota_mes.drop(columns=['Data Pagamento']), ultimo_pagamento, on='Cliente', how='left')

# MARCAR PAGAMENTO NO MÊS PARA COR
df['pagamento_mes'] = df['Data Pagamento'].notna()

# FORMATAR DATAS
df['Data Nota'] = pd.to_datetime(df['Data Nota'], errors='coerce').dt.strftime('%d/%m/%Y')
df['Data Pagamento'] = pd.to_datetime(df['Data Pagamento'], errors='coerce').dt.strftime('%d/%m/%Y')

# DASHBOARD
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = dbc.Container([
    html.H2("Última Nota do Mês - Colorido por Presença de Pagamento", className="my-4"),

    dash_table.DataTable(
        columns=[
            {"name": "Cliente", "id": "Cliente"},
            {"name": "Plano de Saúde", "id": "Plano de Saúde"},
            {"name": "Data Nota", "id": "Data Nota"},
            {"name": "Data Pagamento", "id": "Data Pagamento"},
        ],
        data=df.to_dict('records'),
        style_cell={'textAlign': 'left', 'padding': '5px'},
        style_header={'backgroundColor': 'lightgray', 'fontWeight': 'bold'},
        style_data_conditional=[
            {'if': {'filter_query': '{Data Pagamento} contains "/"'}, 'backgroundColor': '#d4edda'},  # Verde
            {'if': {'filter_query': '{Data Pagamento} = ""'}, 'backgroundColor': '#ffe6f0'},          # Rosa claro
        ],
        page_size=90,
        style_table={'overflowX': 'auto'}
    )
], fluid=True)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8050))
    app.run(debug=True, host="0.0.0.0", port=port)
