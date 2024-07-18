from flask import Flask, request, jsonify
import pandas as pd
from flask_cors import CORS
import numpy as np
import math

# Initialize Flask application
app = Flask(__name__)
# Enable Cross-Origin Resource Sharing (CORS) for the app
CORS(app)

# Global variables to store the uploaded data and column definitions
global_data = []
global_columns = []

@app.route('/upload', methods=['POST'])
def upload_file():
    """
    Endpoint to handle file upload and process the file (CSV or Excel).
    Returns a JSON response containing the data and column information.
    """
    global global_data, global_columns

    # Check if the 'file' part is in the request
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    # Check if the file is selected
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # Check if the file is valid and process it
    if file and (file.filename.endswith('.csv') or file.filename.endswith('.xlsx')):
        try:
            # Read the file into a DataFrame
            if file.filename.endswith('.csv'):
                df = pd.read_csv(file)
            else:
                df = pd.read_excel(file)

            # Replace NaN, Inf, and -Inf with None
            df.replace([np.inf, -np.inf], np.nan, inplace=True)
            df = df.where(pd.notnull(df), None)

            # Convert DataFrame to dictionary format suitable for JSON response
            global_data = df.to_dict(orient='records')
            global_columns = [{'headerName': col, 'field': col, 'sortable': True, 'filter': True, 'editable': True} for col in df.columns]

            # Return the column information and initial page of data
            return get_paginated_data(1)
        except Exception as e:
            # Handle any exceptions that occur during file processing
            return jsonify({'error': 'Error processing file'}), 500
    else:
        # Handle unsupported file formats
        return jsonify({'error': 'Unsupported file format'}), 400

@app.route('/data', methods=['GET'])
def get_paginated_data(page=1):
    """
    Endpoint to get paginated data.
    :param page: Page number (1-indexed)
    :return: JSON response with paginated data
    """
    global global_data, global_columns

    # Set the number of rows per page
    rows_per_page = 20
    start = (page - 1) * rows_per_page
    end = start + rows_per_page

    # Paginate the data
    paginated_data = global_data[start:end]
    total_pages = math.ceil(len(global_data) / rows_per_page)

    # Create response
    response = {
        'columns': global_columns,
        'data': paginated_data,
        'page': page,
        'totalPages': total_pages
    }

    return jsonify(response)

@app.route('/data/<int:page>', methods=['GET'])
def get_page(page):
    """
    Endpoint to handle requests for specific pages of data.
    :param page: Page number (1-indexed)
    :return: JSON response with paginated data
    """
    return get_paginated_data(page)

if __name__ == '__main__':
    # Run the Flask application in debug mode
    app.run(debug=True)
