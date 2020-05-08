'''
Download data through API and return as dataframe

Usage example:

import download_data_geospatial as ddg

BASE_URL = 'https://dataverse.harvard.edu/'
IDENTIFIER = 'doi:10.7910/DVN/SG589T'

df_kenya = ddg.get_fsp_data_through_api(BASE_URL, IDENTIFIER)
'''

import json
import pandas as pd
from pyDataverse.api import Api
import xlrd
from shapely.geometry import Point


def get_fsp_data_through_api(base_url, identifier):
    '''
    Takes base URL and identifier of the FSP data,
    and returns the Pandas dataframe of the file

    Input
        base_url (str): URL of the website
        identifier (str): identifier of the desired data file

    Output
        df (Pandas dataframe): dataframe of the FSP data
    '''

    dtype_col = {'FormName':'str', 'County':'str',
                 'GPSLatitude':'float32', 'GPSLongitude':'float32'}
    geo_columns = list(dtype_col.keys())

    api = Api(base_url)
    resp_dataset = api.get_dataset(identifier)

    files = json.loads(resp_dataset.text)['data']['latestVersion']['files']
    df = pd.DataFrame({col : [] for col in geo_columns})

    for file in files:
        file_id = file['dataFile']['id']
        resp_datafile = api.get_datafile(file_id)
        file_extension = file['dataFile']['filename'].split('.')[-1]
        if file_extension == 'tab':
            rows = resp_datafile.text.split('\n')
            headers = rows[0].split('\t')
            data_rows = \
            [row.replace('"', '').split('\t')
             for row in rows[1:] if row != ''
             and row.split('\t')[headers.index('GPSLatitude')] != '']
            df_file = \
            pd.DataFrame(data_rows,
                         columns=headers)[geo_columns].astype(dtype_col)
        elif file_extension == 'xlsx':
            workbook = xlrd.open_workbook(file_contents=
                                          resp_datafile.content)
            worksheet = workbook.sheet_by_index(0)
            col_names = [col_name.replace(" ", "")
                         for col_name in worksheet.row_values(0)]
            df_file = pd.DataFrame({col : [] for col in geo_columns})
            for col in geo_columns:
                data_col = worksheet.col_values(col_names.index(col),
                                                start_rowx=1)
                for idx_data, data in enumerate(data_col):
                    if type(data) == str:
                        data_col[idx_data] = data.replace('"', '')
                    if data in ['', '--']:
                        data_col[idx_data] = 'nan'
                df_file[col] = pd.Series(data_col, dtype=dtype_col[col])

        df = df.append(df_file[df_file['County'] != 'nan'], ignore_index=True)

    df['geometry'] = \
    df.apply(lambda x: Point(float(x['GPSLongitude']),
                             float(x['GPSLatitude'])), axis=1)

    return df
