'''
Plots location of financial service providers in Kenya

Usage example:

import download_data_geospatial as ddg
import plot_kenya as pk

BASE_URL = 'https://dataverse.harvard.edu/'
IDENTIFIER = 'doi:10.7910/DVN/SG589T'

df_kenya = \
ddg.get_fsp_data_through_api(BASE_URL, IDENTIFIER)
pk.plot_map(df_kenya, 'Mobile Money Agent') 

Can put other formname

Formname: 'Agriculture', 'Bank Agent', 'Capital Markets',
       'Commercial Bank and Mortgage', 'Development Finance',
       'Forex Bureau', 'Hire Purchase', 'Insurance Service Provider',
       'Micro Finance Banks', 'Micro Finance Institutions',
       'Mobile Money Agent', 'Money Transfer Service', 'Pension Provider',
       'Post Office', 'SACCO', 'Stand alone ATM'
'''


import geopandas as gpd
import matplotlib.pyplot as plt


def plot_map(df, formname):
    '''
    Takes dataframe which has a column of shapely geometry
    and a desired form name, and plots in the map of Kenya

    Input
        df (Pandas dataframe): dataframe which has
                               a column of sharpely geometry
        formname (str): desired form name
    '''

    world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
    poly_kenya = world[world.name == 'Kenya']['geometry'].iloc[0]
    df_within_kenya = \
    df[df.apply(lambda x: x['geometry'].within(poly_kenya), axis=1)]
    ax = \
    world[world.name == 'Kenya'].plot(color='white',
                                      edgecolor='black',
                                      figsize=(10, 7))
    df_within_kenya.plot(ax=ax, kind='scatter',
                         x='GPSLongitude', y='GPSLatitude',
                         c='k', s=10, label='Other forms')
    df_within_kenya[df_within_kenya['FormName'] ==
                    formname].plot(ax=ax, kind='scatter',
                                   x='GPSLongitude', y='GPSLatitude',
                                   c='r', s=10, label=formname)
    ax.grid()
    ax.set_axisbelow(True)
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.title('Financial Service Providers in Kenya')
    plt.legend()
    plt.show()

