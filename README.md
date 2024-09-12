#Project Documentation
###Overview
This project consists of a Svelte frontend and a Python backend that allows users to upload files, processes the data, categorizes columns, generates summaries, and visualizes the results using ECharts. The data is displayed in an interactive table powered by ag-Grid, providing features like pagination, column toggling, search, and custom cell rendering.

###Architecture
* Frontend: Built with Svelte, using ag-Grid for data display and ECharts for visualization.
* Backend: Built with Flask in Python, handles file uploads, data processing, column categorization, and summary generation using various statistical techniques.

### Features

##### File Upload and Data Processing
* Users can upload CSV or Excel files.
* The backend processes the file, identifies different column types (e.g., numeric, categorical, date/time), and generates summaries accordingly.
* For numeric data, it computes mean, standard deviation, and other statistical metrics.
* For date/time data, it provides range, unique counts, and more.
* The summaries also include visual elements (e.g., histograms, box plots) sent to the frontend as ECharts options.

##### Dynamic Data Display with ag-Grid

* Displays data in a table format with pagination support.
* The first row contains dynamically rendered visual summaries.
* Column toggling allows users to show/hide certain columns.
* Real-time search functionality filters the data displayed.

##### Interactive Charts with ECharts

* Summaries are visualized using ECharts, enabling interactive and dynamic chart rendering.
* Chart options are dynamically generated and sent from the backend.

### Backend
Technologies Used: Flask, Pandas, NumPy, OpenAI API for LLM-based categorization, ECharts options for visualizations.
##### Endpoints:
```/upload```: Handles file upload, processes the data, categorizes columns, and generates summaries.
```/data/<page>```: Fetches paginated data.
```/search?query=<query>```: Searches for data matching the query.

##### Summary Functions:
```summarize_numeric```: Summarizes numeric columns by calculating mean, standard deviation, etc.
```summarize_categorical```: Summarizes categorical columns by counting unique values, generating bar charts, etc.
```summarize_date_time```: Summarizes date/time columns by calculating range, unique count, and generating histograms.

### Frontend
Technologies Used: Svelte, ag-Grid, ECharts, D3.js, lodash for debouncing search.
##### Components:
```File Upload```: Allows users to upload CSV/Excel files.
```Table Display```: Uses ag-Grid to display data with pagination, dynamic column toggling, and search.
```Dynamic Chart Rendering```: Uses ECharts to render visual summaries in the first row of the ag-Grid table.
```Filtering```: Filters data based on user-selected criteria.
##### Key Functions:
```handleFileUpload```: Handles file upload and sends it to the backend.
```handleFilterData```: Applies filters based on user input.
```search```: Searches through the data in real-time.
```reinitializeGrid```: Re-initializes the ag-Grid table with updated data and settings.
### Usage
##### Upload a File
Click on the "Upload File" button and select a CSV or Excel file to upload.
The backend processes the file, categorizes columns, and sends the summarized data to the frontend.

##### View and Interact with Data
The data is displayed in an ag-Grid table with pagination controls.
The first row contains dynamic visual summaries based on the data content.

##### Search and Filter
Use the search bar to filter data in real-time.
Use filtering options to display specific subsets of the data.

##### Toggle Columns
Click the "Show More" or "Show Less" button to toggle between all and a subset of columns.

### Installation and Setup
##### Backend Setup
Run the Flask server: ```python app_v2.py```
##### Frontend Setup

Install Svelte and dependencies: npm install.
Run the development server: ```npm run dev```