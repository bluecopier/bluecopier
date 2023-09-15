#!/usr/bin/env python

import bluecopier.cli.deploy
import bluecopier.cli.generate  # noqa: F401
from bluecopier.cli.app import app

if __name__ == "__main__":
    app()
