# Script: multiplot_IoT_component.py
# Description: This script takes a stream of serial input from an arduino
#              and using Dash, real-time plots are displayed on a local
#              webserver. The webserver displays thermistor, photocell,
#              humidity sensor and MiCS-5914 data.
#              
# 
# Author: Kevin Rivera
# Creation date: 11/27/2020
# Version: v1.0

######################################### Imports ##############################################

import dash
from dash.dependencies import Output, Input
import dash_core_components as dcc
import dash_html_components as html
import plotly
import plotly.graph_objs as go
from collections import deque
import serial as S
import time


######################################### Variables ############################################

size = 100                                  # The limit set for the maximum container size.
ThermistorDATA = deque(maxlen=size)         # Container that will contain the thermistor readings.
PhotocellDATA = deque(maxlen=size)          # Container that will contain the photocell readings.
DHT11DATA = deque(maxlen=size)              # Container that will contain the DHT11 readings.
MiCS5914DATA = deque(maxlen=size)           # Container that will contain the MiCS-5914 readings.
X = deque(maxlen=size)                      # Container that will contain the 'x' axis values.
X.append(0)                                 # Giving this container an initial value of zero.

Hum = ''                                    # Humidity data extracted from a message will be kept here temporarily.
Therm = ''                                  # Thermistor data extracted from a message will be kept here temporarily.
Gas = ''                                    # Gas sensor data extracted from a message will be kept here temporarily.
Photo = ''									# Photocell data extracted from a message will be kept here temporarily.
prev = ''                                   # First character of the previous extracted message kept here temporarily.

HM = []                                  	# Humidity data will be appended to this list.
TM = []                             		# Thermistor data will be appended to this list.
GS = []                                 	# Gas sensor data will be appended to this list.
PC = []                                 	# Photocell data will be appended to this list.


######################################### Body #################################################

app = dash.Dash(__name__)
app.layout = html.Div(
    [
        html.Label(['', html.A('First person view', href='http://192.168.0.22:5000/')]),
        dcc.Graph(id='Thermistor-output', animate=True),
        dcc.Interval(
            id='graph-update1',
            interval=5000
        ),
        dcc.Graph(id='Photocell-output', animate=True),
        dcc.Interval(
            id='graph-update2',
            interval=5000
        ),
        dcc.Graph(id='DHT11-output', animate=True),
        dcc.Interval(
            id='graph-update3',
            interval=5000
        ),
        dcc.Graph(id='MiCS5914-output', animate=True),
        dcc.Interval(
            id='graph-update4',
            interval=5000
        ),
    ]
)

################################################################################################

@app.callback(Output('Thermistor-output', 'figure'), [Input('graph-update1', 'n_intervals')])
def update_Thermistor_plot(input_data):
    
    port = S.Serial('/dev/ttyACM0',9600)
    message = port.readline()
    message = message.decode()
    com1 = 0
    com2 = 0
    com3 = 0
    k = 0
    flag1 = 0
    flag2 = 0
    tickT = 0
    
    # Collecting and parsing the sensor data.
    while(k < len(message)):
        if(message[k] == ',' and flag1 == 0):
            com1 = k
            Hum = message[1:com1]
            HM.append(float(Hum))
            flag1 = 1
        elif(message[k] == ',' and com1 > 0 and flag2 == 0):
            com2 = k
            Therm = message[com1+1:com2]
            TM.append(float(Therm))
            flag2 = 1
        elif(message[k] == ',' and com2 > 0):
            com3 = k
            Gas = message[com2+1:com3]
            Photo = message[com3+1:]
            GS.append(float(Gas))
            PC.append(float(Photo))
            break
        k = k + 1
    
    # Populating the containers with the appropriate data.
    X.append(X[-1]+1)
    ThermistorDATA.append(float(Therm))
    PhotocellDATA.append(float(Photo))
    DHT11DATA.append(float(Hum))
    MiCS5914DATA.append(float(Gas))
    
    # Setting up the specifications for the thermistor plot.
    data = go.Scatter(
            x=list(X),
            y=list(ThermistorDATA),
            name= 'Scatter',
            mode= 'lines+markers'
            )

    return {'data': [data],'layout' : go.Layout(xaxis=dict(range=[min(X),max(X)]),
                                                yaxis=dict(range=[0,40]),title='Temperature (°C)')}

    port.close()
    
################################################################################################

@app.callback(Output('Photocell-output', 'figure'), [Input('graph-update2', 'n_intervals')])
def update_Photocell_plot(input_data):
    
    # Setting up the specifications for the photocell plot.
    data = go.Scatter(
            x=list(X),
            y=list(PhotocellDATA),
            name= 'Scatter',
            mode= 'lines+markers'
            )

    return {'data': [data],'layout' : go.Layout(xaxis=dict(range=[min(X),max(X)]),
                                                yaxis=dict(range=[min(PhotocellDATA),max(PhotocellDATA)]),title='Photocell output (Ohms)')}


################################################################################################

@app.callback(Output('DHT11-output', 'figure'), [Input('graph-update3', 'n_intervals')])
def update_DHT11_plot(input_data):
    
    # Setting up the specifications for the DHT11 plot.
    data = go.Scatter(
            x=list(X),
            y=list(DHT11DATA),
            name= 'Scatter',
            mode= 'lines+markers'
            )

    return {'data': [data],'layout' : go.Layout(xaxis=dict(range=[min(X),max(X)]),
                                                yaxis=dict(range=[20,50]),title='Humidity (%RH)')}

    
################################################################################################

@app.callback(Output('MiCS5914-output', 'figure'), [Input('graph-update4', 'n_intervals')])
def update_MiCS5914_plot(input_data):   
    
    # Setting up the specifications for the MiCS-5914 plot.
    data = go.Scatter(
            x=list(X),
            y=list(MiCS5914DATA),
            name= 'Scatter',
            mode= 'lines+markers'
            )

    return {'data': [data],'layout' : go.Layout(xaxis=dict(range=[min(X),max(X)]),
                                                yaxis=dict(range=[min(MiCS5914DATA),max(MiCS5914DATA)]),title='MiCS-5914 output (Ohms)')}

    
################################################################################################


if __name__ == '__main__':
    app.run_server(host = '192.168.0.6', debug=True, use_reloader=False)