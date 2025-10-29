from setuptools import setup, find_packages
from pathlib import Path

# Read the contents of README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

# Read requirements safely
def read_requirements(filename):
    try:
        with open(filename) as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    except FileNotFoundError:
        return []  # Prevents crash if file is missing

setup(
    name="creatine-study",
    version="1.0.0",
    author="Ronald Orsini",
    author_email="ronniej7orsini@gmail.com",
    description="A comprehensive creatine supplementation study analysis system",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Ronsini/Creatine-Study",
    py_modules=['main', 'database', 'analysis', 'visualization', 'dashboard'],
    install_requires=read_requirements("requirements.txt"),
    extras_require={
        'dev': [
            'pytest>=7.3.1',
            'pytest-cov>=4.1.0',
            'pytest-mock>=3.10.0',
            'black>=23.3.0',
            'flake8>=6.0.0',
            'mypy>=1.3.0',
            'isort>=5.12.0'
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Topic :: Scientific/Engineering :: Medical Science Apps."
    ],
    python_requires=">=3.8",
    include_package_data=True,
)
