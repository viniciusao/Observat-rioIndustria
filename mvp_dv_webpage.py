import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px

# init
app = dash.Dash(__name__)
server = app.server

# creates a dict of via code to its name
via_cod_to_name = pd.read_excel('d_via.xlsx')
vias = dict(zip(via_cod_to_name['CO_VIA'].tolist(), via_cod_to_name['NO_VIA'].tolist()))

# creates a dict of product code to its name
product_cod_to_name = pd.read_excel('d_sh2.xlsx')
products = dict(zip(product_cod_to_name['CO_NCM'].tolist(), product_cod_to_name['NO_NCM_POR'].tolist()))

# dict of month number to its name
MESES_STANDARD = {1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril', 5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto', 9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'}


df = pd.read_csv('f_comex.csv', sep=';')[['ANO', 'MES', 'COD_NCM', 'COD_VIA', 'VL_QUANTIDADE', 'MOVIMENTACAO']]
df['COD_VIA'].replace(vias, inplace=True)

# all products
df_allproducts = df.groupby(['ANO', 'MES', 'MOVIMENTACAO'], as_index=False).sum('VL_QUANTIDADE')
df_allproducts['MES'].replace(MESES_STANDARD, inplace=True)

# specific products
df_products = df.groupby(['ANO', 'COD_NCM', 'MES', 'MOVIMENTACAO'], as_index=False).sum('VL_QUANTIDADE')
df_products['MES'].replace(MESES_STANDARD, inplace=True)


# dash layout
app.layout = html.Div(children=[
    html.H1(children='Observatório da Industria', style={'font-weight': 'bold', "text-align": "center"}),
    html.Label(['Escolha o ano:'], style={'font-weight': 'bold', "text-align": "center"}),
    dcc.Dropdown(
        id='year_dropdown',
        options=[{'label': i, 'value': i} for i in df['ANO'].unique()]
    ),
    html.Br(),
    html.Label(['Escolha o produto (Todos ou algum em específico):'],style={'font-weight': 'bold', "text-align": "center"}),
    dcc.Dropdown(
        id='product_dropdown',
        options=[{'label': 'Todos os produtos', 'value': 'Todos os produtos'}]+[
            {'label': products[i], 'value': i} for i in df['COD_NCM'].unique()
        ]
    ),
    html.Br(),
    html.Label(['Escolha o tipo de movimentação (Exportação ou Importação):'], style={'font-weight': 'bold', "text-align": "center"}),
    dcc.Dropdown(
        id='movement_type_dropdown',
        options=[
            {'label': i, 'value': i} for i in df['MOVIMENTACAO'].unique()
        ]
    ),
    html.Br(),
    html.Label(['Escolha o tipo de gráfico para plotar:'], style={'font-weight': 'bold', "text-align": "center"}),
    dcc.Dropdown(
        id='graph_type_dropdown',
        options=[
            {'label': 'Gráfico de Barras com a quantidade de Importação ou exportação de um produto ou geral mês a mês.', 'value': 'bar_chart'},
            {'label': 'Gráfico de Pizza com percentual de utilização da VIA.', 'value': 'pie_chart'}
        ],
        value='pie_chart'
    ),
    dcc.Graph(
        id='graphs_here'
    )
])

#---------------------------------------------------------------
# Connecting the Dropdown values to the graph
@app.callback(
    Output(component_id='graphs_here', component_property='figure'),
    [Input(component_id='year_dropdown', component_property='value'),
     Input(component_id='product_dropdown', component_property='value'),
     Input(component_id='movement_type_dropdown', component_property='value'),
     Input(component_id='graph_type_dropdown', component_property='value')]
)
def generate_graphs(year, product, movement_type, graph_type):
    if graph_type == 'bar_chart':
        if product == 'Todos os produtos':
            return px.bar(df_allproducts.query(f'ANO == {year} and MOVIMENTACAO == "{movement_type}"'),
                          x="MES", y="VL_QUANTIDADE", color="VL_QUANTIDADE",
                          labels={'MES': 'MÊS', 'VL_QUANTIDADE': 'TOTAL MOVIMENTADO'})
        return px.bar(df_products.query(f'ANO == {year} and COD_NCM == {product} and MOVIMENTACAO == "{movement_type}"'),
                          x="MES", y="VL_QUANTIDADE", color="VL_QUANTIDADE",
                          labels={'MES': 'MÊS', 'VL_QUANTIDADE': 'TOTAL MOVIMENTADO'})

    elif graph_type == 'pie_chart':
        if product == 'Todos os produtos':
            fig = px.pie(df.query(f'ANO == {year} and MOVIMENTACAO == "{movement_type}"'), names='COD_VIA')
            fig.update_traces(textinfo='percent+label')
            return fig
        fig = px.pie(df.query(f'ANO == {year} and COD_NCM == {product} and MOVIMENTACAO == "{movement_type}"'), names='COD_VIA')
        fig.update_traces(textinfo='percent+label')
        return fig


if __name__ == '__main__':
    app.run_server()