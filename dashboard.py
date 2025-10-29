import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from scipy import stats
import logging
from datetime import datetime
from database import CreatineDatabase
import dash_bootstrap_components as dbc

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Color scheme
COLORS = {
    'creatine': '#4169E1',  # Royal blue
    'placebo': '#FF6B6B'    # Coral red
}

class CreatineDashboard:
    def __init__(self, db: CreatineDatabase):
        """Initialize dashboard with database connection."""
        self.db = db
        self.app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
        self.setup_layout()
        self.setup_callbacks()
        logger.info("Dashboard initialized")

    def setup_layout(self):
        """Set up the dashboard layout."""
        self.app.layout = dbc.Container([
            # Header
            dbc.Row([
                dbc.Col([
                    html.H1("Creatine Supplementation Study", className="mb-1"),
                    html.P("Changes in lean mass over 4 weeks by group and cohort", 
                           className="text-muted mb-0")
                ], width=9),
                dbc.Col([
                    html.Label("Outcome", className="text-muted small"),
                    dcc.Dropdown(
                        id='metric-selector',
                        options=[
                            {'label': 'Strength (1RM)', 'value': 'strength_1rm_kg'},
                            {'label': 'Lean Mass', 'value': 'lean_mass_kg'},
                            {'label': 'Performance Score', 'value': 'performance_score'}
                        ],
                        value='lean_mass_kg',
                        clearable=False
                    )
                ], width=3)
            ], className="mb-4"),

            # KPI Strip
            dbc.Row([
                dbc.Col([
                    html.Div(id='kpi-strip', className="mb-4")
                ], width=12)
            ]),
            
            # Progression Chart
            dbc.Row([
                dbc.Col([
                    html.H5("Lean Mass Over Time (kg)", className="mb-2"),
                    dcc.Graph(id='progression-chart', style={'height': '400px'})
                ], width=12)
            ], className="mb-4"),

            # Comparison Charts
            dbc.Row([
                dbc.Col([
                    html.H5("Results by Age Group", className="mb-2"),
                    dcc.Graph(id='age-comparison-chart', style={'height': '400px'})
                ], width=6),
                dbc.Col([
                    html.H5("Results by Training Status", className="mb-2"),
                    dcc.Graph(id='training-impact-chart', style={'height': '400px'})
                ], width=6)
            ], className="mb-4"),

            # Summary Table
            dbc.Row([
                dbc.Col([
                    html.H5("Summary Statistics", className="mb-3"),
                    html.P("Summary statistics for selected filters (kg)", 
                           className="text-muted small mb-3"),
                    html.Div(id='summary-stats')
                ], width=12)
            ]),
            
            # Footer
            dbc.Row([
                dbc.Col([
                    html.Hr(),
                    html.P("Data source: SQLite database | Dashboard v1.0 | " + 
                           f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                           className="text-muted small text-center")
                ], width=12)
            ], className="mt-4")
        ], fluid=True, style={'padding': '24px'})

    def setup_callbacks(self):
        """Set up dashboard callbacks."""
        @self.app.callback(
            [Output('kpi-strip', 'children'),
             Output('progression-chart', 'figure'),
             Output('age-comparison-chart', 'figure'),
             Output('training-impact-chart', 'figure'),
             Output('summary-stats', 'children')],
            [Input('metric-selector', 'value')]
        )
        def update_charts(metric):
            try:
                # Get data
                progress_data = self.db.get_progress_data()
                
                # Calculate KPIs
                kpi_cards = self._calculate_kpis(progress_data, metric)
                
                # Progression Chart with uncertainty
                prog_fig = self._create_progression_chart(progress_data, metric)

                # Age Comparison Chart
                age_fig = self._create_age_chart(progress_data, metric)

                # Training Impact Chart
                training_fig = self._create_training_chart(progress_data, metric)
                
                # Summary Statistics Table
                stats_table = self._create_summary_table(progress_data, metric)

                return kpi_cards, prog_fig, age_fig, training_fig, stats_table
            except Exception as e:
                logger.error(f"Error updating dashboard: {e}")
                raise

    def _calculate_kpis(self, data: pd.DataFrame, metric: str) -> list:
        """Calculate key performance indicators."""
        # Get final measurements for each participant
        final_data = data.groupby('participant_id').last().reset_index()
        
        # Calculate statistics by group
        creatine_data = final_data[final_data['group_assignment'] == 'creatine'][metric]
        placebo_data = final_data[final_data['group_assignment'] == 'placebo'][metric]
        
        creatine_mean = creatine_data.mean()
        placebo_mean = placebo_data.mean()
        delta = creatine_mean - placebo_mean
        
        creatine_std = creatine_data.std()
        placebo_std = placebo_data.std()
        pooled_std = np.sqrt((creatine_std**2 + placebo_std**2) / 2)
        cohens_d = delta / pooled_std if pooled_std > 0 else 0
        
        # Perform t-test
        t_stat, p_value = stats.ttest_ind(creatine_data, placebo_data)
        
        # Calculate 95% CI
        creatine_se = creatine_std / np.sqrt(len(creatine_data))
        placebo_se = placebo_std / np.sqrt(len(placebo_data))
        ci_lower = delta - 1.96 * pooled_std / np.sqrt(len(creatine_data))
        ci_upper = delta + 1.96 * pooled_std / np.sqrt(len(creatine_data))
        
        # Create KPI cards
        return dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("Group Difference (Δ)", className="text-muted small mb-1"),
                        html.H3(f"{delta:+.2f} kg", className="mb-0"),
                        html.P(f"95% CI: [{ci_lower:.2f}, {ci_upper:.2f}]", 
                               className="text-muted small mb-0")
                    ])
                ], className="text-center h-100")
            ], width=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("Effect Size", className="text-muted small mb-1"),
                        html.H3(f"{cohens_d:.2f}", className="mb-0"),
                        html.P(self._interpret_effect_size(cohens_d), 
                               className="text-muted small mb-0")
                    ])
                ], className="text-center h-100")
            ], width=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("p-value", className="text-muted small mb-1"),
                        html.H3(f"{p_value:.4f}", className="mb-0"),
                        html.P("t-test", className="text-muted small mb-0")
                    ])
                ], className="text-center h-100")
            ], width=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("Sample Size", className="text-muted small mb-1"),
                        html.H3(f"{len(creatine_data)}/{len(placebo_data)}", className="mb-0"),
                        html.P("Creatine / Placebo", className="text-muted small mb-0")
                    ])
                ], className="text-center h-100")
            ], width=3)
        ])
    
    def _interpret_effect_size(self, d: float) -> str:
        """Interpret Cohen's d effect size."""
        abs_d = abs(d)
        if abs_d < 0.2:
            return "Negligible"
        elif abs_d < 0.5:
            return "Small"
        elif abs_d < 0.8:
            return "Medium"
        else:
            return "Large"
    
    def _get_rgba(self, hex_color: str, alpha: float) -> str:
        """Convert hex color to rgba string."""
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        return f'rgba({r}, {g}, {b}, {alpha})'
    
    def _create_progression_chart(self, data: pd.DataFrame, metric: str) -> go.Figure:
        """Create progression chart with uncertainty bands."""
        fig = go.Figure()
        
        # Group data by date and calculate statistics
        for group in ['creatine', 'placebo']:
            group_data = data[data['group_assignment'] == group]
            summary = group_data.groupby('measurement_date')[metric].agg(['mean', 'std', 'count']).reset_index()
            summary['sem'] = summary['std'] / np.sqrt(summary['count'])
            
            # Add confidence band first (so it's behind the line)
            fig.add_trace(go.Scatter(
                x=list(summary['measurement_date']) + list(summary['measurement_date'])[::-1],
                y=list(summary['mean'] + summary['sem'] * 1.96) + list(summary['mean'] - summary['sem'] * 1.96)[::-1],
                fill='toself',
                fillcolor=self._get_rgba(COLORS[group], 0.15),
                line=dict(color='rgba(255,255,255,0)'),
                hoverinfo='skip',
                showlegend=False,
                legendgroup=group
            ))
            
            # Add line on top
            fig.add_trace(go.Scatter(
                x=summary['measurement_date'],
                y=summary['mean'],
                mode='lines+markers',
                name=group.capitalize(),
                line=dict(color=COLORS[group], width=2),
                marker=dict(size=8),
                error_y=dict(type='data', array=summary['sem'] * 1.96, visible=True),
                legendgroup=group
            ))
        
        # Get metric label
        metric_label = metric.replace('_', ' ').title()
        
        fig.update_layout(
            height=400,
            autosize=False,
            margin=dict(l=60, r=20, t=20, b=60),
            showlegend=True,
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
            xaxis_title="Measurement Date",
            yaxis_title=f"{metric_label} (kg)"
        )
        
        return fig
    
    def _create_age_chart(self, data: pd.DataFrame, metric: str) -> go.Figure:
        """Create age group comparison chart."""
        data_copy = data.copy()
        data_copy['age_group'] = pd.cut(data_copy['age'], 
                                        bins=[0, 30, 100],
                                        labels=['Young', 'Older'])
        
        fig = go.Figure()
        
        for group in ['creatine', 'placebo']:
            group_data = data_copy[data_copy['group_assignment'] == group]
            
            for age_group in ['Young', 'Older']:
                age_data = group_data[group_data['age_group'] == age_group][metric]
                n = len(age_data)
                
                if n > 0:
                    fig.add_trace(go.Box(
                        y=age_data,
                        name=age_group,
                        legendgroup=group,
                        legendgrouptitle_text=group.capitalize(),
                        marker_color=COLORS[group],
                        hovertemplate=f'{group.capitalize()} - {age_group}<br>' +
                                    f'Mean: {age_data.mean():.2f}<br>' +
                                    f'N: {n}<extra></extra>'
                    ))
        
        metric_label = metric.replace('_', ' ').title()
        
        fig.update_layout(
            height=400,
            autosize=False,
            boxmode='group',
            showlegend=True,
            margin=dict(l=60, r=20, t=20, b=60),
            xaxis_title="Age Group",
            yaxis_title=f"{metric_label} (kg)"
        )
        
        return fig
    
    def _create_training_chart(self, data: pd.DataFrame, metric: str) -> go.Figure:
        """Create training status comparison chart."""
        fig = go.Figure()
        
        for group in ['creatine', 'placebo']:
            group_data = data[data['group_assignment'] == group]
            
            for status in ['trained', 'untrained']:
                status_data = group_data[group_data['training_status'] == status][metric]
                n = len(status_data)
                
                if n > 0:
                    fig.add_trace(go.Box(
                        y=status_data,
                        name=status.capitalize(),
                        legendgroup=group,
                        legendgrouptitle_text=group.capitalize(),
                        marker_color=COLORS[group],
                        hovertemplate=f'{group.capitalize()} - {status}<br>' +
                                    f'Mean: {status_data.mean():.2f}<br>' +
                                    f'N: {n}<extra></extra>'
                    ))
        
        metric_label = metric.replace('_', ' ').title()
        
        fig.update_layout(
            height=400,
            autosize=False,
            boxmode='group',
            showlegend=True,
            margin=dict(l=60, r=20, t=20, b=60),
            xaxis_title="Training Status",
            yaxis_title=f"{metric_label} (kg)"
        )
        
        return fig
    
    def _create_summary_table(self, data: pd.DataFrame, metric: str) -> html.Div:
        """Create summary statistics table."""
        stats = data.groupby('group_assignment')[metric].agg([
            'mean', 'std', 'count'
        ]).round(2)
        
        stats['mean_std'] = stats['mean'].astype(str) + ' ± ' + stats['std'].astype(str)
        
        table_data = []
        for idx, row in stats.iterrows():
            table_data.append({
                'Group': idx.capitalize(),
                'Mean ± SD': row['mean_std'],
                'N': int(row['count'])
            })
        
        df = pd.DataFrame(table_data)
        
        return dbc.Table.from_dataframe(
            df,
            striped=True,
            bordered=True,
            hover=True,
            className="table-responsive"
        )


    def run_server(self, debug: bool = False, port: int = 8050):
        """Run the dashboard server."""
        try:
            logger.info(f"Starting dashboard server on port {port}")
            self.app.run(debug=debug, port=port)
        except Exception as e:
            logger.error(f"Error running dashboard server: {e}")
            raise

if __name__ == '__main__':
    # Example usage
    db = CreatineDatabase()
    dashboard = CreatineDashboard(db)
    
    try:
        dashboard.run_server(debug=True, port=8050)
    finally:
        db.close()