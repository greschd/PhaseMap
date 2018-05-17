#!/bin/bash
pytest -p no:cov-exclude --cov=phasemap --cov-report=html
