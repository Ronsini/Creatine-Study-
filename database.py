import os
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Union
import pandas as pd
from sqlalchemy import create_engine, text
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CreatineDatabase:
    def __init__(self, db_path: str = "database/creatine_study.db"):
        """Initialize database connection."""
        self.db_path = db_path
        self.ensure_db_directory()
        self.engine = create_engine(f'sqlite:///{db_path}')
        logger.info(f"Database initialized at {db_path}")
        
    def ensure_db_directory(self):
        """Ensure database directory exists."""
        db_dir = os.path.dirname(self.db_path)
        if db_dir:
            Path(db_dir).mkdir(parents=True, exist_ok=True)

    def init_database(self):
        """Initialize database with schema."""
        try:
            schema_path = Path("schema.sql")
            with open(schema_path, 'r') as f:
                schema_sql = f.read()
                
            with self.engine.connect() as conn:
                # Split the schema SQL into individual statements
                statements = schema_sql.split(';')
                for statement in statements:
                    if statement.strip():
                        conn.execute(text(statement))
                conn.commit()
            logger.info("Database schema initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise

    def add_participant(self, participant_data: Dict) -> int:
        """Add a new participant to the database."""
        try:
            query = """
            INSERT INTO participants (
                age, gender, weight_kg, height_cm, training_experience_years,
                training_status, group_assignment, dosing_protocol, population_category
            ) VALUES (
                :age, :gender, :weight_kg, :height_cm, :training_experience_years,
                :training_status, :group_assignment, :dosing_protocol, :population_category
            )
            """
            with self.engine.connect() as conn:
                result = conn.execute(text(query), participant_data)
                conn.commit()
                logger.info(f"Added new participant with ID: {result.lastrowid}")
                return result.lastrowid
        except Exception as e:
            logger.error(f"Error adding participant: {e}")
            raise

    def add_measurement(self, measurement_data: Dict) -> int:
        """
        Add a new measurement to the database.
        Returns the ID of the newly created measurement.
        """
        try:
            # Validate required fields
            required_fields = ['participant_id', 'measurement_date', 'strength_1rm_kg',
                             'lean_mass_kg']
            for field in required_fields:
                if field not in measurement_data:
                    raise ValueError(f"Missing required field: {field}")

            query = """
            INSERT INTO measurements (
                participant_id, measurement_date, strength_1rm_kg,
                lean_mass_kg, muscle_thickness_mm, creatine_kinase_level,
                performance_score, fatigue_level
            ) VALUES (
                :participant_id, :measurement_date, :strength_1rm_kg,
                :lean_mass_kg, :muscle_thickness_mm, :creatine_kinase_level,
                :performance_score, :fatigue_level
            )
            """
            with self.engine.connect() as conn:
                result = conn.execute(text(query), measurement_data)
                conn.commit()
                new_id = result.lastrowid
                
            logger.info(f"Added new measurement for participant {measurement_data['participant_id']}")
            return new_id
        except Exception as e:
            logger.error(f"Error adding measurement: {e}")
            raise

    def get_participant_data(self, participant_id: Optional[int] = None) -> pd.DataFrame:
        """Retrieve participant data."""
        try:
            query = "SELECT * FROM participants"
            if participant_id:
                query += f" WHERE participant_id = {participant_id}"
            
            df = pd.read_sql_query(query, self.engine)
            logger.info(f"Retrieved data for {len(df)} participants")
            return df
        except Exception as e:
            logger.error(f"Error retrieving participant data: {e}")
            raise

    def get_measurements(self, 
                        participant_id: Optional[int] = None, 
                        start_date: Optional[str] = None,
                        end_date: Optional[str] = None) -> pd.DataFrame:
        """Retrieve measurements data with optional filters."""
        try:
            conditions = []
            if participant_id:
                conditions.append(f"participant_id = {participant_id}")
            if start_date:
                conditions.append(f"measurement_date >= '{start_date}'")
            if end_date:
                conditions.append(f"measurement_date <= '{end_date}'")
                
            query = "SELECT * FROM measurements"
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            query += " ORDER BY measurement_date"
                
            df = pd.read_sql_query(query, self.engine)
            logger.info(f"Retrieved {len(df)} measurements")
            return df
        except Exception as e:
            logger.error(f"Error retrieving measurements: {e}")
            raise

    def get_progress_data(self) -> pd.DataFrame:
        """Get participant progress data joined with measurements."""
        try:
            query = """
            SELECT 
                p.participant_id,
                p.age,
                p.training_status,
                p.group_assignment,
                m.measurement_date,
                m.strength_1rm_kg,
                m.lean_mass_kg,
                m.performance_score,
                m.muscle_thickness_mm,
                m.creatine_kinase_level,
                m.fatigue_level
            FROM participants p
            JOIN measurements m ON p.participant_id = m.participant_id
            ORDER BY p.participant_id, m.measurement_date
            """
            df = pd.read_sql_query(query, self.engine)
            logger.info(f"Retrieved progress data with {len(df)} records")
            return df
        except Exception as e:
            logger.error(f"Error retrieving progress data: {e}")
            raise

    def run_analysis_query(self, query_name: str) -> pd.DataFrame:
        """Run a predefined analysis query."""
        try:
            queries_path = Path("queries.sql")
            with open(queries_path, 'r') as f:
                queries = f.read()
                
            # Split queries into a dictionary
            query_dict = {}
            current_query = []
            current_name = None
            
            for line in queries.split('\n'):
                if line.startswith('-- '):
                    if current_name and current_query:
                        query_dict[current_name] = '\n'.join(current_query)
                    current_name = line[3:].strip()
                    current_query = []
                else:
                    current_query.append(line)
                    
            if current_name and current_query:
                query_dict[current_name] = '\n'.join(current_query)
                
            if query_name not in query_dict:
                raise ValueError(f"Query '{query_name}' not found")
                
            df = pd.read_sql_query(query_dict[query_name], self.engine)
            logger.info(f"Successfully ran analysis query: {query_name}")
            return df
        except Exception as e:
            logger.error(f"Error running analysis query: {e}")
            raise

    def update_participant(self, participant_id: int, update_data: Dict) -> bool:
        """Update participant information."""
        try:
            set_clauses = []
            for key in update_data.keys():
                set_clauses.append(f"{key} = :{key}")
            
            query = f"""
            UPDATE participants 
            SET {', '.join(set_clauses)}
            WHERE participant_id = :participant_id
            """
            
            update_data['participant_id'] = participant_id
            
            with self.engine.connect() as conn:
                result = conn.execute(text(query), update_data)
                conn.commit()
                
            success = result.rowcount > 0
            if success:
                logger.info(f"Updated participant {participant_id}")
            else:
                logger.warning(f"No participant found with ID {participant_id}")
            return success
        except Exception as e:
            logger.error(f"Error updating participant: {e}")
            raise

    def backup_database(self, backup_path: Optional[str] = None) -> str:
        """Create a backup of the database."""
        try:
            if backup_path is None:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                backup_path = f"{self.db_path}.backup_{timestamp}"
            
            with sqlite3.connect(self.db_path) as source:
                backup = sqlite3.connect(backup_path)
                source.backup(backup)
                backup.close()
                
            logger.info(f"Database backed up to {backup_path}")
            return backup_path
        except Exception as e:
            logger.error(f"Error backing up database: {e}")
            raise

    def close(self):
        """Close the database connection."""
        try:
            self.engine.dispose()
            logger.info("Database connection closed")
        except Exception as e:
            logger.error(f"Error closing database connection: {e}")
            raise

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Creatine study database operations')
    parser.add_argument('--init', action='store_true', help='Initialize the database')
    parser.add_argument('--backup', action='store_true', help='Create a database backup')
    parser.add_argument('--backup-path', type=str, help='Custom backup file path')
    
    args = parser.parse_args()
    
    db = CreatineDatabase()
    
    if args.init:
        print("Initializing database...")
        db.init_database()
        print("Database initialized successfully!")
        
    if args.backup:
        print("Creating database backup...")
        backup_path = db.backup_database(args.backup_path)
        print(f"Backup created successfully at: {backup_path}")