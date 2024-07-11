<script>
  import { onMount } from 'svelte';
  import 'ag-grid-community/styles/ag-grid.css';
  import 'ag-grid-community/styles/ag-theme-alpine.css';
  import { Grid } from 'ag-grid-community';
  import FilterComponent from './FilterComponent.svelte';
  import * as d3 from 'd3';

  let gridDiv;
  let fileInput;
  let rawData = [];
  let gridData = [];
  let columnDefs = [];
  let showTable = false;

  let mean = 0;
  let stdDev = 0;

  const colorPalettes = {
    analytical: ['#ADD8E6', '#90EE90', '#FFA07A', '#FF6347'], // Lighter shades
    business: ['#D8BFD8', '#B0E0E6', '#FFD700', '#98FB98'],
    financial: ['#FFB6C1', '#FFDAB9', '#E6E6FA', '#F0E68C'],
    marketing: ['#FFE4E1', '#F5DEB3', '#FFFACD', '#E0FFFF']
  };

  let selectedColors = colorPalettes.analytical;  // Default color palette

  function getTextColor(backgroundColor) {
    const color = d3.hsl(backgroundColor);
    const luminance = color.l;
    const adjustedColor = luminance < 0.5 ? color.brighter(1.5) : color.darker(1.5);
    return adjustedColor.toString();
  }

  function createHighlightSpan(text, backgroundColor) {
    const span = document.createElement('span');
    span.style.backgroundColor = backgroundColor;
    span.style.borderRadius = '10px';
    span.style.padding = '2px 8px';
    span.style.fontWeight = 'bold';
    span.innerText = text;
    return span;
  }

  function cellRenderer(params) {
    const value = params.value;
    if (params.data[`${params.colDef.field}_meetsCriteria`]) {
      const highlightColor = 'rgba(255, 0, 0, 0.1)'; // Light red
      const span = createHighlightSpan(value, highlightColor);
      return span.outerHTML;
    } else if (params.colDef.field === 'value' && params.data.stdDevValue !== undefined) {
      const deviation = Math.abs(params.data.stdDevValue);
      let backgroundColor;
      if (deviation < 1) {
        backgroundColor = selectedColors[0];
      } else if (deviation < 2) {
        backgroundColor = selectedColors[1];
      } else if (deviation < 3) {
        backgroundColor = selectedColors[2];
      } else {
        backgroundColor = selectedColors[3];
      }
      const textColor = getTextColor(backgroundColor);
      const span = createHighlightSpan(value, backgroundColor);
      span.style.color = textColor;
      return span.outerHTML;
    }
    return value;
  }

  let gridOptions = {
    columnDefs: [],
    rowData: [],
    defaultColDef: {
      sortable: true,
      filter: true,
      editable: true,
      cellRenderer: cellRenderer
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

      // Calculate mean and standard deviation for the dataset
      const values = rawData.map(row => row.value).filter(value => typeof value === 'number');
      mean = d3.mean(values);
      stdDev = d3.deviation(values);

      // Add stdDevValue to each row for coloring
      rawData.forEach(row => {
        if (typeof row.value === 'number') {
          row.stdDevValue = (row.value - mean) / stdDev;
        }
      });

      showTable = true;  // Show table after processing
    } catch (error) {
      console.error('Error uploading file:', error);
    }
  }

  function handleFilterData(event) {
    gridData = event.detail.data;
    const profile = event.detail.profile;
    if (profile) {
      selectedColors = colorPalettes[profile];
    }
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
