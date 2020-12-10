import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import numpy as np
import networkx as nx
import plotly.graph_objects as go
from dash.dependencies import Input, Output

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# Data Processing
# Load in Roamed File
roam_file = "../../sortlog/h3c-wx7-20161118/h3c-wx7-20161118-info-formatted/h3c-wx7-20161118-roamed-formatted.csv"
roam_df = pd.read_csv(roam_file, engine='python')

# Load in Successfully Login File
login_file = "../../sortlog/h3c-wx7-20161118/h3c-wx7-20161118-info-formatted/h3c-wx7-20161118-successfully-formatted.csv"
login_df = pd.read_csv(login_file, engine='python')

# Load in Location File
location_file = "../../reference-table/APLocationMapping.csv"
location_df = pd.read_csv(location_file, engine='python')

app.layout = html.Div([
    html.Div(
        className="app-header",
        children=[
            html.Div('Applying Big Data Analytics to a Campus Wi-Fi Network', className="app-header--title")
        ]
    ),
    html.Div(
        className="app",
        children=[
            html.Div(
                className="app-graph",
                children=[
                    dcc.Graph(
                        id="utilization-rate-graph",
                        config={
                            'scrollZoom': True
                        }
                    )
                ]
            ),
            html.Div(
                className="app-slider",
                children=[
                    html.Div(
                        className="slider",
                        children=[
                            html.Div(id='time-range-display'),
                            dcc.RangeSlider(
                                    className="slider-label",
                                    id='time-slider',
                                    min=0,
                                    max=24,
                                    step=1,
                                    value=[0,1],
                                    marks={str(i):str(i) for i in range(25)}
                            )
                        ]
                    ),
                    html.Div(
                        className="slider",
                        children=[
                            html.Div("Minimum Edge Weight (No. of Roaming) to Show",className="label"),
                            dcc.Slider(
                                    className="slider-label",
                                    id='edge-weight-slider',
                                    min=0,
                                    max=50,
                                    step=1,
                                    value=20,
                                    marks={str(i):str(i) for i in range(0,51,5)}
                            )
                        ]
                    ),
                    html.Div(
                        className="slider",
                        children=[
                            html.Div ("Minimum Edge Weight to Highlight",className="label"),
                            dcc.Slider(
                                    className="slider-label",
                                    id='color-edge-weight-slider',
                                    min=0,
                                    max=100,
                                    step=1,
                                    value=50,
                                    marks={str(i):str(i) for i in range(0,101,5)}
                            )
                        ]
                    ),
                    html.Div(
                        className="slider",
                        children=[
                            html.Div ("Node Size Scale Factor",className="label"),
                            dcc.Slider(
                                    className="slider-label",
                                    id='node-scale-slider',
                                    min=0,
                                    max=0.1,
                                    step=0.001,
                                    value=0.01,
                                    marks={str(i):str(i) for i in np.arange(0,0.1,0.01)}
                            )
                        ]
                    )
                ]
            )
        ]
    ),
    html.Div('Senior Design Project by David Po', className="app-header--name")
]
)

@app.callback(
    Output('utilization-rate-graph', 'figure'),
    [Input('time-slider', 'value'),
     Input('edge-weight-slider', 'value'),
     Input('color-edge-weight-slider', 'value'),
     Input('node-scale-slider', 'value')])
def update_figure(time,edge_weight_threshold,color_threshold,node_size_scale):
    # Graph with Weighting
    start_time,end_time = time
    start_time=str(start_time).zfill(2) + ":00:00"
    end_time=str(end_time).zfill(2) + ":00:00"

    #Load in data
    data_df = roam_df.where((roam_df["Time"] >= start_time) & (roam_df["Time"] <= end_time))
    data_df.dropna(inplace=True)
    data_df.info()

    # Model Each Roaming as an Edge
    roam_edge = []
    for index, row in data_df.iterrows():
        roam_edge.append((row['FromMacAddress'], row['ToMacAddress']))

    # Model the number of roam happened in the period by edge weight
    edge_weight = {}
    for edge in roam_edge:
        if edge in edge_weight:
            edge_weight[edge] += 1
        else:
            edge_weight[edge] = 1

    node_roamout={}
    for edge in edge_weight:
        source=edge[0]
        dest=edge[1]
        if source in node_roamout:
            node_roamout[source][dest]=edge_weight[edge]
        else:
            tmp={}
            tmp[dest]=edge_weight[edge]
            node_roamout[source] = tmp

    for node in node_roamout:
        unsorted_dict = node_roamout[node]
        sorted_dict = sorted(unsorted_dict.items(), key=lambda unsorted: unsorted[1], reverse=True)
        node_roamout[node]=sorted_dict

    # Model Change of User of an AP with Node Size = No.of login - No.of disconnect + Roam In - Roam Out (Within the defined time period)
    # Absolute number of user cannot be model due to finite amount of data
    login_count = login_df['BSSID'].value_counts()
    roamin_count = roam_df['ToMacAddress'].value_counts()
    roamout_count = roam_df['FromMacAddress'].value_counts()
    node_count = {}
    for mac, count in login_count.iteritems():
        node_count[mac] = count
    for mac, count in roamin_count.iteritems():
        if mac in node_count:
            node_count[mac] += count
        else:
            node_count[mac] = count
    for mac, count in roamout_count.iteritems():
        if mac in node_count:
            node_count[mac] -= count
        else:
            node_count[mac] = -1 * count

    # Graphing usng networkx
    G = nx.Graph()

     # Plot edge with weight(no.of roaming) >threshold
    for key in edge_weight:
        if edge_weight[key] > edge_weight_threshold:
            G.add_edge(key[0], key[1], weight=edge_weight[key])

    # Add node weight to the graph
    node_weight = {}
    for mac in node_count:
        tmp = {}
        if node_count[mac] > 0:  #Currently cannot handle node weight < 0 (Node with -ve net change of user)
            tmp['weight'] = node_count[mac]
        else:
            tmp['weight'] = 1
        node_weight[mac] = tmp
    nx.set_node_attributes(G, node_weight)

    #Set Node size and position
    node_size = [node_size_scale * nx.get_node_attributes(G, 'weight')[v] for v in G]
    pos = nx.spring_layout(G, seed=2, iterations=70, k=0.7)

    ## Add Node Position with Spring Layout (Will be substituted with physical location later)
    for node in G.nodes:
        G.nodes[node]['pos'] = list(pos[node])

    ## Plot with Plotly
    # Reference: https://plot.ly/ipython-notebooks/network-graphs/

    # Generate Edge Scatter for Non-Colored Edge
    edge_x = []
    edge_y = []
    for edge in G.edges():
        if edge in edge_weight:
            if (edge_weight[edge] <= color_threshold):
                x0, y0 = G.nodes[edge[0]]['pos']
                x1, y1 = G.nodes[edge[1]]['pos']
                edge_x.append(x0)
                edge_x.append(x1)
                edge_x.append(None)
                edge_y.append(y0)
                edge_y.append(y1)
                edge_y.append(None)

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=1,color='#888'),
        hoverinfo='none',
        mode='lines')

    #Generate Edge Scatter for Colored Edge
    color_edge_x = []
    color_edge_y = []
    for edge in G.edges():
        if edge in edge_weight:
            if (edge_weight[edge]>color_threshold):
                x0, y0 = G.nodes[edge[0]]['pos']
                x1, y1 = G.nodes[edge[1]]['pos']
                color_edge_x.append(x0)
                color_edge_x.append(x1)
                color_edge_x.append(None)
                color_edge_y.append(y0)
                color_edge_y.append(y1)
                color_edge_y.append(None)

    color_edge_trace = go.Scatter(
        x=color_edge_x, y=color_edge_y,
        line=dict(width=1, color='#ff0000'),
        hoverinfo='none',
        mode='lines')

    #Generate Node Scatter for Nodes
    node_x = []
    node_y = []
    for node in G.nodes():
        x, y = G.nodes[node]['pos']
        node_x.append(x)
        node_y.append(y)

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers',
        hoverinfo='text',
        marker=dict(
            showscale=True,
            colorscale='Blues',
            reversescale=False,
            color=[],
            opacity=0.8,
            size=node_size,
            colorbar=dict(
                thickness=15,
                title='No. of Node Connections',
                title_font_size=14,
                xanchor='left',
                titleside='right'
            ),
            line=dict(width=0.6, color="#111")
        )
    )
    #Degree coloring
    node_adjacencies = []
    for node, adjacencies in enumerate(G.adjacency()):
        node_adjacencies.append(len(adjacencies[1]))
    node_trace.marker.color = node_adjacencies



    #Node label
    node_text = []
    for node in G.nodes():
        location = location_df.loc[location_df["APMacAddress"] == node]
        if len(location) ==1:
            location = location.iloc[0][1]
        else:
            location = 'Unknown'
        tmp='Null'
        if node in node_roamout:
            tmp=''
            weight_list = node_roamout[node]
            count = 0
            for dest, weight in weight_list:
                if count > 7:
                    break
                tmp+=str(dest) + "   " + str(weight) + '<br>'
                count+=1
        node_text.append('Mac Address: ' + str(node) + '<br>Location: ' + location + '<br>Roam Out (Destination,Count):<br>' + tmp)
    node_trace.text = node_text

    return {
        'data':[edge_trace, node_trace,color_edge_trace],
        'layout':go.Layout(
                title='<br> Campus Wifi Network Utilization Rate',
                titlefont_size=20 ,
                showlegend=False,
                hovermode='closest',
                hoverdistance = 30,
                dragmode = 'pan',
                plot_bgcolor="#fff",
                margin=dict(b=20, l=5, r=5, t=40),
                annotations=[dict(
                    text="",
                    showarrow=False,
                    xref="paper", yref="paper",
                    x=0.005, y=-0.002)],
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                transition = {'duration': 500},
        )
    }
@app.callback(
    dash.dependencies.Output('time-range-display', 'children'),
    [dash.dependencies.Input('time-slider', 'value')])
def update_output(value):
    start_time, end_time = value
    start_time = str(start_time).zfill(2) + ":00:00"
    end_time = str(end_time).zfill(2) + ":00:00"
    return html.Div("Time Range " + start_time + "    " + end_time,className="label")

if __name__ == '__main__':
    app.run_server(debug=True)