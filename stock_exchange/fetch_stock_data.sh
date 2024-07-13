#!/bin/bash

# API URL
API_URL="http://localhost:8000/api/stock_data?symbol=AAPL"

# Directory to save the response
OUTPUT_DIR="/mnt/d/project/templates/stock_data"

# Create the output directory if it doesn't exist
mkdir -p $OUTPUT_DIR

# Filename with timestamp
OUTPUT_FILE="$OUTPUT_DIR/stock_data_$(date +'%Y%m%d%H%M').json"

# Make the API call and save the response
curl -s $API_URL -o $OUTPUT_FILE
