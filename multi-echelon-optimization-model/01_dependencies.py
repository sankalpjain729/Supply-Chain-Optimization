"""
01_DEPENDENCIES.PY
==================
Installs all required packages for the Multi-Echelon Supply Chain Optimization Model.

Dependencies:
- pyomo: Mathematical optimization modeling language
- pandas: Data manipulation and analysis
- numpy: Numerical computing
- networkx: Graph theory and network analysis
- matplotlib: Data visualization
- glpk: GNU Linear Programming Kit (solver)
"""

import subprocess
import sys

def install_dependencies():
    """Install all required packages"""
    
    print("=" * 60)
    print("INSTALLING DEPENDENCIES...")
    print("=" * 60)
    
    # Install Python packages
    packages = ['pyomo', 'pandas', 'numpy', 'networkx', 'matplotlib']
    
    for package in packages:
        print(f"\nInstalling {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", package])
        print(f"✓ {package} installed successfully")
    
    print("\n" + "=" * 60)
    print("ALL PYTHON PACKAGES INSTALLED SUCCESSFULLY!")
    print("=" * 60)

if __name__ == "__main__":
    install_dependencies()
