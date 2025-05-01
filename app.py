from dash import Dash, dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc
from utils.data_loader import load_and_process_data
from utils.figures import create_fuel_trend_line_chart, create_fuel_composition_pie, create_pm25_ev_chart
from utils.components import create_controls, create_summary_cards
import plotly.express as px  # Add this import at the top

from dash import Dash, dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc
import plotly.express as px
from utils.data_loader import load_and_process_data
from utils.figures import create_fuel_trend_line_chart, create_fuel_composition_pie, create_pm25_ev_chart
from utils.components import create_controls, create_summary_cards

# Load all data
data = load_and_process_data()
vehicle_df = data['vehicle_data']
combined_df = data['combined_data']

# Initialize app
app = Dash(__name__, external_stylesheets=[dbc.themes.LUX])
app.title = "Transportation Trends in California"

# Define consistent colors
COLORS = {
    'Electric': '#2ca02c',  # Green for electric
    'Gasoline': '#ff7f0e',  # Orange for gasoline
    'Diesel': '#1f77b4',  # Blue for diesel
    'Hybrid': '#9467bd',  # Purple for hybrid
    'Other': '#7f7f7f'  # Gray for others
}

# Create layout
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("Transportation Trends in California", className="my-4")),
        dbc.Row(html.H5("Allie Peterson", className="my-1")),
        dbc.Row(html.H5("CS150 Community Action Computing, Westmont College", className="my-1")),
    ]),

    dbc.Row(create_summary_cards(vehicle_df), className="mb-4"),

    dbc.Row([
        # Left column - Filters and summary cards
        dbc.Col([
            # Filters card
            create_controls(vehicle_df),

            # Data summary card
            dbc.Card([
                dbc.CardBody([
                    html.H4("Data Summary", className="card-title"),
                    html.Hr(),
                    html.Div(id='data-summary')
                ])
            ], className="shadow-sm mb-4"),

            # Horizontal bar chart card
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(id='composition-chart')
                ])
            ], className="shadow-sm")
        ], width=3, className="pe-3"),

        # Right column - Main content
        dbc.Col([
            # Main trend chart
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(
                        id='trend-chart',
                        figure=create_fuel_trend_line_chart(vehicle_df)
                    )
                ])
            ], className="mb-4 shadow-sm"),

            # PM2.5 EV chart
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(
                        id='pm25-ev-chart',
                        figure=create_pm25_ev_chart(combined_df)
                    )
                ])
            ], className="shadow-sm")
        ], width=9)
    ])
], fluid=True)


# Callbacks
@callback(
    Output('trend-chart', 'figure'),
    Output('composition-chart', 'figure'),
    Output('data-summary', 'children'),
    Input('fuel-type-dropdown', 'value'),
    Input('year-slider', 'value')
)
def update_charts(selected_fuels, year_range):
    filtered_df = vehicle_df.copy()

    # Apply fuel type filter
    if selected_fuels:
        filtered_df = filtered_df[filtered_df['Fuel'].isin(selected_fuels)]

    # Apply year range filter
    filtered_df = filtered_df[
        (filtered_df['year'] >= year_range[0]) &
        (filtered_df['year'] <= year_range[1])
        ]

    # Create figures with consistent coloring
    line_fig = create_fuel_trend_line_chart(filtered_df)

    # Update colors for all charts to make Electric consistently green
    for trace in line_fig.data:
        if 'Electric' in trace.name:
            trace.line.color = COLORS['Electric']

    # Create horizontal bar chart with consistent coloring
    year_df = filtered_df[filtered_df['year'] == year_range[1]]
    if not year_df.empty:
        year_df['Percentage'] = (year_df['Vehicles'] / year_df['Vehicles'].sum()) * 100

        # Assign colors based on fuel type
        year_df['Color'] = year_df['Fuel'].apply(
            lambda x: COLORS['Electric'] if 'Electric' in x
            else COLORS.get(x.split()[0], COLORS['Other'])
        )

        bar_fig = px.bar(
            year_df.sort_values('Percentage', ascending=True),
            x='Percentage',
            y='Fuel',
            orientation='h',
            title=f'Fuel Composition ({year_range[1]})',
            labels={'Percentage': 'Percentage (%)', 'Fuel': 'Fuel Type'},
            color='Fuel',
            color_discrete_map={
                fuel: COLORS['Electric'] if 'Electric' in fuel else COLORS.get(fuel.split()[0], COLORS['Other'])
                for fuel in year_df['Fuel'].unique()
            },
            height=400
        )
        bar_fig.update_layout(showlegend=False)
    else:
        bar_fig = px.bar(title="No data available")

    # Create summary with electric vehicle emphasis
    if filtered_df.empty:
        summary = "No data available for selected filters"
    else:
        total = filtered_df['Vehicles'].sum() / 1_000_000
        electric_total = filtered_df[filtered_df['Fuel'].str.contains('Electric')]['Vehicles'].sum() / 1_000_000
        year_min, year_max = filtered_df['year'].min(), filtered_df['year'].max()
        fuels = len(filtered_df['Fuel'].unique())

        summary = [
            html.P(f"📅 Years: {year_min} to {year_max}"),
            html.P(f"🚗 Total Vehicles: {total:,.2f} million"),
            html.P(f"🔌 Electric Vehicles: {electric_total:,.2f} million", style={'color': COLORS['Electric']}),
            html.P(f"⛽ Fuel Types: {fuels}"),
            html.P(f"📊 Data Points: {len(filtered_df)}")
        ]

    return line_fig, bar_fig, summary


if __name__ == '__main__':
    app.run(debug=True)