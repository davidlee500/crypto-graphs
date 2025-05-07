import plotly.graph_objs as go
from datetime import datetime
import logging
import pandas as pd
from typing import Optional

def create_scatter_plot(df: pd.DataFrame, output_file: str, title: str) -> None:
    """Create an interactive scatter plot."""
    if df.empty:
        logging.error("No data to plot. DataFrame is empty.")
        return
        
    # Create color gradient based on percentage change
    colors = df['percent_change'].apply(lambda x: 
        f'rgba(255,0,0,{min(abs(x)/100, 1)})' if x < 0 
        else f'rgba(0,0,255,{min(abs(x)/100, 1)})'
    )
    
    # Create trace
    trace = go.Scatter(
        x=df['market_cap'],
        y=df['percent_change'],
        mode='markers',
        marker=dict(
            size=12,
            color=colors,
            opacity=0.8,
            line=dict(width=1, color='black')
        ),
        hovertemplate=(
            "<b>%{customdata[0]}</b><br>" +
            "Market Cap: %{customdata[1]}<br>" +
            "Nov 4 Price: %{customdata[2]}<br>" +
            "Current Price: %{customdata[3]}<br>" +
            "Change: %{customdata[4]}%<extra></extra>"
        ),
        customdata=df[['name', 'market_cap_formatted', 'start_price_formatted', 
                       'current_price_formatted', 'percent_change_rounded']].values
    )
    
    # Create zero line
    zero_line = go.Scatter(
        x=[df['market_cap'].min(), df['market_cap'].max()],
        y=[0, 0],
        mode='lines',
        line=dict(color='black', width=1, dash='dash'),
        showlegend=False
    )
    
    # Create layout
    layout = go.Layout(
        title=title,
        xaxis=dict(
            title="Market Cap (USD, Nov 4, 2024)",
            type="log",
            showgrid=True
        ),
        yaxis=dict(
            title="Percent Price Change (log scale)",
            type="log",
            showgrid=True,
            ticktext=['-1000%', '-100%', '-10%', '0%', '10%', '100%', '1000%'],
            tickvals=[-1000, -100, -10, 0, 10, 100, 1000]
        ),
        showlegend=False,
        hovermode='closest',
        template="simple_white",
        annotations=[{
            'text': 'Color intensity indicates magnitude of change',
            'showarrow': False,
            'xref': 'paper',
            'yref': 'paper',
            'x': 0,
            'y': 1.05
        }]
    )
    
    # Create figure
    fig = go.Figure(data=[trace, zero_line], layout=layout)
    
    # Save to HTML
    try:
        fig.write_html(
            output_file,
            include_plotlyjs='cdn',
            full_html=True,
            include_mathjax=False,
            config={'displayModeBar': False}
        )
        logging.info(f"Chart saved to {output_file}")
    except Exception as e:
        logging.error(f"Error saving chart: {e}")
        raise 