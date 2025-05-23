"""
Visualization components for displaying analysis results.
"""
import plotly.graph_objects as go
import streamlit as st
from .config import SENTIMENT_COLORS

def create_sentiment_chart(sentiment_score):
    """
    Create a sentiment score visualization with Plotly.
    
    Args:
        sentiment_score: Sentiment score (0-100)
        
    Returns:
        Plotly figure object
    """
    fig = go.Figure()
    
    # Add the three colored segments
    fig.add_trace(
        go.Bar(
            y=["Sentiment"], 
            x=[SENTIMENT_COLORS[0][1]], 
            orientation="h", 
            marker=dict(color=SENTIMENT_COLORS[0][2]), 
            showlegend=False, 
            hoverinfo="skip"
        )
    )
    fig.add_trace(
        go.Bar(
            y=["Sentiment"], 
            x=[SENTIMENT_COLORS[1][1] - SENTIMENT_COLORS[0][1]], 
            orientation="h", 
            marker=dict(color=SENTIMENT_COLORS[1][2]), 
            showlegend=False, 
            hoverinfo="skip"
        )
    )
    fig.add_trace(
        go.Bar(
            y=["Sentiment"], 
            x=[SENTIMENT_COLORS[2][1] - SENTIMENT_COLORS[1][1]], 
            orientation="h", 
            marker=dict(color=SENTIMENT_COLORS[2][2]), 
            showlegend=False, 
            hoverinfo="skip"
        )
    )
    
    # Add marker for the score
    fig.add_shape(
        type="line", 
        x0=sentiment_score, 
        x1=sentiment_score, 
        y0=-0.4, 
        y1=0.4, 
        line=dict(color="white", width=3)
    )
    
    # Add label for the score
    fig.add_annotation(
        x=sentiment_score, 
        y=0, 
        text=f"<b>{sentiment_score:.1f}</b>", 
        showarrow=False, 
        yshift=-25, 
        font=dict(color="white", size=14), 
        bgcolor="rgba(0,0,0,0.7)"
    )
    
    # Layout settings
    fig.update_layout(
        barmode="stack", 
        height=120, 
        margin=dict(l=10, r=10, t=40, b=20),
        xaxis=dict(
            range=[0, 100], 
            showticklabels=False, 
            fixedrange=True, 
            zeroline=False, 
            showgrid=False
        ),
        yaxis=dict(
            showticklabels=False, 
            fixedrange=True, 
            showgrid=False
        ),
        paper_bgcolor="rgba(0,0,0,0)", 
        plot_bgcolor="rgba(0,0,0,0)"
    )
    
    return fig

def create_topics_chart(topic_scores):
    """
    Create a radar chart for topic scores.
    
    Args:
        topic_scores: Dictionary of category scores
        
    Returns:
        Plotly figure object
    """
    # Extract and prepare data
    labels, values, evidence = [], [], []
    
    for cat, data in topic_scores.items():
        labels.append(cat.replace("_", " ").title())
        values.append(data.get("score", 0))
        evidence.append("<br>".join(data.get("evidence", [])) or "No sample tweets.")
    
    # Create radar chart
    fig = go.Figure(
        go.Scatterpolar(
            r=values, 
            theta=labels, 
            fill="toself", 
            customdata=evidence,
            hovertemplate="<b>%{theta}</b>: %{r:.1f}/100<br>%{customdata}<extra></extra>"
        )
    )
    
    # Layout settings
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                range=[0, 100], 
                showticklabels=False, 
                ticks=""
            ), 
            angularaxis=dict(direction="clockwise")
        ),
        showlegend=False, 
        height=420, 
        margin=dict(l=40, r=40, t=40, b=40),
        paper_bgcolor="rgba(0,0,0,0)", 
        plot_bgcolor="rgba(0,0,0,0)"
    )
    
    return fig 