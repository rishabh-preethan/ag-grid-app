<script>
  // This component gets the table data from the backend and renders the ag-grid table with that data and its summary

  import { onMount } from 'svelte';
  import 'ag-grid-community/styles/ag-grid.css';
  import 'ag-grid-community/styles/ag-theme-alpine.css';
  import { Grid } from 'ag-grid-community';
  import FilterComponent from './FilterComponent.svelte';
  import * as d3 from 'd3';
  import debounce from 'lodash/debounce';
  import * as echarts from 'echarts';

  let gridDiv;
  let fileInput;
  let rawData = [];
  let gridData = [];
  let columnDefs = [];
  let showTable = false;
  let showAllColumns = false;
  let currentPage = 1;
  let totalPages = 1;
  let searchQuery = '';

  let mean = 0;
  let stdDev = 0;

  const colorPalettes = {
    analytical: ['#ADD8E6', '#90EE90', '#FFA07A', '#FF6347'],
    business: ['#D8BFD8', '#B0E0E6', '#FFD700', '#98FB98'],
    financial: ['#FFB6C1', '#FFDAB9', '#E6E6FA', '#F0E68C'],
    marketing: ['#FFE4E1', '#F5DEB3', '#FFFACD', '#E0FFFF']
  };

  let selectedColors = colorPalettes.analytical;

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
    const columnName = params.colDef.field; // Get the current column name dynamically

    // Check if we are on the first row and handling the column dynamically
    if (params.node.rowIndex === 0) {
      // Check if chart options exist for the dynamic column name
      if (params.data && params.data[columnName] && params.data[columnName].chart_options) {
        const chartDiv = document.createElement('div');
        chartDiv.style.width = '200%';
        chartDiv.style.height = '200px'; // Adjust height as needed

        const chart = echarts.init(chartDiv);
        chart.setOption(params.data[columnName].chart_options); // Use dynamic column name

        return chartDiv;
      } else {
        console.error(`Chart options are not defined for column: ${columnName}`);
        return 'No chart options'; // Return a fallback or placeholder
      }
    }

    // Handle other cases
    if (params.data[`${params.colDef.field}_meetsCriteria`]) {
      const highlightColor = 'rgba(255, 0, 0, 0.1)';
      const span = createHighlightSpan(params.value, highlightColor);
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
      const span = createHighlightSpan(params.value, backgroundColor);
      span.style.color = textColor;
      return span.outerHTML;
    }

    return params.value;
  }

  let gridOptions = {
  columnDefs: [],
  rowData: [],
  defaultColDef: {
    sortable: true,
    filter: true,
    editable: true,
    cellRenderer: cellRenderer,
    cellStyle: (params) => {
      // Center-align text and wrap for the first row on the first page
      if (params.node.rowIndex === 0 && currentPage === 1) {
        return {
          textAlign: 'center',
          whiteSpace: 'normal',
          overflow: 'hidden',
          textOverflow: 'ellipsis',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          lineHeight: '1.4',
        };
      }
      return null; // Default styling for other rows
    },
    autoHeight: true, // Enable text wrapping for all rows
  },
  getRowHeight: (params) => {
    // Apply larger height to the first row on the first page
    if (params.node.rowIndex === 0 && currentPage === 1) {
      return 60; // Adjust the height to make the row appear larger
    }
    return 30; // Default row height
  },
  onGridReady: (params) => {
    setTimeout(() => {
      params.api.resetRowHeights(); // Ensure all rows are recalculated after grid is ready
    }, 0);
  }
};

function updateRowHeights() {
  if (gridOptions.api) {
    gridOptions.api.resetRowHeights();
  }
}

// Call this function whenever you change row data or the page
function handlePageChange() {
  fetchPage(currentPage).then(() => {
    updateRowHeights();
  });
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

    const result = await response.json();

    const { columns, data, page, totalPages: total } = result;

    // Verify the structure of the received data
    console.log(data); // Check the data format here

    columnDefs = columns;
    gridData = data;
    rawData = data;
    currentPage = page;
    totalPages = total;

    showTable = true;
    reinitializeGrid();
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

  async function fetchPage(page) {
    try {
      const response = await fetch(`http://localhost:5000/data/${page}`);
      if (!response.ok) {
        throw new Error('Failed to fetch page data');
      }

      const result = await response.json();
      const { data, page: current, totalPages: total } = result;

      gridData = data;
      currentPage = current;
      totalPages = total;

      reinitializeGrid();
    } catch (error) {
      console.error('Error fetching page data:', error);
    }
  }

  async function search(query) {
    try {
      const response = await fetch(`http://localhost:5000/search?query=${encodeURIComponent(query)}`);
      if (!response.ok) {
        throw new Error('Failed to search data');
      }

      const result = await response.json();
      const { data, page, totalPages: total } = result;

      gridData = data;
      currentPage = page;
      totalPages = total;

      reinitializeGrid();
    } catch (error) {
      console.error('Error searching data:', error);
    }
  }

  const debouncedSearch = debounce(search, 300);

  function handleSearch(event) {
    searchQuery = event.target.value;
    debouncedSearch(searchQuery);
  }

  function reinitializeGrid() {
    if (gridOptions.api) {
      gridOptions.api.destroy();
    }

    gridOptions.columnDefs = showAllColumns ? columnDefs : columnDefs.slice(0, 3);
    gridOptions.rowData = gridData;

    if (gridDiv) {
      new Grid(gridDiv, gridOptions);
      updateRowHeights();
    }
  }



  function toggleColumns() {
    showAllColumns = !showAllColumns;
    reinitializeGrid();
  }

  function nextPage() {
    if (currentPage < totalPages) {
      fetchPage(currentPage + 1);
    }
  }

  function prevPage() {
    if (currentPage > 1) {
      fetchPage(currentPage - 1);
    }
  }

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
    --ag-header-height: 30px;
    --ag-header-column-font-weight: bold;
  }

  .file-upload-button {
    background-color: white;
    border: 1px solid black;
    border-radius: 5px;
    padding: 0.5rem 1rem;
    margin: 0.2rem;
    cursor: pointer;
    font-size: 14px;
    transition: background-color 0.3s;
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
    transition: background-color 0.3s;
  }

  .toggle-button:hover {
    background-color: #f0f0f0;
  }

  .pagination-button {
    background-color: white;
    border: 1px solid black;
    border-radius: 5px;
    padding: 0.5rem 1rem;
    margin: 0.2rem;
    cursor: pointer;
    font-size: 14px;
    transition: background-color 0.3s;
  }

  .pagination-button:hover {
    background-color: #f0f0f0;
  }

  .search-input {
    width: 100%;
    max-width: 600px;
    padding: 0.5rem;
    margin: 0.2rem;
    border: 1px solid #ccc;
    border-radius: 5px;
    font-size: 14px;
  }

  .controls {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }

  @media (max-width: 600px) {
    .ag-theme-alpine {
      height: 400px;
      width: 100%;
    }

    .file-upload-button,
    .toggle-button,
    .pagination-button,
    .search-input {
      font-size: 12px;
      padding: 0.4rem 0.8rem;
    }
  }
</style>

<div>
  <input type="file" bind:this={fileInput} class="file-upload-button" accept=".csv, .xlsx" on:change={handleFileUpload} />
  {#if showTable}
    <div class="controls">
      <input type="text" class="search-input" placeholder="Search..." on:input={handleSearch} />
      <FilterComponent data={rawData} on:filterData={handleFilterData} />
    </div>
    <div bind:this={gridDiv} class="ag-theme-alpine"></div>
    <button class="toggle-button" on:click={toggleColumns}>
      {showAllColumns ? 'Show Less' : 'Show More'}
    </button>
    <button class="pagination-button" on:click={prevPage} disabled={currentPage === 1}>Previous</button>
    <button class="pagination-button" on:click={nextPage} disabled={currentPage === totalPages}>Next</button>
    <span>Page {currentPage} of {totalPages}</span>
  {/if}
</div>
