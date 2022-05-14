from dash import Dash, dcc, html, Input, Output, dash_table
import plotly.express as px
import pandas as pd
import numpy as np
import os

app = Dash(__name__)
server = app.server

################### Load and Clean Data #####################

cluster_cluster_csv = "https://raw.githubusercontent.com/mattlucich/data-608-final/first/clusters_cluster.csv"
df_cluster_cluster = pd.read_csv(cluster_cluster_csv)
clusters_clusters_sorted = np.array(list(set(df_cluster_cluster.sort_values(by="cluster")["cluster_broad"])))
clusters_clusters_sorted_list = list(np.sort(clusters_clusters_sorted))

cluster_bar_csv = "https://raw.githubusercontent.com/mattlucich/data-608-final/first/cluster_broad_bar.csv"
df_cluster_bar = pd.read_csv(cluster_bar_csv)
df_visual_bar = df_cluster_bar[['cluster_broad','date_publish', 'outlet', 'headline']]

articles_cluster_csv = "https://raw.githubusercontent.com/mattlucich/data-608-final/first/articles_cluster.csv"
df_articles_cluster = pd.read_csv(articles_cluster_csv)
df_articles_cluster = df_articles_cluster.rename(columns={"date_publish":"Publish", "outlet":"Outlet", "headline":"Headline"})

outlet_total_perc = "https://raw.githubusercontent.com/mattlucich/data-608-final/first/total_outlet_perc.csv"
df_outlet_perc = pd.read_csv(outlet_total_perc)

# Create unique list of cluster numbers, sorted ascending
clusters_sorted = np.array(list(set(df_articles_cluster.sort_values(by="cluster")["cluster"])))
clusters_sorted_list = list(np.sort(clusters_sorted))

# Get all outlets in the dataset, then find which outlets did not cover the news event in cluster 1 (default in dropdown)
all_outlets = set(df_articles_cluster["Outlet"])
default_did_not_cover = all_outlets - set(df_articles_cluster.loc[df_articles_cluster["cluster"] == 1]["Outlet"])
default_did_not_cover_str = ', '.join(default_did_not_cover)

# Trim dataframe to columns we want displayed in visible table
df_articles_cluster_table = df_articles_cluster[["cluster", "Publish", "Outlet", "Headline"]]


################### Event Cluster 3D #####################

fig1 = px.scatter_3d(df_articles_cluster, x='comp1', y='comp2', z='comp3', height=600,
                     color="cluster", hover_data=["Headline"])


################### Broad Cluster 3D #####################

fig2 = px.scatter_3d(df_cluster_cluster, x='comp1', y='comp2', z='comp3', height=600,
                    color="cluster_broad", hover_data=["cluster_terms_str","headline"])


################### Bar chart #####################

fig3 = px.histogram(df_visual_bar.loc[df_visual_bar["cluster_broad"]==0], x="outlet", 
            histnorm='probability density', title="Number of Articles by Outlet")

fig3.add_scatter(x=df_outlet_perc["outlet"].to_list(), 
                y=df_outlet_perc["Outlet_Perc"].to_list(), 
                name="Perc of DB", mode="markers", row=1, col=1)

fig3.update_layout(barmode='relative', xaxis={'categoryorder':'total descending'},
                yaxis_title="Percent of Articles on Topic", xaxis_title="Outlet")


################## App Layout ####################

app.layout = html.Div(children=[
    html.H1(children='MEDIA BIAS', 
            style={"margin-left": "2rem", "font-family": "Tahoma", "color": "#142d4c"}),

    html.Div(children='''Detecting Event Selection''', 
            style={"margin-left": "2rem", "margin-top": "-1.1rem", "font-size": "1.25rem",
                    "font-family": "Tahoma", "color": "#385170"}),

    html.H2(children='Clusters of Articles into News Events', 
            style={"margin-left": "2rem", 'text-align':'center', "font-family": "Tahoma", "color": "#142d4c"}),

    dcc.Graph(
        id='article-cluster-3d',
        figure=fig1
    ),

    html.Div(children='Select Cluster:', 
            style={"margin-left": "2rem", "font-size": "1.25rem", "font-weight": "bold",
                    "font-family": "Tahoma", "color": "#385170"}),

    dcc.Dropdown(clusters_sorted_list, 1, id='cluster-dropdown', 
                style={"width": "50%", "margin-top": "1rem","margin-bottom": "1rem", 
                        "margin-left": "1rem", "font-family": "Tahoma"}),

    html.Div(children='Top News Event Terms:', 
            style={"margin-left": "2rem", "font-size": "1.25rem", "font-weight": "bold", "padding-bottom": "1rem",
                    "font-family": "Tahoma", "color": "#385170"}),

    html.Div(children=df_articles_cluster.loc[df_articles_cluster["cluster"] == 1]["cluster_terms_str"].values[0], 
            id='top-terms-cluster', 
            style={"margin-left": "2rem", "font-size": "1.25rem", "padding-bottom": "1rem",
                    "font-family": "Tahoma", "color": "#385170"}),

    html.Div(children='Did Not Cover:', 
            style={"margin-left": "2rem", "font-size": "1.25rem", "font-weight": "bold", "padding-bottom": "1rem",
                    "font-family": "Tahoma", "color": "#385170"}),

    html.Div(children=default_did_not_cover_str, 
            id='did-not-cover', 
            style={"margin-left": "2rem", "font-size": "1.25rem", "padding-bottom": "1rem",
                    "font-family": "Tahoma", "color": "#385170"}),

    dash_table.DataTable(df_articles_cluster_table[df_articles_cluster_table["cluster"]==1].drop(columns=['cluster']).to_dict('records'), 
                                [{"name": i, "id": i} for i in df_articles_cluster_table.drop(columns=['cluster']).columns],
                                id="covered-table",
                                style_header={'backgroundColor': 'rgb(210, 210, 210)','color': 'black',
                                            'fontWeight': 'bold', "font-family": "Tahoma"},
                                style_cell={"font-family": "Tahoma"},
                                style_table={"margin-left": "2rem", "font-size": ".85rem", "width": "1300px",
                                            "padding-bottom": "1rem", "font-family": "Tahoma", "color": "#385170"}),

    html.H2(children='Clusters of News Events into Topics', 
            style={"margin-left": "2rem", 'text-align':'center', "font-family": "Tahoma", "color": "#142d4c"}),


    dcc.Graph(
        id='cluster-cluster-3d',
        figure=fig2
    ),

    html.Div(children='Select Topic Cluster:', 
            style={"margin-left": "2rem", "font-size": "1.25rem", "font-weight": "bold",
                    "font-family": "Tahoma", "color": "#385170"}),

    dcc.Dropdown(clusters_clusters_sorted_list, 0, id='cluster-broad-dropdown', 
                style={"width": "50%", "margin-top": "1rem","margin-bottom": "1rem", 
                        "margin-left": "1rem", "font-family": "Tahoma"}),

    dcc.Graph(
        id='bar-broad-cluster',
        figure=fig3
    ),

    html.Div(children='Brought to you by Matthew L.', 
        style={"margin-top": "3rem", "font-size": ".75rem", 'text-align':'center', 
            "font-family": "Tahoma", "color": "#03045e"}),

])


################## Update Top Terms ####################

@app.callback(
    Output('top-terms-cluster', 'children'),
    Input('cluster-dropdown', 'value'))
def update_top_terms(cluster_drop):
    df_articles_cluster_filter = df_articles_cluster.loc[df_articles_cluster["cluster"] == cluster_drop]
    top_terms_str = df_articles_cluster_filter["cluster_terms_str"].values[0]

    return top_terms_str


################## Update Outlets That Did Not Cover ####################

@app.callback(
    Output('did-not-cover', 'children'),
    Input('cluster-dropdown', 'value'))
def update_did_not_cover(cluster_drop):
    default_did_not_cover = all_outlets - set(df_articles_cluster.loc[df_articles_cluster["cluster"] == cluster_drop]["Outlet"])
    default_did_not_cover_str = ', '.join(default_did_not_cover)
    return default_did_not_cover_str


################## Update Data Table ####################

@app.callback(
    Output('covered-table', 'data'),
    Input('cluster-dropdown', 'value'))
def update_data_table(cluster_drop):
    df_table_filtered = df_articles_cluster_table[df_articles_cluster_table["cluster"]==cluster_drop].drop(columns=['cluster']).to_dict('records')
    return df_table_filtered


################## Update Bar Chart ####################

@app.callback(
    Output('bar-broad-cluster', 'figure'),
    Input('cluster-broad-dropdown', 'value'))
def update_bar_chart(cluster_drop):
    fig3 = px.histogram(df_visual_bar.loc[df_visual_bar["cluster_broad"]==cluster_drop], x="outlet", 
                histnorm='probability density', title="Number of Articles by Outlet")

    fig3.add_scatter(x=df_outlet_perc["outlet"].to_list(), 
                    y=df_outlet_perc["Outlet_Perc"].to_list(), 
                    name="Perc of DB", mode="markers", row=1, col=1)

    fig3.update_layout(barmode='relative', xaxis={'categoryorder':'total descending'},
                    yaxis_title="Percent of Articles on Topic", xaxis_title="Outlet")

    return fig3


if __name__ == '__main__':
    app.run_server(debug=True)