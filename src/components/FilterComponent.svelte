<script>
  import { createEventDispatcher, onMount } from 'svelte';
  import * as d3 from 'd3';

  export let data = [];
  const dispatch = createEventDispatcher();

  let step = 1;
  let selectedCriteria = null;
  let selectedProfile = null;
  let selectedValue = null;
  let values = [];
  let displayedValues = [];
  let ranges = [];
  let mean = 0;
  let stdDev = 0;

  const profiles = {
    analytical: {
      name: 'Analytical',
      colors: [d3.interpolateBlues, d3.interpolateGreens, d3.interpolateOranges, d3.interpolateReds]
    },
    business: {
      name: 'Business',
      colors: [d3.interpolatePurples, d3.interpolateCool, d3.interpolateWarm, d3.interpolateYlGnBu]
    },
    financial: {
      name: 'Financial',
      colors: [d3.interpolateRdYlBu, d3.interpolateSpectral, d3.interpolatePiYG, d3.interpolateViridis]
    },
    marketing: {
      name: 'Marketing',
      colors: [d3.interpolateMagma, d3.interpolatePlasma, d3.interpolateInferno, d3.interpolateCividis]
    }
  };

  onMount(() => {
    generateValuesAndRanges();
  });

  function generateValuesAndRanges() {
    if (data.length > 0) {
      values = [...new Set(data.flatMap(row => Object.values(row).filter(value => typeof value === 'number')))];
      values.sort((a, b) => a - b);  // Sort values for better UI experience

      mean = d3.mean(values);
      stdDev = d3.deviation(values);

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
    if (criteria === 'stdDev') {
      step = 3;  // Go to profile selection step
    } else {
      step = 2;
    }
  }

  function handleProfileSelection(profile) {
    selectedProfile = profile;
    applyFilter();
    step = 1;  // Reset step
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
      let stdDevValue = 0;
      if (selectedCriteria === 'above') {
        meetsCriteria = Object.entries(row).some(([key, value]) => {
          if (typeof value === 'number' && value > selectedValue) {
            row[`${key}_meetsCriteria`] = true;
          }
          return value > selectedValue;
        });
      } else if (selectedCriteria === 'below') {
        meetsCriteria = Object.entries(row).some(([key, value]) => {
          if (typeof value === 'number' && value < selectedValue) {
            row[`${key}_meetsCriteria`] = true;
          }
          return value < selectedValue;
        });
      } else if (selectedCriteria === 'equal') {
        meetsCriteria = Object.entries(row).some(([key, value]) => {
          if (typeof value === 'number' && value >= selectedValue.min && value <= selectedValue.max) {
            row[`${key}_meetsCriteria`] = true;
          }
          return value >= selectedValue.min && value <= selectedValue.max;
        });
      } else if (selectedCriteria === 'stdDev') {
        stdDevValue = Object.entries(row).filter(([key, value]) => typeof value === 'number').map(([key, value]) => {
          return (value - mean) / stdDev;
        })[0]; // Assuming single numeric value per row for simplicity
        row['stdDevValue'] = stdDevValue;
      }
      return { ...row, meetsCriteria, stdDevValue };
    });

    dispatch('filterData', { data: markedData, profile: selectedProfile });
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
    <button on:click={() => handleCriteriaSelection('stdDev')}>Std Deviation</button>
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

  {#if step === 3}
    {#each Object.keys(profiles) as profile}
      <button on:click={() => handleProfileSelection(profile)}>
        {profiles[profile].name}
      </button>
    {/each}
  {/if}
</div>
