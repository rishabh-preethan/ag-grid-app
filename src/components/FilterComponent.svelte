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

  // Define color profiles with names and color arrays
  const profiles = {
    analytical: {
      name: 'Analytical',
      colors: ['#ADD8E6', '#90EE90', '#FFA07A', '#FF6347'] // Lighter shades
    },
    business: {
      name: 'Business',
      colors: ['#D8BFD8', '#B0E0E6', '#FFD700', '#98FB98']
    },
    financial: {
      name: 'Financial',
      colors: ['#FFB6C1', '#FFDAB9', '#E6E6FA', '#F0E68C']
    },
    marketing: {
      name: 'Marketing',
      colors: ['#FFE4E1', '#F5DEB3', '#FFFACD', '#E0FFFF']
    }
  };

  // Run this function when the component is mounted
  onMount(() => {
    generateValuesAndRanges();
  });

  /**
   * Generates unique values from data and calculates mean, standard deviation, and ranges.
   */
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

  /**
   * Generates values to display for selection based on the range.
   * @param {number} minValue - The minimum value in the dataset.
   * @param {number} maxValue - The maximum value in the dataset.
   * @returns {number[]} Array of displayed values.
   */
  function generateDisplayedValues(minValue, maxValue) {
    const stepSize = Math.ceil((maxValue - minValue) / 4);
    return [minValue, minValue + stepSize, minValue + 2 * stepSize, minValue + 3 * stepSize, maxValue];
  }

  /**
   * Handles selection of a filter criteria.
   * @param {string} criteria - The selected filter criteria.
   */
  function handleCriteriaSelection(criteria) {
    selectedCriteria = criteria;
    if (criteria === 'stdDev') {
      step = 3;  // Go to profile selection step
    } else if (criteria === 'textFilter') {
      step = 4; // Go to text filter selection step
    } else {
      step = 2;
    }
  }

  /**
   * Handles selection of a profile for standard deviation coloring.
   * @param {string} profile - The selected profile.
   */
  function handleProfileSelection(profile) {
    selectedProfile = profile;
    applyFilter();
    step = 1;  // Reset step
  }

  /**
   * Handles selection of a numeric value.
   * @param {number} value - The selected value.
   */
  function handleValueSelection(value) {
    selectedValue = value;
    applyFilter();
  }

  /**
   * Handles selection of a range of values.
   * @param {object} range - The selected range.
   */
  function handleRangeSelection(range) {
    selectedValue = range;
    applyFilter();
  }

  /**
   * Handles selection of a text filter.
   * @param {string} filter - The selected text filter.
   */
  function handleTextFilterSelection(filter) {
    selectedValue = filter;
    applyFilter();
  }

  /**
   * Applies the selected filter criteria to the data and dispatches the filtered data.
   */
  function applyFilter() {
    const markedData = data.map(row => {
      if (selectedCriteria === 'above') {
        Object.entries(row).forEach(([key, value]) => {
          if (typeof value === 'number' && value > selectedValue) {
            row[`${key}_meetsCriteria`] = true;
          }
        });
      } else if (selectedCriteria === 'below') {
        Object.entries(row).forEach(([key, value]) => {
          if (typeof value === 'number' && value < selectedValue) {
            row[`${key}_meetsCriteria`] = true;
          }
        });
      } else if (selectedCriteria === 'equal') {
        Object.entries(row).forEach(([key, value]) => {
          if (typeof value === 'number' && value >= selectedValue.min && value <= selectedValue.max) {
            row[`${key}_meetsCriteria`] = true;
          }
        });
      } else if (selectedCriteria === 'stdDev') {
        Object.entries(row).forEach(([key, value]) => {
          if (typeof value === 'number') {
            row[`${key}_stdDevValue`] = (value - mean) / stdDev;
          }
        });
      } else if (selectedCriteria === 'textFilter') {
        Object.entries(row).forEach(([key, value]) => {
          if (typeof value === 'string' && (
            (selectedValue === 'endsWithPradesh' && value.endsWith('Pradesh')) ||
            (selectedValue === 'hasH' && value.includes('h'))
          )) {
            row[`${key}_meetsCriteria`] = true;
          }
        });
      }
      return row;
    });

    dispatch('filterData', { data: markedData, profile: selectedProfile });
  }
</script>

<style>
  .filter-buttons {
    margin-bottom: 1rem;
    border-radius: 10px;
  }

  .filter-buttons button {
    background-color: white;
    border: 1px solid black;
    border-radius: 15px;
    padding: 0.5rem 1rem;
    margin: 0.2rem;
    cursor: pointer;
    font-size: 12px;
    font-weight: bold;
    transition: background-color 0.3s; /* Add transition for hover effect */
  }

  .filter-buttons button:hover {
    background-color: #f0f0f0;
  }

  @media (max-width: 600px) {
    .filter-buttons button {
      font-size: 10px;
      padding: 0.3rem 0.6rem;
    }
  }
</style>

<div class="filter-buttons">
  {#if step === 1}
    <button on:click={() => handleCriteriaSelection('above')}>Above</button>
    <button on:click={() => handleCriteriaSelection('below')}>Below</button>
    <button on:click={() => handleCriteriaSelection('equal')}>Equal To</button>
    <button on:click={() => handleCriteriaSelection('stdDev')}>Std Deviation</button>
    <button on:click={() => handleCriteriaSelection('textFilter')}>Text Filter</button>
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

  {#if step === 4}
    <button on:click={() => handleTextFilterSelection('endsWithPradesh')}>Ends with 'Pradesh'</button>
    <button on:click={() => handleTextFilterSelection('hasH')}>Has an 'h'</button>
  {/if}
</div>
