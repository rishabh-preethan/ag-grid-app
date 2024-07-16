<script>
  import { onMount } from 'svelte';
  import 'ag-grid-community/styles/ag-grid.css';
  import 'ag-grid-community/styles/ag-theme-alpine.css';
  import { Grid } from 'ag-grid-community';
  import FilterComponent from './FilterComponent.svelte';
  import * as d3 from 'd3';

  let gridDiv;
  let fileInput;
  let rawData = [];  // Store raw data from the file
  let gridData = [];  // Store filtered data for the grid
  let columnDefs = [];  // Store column definitions for the grid
  let showTable = false;  // Control visibility of the grid
  let showAllColumns = false; // Control visibility of all columns

  let mean = 0;  // Mean of the data values
  let stdDev = 0;  // Standard deviation of the data values

  // Define color palettes for different profiles
  const colorPalettes = {
    analytical: ['#ADD8E6', '#90EE90', '#FFA07A', '#FF6347'],
    business: ['#D8BFD8', '#B0E0E6', '#FFD700', '#98FB98'],
    financial: ['#FFB6C1', '#FFDAB9', '#E6E6FA', '#F0E68C'],
    marketing: ['#FFE4E1', '#F5DEB3', '#FFFACD', '#E0FFFF']
  };

  let selectedColors = colorPalettes.analytical;  // Default color palette

  /**
   * Determines the appropriate text color based on the background color.
   * @param {string} backgroundColor - The background color in any CSS color format.
   * @returns {string} The text color in the same format as the background color.
   */
  function getTextColor(backgroundColor) {
    const color = d3.hsl(backgroundColor);
    const luminance = color.l;
    const adjustedColor = luminance < 0.5 ? color.brighter(1.5) : color.darker(1.5);
    return adjustedColor.toString();
  }

  /**
   * Creates a span element with highlighted background.
   * @param {string} text - The text content of the span.
   * @param {string} backgroundColor - The background color for the span.
   * @returns {HTMLElement} The created span element.
   */
  function createHighlightSpan(text, backgroundColor) {
    const span = document.createElement('span');
    span.style.backgroundColor = backgroundColor;
    span.style.borderRadius = '10px';
    span.style.padding = '2px 8px';
    span.style.fontWeight = 'bold';
    span.innerText = text;
    return span;
  }

  /**
   * Custom cell renderer for the grid. Highlights cells based on criteria.
   * @param {object} params - Parameters provided by the ag-Grid framework.
   * @returns {string} The HTML string for the cell content.
   */
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

  // Grid options
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

  /**
   * Handles the file upload event, sends the file to the server, and processes the response.
   * @param {Event} event - The file upload event.
   */
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

  /**
   * Handles the filtered data event, updates the grid data and reinitializes the grid.
   * @param {Event} event - The custom event containing filtered data and profile information.
   */
  function handleFilterData(event) {
    gridData = event.detail.data;
    const profile = event.detail.profile;
    if (profile) {
      selectedColors = colorPalettes[profile];
    }
    reinitializeGrid();
  }

  /**
   * Reinitializes the grid with new data and column definitions.
   */
  function reinitializeGrid() {
    if (gridOptions.api) {
      gridOptions.api.destroy();
    }

    gridOptions.columnDefs = showAllColumns ? columnDefs : columnDefs.slice(0, 3);
    gridOptions.rowData = gridData;

    // Ensure gridDiv is available before initializing Grid
    if (gridDiv) {
      new Grid(gridDiv, gridOptions);
    }
  }

  /**
   * Toggles the visibility of all columns.
   */
  function toggleColumns() {
    showAllColumns = !showAllColumns;
    reinitializeGrid();
  }

  /**
   * Initializes the grid on component mount.
   */
  onMount(() => {
    reinitializeGrid();
  });
</script>

<style>
  .ag-theme-alpine {
    height: 600px;
    width: 100%;
    max-width: 620px;
    border-width: 3px;
    border-radius: 10px;
    overflow: hidden;
    --ag-header-height: 30px; /* Smaller menu bar height */
    --ag-header-column-font-weight: bold; /* Make column names bold */
  }

  .file-upload-button {
    background-color: white;
    border: 1px solid black;
    border-radius: 5px;
    padding: 0.5rem 1rem;
    margin: 0.2rem;
    cursor: pointer;
    font-size: 14px;
    transition: background-color 0.3s; /* Add transition for hover effect */
  }

  .file-upload-button:hover {
    background-color: #f0f0f0;
  }

  .toggle-button {
    background-color: white;
    border: 1px solid black;
    border-radius: 5px;
    padding: 0.5rem 1rem;
    margin: 0.2rem;
    cursor: pointer;
    font-size: 14px;
    transition: background-color 0.3s; /* Add transition for hover effect */
  }

  .toggle-button:hover {
    background-color: #f0f0f0;
  }

  @media (max-width: 600px) {
    .ag-theme-alpine {
      height: 400px;
      width: 100%;
    }

    .file-upload-button,
    .toggle-button {
      font-size: 12px;
      padding: 0.4rem 0.8rem;
    }
  }
</style>

<div>
  <input type="file" bind:this={fileInput} class="file-upload-button" accept=".csv, .xlsx" on:change={handleFileUpload} />
  {#if rawData.length > 0}
    <FilterComponent data={rawData} on:filterData={handleFilterData} />
  {/if}
  {#if showTable}
    <div bind:this={gridDiv} class="ag-theme-alpine"></div>
  {/if}
  {#if showTable}
    <button class="toggle-button" on:click={toggleColumns}>
      {showAllColumns ? 'Show Less' : 'Show More'}
    </button>
  {/if}
</div>
