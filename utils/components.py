import dash_bootstrap_components as dbc
from dash import dcc, html


def create_controls(df):
    """Create interactive controls for dashboard"""
    if df.empty:
        years = []
        fuels = []
    else:
        years = sorted(df['year'].unique())
        fuels = sorted(df['Fuel'].unique())

    return dbc.Card([
        dbc.CardBody([
            html.H4("Filters", className="card-title"),
            html.Hr(),

            html.Label("Fuel Types", className="font-weight-bold"),
            dcc.Dropdown(
                id='fuel-type-dropdown',
                options=[{'label': f, 'value': f} for f in fuels],
                value=fuels[:3] if fuels else [],
                multi=True,
                placeholder="Select fuel types"
            ),

            html.Br(),

            html.Label("Year Range", className="font-weight-bold"),
            dcc.RangeSlider(
                id='year-slider',
                min=min(years) if years else 0,
                max=max(years) if years else 0,
                value=[min(years), max(years)] if years else [0, 0],
                marks={str(y): str(y) for y in years},
                step=1
            )
        ])
    ], className="shadow-sm")


def create_summary_cards(df):
    """Create summary cards for dashboard"""
    if df.empty:
        return []

    latest_year = df['year'].max()
    latest_data = df[df['year'] == latest_year]

    cards = [
        dbc.Col(
            dbc.Card([
                dbc.CardBody([
                    html.H6("Total Vehicles", className="card-title"),
                    html.H4(
                        f"{latest_data['Vehicles'].sum() / 1_000_000:,.1f}M",
                        className="card-text text-primary"
                    ),
                    html.Small(f"in {latest_year}", className="text-muted")
                ])
            ], className="border-primary shadow-sm"),
            width=3
        )
    ]

    for fuel_type in ['Electric', 'Hybrid', 'Gasoline']:
        filtered = latest_data[latest_data['Fuel'].str.contains(fuel_type)]
        total = filtered['Vehicles'].sum() / 1_000_000 if not filtered.empty else 0

        color = {
            'Electric': 'success',
            'Hybrid': 'info',
            'Gasoline': 'warning'
        }.get(fuel_type, 'secondary')

        cards.append(
            dbc.Col(
                dbc.Card([
                    dbc.CardBody([
                        html.H6(f"{fuel_type} Vehicles", className="card-title"),
                        html.H4(
                            f"{total:,.1f}M",
                            className=f"card-text text-{color}"
                        ),
                        html.Small(f"in {latest_year}", className="text-muted")
                    ])
                ], className=f"border-{color} shadow-sm"),
                width=3
            )
        )

    return cards