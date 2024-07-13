#!/bin/bash

# Define the API endpoint
API_ENDPOINT="http://localhost:8000/stocks/AAPL"

# Log file location
LOG_FILE="/mnt/d/project/fetch_stock_data.log"

# Call the API endpoint and log the response
response=$(curl -s -X GET "$API_ENDPOINT")
echo "$(date): $response" >> "$LOG_FILE"
