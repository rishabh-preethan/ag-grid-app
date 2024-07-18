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
    global global_data, global_columns

    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and (file.filename.endswith('.csv') or file.filename.endswith('.xlsx')):
        try:
            if file.filename.endswith('.csv'):
                df = pd.read_csv(file)
            else:
                df = pd.read_excel(file)

            df.replace([np.inf, -np.inf], np.nan, inplace=True)
            df = df.where(pd.notnull(df), None)

            global_data = df.to_dict(orient='records')
            global_columns = [{'headerName': col, 'field': col, 'sortable': True, 'filter': True, 'editable': True} for col in df.columns]

            return get_paginated_data(1)
        except Exception as e:
            return jsonify({'error': 'Error processing file'}), 500
    else:
        return jsonify({'error': 'Unsupported file format'}), 400

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

@app.route('/search', methods=['GET'])
def search_data():
    global global_data, global_columns

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
    app.run(debug=True)
