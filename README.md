# Creatine Supplementation Study Analysis

A comprehensive system for analyzing and visualizing the effects of creatine supplementation on strength, muscle mass, and performance metrics.

This project demonstrates advanced data science capabilities including SQLite database management, statistical analysis with effect sizes and hypothesis testing, and interactive visualization with Plotly Dash. Perfect for showcasing skills in data engineering, statistical analysis, and scientific visualization.

## Features

- **Data Management**: SQLite database for storing participant data and measurements.
- **Advanced Analysis**: Statistical analysis of supplementation effects across different populations.
- **Interactive Visualization**: Dynamic plots and charts using Plotly and Dash.
- **Research-Based**: Implementation based on peer-reviewed research findings.
- **Comprehensive Testing**: Full test coverage with pytest.
- **Interactive Dashboard**: Web-based dashboard for real-time data exploration.

### Dashboard Features

- **KPI Strip**: Group difference, effect size (Cohen's d), p-value, and sample size
- **Interactive Charts**: Time series progression with confidence bands
- **Age & Training Comparisons**: Boxplots for different population groups
- **Statistical Analysis**: Automated t-tests and effect size calculations
- **Professional Visualization**: Publication-ready charts with uncertainty bands

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Ronsini/Creatine-Study-.git
cd Creatine-Study-
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Quick Start

1. Initialize the database with sample data:
```bash
python main.py --init-db
```

2. Launch the interactive dashboard:
```bash
python main.py --dashboard
```

3. Open your browser to http://localhost:8050

You can also run standalone analysis:
```bash
python main.py --analyze
python main.py --visualize
```

## Project Structure

```
creatine-study/
├── database/              # Database files
│   └── creatine_study.db  # SQLite database
├── main.py                # Main entry point
├── database.py            # Database operations
├── analysis.py            # Statistical analysis
├── visualization.py       # Static visualizations
├── dashboard.py           # Interactive Dash dashboard
├── schema.sql            # Database schema
├── queries.sql           # Analysis queries
├── test_database.py      # Database tests
├── test_analysis.py      # Analysis tests
├── test_visualization.py # Visualization tests
└── requirements.txt       # Python dependencies
```

## Usage Examples

### Basic Analysis
```python
from database import CreatineDatabase
from analysis import CreatineAnalysis

# Initialize database
db = CreatineDatabase()

# Create analysis instance
analysis = CreatineAnalysis(db)

# Generate comprehensive report
report = analysis.generate_summary_report()
```

### Visualization
```python
from visualization import CreatineVisualization

# Create visualization instance
viz = CreatineVisualization(db)

# Generate plots
viz.generate_summary_plots('output/plots')
```

### Interactive Dashboard
```python
from dashboard import CreatineDashboard

# Create and run dashboard
dashboard = CreatineDashboard(db)
dashboard.run_server(debug=True)
```

## Testing

Run the test suite:
```bash
pytest test_*.py
```

Generate coverage report:
```bash
pytest --cov=. test_*.py
```

## Contributing

1. Fork the repository.
2. Create your feature branch (`git checkout -b feature/amazing-feature`).
3. Commit your changes (`git commit -m 'Add amazing feature'`).
4. Push to the branch (`git push origin feature/amazing-feature`).
5. Open a Pull Request.

## Development Setup

Install development dependencies:
```bash
pip install -e .[dev,docs]
```

Format code:
```bash
black .
isort .
```

Run linters:
```bash
flake8 .
mypy .
```

## Documentation

Build the documentation:
```bash
cd docs
make html
```

View the documentation at `docs/_build/html/index.html`.

## Acknowledgments

- Research based on [PMC8949037](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8949037/).
- Database design inspired by clinical trial data management systems.
- Visualization approaches based on scientific publication standards.

## Contact

Ronald Orsini - ronniej7orsini@gmail.com

Project Link: [https://github.com/Ronsini/creatine-study-](https://github.com/Ronsini/creatine-study-)

