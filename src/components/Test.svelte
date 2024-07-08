<script>
    import { onMount } from 'svelte';
    import 'ag-grid-community/styles/ag-grid.css';
    import 'ag-grid-community/styles/ag-theme-alpine.css';
    import { Grid } from 'ag-grid-community';
  
    let gridDiv;
    let gridOptions;
  
    const columnDefs = [
      { headerName: 'Name', field: 'name', sortable: true, filter: true },
      { headerName: 'Value', field: 'value', sortable: true, filter: 'agNumberColumnFilter', editable: true, cellRenderer: 'highlightRenderer' },
      { headerName: 'Date', field: 'date', sortable: true, filter: true },
      {
        headerName: 'Calculated Value',
        field: 'calculatedValue',
        valueGetter: (params) => {
          return params.data.value ? params.data.value * 2 : null;
        },
        editable: true,
        sortable: true,
        filter: 'agNumberColumnFilter',
        cellRenderer: 'highlightRenderer'
      }
    ];
  
    const rowData = [
      { name: 'Record 1', value: 10, date: '2024-01-01' },
      { name: 'Record 2', value: 20, date: '2024-02-01' },
      { name: 'Record 3', value: 30, date: '2024-03-01' }
    ];
  
    function highlightRenderer(params) {
      const value = params.value;
      const filterModel = params.api.getFilterModel();
      let color = 'black';
      let backgroundColor = '';
  
      // Check if the column is filtered with 'greaterThan'
      if (filterModel[params.colDef.field] && filterModel[params.colDef.field].type === 'greaterThan') {
        const filterValue = filterModel[params.colDef.field].filter;
        if (value > filterValue) {
          backgroundColor = 'lightgreen';
        }
      }
  
      return `<span style="color: ${color}; background-color: ${backgroundColor};">${value}</span>`;
    }
  
    onMount(() => {
      gridOptions = {
        columnDefs,
        rowData,
        frameworkComponents: {
          highlightRenderer
        },
        defaultColDef: {
          sortable: true,
          filter: true,
          editable: true
        }
      };
  
      new Grid(gridDiv, gridOptions);
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
  
  <div bind:this={gridDiv} class="ag-theme-alpine"></div>
  