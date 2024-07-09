from flask import Flask, request, jsonify
import pandas as pd
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        print("No file part in request")
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        print("No file selected")
        return jsonify({'error': 'No selected file'}), 400

    if file and (file.filename.endswith('.csv') or file.filename.endswith('.xlsx')):
        try:
            if file.filename.endswith('.csv'):
                df = pd.read_csv(file)
            else:
                df = pd.read_excel(file)
            
            data = df.to_dict(orient='records')
            columns = [{'headerName': col, 'field': col, 'sortable': True, 'filter': True, 'editable': True} for col in df.columns]
            
            print("Columns:", columns)
            print("Data sample:", data[:5])  # Print first 5 rows for debugging

            return jsonify({'columns': columns, 'data': data})
        except Exception as e:
            print("Error processing file:", e)
            return jsonify({'error': 'Error processing file'}), 500
    else:
        print("Unsupported file format")
        return jsonify({'error': 'Unsupported file format'}), 400

if __name__ == '__main__':
    app.run(debug=True)
