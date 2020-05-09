#!/bin/bash
flake8 *.py --verbose  --count --show-source --statistics --max-line-length=127
#flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
