"""Legacy editor entry point; gameplay verification now runs in native C++."""
from pathlib import Path
import runpy
runpy.run_path(str(Path(__file__).with_name('start_native_pie.py')))
