<script>
  import { onMount } from 'svelte';
  import 'ag-grid-community/styles/ag-grid.css';
  import 'ag-grid-community/styles/ag-theme-alpine.css';
  import { Grid } from 'ag-grid-community';
  import Papa from 'papaparse';
  import * as XLSX from 'xlsx';

  let gridDiv;
  let fileInput;

  let gridOptions = {
    columnDefs: [],
    rowData: [],
    frameworkComponents: {
      highlightRenderer
    },
    defaultColDef: {
      sortable: true,
      filter: true,
      editable: true
    }
  };

  function highlightRenderer(params) {
    const value = params.value;
    const threshold = 15; // Customize this value as needed
    let color = 'black';

    if (value > threshold) {
      color = 'green';
    } else if (value < threshold) {
      color = 'red';
    }

    return `<span style="color: ${color};">${value}</span>`;
  }

  function handleFileUpload(event) {
    const file = event.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    const fileExtension = file.name.split('.').pop();

    reader.onload = (e) => {
      const data = e.target.result;
      if (fileExtension === 'csv') {
        Papa.parse(data, {
          header: true,
          complete: (results) => {
            const { meta, data } = results;
            gridOptions.columnDefs = meta.fields.map(field => ({
              headerName: field.charAt(0).toUpperCase() + field.slice(1),
              field: field,
              sortable: true,
              filter: true,
              editable: true,
              cellRenderer: field === 'value' || field === 'calculatedValue' ? 'highlightRenderer' : null
            }));
            gridOptions.rowData = data;
            reinitializeGrid();
          }
        });
      } else if (fileExtension === 'xlsx') {
        const workbook = XLSX.read(data, { type: 'binary' });
        const sheetName = workbook.SheetNames[0];
        const sheet = workbook.Sheets[sheetName];
        const jsonData = XLSX.utils.sheet_to_json(sheet, { header: 1 });
        const headers = jsonData[0];
        const rowData = jsonData.slice(1).map(row => {
          let rowData = {};
          row.forEach((cell, i) => {
            rowData[headers[i]] = cell;
          });
          return rowData;
        });
        gridOptions.columnDefs = headers.map(header => ({
          headerName: header.charAt(0).toUpperCase() + header.slice(1),
          field: header,
          sortable: true,
          filter: true,
          editable: true,
          cellRenderer: header === 'value' || header === 'calculatedValue' ? 'highlightRenderer' : null
        }));
        gridOptions.rowData = rowData;
        reinitializeGrid();
      }
    };

    if (fileExtension === 'csv') {
      reader.readAsText(file);
    } else if (fileExtension === 'xlsx') {
      reader.readAsBinaryString(file);
    }
  }

  function reinitializeGrid() {
    if (gridOptions.api) {
      gridOptions.api.destroy();
    }
    new Grid(gridDiv, gridOptions);
  }

  onMount(() => {
    reinitializeGrid();
  });
</script>

<style>
  .ag-theme-alpine {
    height: 400px;
    width: 100%;
    border-width: 3px;
    border-radius: 5px;
    overflow: hidden;
  }
</style>

<div>
  <input type="file" bind:this={fileInput} accept=".csv, .xlsx" on:change={handleFileUpload} />
  <div bind:this={gridDiv} class="ag-theme-alpine"></div>
</div>
