import sys
from pathlib import Path

# Add the mcp/ directory to sys.path so chromatic_skills_server is importable
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
