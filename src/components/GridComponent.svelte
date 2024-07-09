<script>
  import { onMount } from 'svelte';
  import 'ag-grid-community/styles/ag-grid.css';
  import 'ag-grid-community/styles/ag-theme-alpine.css';
  import { Grid } from 'ag-grid-community';

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
    const threshold = 15;
    let color = 'black';

    if (value > threshold) {
      color = 'green';
    } else if (value < threshold) {
      color = 'red';
    }

    return `<span style="color: ${color};">${value}</span>`;
  }

  async function handleFileUpload(event) {
    const file = event.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('http://localhost:5000/upload', {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        throw new Error('File upload failed');
      }

      const { columns, data } = await response.json();

      console.log("Columns received:", columns);  // Debug print
      console.log("Data received:", data);  // Debug print

      gridOptions.columnDefs = columns;
      gridOptions.rowData = data;
      reinitializeGrid();
    } catch (error) {
      console.error('Error uploading file:', error);
      // Handle error appropriately
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
