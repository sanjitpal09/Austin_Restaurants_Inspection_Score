import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly
import pandas as pd
from plotly.graph_objs import *
from dash.dependencies import Input, Output

app = dash.Dash()

data_df = pd.read_csv('https://data.austintexas.gov/api/views/ecmv-9xxi/rows.csv?accessType=DOWNLOAD')
data_df['Coordinates']=data_df['Address'].apply(lambda s: s[s.find("(")+1:s.find(")")])
new_df = data_df['Coordinates'].apply(lambda x: pd.Series([i for i in reversed(x.split(','))]))
data_df['Longitude']=new_df[0]
data_df['Latitude']=new_df[1]
data_df['Date'] = pd.to_datetime(data_df['Inspection Date'])
data_df['Year']=data_df['Date'].dt.year
data_df= data_df[data_df['Year']==2017]
data_df = data_df[['Restaurant Name','Zip Code','Score','Latitude','Longitude','Year']]
data_df['Zip Code'] = data_df['Zip Code'].str[-5:]
data_df['Zip Code'] = data_df['Zip Code'].astype(str).astype(int)
data_df['Latitude'] = pd.to_numeric(data_df['Latitude'], errors='coerce').fillna(0)
data_df['Longitude'] = pd.to_numeric(data_df['Longitude'], errors='coerce').fillna(0)
final_df = data_df.groupby(['Restaurant Name','Year','Zip Code'],as_index = False).mean()
final_df['Restaurant Name'] = 'Restaurant Name:' + final_df['Restaurant Name'].astype(str) + ', Inspection Score:'+  final_df['Score'].astype(str)
final_df2 = final_df[['Restaurant Name','Zip Code','Latitude','Longitude']]
final_df2 = final_df2[final_df2.Latitude != 0]
final_df2 = final_df2[final_df2.Longitude !=0]
final_df2.rename(columns={'Restaurant Name': 'Restaurant'}, inplace=True)
final_df2.rename(columns={'Zip Code': 'Zip_Code'}, inplace=True)
available_zipcode = final_df2['Zip_Code'].unique()

mapbox_access_token = 'pk.eyJ1IjoiYWxpc2hvYmVpcmkiLCJhIjoiY2ozYnM3YTUxMDAxeDMzcGNjbmZyMmplZiJ9.ZjmQ0C2MNs1AzEBC_Syadg'
layout = dict(
    autosize=True,
    hovermode="closest",
    title='Restaurant Map',
    mapbox=dict(
        accesstoken=mapbox_access_token,
        center=dict(
        lon=-97.755996,
        lat=30.307182
        ),
        zoom=7,
        )
    )

app.layout = html.Div([
            html.Div([
            html.Label('Enter Zip Code'),
            dcc.Dropdown(
                id='Available ZipCodes',
                options=[{'label': i, 'value': i} for i in available_zipcode],
                value= 78610
            )]
            ),
            html.Div(
                    [
                        dcc.Graph(id='main_graph')
                    ]
                )

    ])
@app.callback(Output('main_graph', 'figure'),
              [Input('Available ZipCodes', 'value')])
def update_figure(selected_zipcode):
    filtered_df = final_df2[final_df2.Zip_Code == selected_zipcode]
    traces = []
    counter_res = filtered_df.Restaurant.count()
    for rest in range(counter_res):
        trace = dict(
            type='scattermapbox',
            lon=filtered_df['Longitude'][rest],
            lat=filtered_df['Latitude'][rest],
            text=filtered_df['Restaurant'][rest],
            marker=dict(
                size=10,

            )
        )
        traces.append(trace)
    figure = dict(data=traces, layout=layout)
    return figure

if __name__ == '__main__':
    app.run_server(debug=True)
