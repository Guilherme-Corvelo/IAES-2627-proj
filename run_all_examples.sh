#!/bin/bash

# Water Bucket Solver - Run All Examples
# This script runs all examples using both Python and MiniZinc (if available)

echo "========================================="
echo "Water Bucket Problem Solver"
echo "Running All Examples"
echo "========================================="
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python3 not found. Please install Python 3."
    exit 1
fi

echo "[1/4] Running Python BFS Solver..."
echo "========================================="
python3 water_bucket_solver.py
echo ""

# Check if MiniZinc is available
if command -v minizinc &> /dev/null; then
    echo "[2/4] Running MiniZinc - Classic 8-5-3 Problem"
    echo "========================================="
    minizinc water_bucket.mzn water_bucket_8_5_3.dzn
    echo ""
    
    echo "[3/4] Running MiniZinc - Custom 10-7-4 Problem"
    echo "========================================="
    minizinc water_bucket.mzn water_bucket_10_7_4.dzn
    echo ""
    
    echo "[4/4] Running MiniZinc - Custom 9-6-4 Problem"
    echo "========================================="
    minizinc water_bucket.mzn water_bucket_9_6_4.dzn
    echo ""
    
    echo "========================================="
    echo "All examples completed successfully!"
    echo "========================================="
else
    echo "[2/4] MiniZinc not found (skipping)"
    echo "To install MiniZinc, visit: https://www.minizinc.org/"
    echo ""
    echo "========================================="
    echo "Python examples completed successfully!"
    echo "========================================="
fi
