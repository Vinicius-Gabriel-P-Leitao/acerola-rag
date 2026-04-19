import sys
from pathlib import Path

# garante que o root do projeto está no sys.path
sys.path.insert(0, str(Path(__file__).parents[2]))
