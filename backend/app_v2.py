from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import pandas as pd
import os
import numpy as np
import math
import json
from openai import AzureOpenAI
from functions_v2 import (
    summarize_date_time, summarize_numeric, summarize_categorical, summarize_text,
    summarize_identifiers, summarize_financial, summarize_geospatial, summarize_boolean,
    summarize_binary, summarize_contact_information, summarize_aggregated_mixed,
    summarize_special_symbols, summarize_ratings_scoring, summarize_duration,
    summarize_survey_feedback, summarize_file_references, summarize_miscellaneous,
    summarize_names
)

app = Flask(__name__)   
CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}})

# Azure OpenAI configuration
GRAPHRAG_LLM_DEPLOYMENT_NAME = "gpt-4o"
GRAPHRAG_LLM_API_KEY = "7c90d344cb524b9885202a7603641589"
GRAPHRAG_LLM_API_BASE = "https://azure-isv-success-in.openai.azure.com/"
GRAPHRAG_LLM_API_VERSION = "2024-06-01"

# Initialize the Azure OpenAI client
client = AzureOpenAI(
    api_key=GRAPHRAG_LLM_API_KEY,
    api_version=GRAPHRAG_LLM_API_VERSION,
    base_url=f"{GRAPHRAG_LLM_API_BASE}openai/deployments/{GRAPHRAG_LLM_DEPLOYMENT_NAME}"
)

# Mapping of column types to handler functions
column_type_handlers = {
    "Date/Time": summarize_date_time,
    "Numeric": summarize_numeric,
    "Categorical": summarize_categorical,
    "Text": summarize_text,
    "Identifiers": summarize_identifiers,
    "Financial": summarize_financial,
    "Geospatial": summarize_geospatial,
    "Boolean": summarize_boolean,
    "Binary": summarize_binary,
    "Contact Information": summarize_contact_information,
    "Aggregated/Mixed Data": summarize_aggregated_mixed,
    "Special Symbols": summarize_special_symbols,
    "Ratings/Scoring": summarize_ratings_scoring,
    "Duration": summarize_duration,
    "Survey/Feedback": summarize_survey_feedback,
    "File References": summarize_file_references,
    "Miscellaneous": summarize_miscellaneous,
    "Names": summarize_names
}

# Global variables to store the uploaded data and column definitions
global_data = []
global_columns = []

# Function to generate prompt for the LLM to identify column type
def generate_prompt(column_name, column_data_sample):
    system_prompt = "Assistant is a large language model trained by OpenAI."
    user_prompt = f"""
    You are a data analyst tasked with identifying the type of data in a given column from a CSV file.
    The possible column types are as follows:
    1. **Date/Time**: Data representing dates or times in various formats (e.g., YYYY-MM-DD, MM/DD/YYYY, Month Day, Year, time stamps).
    2. **Numeric**: Contains numerical data like integers or floats without any alphabetical characters.
    3. **Categorical**: Limited set of unique values that repeat frequently, such as categories, labels, or codes (e.g., colors, yes/no).
    4. **Text**: Free-form text that can include sentences, paragraphs, or varying-length strings.
    5. **Identifiers (IDs)**: Unique identifiers often alphanumeric, like serial numbers, UUIDs, or IDs (e.g., product IDs, result IDs).
    6. **Financial**: Data formatted as currency or financial figures, often including symbols like $, €, etc.
    7. **Geospatial**: Data representing geographical coordinates, locations, or addresses.
    8. **Boolean**: Data with only two unique values (e.g., True/False, Yes/No).
    9. **Binary**: Data in binary format, such as 0/1 or other binary representations.
    10. **Contact Information**: Data that matches formats for emails, phone numbers, or addresses.
    11. **Aggregated/Mixed Data**: JSON, XML, or other nested structures or mixed types of data.
    12. **Special Symbols**: Frequent use of special characters or symbols (e.g., #, @, %).
    13. **Ratings/Scoring**: Numeric data within a specific range (e.g., 1-5, 1-10).
    14. **Duration**: Time durations or periods (e.g., HH:MM:SS, '2 days', '3 hours').
    15. **Survey/Feedback**: Predefined answers or free-form feedback from surveys.
    16. **File References**: File paths or URLs pointing to external resources.
    17. **Miscellaneous**: Data that does not fit into any of the above categories.
    18. **Names**: Contains first names, last names, full names, or lists of names.

    Additionally, consider the following clues from the column name:
    - If the column name contains "id" or "ID", it is likely an **Identifiers (IDs)** type.
    - If the column name contains "date", "time", "year", "month", or "day", it is likely a **Date/Time** type.
    - If the column name includes "amount", "price", "cost", or "revenue", it may be a **Financial** type.
    - If the column name contains "email", "phone", "address", it may be **Contact Information**.
    - If the column name contains "lat", "long", "geo", "address", it may be a **Geospatial** type.
    - If the column name has "score", "rating", it is likely a **Ratings/Scoring** type.

    Analyze both the column name and data sample thoroughly to determine the most appropriate type from the list above. 

    Here is a sample of the data from the column '{column_name}':

    {column_data_sample}

    Please provide only the most appropriate column type from the list above as a single word.
    """
    return system_prompt, user_prompt

def convert_to_serializable(data):
    """Convert DataFrame to a serializable format."""
    def handle_value(val):
        if pd.isna(val):
            return None
        if isinstance(val, (np.integer, np.float64, np.bool_)):
            return val.item()
        if isinstance(val, bytes):
            return val.decode('utf-8')  # Handle bytes (base64 images)
        return val

    if isinstance(data, pd.DataFrame):
        data = data.applymap(handle_value)
        return data.to_dict(orient='records')
    if isinstance(data, dict):
        return {k: handle_value(v) for k, v in data.items()}
    if isinstance(data, list):
        return [handle_value(item) for item in data]
    return data


@app.route('/upload', methods=['POST'])
def upload_file():
    global global_data, global_columns
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    # Save the uploaded file
    file_path = os.path.join(os.getcwd(), file.filename)
    file.save(file_path)

    # Read the file into a DataFrame
    if file.filename.endswith('.csv'):
        df = pd.read_csv(file_path)
    elif file.filename.endswith(('.xls', '.xlsx')):
        df = pd.read_excel(file_path)
    else:
        return jsonify({'error': 'Unsupported file type'}), 400

    # Initialize an empty dictionary to store the column types
    column_types = {}

    # Iterate through each column and generate a prompt for the LLM
    for column_name in df.columns:
        column_data_sample = df[column_name].dropna().head(5).to_list()
        column_data_sample_str = '\n'.join([f"{i+1}. \"{str(value)}\"" for i, value in enumerate(column_data_sample)])
        system_prompt, user_prompt = generate_prompt(column_name, column_data_sample_str)
        
        # Send the prompt to the OpenAI model
        response = client.chat.completions.create(
            model="gpt-35-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )

        identified_type = response.choices[0].message.content.strip()

        valid_types = [
            "Date/Time", "Numeric", "Categorical", "Text", "Identifiers", "Financial", "Geospatial", "Boolean", "Binary",
            "Contact Information", "Aggregated/Mixed Data", "Special Symbols", "Ratings/Scoring", "Duration", 
            "Survey/Feedback", "File References", "Miscellaneous", "Names"
        ]
        if identified_type in valid_types:
            column_types[column_name] = identified_type
        else:
            if "id" in column_name.lower():
                column_types[column_name] = "Identifiers"
            elif any(x in column_name.lower() for x in ["date", "time", "year", "month", "day"]):
                column_types[column_name] = "Date/Time"
            elif any(x in column_name.lower() for x in ["amount", "price", "cost", "revenue"]):
                column_types[column_name] = "Financial"
            elif any(x in column_name.lower() for x in ["email", "phone", "address"]):
                column_types[column_name] = "Contact Information"
            elif any(x in column_name.lower() for x in ["lat", "long", "geo", "address"]):
                column_types[column_name] = "Geospatial"
            elif any(x in column_name.lower() for x in ["score", "rating"]):
                column_types[column_name] = "Ratings/Scoring"
            else:
                column_types[column_name] = "Miscellaneous"

    # Prepare the JSON response with summaries
    summary = {}
    for column_name, column_type in column_types.items():
        handler_function = column_type_handlers.get(column_type)
        if handler_function:
            try:
                # Execute the summary function
                result = handler_function(df, column_name)

                # Add formatted summary text and chart options together
                summary[column_name] = {
                    'summary_text': ', '.join([f"{key}: {value}" for key, value in result.items() if key != 'chart_options']),
                    'chart_options': result.get('chart_options', {})
                }
            except Exception as e:
                summary[column_name] = {
                    'summary_text': f"Error processing column '{column_name}': {str(e)}",
                    'chart_options': {}
                }

    # Insert the formatted summary and chart options into the first row
    summary_row = {}
    for col in df.columns:
        summary_row[col] = {
            'summary': summary.get(col, {}).get('summary_text', ""),
            'chart_options': summary.get(col, {}).get('chart_options', {})
        }

    # Serialize DataFrame data
    data_rows = convert_to_serializable(df.to_dict(orient='records'))

    # Combine the summary_row with the rest of the data
    global_data = [summary_row] + data_rows
    global_columns = [{'headerName': col, 'field': col, 'sortable': True, 'filter': True, 'editable': True} for col in df.columns]

    # Return paginated data
    return get_paginated_data(1)



@app.route('/data', methods=['GET'])
def get_paginated_data(page=1):
    global global_data, global_columns

    rows_per_page = 20
    start = (page - 1) * rows_per_page
    end = start + rows_per_page

    paginated_data = global_data[start:end]
    total_pages = math.ceil(len(global_data) / rows_per_page)

    response = {
        'columns': global_columns,
        'data': paginated_data,
        'page': page,
        'totalPages': total_pages
    }

    return jsonify(response)


@app.route('/data/<int:page>', methods=['GET'])
def get_page(page):
    return get_paginated_data(page)

@app.route('/images/<filename>', methods=['GET'])
def get_image(filename):
    file_path = os.path.join('images', filename)
    if os.path.exists(file_path):
        return send_file(file_path)
    else:
        return jsonify({'error': 'Image not found'}), 404
    
# Search 
@app.route('/search', methods=['GET'])
def search_data():
    query = request.args.get('query', '')

    if query:
        filtered_data = [row for row in global_data if any(query.lower() in str(value).lower() for value in row.values())]
    else:
        filtered_data = global_data

    rows_per_page = 20
    total_pages = math.ceil(len(filtered_data) / rows_per_page)

    response = {
        'columns': global_columns,
        'data': filtered_data[:rows_per_page],
        'page': 1,
        'totalPages': total_pages
    }

    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
