import pandas as pd
import dash
from dash import dash_table, html
import dash_bootstrap_components as dbc
from datetime import datetime

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

# === DATAS ATUAIS ===
hoje = datetime.today()
mes_atual = hoje.month
ano_atual = hoje.year

# === FILTRAR NOTAS DO MÊS ATUAL ===
df_notas_mes = df_demo[
    (df_demo['Data Nota'].dt.month == mes_atual) &
    (df_demo['Data Nota'].dt.year == ano_atual)
].copy()

# PEGAR A ÚLTIMA NOTA DE CADA CLIENTE NO MÊS (com situação)
ultima_nota_mes = df_notas_mes.sort_values('Data Nota').drop_duplicates('Cliente', keep='last')

# OBTER O ÚLTIMO PAGAMENTO NO MÊS ATUAL PARA CADA CLIENTE
df_pagamentos_mes = df_demo[
    (df_demo['Data Pagamento'].notna()) &
    (df_demo['Data Pagamento'].dt.month == mes_atual) &
    (df_demo['Data Pagamento'].dt.year == ano_atual)
].copy()

ultimo_pagamento = df_pagamentos_mes.sort_values('Data Pagamento').drop_duplicates('Cliente', keep='last')[['Cliente', 'Data Pagamento']]

# JUNTAR: última nota do mês com último pagamento do mês
df = pd.merge(ultima_nota_mes.drop(columns=['Data Pagamento']), ultimo_pagamento, on='Cliente', how='left')

# FORMATAR DATAS
df['Data Nota'] = pd.to_datetime(df['Data Nota'], errors='coerce').dt.strftime('%d/%m/%Y')
df['Data Pagamento'] = pd.to_datetime(df['Data Pagamento'], errors='coerce').dt.strftime('%d/%m/%Y')

# DASHBOARD
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = dbc.Container([
    html.H2("Última Nota Emitida no Mês e Situação Real", className="my-4"),

    dash_table.DataTable(
        columns=[
            {"name": "Cliente", "id": "Cliente"},
            {"name": "Plano de Saúde", "id": "Plano de Saúde"},
            {"name": "Data Nota", "id": "Data Nota"},
            {"name": "Data Pagamento", "id": "Data Pagamento"},
            {"name": "Situação", "id": "Situação"},
        ],
        data=df.to_dict('records'),
        style_cell={'textAlign': 'left', 'padding': '5px'},
        style_header={'backgroundColor': 'lightgray', 'fontWeight': 'bold'},
        style_data_conditional=[
            {'if': {'filter_query': '{Situação} = "Pago"'}, 'backgroundColor': '#d4edda'},
            {'if': {'filter_query': '{Situação} = "Parcial"'}, 'backgroundColor': '#fff3cd'},
            {'if': {'filter_query': '{Situação} = "A PAGAR"'}, 'backgroundColor': '#f8d7da'},
        ],
        page_size=20,
        style_table={'overflowX': 'auto'}
    )
], fluid=True)

if __name__ == "__main__":
    app.run(debug=True)
