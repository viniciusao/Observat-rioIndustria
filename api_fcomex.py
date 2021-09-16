from flask_restful import Resource
import pandas as pd
from flask import Flask
from flask import jsonify
from flask_restful import Api
import json

MESES_STANDARD = {1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril', 5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto', 9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'}
df = pd.read_csv('f_comex.csv', sep=';')[['ANO', 'MES', 'COD_NCM', 'COD_VIA', 'VL_QUANTIDADE', 'MOVIMENTACAO']]


class GetAllProducts(Resource):

    @staticmethod
    def get():
        df_allproducts = df.groupby(['ANO', 'MES', 'MOVIMENTACAO'], as_index=False).sum('VL_QUANTIDADE')
        df_allproducts['MES'].replace(MESES_STANDARD, inplace=True)
        result = df_allproducts.to_json()
        return jsonify({'result': json.loads(result)})


class GetSpecificProducts(Resource):

    @staticmethod
    def get():
        df_products = df.groupby(['ANO', 'COD_NCM', 'MES', 'MOVIMENTACAO'], as_index=False).sum('VL_QUANTIDADE')
        df_products['MES'].replace(MESES_STANDARD, inplace=True)
        result = df_products.to_json()
        return jsonify({'result': json.loads(result)})

class GetVias(Resource):

    @staticmethod
    def get():
        via_cod_to_name = pd.read_excel('d_via.xlsx')
        vias = dict(zip(via_cod_to_name['CO_VIA'].tolist(), via_cod_to_name['NO_VIA'].tolist()))
        df['COD_VIA'].replace(vias, inplace=True)
        result = df.to_json()
        return jsonify({'result': json.loads(result)})


app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

api = Api(app)
api.add_resource(GetAllProducts, '/get_allproducts_df')
api.add_resource(GetSpecificProducts, '/get_specificproducts_df')
api.add_resource(GetVias, '/get_vias_df')

if __name__ == '__main__':
    app.run()