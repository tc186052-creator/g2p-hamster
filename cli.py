#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Shim — code thật nằm ở g2p_hamster/cli.py (cũng cài được qua lệnh
`g2p-hamster` sau khi `pip install .`)."""
from g2p_hamster.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
