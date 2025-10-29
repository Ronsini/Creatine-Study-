import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
import logging
from datetime import datetime, timedelta
from database import CreatineDatabase

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CreatineAnalysis:
    def __init__(self, db: CreatineDatabase):
        """Initialize analysis with database connection."""
        self.db = db
        logger.info("Analysis module initialized")

    def calculate_effect_sizes(self) -> Dict[str, pd.DataFrame]:
        """Calculate effect sizes for different metrics and groups."""
        try:
            # Get population category analysis
            population_effects = self.db.run_analysis_query("Population Category Analysis")
            
            # Calculate Cohen's d effect sizes
            progress_data = self.db.get_progress_data()
            effect_sizes = {}
            
            for metric in ['strength_1rm_kg', 'lean_mass_kg', 'performance_score']:
                effects = []
                for group in progress_data['group_assignment'].unique():
                    creatine = progress_data[
                        (progress_data['group_assignment'] == 'creatine') & 
                        (progress_data[metric].notnull())
                    ][metric]
                    placebo = progress_data[
                        (progress_data['group_assignment'] == 'placebo') & 
                        (progress_data[metric].notnull())
                    ][metric]
                    
                    # Calculate Cohen's d
                    pooled_std = np.sqrt((np.var(creatine) + np.var(placebo)) / 2)
                    effect_size = (np.mean(creatine) - np.mean(placebo)) / pooled_std
                    
                    effects.append({
                        'metric': metric,
                        'effect_size': effect_size,
                        'interpretation': self._interpret_effect_size(effect_size)
                    })
                
                effect_sizes[metric] = pd.DataFrame(effects)
            
            results = {
                'population_effects': population_effects,
                'effect_sizes': effect_sizes
            }
            
            logger.info("Effect sizes calculated successfully")
            return results
        except Exception as e:
            logger.error(f"Error calculating effect sizes: {e}")
            raise

    def _interpret_effect_size(self, d: float) -> str:
        """Interpret Cohen's d effect size."""
        if abs(d) < 0.2:
            return "Negligible"
        elif abs(d) < 0.5:
            return "Small"
        elif abs(d) < 0.8:
            return "Medium"
        else:
            return "Large"

    def analyze_progression_rates(self) -> Dict[str, pd.DataFrame]:
        """Analyze progression rates for different groups and metrics."""
        try:
            progress_data = self.db.get_progress_data()
        
            # Calculate rates using linear regression
            results = []
            for pid in progress_data['participant_id'].unique():
                participant_data = progress_data[progress_data['participant_id'] == pid]
            
                # Convert dates to numeric values
                dates = pd.to_datetime(participant_data['measurement_date'])
                days = (dates - dates.min()).dt.days.values.reshape(-1, 1)
            
                # Calculate rates for each metric
                metrics = ['strength_1rm_kg', 'lean_mass_kg', 'performance_score']
                rates = {}
            
                for metric in metrics:
                    if participant_data[metric].notnull().all():
                        reg = LinearRegression().fit(days, participant_data[metric])
                        rates[f'{metric}_rate'] = reg.coef_[0]
                        rates[f'{metric}_r2'] = r2_score(participant_data[metric], reg.predict(days))
            
                # Add participant info
                rates['participant_id'] = pid
                rates['group_assignment'] = participant_data['group_assignment'].iloc[0]
                rates['training_status'] = participant_data['training_status'].iloc[0]
            
                results.append(rates)
        
            rates_df = pd.DataFrame(results)
        
            # Calculate summary statistics with flattened column names
            group_stats = []
            for (group, status) in rates_df.groupby(['group_assignment', 'training_status']).groups:
                group_data = rates_df[(rates_df['group_assignment'] == group) & 
                                    (rates_df['training_status'] == status)]
                stats = {
                    'group_assignment': group,
                    'training_status': status
                }
            
                for col in ['strength_1rm_kg_rate', 'lean_mass_kg_rate', 'performance_score_rate']:
                    stats[f'{col}_mean'] = group_data[col].mean()
                    stats[f'{col}_std'] = group_data[col].std()
            
                group_stats.append(stats)
            
            summary_stats = pd.DataFrame(group_stats)
        
            analysis_results = {
                'individual_rates': rates_df,
                'summary_statistics': summary_stats
            }
        
            logger.info("Progression rates analyzed successfully")
            return analysis_results
        except Exception as e:
            logger.error(f"Error analyzing progression rates: {e}")
            raise

    def analyze_training_impact(self) -> Dict[str, pd.DataFrame]:
        """Analyze the impact of different training protocols."""
        try:
            # Get training program analysis
            program_analysis = self.db.run_analysis_query("Training Program Analysis")
            
            # Get training compliance impact
            compliance_analysis = self.db.run_analysis_query("Training Compliance Impact")
            
            # Combine analyses
            results = {
                'program_analysis': program_analysis,
                'compliance_analysis': compliance_analysis
            }
            
            logger.info("Training impact analysis completed")
            return results
        except Exception as e:
            logger.error(f"Error analyzing training impact: {e}")
            raise

    def analyze_age_effects(self) -> pd.DataFrame:
        """Analyze the effect of age on supplementation outcomes."""
        try:
            age_analysis = self.db.run_analysis_query("Age Group Analysis")
            logger.info("Age effects analysis completed")
            return age_analysis
        except Exception as e:
            logger.error(f"Error analyzing age effects: {e}")
            raise

    def analyze_dosing_protocols(self) -> pd.DataFrame:
        """Analyze effectiveness of different dosing protocols."""
        try:
            dosing_analysis = self.db.run_analysis_query("Dosing Protocol Analysis")
            logger.info("Dosing protocol analysis completed")
            return dosing_analysis
        except Exception as e:
            logger.error(f"Error analyzing dosing protocols: {e}")
            raise

    def analyze_fatigue_and_recovery(self) -> Dict[str, pd.DataFrame]:
        """Analyze fatigue levels and recovery patterns."""
        try:
            # Get fatigue level analysis
            fatigue_analysis = self.db.run_analysis_query("Fatigue Level Analysis")
            
            # Calculate recovery patterns
            progress_data = self.db.get_progress_data()
            recovery_patterns = []
            
            for pid in progress_data['participant_id'].unique():
                participant_data = progress_data[progress_data['participant_id'] == pid].sort_values('measurement_date')
                
                if len(participant_data) > 1:
                    # Calculate recovery metrics
                    fatigue_recovery = participant_data['fatigue_level'].diff().mean()
                    performance_recovery = participant_data['performance_score'].diff().mean()
                    
                    recovery_patterns.append({
                        'participant_id': pid,
                        'group_assignment': participant_data['group_assignment'].iloc[0],
                        'avg_fatigue_recovery': fatigue_recovery,
                        'avg_performance_recovery': performance_recovery
                    })
            
            recovery_df = pd.DataFrame(recovery_patterns)
            
            results = {
                'fatigue_analysis': fatigue_analysis,
                'recovery_patterns': recovery_df
            }
            
            logger.info("Fatigue and recovery analysis completed")
            return results
        except Exception as e:
            logger.error(f"Error analyzing fatigue and recovery: {e}")
            raise

    def generate_summary_report(self) -> Dict:
        """Generate a comprehensive summary report of all analyses."""
        try:
            report = {
                'effect_sizes': self.calculate_effect_sizes(),
                'progression_rates': self.analyze_progression_rates(),
                'training_impact': self.analyze_training_impact(),
                'age_effects': self.analyze_age_effects(),
                'dosing_protocols': self.analyze_dosing_protocols(),
                'fatigue_recovery': self.analyze_fatigue_and_recovery()
            }
            
            logger.info("Summary report generated successfully")
            return report
        except Exception as e:
            logger.error(f"Error generating summary report: {e}")
            raise

if __name__ == "__main__":
    # Example usage
    db = CreatineDatabase()
    analysis = CreatineAnalysis(db)
    
    # Generate and print summary report
    try:
        report = analysis.generate_summary_report()
        print("\nCreatine Study Analysis Report")
        print("=============================")
        
        for section, data in report.items():
            print(f"\n{section.replace('_', ' ').title()}:")
            print("-" * (len(section) + 1))
            if isinstance(data, dict):
                for key, value in data.items():
                    print(f"\n{key}:")
                    print(value)
            else:
                print(data)
    finally:
        db.close()