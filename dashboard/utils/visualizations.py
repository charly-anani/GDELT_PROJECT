import plotly.graph_objects as go
import plotly.express as px

PLOTLY_THEME_TEMPLATE = "plotly_dark"
COLOR_PALETTE = {
    "primary": "#58a6ff",   # Soft blue
    "secondary": "#3fb950", # Soft green (Cooperation)
    "danger": "#ff7b72",    # Soft red (Conflict/Risk)
    "warning": "#d29922",   # Orange (Warning)
    "background": "rgba(0,0,0,0)", # Transparent
    "paper_bg": "rgba(0,0,0,0)",
    "gridline": "rgba(255,255,255,0.05)",
    "text": "#c9d1d9"
}

def apply_premium_layout(fig):
    fig.update_layout(
        template=PLOTLY_THEME_TEMPLATE,
        plot_bgcolor=COLOR_PALETTE["background"],
        paper_bgcolor=COLOR_PALETTE["paper_bg"],
        font=dict(family="Inter, sans-serif", color=COLOR_PALETTE["text"], size=12),
        margin=dict(l=10, r=10, t=40, b=10),
        xaxis=dict(showgrid=True, gridcolor=COLOR_PALETTE["gridline"], zeroline=False),
        yaxis=dict(showgrid=True, gridcolor=COLOR_PALETTE["gridline"], zeroline=False),
        hoverlabel=dict(bgcolor="#161b22", font_size=13, font_family="Inter", bordercolor="#30363d")
    )
    return fig

def create_timeline_chart(df, date_col, value_col, title, color="primary"):
    fig = px.area(
        df, x=date_col, y=value_col, title=title,
        color_discrete_sequence=[COLOR_PALETTE.get(color, color)]
    )
    fig.update_traces(fillcolor=f'rgba{tuple(int(COLOR_PALETTE.get(color, color).lstrip("#")[i:i+2], 16) for i in (0, 2, 4)) + (0.2,)}', line=dict(width=3))
    return apply_premium_layout(fig)

def create_donut_chart(df, names_col, values_col, title, colors=None):
    if colors is None:
        colors = [COLOR_PALETTE['primary'], COLOR_PALETTE['secondary'], COLOR_PALETTE['warning'], COLOR_PALETTE['danger']]
    fig = px.pie(df, names=names_col, values=values_col, hole=0.6, title=title, color_discrete_sequence=colors)
    fig.update_traces(textposition='inside', textinfo='percent', hovertemplate="<b>%{label}</b><br>Value: %{value:,}<br>Share: %{percent}<extra></extra>")
    fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5))
    return apply_premium_layout(fig)
