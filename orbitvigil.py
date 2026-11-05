#!/usr/bin/env python3
"""OrbitVigil root entry point."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from orbitvigil.cli import main

if __name__ == "__main__":
    main()
