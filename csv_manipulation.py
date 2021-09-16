import glob
import pandas as pd


class CSVArranger:

    new_columns = ['ANO', 'MES', 'COD_NCM', 'COD_UNIDADE', 'COD_PAIS', 'SG_UF', 'COD_VIA', 'COD_URF', 'VL_QUANTIDADE', 'VL_PESO_KG', 'VL_FOB']
    change_values = {'COD_NCM': '8', 'COD_URF': '7', 'COD_PAIS': '3'}

    def __init__(self, path: str):
        self.dfs = []
        self.current_df = None
        self.downloaded_csv_files_comex = path

    def go(self):
        self._read_csv_files()
        self._drop_columns()
        self._change_columns_values()
        self._export_to_csv()

    def _read_csv_files(self):
        for c, csv_file in enumerate(glob.glob('/'.join((self.downloaded_csv_files_comex, '*.csv')))):
            if c == 1:
                break
            df = pd.read_csv(csv_file, sep=';')
            df['MOVIMENTACAO'] = pd.Series(['Importação' if 'IMP' in csv_file else 'Exportação' for _ in range(len(df.index))])
            self.dfs.append(df)

    def _drop_columns(self):
        df = pd.concat(self.dfs)
        df.drop('VL_SEGURO', inplace=True, axis=1)
        df.drop('VL_FRETE', inplace=True, axis=1)
        self.current_df = df

    def _change_columns_values(self):
        columns = self.current_df.columns.to_list()
        self.current_df.rename(columns=dict(zip(columns, self.new_columns)), inplace=True)
        for k in self.change_values:
            self.current_df[k] = [str(v).zfill(len(str(v))+1) if str(v).startswith(self.change_values[k]) else v for v in self.current_df[k]]

    def _export_to_csv(self):
        self.current_df.to_csv('f_comex.csv', index=False)
