import sys
from pathlib import Path

# Make broker/src importable from any test in this directory
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "broker" / "src"))
