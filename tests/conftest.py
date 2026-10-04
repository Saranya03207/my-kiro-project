"""
Pytest configuration file.
Adds project root to Python path for imports and configures Hypothesis.
"""
import sys
import os
from hypothesis import settings

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Register default profile with deadline=None to prevent flaky timing failures
# on Windows systems during SQLite schema creation in property-based tests
settings.register_profile("default", deadline=None)
settings.load_profile("default")
