<script>
  import { onMount } from 'svelte';
  import 'ag-grid-community/styles/ag-grid.css';
  import 'ag-grid-community/styles/ag-theme-alpine.css';
  import { Grid } from 'ag-grid-community';
  import FilterComponent from './FilterComponent.svelte';

  let gridDiv;
  let fileInput;
  let rawData = [];
  let gridData = [];
  let columnDefs = [];
  let showTable = false;

  let gridOptions = {
    columnDefs: [],
    rowData: [],
    defaultColDef: {
      sortable: true,
      filter: true,
      editable: true,
      cellStyle: params => {
        if (params.data && params.data.meetsCriteria) {
          return { 'background-color': 'lightcoral' };
        }
        return null;
      }
    }
  };

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

      const result = await response.json();

      console.log("Response received:", result);  // Debug print

      const { columns, data } = result;

      columnDefs = columns;
      rawData = data;
      showTable = false;  // Hide table initially
    } catch (error) {
      console.error('Error uploading file:', error);
    }
  }

  function handleFilterData(event) {
    gridData = event.detail.data;
    showTable = true;
    reinitializeGrid();
  }

  function reinitializeGrid() {
    if (gridOptions.api) {
      gridOptions.api.destroy();
    }

    gridOptions.columnDefs = columnDefs;
    gridOptions.rowData = gridData;

    // Ensure gridDiv is available before initializing Grid
    if (gridDiv) {
      new Grid(gridDiv, gridOptions);
    }
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
  {#if rawData.length > 0}
    <FilterComponent data={rawData} on:filterData={handleFilterData} />
  {/if}
  {#if showTable}
    <div bind:this={gridDiv} class="ag-theme-alpine"></div>
  {/if}
</div>
