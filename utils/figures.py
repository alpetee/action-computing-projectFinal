import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go

def create_fuel_trend_line_chart(df):
    """Create line chart of vehicle trends by fuel type"""
    if df.empty:
        return px.line(title="No Data Available")

    # Convert to millions for display
    chart_df = df.copy()
    chart_df['Vehicles (millions)'] = chart_df['Vehicles'] / 1_000_000

    fig = px.line(
        chart_df,
        x='year',
        y='Vehicles (millions)',
        color='Fuel',
        title='Vehicle Trends by Fuel Type',
        labels={'Vehicles (millions)': 'Vehicles (millions)', 'year': 'Year'},
        template='plotly_white'
    )

    fig.update_layout(
        hovermode='x unified',
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1
        ),
        margin=dict(l=50, r=50, b=50, t=80),
        height=500
    )

    # Remove the range slider
    fig.update_xaxes(dtick=1, rangeslider_visible=False)
    return fig


def create_fuel_composition_pie(df, year):
    """Create pie chart of fuel composition for specific year"""
    if df.empty:
        return px.pie(title="No Data Available")

    year_df = df[df['year'] == year].copy()
    if year_df.empty:
        return px.pie(title=f"No Data for {year}")

    year_df['Vehicles (millions)'] = year_df['Vehicles'] / 1_000_000

    fig = px.pie(
        year_df,
        values='Vehicles (millions)',
        names='Fuel',
        title=f'Fuel Composition ({year})',
        hole=0.4,
        template='plotly_white'
    )

    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        insidetextfont=dict(size=12)
    )

    fig.update_layout(
        uniformtext_minsize=12,
        uniformtext_mode='hide',
        height=500
    )

    return fig


def create_pm25_ev_chart(combined_df):
    """Create dual-axis line chart for PM2.5 and Electric Vehicles over time"""
    if combined_df.empty or len(combined_df) < 2:
        return go.Figure()

    # Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Add EV line (primary y-axis)
    fig.add_trace(
        go.Scatter(
            x=combined_df['year'],
            y=combined_df['Vehicles'] / 1000,  # Show in thousands
            name="Electric Vehicles (thousands)",
            line=dict(color='#2ca02c', width=3),
            mode='lines+markers',
            marker=dict(size=8)
        ),
        secondary_y=False,
    )

    # Add PM2.5 line (secondary y-axis)
    fig.add_trace(
        go.Scatter(
            x=combined_df['year'],
            y=combined_df['Avg PM2.5'],
            name="Avg PM2.5 (µg/m³)",
            line=dict(color='#d62728', width=3),
            mode='lines+markers',
            marker=dict(size=8, symbol='diamond')
        ),
        secondary_y=True,
    )

    # Update layout
    fig.update_layout(
        title_text="Electric Vehicles and PM2.5 Trends Over Time",
        hovermode='x unified',
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1
        ),
        margin=dict(l=50, r=50, b=50, t=80),
        height=500,
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(
            showgrid=True,
            gridcolor='white',
            dtick=1  # Show every year
        )
    )

    # Set y-axes titles and styling
    fig.update_yaxes(
        title_text="Electric Vehicles (thousands)",
        secondary_y=False,
        gridcolor='white'
    )
    fig.update_yaxes(
        title_text="Average PM2.5 (µg/m³)",
        secondary_y=True,
        gridcolor='white'
    )

    # Remove the range slider
    fig.update_xaxes(
        rangeslider_visible=False
    )

    return fig
