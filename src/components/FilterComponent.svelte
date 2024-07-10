<script>
    import { createEventDispatcher, onMount } from 'svelte';
  
    export let data = [];
    const dispatch = createEventDispatcher();
  
    let step = 1;
    let selectedCriteria = null;
    let selectedValue = null;
    let values = [];
    let displayedValues = [];
    let ranges = [];
  
    onMount(() => {
      generateValuesAndRanges();
    });
  
    function generateValuesAndRanges() {
      if (data.length > 0) {
        values = [...new Set(data.flatMap(row => Object.values(row).filter(value => typeof value === 'number')))];
        values.sort((a, b) => a - b);  // Sort values for better UI experience
        
        const minValue = Math.min(...values);
        const maxValue = Math.max(...values);
        const stepSize = Math.ceil((maxValue - minValue) / 5);
        for (let i = minValue; i <= maxValue; i += stepSize) {
          ranges.push({ min: i, max: i + stepSize - 1 });
        }
        
        displayedValues = generateDisplayedValues(minValue, maxValue);
      }
    }
  
    function generateDisplayedValues(minValue, maxValue) {
      const stepSize = Math.ceil((maxValue - minValue) / 4);
      return [minValue, minValue + stepSize, minValue + 2 * stepSize, minValue + 3 * stepSize, maxValue];
    }
  
    function handleCriteriaSelection(criteria) {
      selectedCriteria = criteria;
      step = 2;
    }
  
    function handleValueSelection(value) {
      selectedValue = value;
      applyFilter();
    }
  
    function handleRangeSelection(range) {
      selectedValue = range;
      applyFilter();
    }
  
    function applyFilter() {
      const markedData = data.map(row => {
        let meetsCriteria = false;
        if (selectedCriteria === 'above') {
          meetsCriteria = Object.values(row).some(value => value > selectedValue);
        } else if (selectedCriteria === 'below') {
          meetsCriteria = Object.values(row).some(value => value < selectedValue);
        } else if (selectedCriteria === 'equal') {
          meetsCriteria = Object.values(row).some(value => value >= selectedValue.min && value <= selectedValue.max);
        }
        return { ...row, meetsCriteria };
      });
  
      dispatch('filterData', { data: markedData });
    }
  </script>
  
  <style>
    .filter-buttons {
      margin-bottom: 1rem;
      border-radius: 10px;
    }
  </style>
  
  <div class="filter-buttons">
    {#if step === 1}
      <button on:click={() => handleCriteriaSelection('above')}>Above</button>
      <button on:click={() => handleCriteriaSelection('below')}>Below</button>
      <button on:click={() => handleCriteriaSelection('equal')}>Equal To</button>
    {/if}
  
    {#if step === 2 && (selectedCriteria === 'above' || selectedCriteria === 'below')}
      {#each displayedValues as value}
        <button on:click={() => handleValueSelection(value)}>
          {value}
        </button>
      {/each}
    {/if}
  
    {#if step === 2 && selectedCriteria === 'equal'}
      {#each ranges as range}
        <button on:click={() => handleRangeSelection(range)}>
          {range.min} - {range.max}
        </button>
      {/each}
    {/if}
  </div>
  