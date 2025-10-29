import argparse
import logging
from pathlib import Path
from datetime import datetime, timedelta
import json

import numpy as np
from datetime import date

import pandas as pd
from database import CreatineDatabase
from analysis import CreatineAnalysis
from visualization import CreatineVisualization
from dashboard import CreatineDashboard

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CreatineStudy:
    def __init__(self):
        """Initialize the creatine study components."""
        self.db = CreatineDatabase()
        self.analysis = CreatineAnalysis(self.db)
        self.visualization = CreatineVisualization(self.db)
        self.dashboard = CreatineDashboard(self.db)
        
    def initialize_database(self):
        """Initialize the database with schema."""
        try:
            logger.info("Initializing database...")
            self.db.init_database()
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise

    def run_analysis(self, output_dir: str = 'results'):
        """Run comprehensive analysis and save results."""
        try:
            logger.info("Running analysis...")
        
            # Create output directory
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
        
            # Generate report
            raw_report = self.analysis.generate_summary_report()
        
            # Save results
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
            def make_serializable(obj):
                if isinstance(obj, pd.DataFrame):
                    return obj.to_dict('records')
                elif isinstance(obj, pd.Series):
                    return obj.to_dict()
                elif isinstance(obj, dict):
                    return {str(k): make_serializable(v) for k, v in obj.items()}
                elif isinstance(obj, (list, tuple)):
                    return [make_serializable(i) for i in obj]
                elif isinstance(obj, (np.int64, np.float64)):
                    return obj.item()
                elif isinstance(obj, (datetime, date)):
                    return obj.isoformat()
                elif pd.isna(obj):
                    return None
                return obj if isinstance(obj, (str, int, float, bool, type(None))) else str(obj)

            # Convert report to serializable format
            serializable_report = make_serializable(raw_report)
        
            # Save report
            report_path = output_path / f'analysis_report_{timestamp}.json'
            with open(report_path, 'w') as f:
                json.dump(serializable_report, f, indent=4)
        
            logger.info(f"Analysis results saved to {report_path}")
            return raw_report
        except Exception as e:
            logger.error(f"Failed to run analysis: {e}")
            raise

    def generate_visualizations(self, output_dir: str = 'plots'):
        """Generate all visualizations."""
        try:
            logger.info("Generating visualizations...")
            self.visualization.generate_summary_plots(output_dir)
            logger.info(f"Visualizations saved to {output_dir}")
        except Exception as e:
            logger.error(f"Failed to generate visualizations: {e}")
            raise

    def run_dashboard(self, debug: bool = False, port: int = 8050):
        """Run the interactive dashboard."""
        try:
            logger.info("Starting dashboard...")
            self.dashboard.run_server(debug=debug, port=port)
        except Exception as e:
            logger.error(f"Failed to run dashboard: {e}")
            raise

    def backup_database(self):
        """Create a backup of the database."""
        try:
            logger.info("Creating database backup...")
            backup_path = self.db.backup_database()
            logger.info(f"Database backed up to {backup_path}")
        except Exception as e:
            logger.error(f"Failed to backup database: {e}")
            raise

    def cleanup(self):
        """Clean up resources."""
        try:
            self.db.close()
            logger.info("Cleanup completed")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
            raise

    def add_sample_data(self):
        """Add sample data for testing"""
        try:
            logger.info("Adding sample data...")
        
            # Add participants with correct population categories
            participants = [
                # Young Trained Creatine Group
                {
                    'age': 25,
                    'gender': 'male',
                    'weight_kg': 75.5,
                    'height_cm': 180.0,
                    'training_status': 'trained',
                    'group_assignment': 'creatine',
                    'dosing_protocol': 'loading',
                    'population_category': 'young trained',
                    'training_experience_years': 3.5
                },
                # Young Trained Placebo Group
                {
                    'age': 28,
                    'gender': 'male',
                    'weight_kg': 78.0,
                    'height_cm': 175.0,
                    'training_status': 'trained',
                    'group_assignment': 'placebo',
                    'dosing_protocol': 'loading',
                    'population_category': 'young trained',
                    'training_experience_years': 4.0
                },
                # Older Untrained Creatine Group
                {
                    'age': 52,
                    'gender': 'male',
                    'weight_kg': 82.0,
                    'height_cm': 178.0,
                    'training_status': 'untrained',
                    'group_assignment': 'creatine',
                    'dosing_protocol': 'maintenance',
                    'population_category': 'older untrained',
                    'training_experience_years': 0.5
                },
                # Older Untrained Placebo Group
                {
                    'age': 55,
                    'gender': 'male',
                    'weight_kg': 80.0,
                    'height_cm': 176.0,
                    'training_status': 'untrained',
                    'group_assignment': 'placebo',
                    'dosing_protocol': 'maintenance',
                    'population_category': 'older untrained',
                    'training_experience_years': 0.2
                }
            ]
        
            participant_ids = []
            for p in participants:
                participant_ids.append(self.db.add_participant(p))
                
            # Add measurements for each participant
            start_date = datetime.now().date()
        
            for pid, participant in zip(participant_ids, participants):
                for week in range(6):  # 6 weeks of data
                    measurement_date = start_date + timedelta(weeks=week)
                
                    # Different progression rates based on age and group
                    if participant['age'] < 30 and participant['group_assignment'] == 'creatine':
                        # Young creatine - highest gains
                        strength_increment = 5 * week
                        mass_increment = 0.5 * week
                    elif participant['age'] < 30 and participant['group_assignment'] == 'placebo':
                        # Young placebo - moderate gains
                        strength_increment = 3 * week
                        mass_increment = 0.3 * week
                    elif participant['age'] >= 50 and participant['group_assignment'] == 'creatine':
                        # Older creatine - moderate-low gains
                        strength_increment = 2.5 * week
                        mass_increment = 0.25 * week
                    else:
                        # Older placebo - lowest gains
                        strength_increment = 2 * week
                        mass_increment = 0.2 * week
                
                    self.db.add_measurement({
                        'participant_id': pid,
                        'measurement_date': measurement_date,
                        'strength_1rm_kg': 100.0 + strength_increment,
                        'lean_mass_kg': 65.0 + mass_increment,
                        'muscle_thickness_mm': 35.0 + (week * 0.2),
                        'creatine_kinase_level': 150.0 + (week * 10),
                        'performance_score': 8.5 + (week * 0.2),
                        'fatigue_level': 3
                    })
            
            logger.info("Sample data added successfully")
        except Exception as e:
            logger.error(f"Error adding sample data: {e}")
            raise

def main():
    parser = argparse.ArgumentParser(description='Creatine Supplementation Study Analysis')
    parser.add_argument('--init-db', action='store_true', help='Initialize the database')
    parser.add_argument('--analyze', action='store_true', help='Run analysis')
    parser.add_argument('--visualize', action='store_true', help='Generate visualizations')
    parser.add_argument('--dashboard', action='store_true', help='Run interactive dashboard')
    parser.add_argument('--backup', action='store_true', help='Create database backup')
    parser.add_argument('--port', type=int, default=8050, help='Dashboard port number')
    
    args = parser.parse_args()
    
    study = CreatineStudy()
    
    try:
        if args.init_db:
            study.initialize_database()
            study.add_sample_data()  # Add this line
            
        if args.analyze:
            study.run_analysis()
            
        if args.visualize:
            study.generate_visualizations()
            
        if args.dashboard:
            study.run_dashboard(port=args.port)
            
        if not any(vars(args).values()):
            parser.print_help()
    except Exception as e:
        logger.error(f"Application error: {e}")
        raise
    finally:
        study.cleanup()

if __name__ == "__main__":
    main()