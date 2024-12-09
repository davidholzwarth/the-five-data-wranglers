import dash
from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from config import df_ba_ratings, df_rb_ratings
from src.models.seasonality_analysis import *

#plot_beer_style_ranking_by_amount(df_rb_ratings, df_rb_ratings['style'].unique(),  300, 14)

styles = df_ba_ratings['style'].unique()

# Example function to generate plot based on selected styles
def generate_plot(selected_styles):
    # If no styles are selected, return an empty figure
    if not selected_styles:
        return go.Figure()

    # Create a plotly figure with the selected styles
    fig = go.Figure()
    
    fig = plot_beer_style_ranking_by_amount(df_ba_ratings, selected_styles)
    return fig

# Initialize the Dash app
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Interactive Plot with Checkbox Filtering"),
    
    # Selecting type of plot
    html.Div([
        html.Label('Plot Type:'),
        dcc.RadioItems(
            id='plot-type', 
            options=['One plot', 'Several plots'], 
            value='One plot'),
    ]),
    
    # Graph to display the plot
    dcc.Graph(id="main-plot"),
])

# Define the callback to update the plot based on the selected styles
@app.callback(
    Output("main-plot", "figure"),
    Input("style-checklist", "value")
)

def update_plot(selected_styles):
    return generate_plot(selected_styles)

# Define the callback to save the plot as an HTML file when the button is clicked
@app.callback(
    Output("save-button", "children"),
    Input("plot-type", "value"),
)

def save_plot_as_html(value):
    
    return "Save Plot as HTML"

# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)
