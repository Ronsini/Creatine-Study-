import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, Optional, List, Tuple
import pandas as pd
import numpy as np
from pathlib import Path
import logging
from database import CreatineDatabase

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CreatineVisualization:
    def __init__(self, db: CreatineDatabase):
        self.db = db
        self.setup_plot_style()
        # Define consistent colors
        self.colors = {
            'young_creatine': '#4169E1',  # Blue
            'older_creatine': '#000000',  # Black
            'placebo': '#FF6B6B'          # Red
        }
        logger.info("Visualization module initialized")

    def setup_plot_style(self):
        try:
            plt.style.use('seaborn-v0_8')
        except:
            plt.style.use('default')
        plt.rcParams['figure.figsize'] = [12, 6]
        plt.rcParams['figure.dpi'] = 100
        plt.rcParams['axes.titlesize'] = 14
        plt.rcParams['axes.labelsize'] = 12

    def set_axis_limits(self, ax, data, y_column):
        """Set consistent axis limits with some padding"""
        y_min = data[y_column].min()
        y_max = data[y_column].max()
        padding = (y_max - y_min) * 0.1  # 10% padding
        ax.set_ylim(y_min - padding, y_max + padding)

    def plot_strength_progression(self, save_path: Optional[str] = None):
        try:
            data = self.db.get_progress_data()
            data = data.rename(columns={
                'measurement_date': 'Measurement Date',
                'strength_1rm_kg': 'Maximum Strength (kg)',
                'age_group': 'Age Group'
            })
            data['Age Group'] = np.where(data['age'] < 30, 'Young', 'Older')
            
            fig, ax = plt.subplots(figsize=(12, 6))
            
            for group in ['creatine', 'placebo']:
                for age in ['Young', 'Older']:
                    mask = (data['group_assignment'] == group) & (data['Age Group'] == age)
                    if age == 'Older' and group == 'creatine':
                        color = self.colors['older_creatine']
                    elif group == 'creatine':
                        color = self.colors['young_creatine']
                    else:
                        color = self.colors['placebo']
                    
                    sns.lineplot(
                        data=data[mask],
                        x='Measurement Date',
                        y='Maximum Strength (kg)',
                        label=f'{group.capitalize()} ({age})',
                        color=color,
                        marker='o',
                        ax=ax
                    )

            ax.set_title('Maximum Strength Progression Over Time')
            ax.set_xlabel('Measurement Date')
            ax.set_ylabel('Maximum Strength (kg)')
            plt.xticks(rotation=45)
            self.set_axis_limits(ax, data, 'Maximum Strength (kg)')
            
            if save_path:
                plt.savefig(save_path, bbox_inches='tight', dpi=300)
            return fig
        except Exception as e:
            logger.error(f"Error plotting strength progression: {e}")
            raise

    def plot_mass_changes(self, save_path: Optional[str] = None):
        try:
            data = self.db.get_progress_data()
            data = data.rename(columns={
                'measurement_date': 'Measurement Date',
                'lean_mass_kg': 'Lean Mass (kg)',
                'age_group': 'Age Group'
            })
            data['Age Group'] = np.where(data['age'] < 30, 'Young', 'Older')
            
            fig, ax = plt.subplots(figsize=(12, 6))
            
            for group in ['creatine', 'placebo']:
                for age in ['Young', 'Older']:
                    mask = (data['group_assignment'] == group) & (data['Age Group'] == age)
                    if age == 'Older' and group == 'creatine':
                        color = self.colors['older_creatine']
                    elif group == 'creatine':
                        color = self.colors['young_creatine']
                    else:
                        color = self.colors['placebo']
                    
                    sns.lineplot(
                        data=data[mask],
                        x='Measurement Date',
                        y='Lean Mass (kg)',
                        label=f'{group.capitalize()} ({age})',
                        color=color,
                        marker='o',
                        ax=ax
                    )

            ax.set_title('Lean Mass Changes Over Time')
            ax.set_xlabel('Measurement Date')
            ax.set_ylabel('Lean Mass (kg)')
            plt.xticks(rotation=45)
            self.set_axis_limits(ax, data, 'Lean Mass (kg)')
            
            if save_path:
                plt.savefig(save_path, bbox_inches='tight', dpi=300)
            return fig
        except Exception as e:
            logger.error(f"Error plotting mass changes: {e}")
            raise

    def plot_effect_sizes(self, save_path: Optional[str] = None):
        try:
            progress_data = self.db.get_progress_data()
            metrics = ['strength_1rm_kg', 'lean_mass_kg', 'performance_score']
            
            effect_sizes = []
            for metric in metrics:
                creatine = progress_data[progress_data['group_assignment'] == 'creatine'][metric]
                placebo = progress_data[progress_data['group_assignment'] == 'placebo'][metric]
                
                pooled_std = np.sqrt((np.var(creatine) + np.var(placebo)) / 2)
                effect_size = (np.mean(creatine) - np.mean(placebo)) / pooled_std
                
                metric_name = {
                    'strength_1rm_kg': 'Maximum Strength',
                    'lean_mass_kg': 'Lean Mass',
                    'performance_score': 'Performance Score'
                }.get(metric, metric)
                
                effect_sizes.append({
                    'Metric': metric_name,
                    'Effect Size': effect_size
                })
            
            effect_df = pd.DataFrame(effect_sizes)
            
            fig, ax = plt.subplots(figsize=(10, 6))
            sns.barplot(data=effect_df, x='Metric', y='Effect Size', ax=ax)
            
            ax.set_title('Effect Sizes (Cohen\'s d)')
            ax.set_xlabel('Metric Type')
            ax.set_ylabel('Effect Size (d)')
            plt.xticks(rotation=45)
            
            # Set fixed y-axis limits for effect sizes
            ax.set_ylim(-0.2, 1.2)  # Typical range for effect sizes
            
            ax.axhline(y=0.2, color='gray', linestyle='--', alpha=0.5)
            ax.axhline(y=0.5, color='gray', linestyle='--', alpha=0.5)
            ax.axhline(y=0.8, color='gray', linestyle='--', alpha=0.5)
            
            if save_path:
                plt.savefig(save_path, bbox_inches='tight')
            return fig
        except Exception as e:
            logger.error(f"Error plotting effect sizes: {e}")
            raise

    def plot_age_comparison(self, save_path: Optional[str] = None):
        try:
            data = self.db.get_progress_data()
            data = data.rename(columns={
                'strength_1rm_kg': 'Maximum Strength (kg)',
                'lean_mass_kg': 'Lean Mass (kg)',
                'age_group': 'Age Group',
                'group_assignment': 'Group'
            })
            data['Age Group'] = np.where(data['age'] < 30, 'Young', 'Older')
        
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
            # Use consistent colors
            young_palette = {
                'creatine': self.colors['young_creatine'],
                'placebo': self.colors['placebo']
            }
            older_palette = {
                'creatine': self.colors['older_creatine'],
                'placebo': self.colors['placebo']
            }
        
            # First plot - Maximum Strength
            sns.boxplot(
                data=data[data['Age Group'] == 'Young'],
                x='Age Group',
                y='Maximum Strength (kg)',
                hue='Group',
                palette=young_palette,
                ax=ax1
            )
            sns.boxplot(
                data=data[data['Age Group'] == 'Older'],
                x='Age Group',
                y='Maximum Strength (kg)',
                hue='Group',
                palette=older_palette,
                ax=ax1
            )
            ax1.set_title('Maximum Strength by Age Group')
            ax1.set_xlabel('Age Group')
            ax1.set_ylabel('Maximum Strength (kg)')
            self.set_axis_limits(ax1, data, 'Maximum Strength (kg)')
        
            # Second plot - Lean Mass
            sns.boxplot(
                data=data[data['Age Group'] == 'Young'],
                x='Age Group',
                y='Lean Mass (kg)',
                hue='Group',
                palette=young_palette,
                ax=ax2
            )
            sns.boxplot(
                data=data[data['Age Group'] == 'Older'],
                x='Age Group',
                y='Lean Mass (kg)',
                hue='Group',
                palette=older_palette,
                ax=ax2
            )
            ax2.set_title('Lean Mass by Age Group')
            ax2.set_xlabel('Age Group')
            ax2.set_ylabel('Lean Mass (kg)')
            self.set_axis_limits(ax2, data, 'Lean Mass (kg)')
        
            plt.tight_layout()
        
            if save_path:
                plt.savefig(save_path, bbox_inches='tight')
            return fig
        except Exception as e:
            logger.error(f"Error plotting age comparison: {e}")
            raise

    def plot_training_compliance(self, save_path: Optional[str] = None):
        try:
            compliance_data = self.db.run_analysis_query("Training Compliance Impact")
            compliance_data = compliance_data.rename(columns={
                'training_status': 'Training Status',
                'strength_gain_percentage': 'Strength Gain (%)',
                'mass_gain_percentage': 'Mass Gain (%)',
                'high_compliance': 'High Compliance'
            })
            
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
            
            # Plot strength gains
            sns.barplot(
                data=compliance_data,
                x='Training Status',
                y='Strength Gain (%)',
                hue='High Compliance',
                ax=ax1
            )
            ax1.set_title('Strength Gains by Training Status')
            ax1.set_xlabel('Training Status')
            ax1.set_ylabel('Strength Gain (%)')
            plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)
            self.set_axis_limits(ax1, compliance_data, 'Strength Gain (%)')
            
            # Plot mass gains
            sns.barplot(
                data=compliance_data,
                x='Training Status',
                y='Mass Gain (%)',
                hue='High Compliance',
                ax=ax2
            )
            ax2.set_title('Mass Gains by Training Status')
            ax2.set_xlabel('Training Status')
            ax2.set_ylabel('Mass Gain (%)')
            plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45)
            self.set_axis_limits(ax2, compliance_data, 'Mass Gain (%)')
            
            plt.tight_layout()
            
            if save_path:
                plt.savefig(save_path, bbox_inches='tight')
            return fig
        except Exception as e:
            logger.error(f"Error plotting training compliance: {e}")
            raise

    def generate_summary_plots(self, output_dir: str = 'plots'):
        try:
            Path(output_dir).mkdir(parents=True, exist_ok=True)
            
            plots = {
                'strength_progression.png': self.plot_strength_progression,
                'mass_changes.png': self.plot_mass_changes,
                'effect_sizes.png': self.plot_effect_sizes,
                'age_comparison.png': self.plot_age_comparison,
                'training_compliance.png': self.plot_training_compliance
            }
            
            for filename, plot_func in plots.items():
                save_path = str(Path(output_dir) / filename)
                plot_func(save_path)
                plt.close()
            
            logger.info(f"Generated all summary plots in {output_dir}")
        except Exception as e:
            logger.error(f"Error generating summary plots: {e}")
            raise


if __name__ == '__main__':
    # Create database and visualization instances
    db = CreatineDatabase()
    viz = CreatineVisualization(db)
    
    try:
        # Generate all summary plots
        viz.generate_summary_plots()
        logger.info("Successfully generated all plots")
    except Exception as e:
        logger.error(f"Error in main execution: {e}")
    finally:
        # Always close the database connection
        db.close()