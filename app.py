import pandas as pd
import dash
from dash import dash_table, html, dcc, Input, Output
import dash_bootstrap_components as dbc
from datetime import datetime
import os

# === CONFIGURAÇÃO DO GOOGLE SHEETS ===
spreadsheet_id = "13Yqhezy8VIknbs0083sCwsIgqw5VIJrqCTM8_Ry_de0"
sheet_name = "DEMONSTRATIVO"
csv_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"

# === DASH APP ===
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = dbc.Container([
    html.H2("Relatório - Clientes", className="my-4"),

    dcc.Interval(id='interval-atualizacao', interval=60*1000, n_intervals=0),  # Atualiza a cada 60 segundos

    dbc.Row([
        dbc.Col(
            dash_table.DataTable(
                id='tabela-esquerda',
                columns=[
                    {"name": "Cliente", "id": "Cliente"},
                    {"name": "Plano de Saúde", "id": "Plano de Saúde"},
                    {"name": "Data Nota", "id": "Data Nota"},
                    {"name": "Data Pagamento", "id": "Data Pagamento"},
                ],
                style_cell={
                    'textAlign': 'left',
                    'padding': '5px',
                    'minWidth': '100px',
                    'fontSize': '13px',
                    'whiteSpace': 'normal'
                },
                style_header={'backgroundColor': 'lightgray', 'fontWeight': 'bold'},
                style_data_conditional=[
                    {'if': {'filter_query': '{Data Pagamento} contains "/"'}, 'backgroundColor': '#d4edda'},
                    {'if': {'filter_query': '{Data Pagamento} = ""'}, 'backgroundColor': '#ffe6f0'},
                ],
                page_size=20,
                style_table={'overflowX': 'auto'}
            ),
            width=6
        ),
        dbc.Col(
            dash_table.DataTable(
                id='tabela-direita',
                columns=[
                    {"name": "Cliente", "id": "Cliente"},
                    {"name": "Plano de Saúde", "id": "Plano de Saúde"},
                    {"name": "Data Nota", "id": "Data Nota"},
                    {"name": "Data Pagamento", "id": "Data Pagamento"},
                ],
                style_cell={
                    'textAlign': 'left',
                    'padding': '5px',
                    'minWidth': '100px',
                    'fontSize': '13px',
                    'whiteSpace': 'normal'
                },
                style_header={'backgroundColor': 'lightgray', 'fontWeight': 'bold'},
                style_data_conditional=[
                    {'if': {'filter_query': '{Data Pagamento} contains "/"'}, 'backgroundColor': '#d4edda'},
                    {'if': {'filter_query': '{Data Pagamento} = ""'}, 'backgroundColor': '#ffe6f0'},
                ],
                page_size=20,
                style_table={'overflowX': 'auto'}
            ),
            width=6
        )
    ])
], fluid=True)

# === CALLBACK PARA ATUALIZAÇÃO AUTOMÁTICA ===
@app.callback(
    [Output('tabela-esquerda', 'data'),
     Output('tabela-direita', 'data')],
    Input('interval-atualizacao', 'n_intervals')
)
def atualizar_dados(n):
    df_demo = pd.read_csv(csv_url)

    df_demo = df_demo.rename(columns={
        'NOME DO CLIENTE': 'Cliente',
        'DATA NF': 'Data Nota',
        'DATA PGTO': 'Data Pagamento',
        'PLANO': 'Plano de Saúde',
        'SITUAÇÃO': 'Situação'
    })

    df_demo['Data Nota'] = pd.to_datetime(df_demo['Data Nota'], errors='coerce', dayfirst=True)
    df_demo['Data Pagamento'] = pd.to_datetime(df_demo['Data Pagamento'], errors='coerce', dayfirst=True)

    hoje = datetime.today()
    mes_atual = hoje.month
    ano_atual = hoje.year

    df_notas_mes = df_demo[
        (df_demo['Data Nota'].dt.month == mes_atual) &
        (df_demo['Data Nota'].dt.year == ano_atual)
    ].copy()

    ultima_nota_mes = df_notas_mes.sort_values('Data Nota').drop_duplicates('Cliente', keep='last')

    df_pagamentos_mes = df_demo[
        (df_demo['Data Pagamento'].notna()) &
        (df_demo['Data Pagamento'].dt.month == mes_atual) &
        (df_demo['Data Pagamento'].dt.year == ano_atual)
    ].copy()

    ultimo_pagamento = df_pagamentos_mes.sort_values('Data Pagamento').drop_duplicates('Cliente', keep='last')[['Cliente', 'Data Pagamento']]

    df = pd.merge(ultima_nota_mes.drop(columns=['Data Pagamento']), ultimo_pagamento, on='Cliente', how='left')

    df['Data Nota'] = pd.to_datetime(df['Data Nota'], errors='coerce').dt.strftime('%d/%m/%Y')
    df['Data Pagamento'] = pd.to_datetime(df['Data Pagamento'], errors='coerce').dt.strftime('%d/%m/%Y')

    dados = df.to_dict('records')
    return dados, dados

# === EXECUÇÃO ===
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8050))
    app.run(debug=True, host="0.0.0.0", port=port)

