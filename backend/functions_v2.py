import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Use Agg backend for non-interactive plots
from io import BytesIO
import base64
import seaborn as sns
import os
from datetime import datetime
from collections import Counter
import numpy as np
from dateutil import parser


def summarize_date_time(df, column_name):
    # Attempt to parse dates using dateutil.parser
    def try_parse_date(value):
        try:
            # Try to parse the value; if successful, return the parsed date
            return parser.parse(value)
        except (parser.ParserError, TypeError, ValueError):
            # If parsing fails, return NaT (Not a Time)
            return pd.NaT

    # Apply the parsing function to the column
    date_series = df[column_name].apply(try_parse_date)

    # Convert dates to strings for ECharts
    date_series_str = date_series.dropna().dt.strftime("%Y-%m-%d")
    
    # Get date counts
    date_counts = Counter(date_series_str)
    sorted_dates = sorted(date_counts.keys())
    sorted_counts = [date_counts[date] for date in sorted_dates]

    # Generate ECharts options for date distribution
    chart_options = {
        "title": {
            # "text": f"Distribution of {column_name}"
        },
        "tooltip": {
            "trigger": "item",
            "formatter": "{b}: {c}",  # Display category, count, and percentage
            "position": 'top'  # Position tooltip above the mouse pointer
        },
        "xAxis": {
            "type": "category",
            "data": sorted_dates,
            "axisLabel": {
                "show": False  # Hide x-axis labels
            },
            "axisTick": {
                "show": False  # Hide x-axis ticks
            }
        },
        "yAxis": {
            "type": "value",
            "axisLabel": {
                "show": False  # Hide y-axis labels
            }
        },
        "series": [
            {
                "name": column_name,
                "type": "bar",
                "data": sorted_counts,
                "color": "skyblue"
            }
        ]
    }
    
    date_summary = {
        'chart_options': chart_options  # Include ECharts options in the summary
    }
    
    return date_summary



def summarize_numeric(df, column_name):
    # Calculate summary statistics
    summary = {}

    # Drop NA values
    data = df[column_name].dropna()

    # Calculate basic statistics
    mean_value = data.mean()
    median_value = data.median()
    std_dev = data.std()

    # Calculate histogram data (dynamic bin size based on data range)
    bin_count = 30  # Set the number of bins
    counts, bin_edges = np.histogram(data, bins=bin_count)
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2

    # Convert histogram data to ECharts format with meaningful labels
    chart_options = {
        "title": {
            "subtext": f"Mean: {mean_value:.2f}, Median: {median_value:.2f}",
            "textStyle": {
                "fontSize": 14  # Smaller font size for the title
            },
            "subtextStyle": {
                "fontSize": 12  # Smaller font size for the subtext
            },
            "left": 'center',
            "top": 10  # Add some top padding
        },
        "tooltip": {
            "trigger": "item",
            "formatter": "{b}: {c}",  # Display category, count, and percentage
            "position": 'top'  # Position tooltip above the mouse pointer
        },
        "grid": {
            "top": 60  # Add more space at the top to prevent overlap
        },
        "xAxis": {
            "type": "category",
            "data": [f"{round(edge, 2)}" for edge in bin_centers],
            "axisLabel": {
                "show": False  # Hide x-axis labels
            },
            "axisTick": {
                "show": False  # Hide x-axis ticks
            }
        },
        "yAxis": {
            "type": "value",
            "nameLocation": "middle",
            "nameGap": 35,  # Increase the gap between the y-axis label and the axis
            "axisLabel": {
                "show": False  # Hide y-axis labels
            },
            "splitLine": {
                "show": False  # Hide y-axis grid lines
            }
        },
        "series": [
            {
                "name": column_name,
                "type": "bar",
                "data": counts.tolist(),
                "color": "#5570c6"
            }
        ]
    }

    # Include the ECharts options in the summary
    summary['chart_options'] = chart_options

    return summary


def summarize_categorical(df, column_name):
    # Get the value counts
    value_counts = df[column_name].value_counts()
    
    # Summary statistics
    summary = {}
    
    # Top 5 categories and frequencies
    top_categories = value_counts.head(5)
    categories = top_categories.index.tolist()
    frequencies = top_categories.values.tolist()
    
    # Generate ECharts options
    chart_options = {
        "title": {
            # "text": f"Top Categories",
            "textStyle": {
                "fontSize": 14  # Smaller font size for the title
            },
            "left": 'center',
            "top": 10  # Add some top padding
        },
        "tooltip": {
            "trigger": "item",
            "formatter": "{b}: {c}",  # Display category, count, and percentage
            "position": 'top'  # Position tooltip above the mouse pointer
        },
        "grid": {
            "top": 60  # Add more space at the top to prevent overlap
        },
        "xAxis": {
            "type": "category",
            "data": categories,
            "axisLabel": {
                "show": False  # Hide x-axis labels
            },
            "axisTick": {
                "show": False  # Hide x-axis ticks
            }
        },
        "yAxis": {
            "type": "value",
            "nameLocation": "middle",
            "nameGap": 35,  # Increase the gap between the y-axis label and the axis
            "axisLabel": {
                "show": False  # Hide y-axis labels
            }
        },
        "series": [
            {
                "name": column_name,
                "type": "bar",
                "data": frequencies,
                "color": "#d81159"  # Use a color scheme appropriate for ECharts
            }
        ]
    }
    
    # Include ECharts options in the summary
    summary['chart_options'] = chart_options
    
    return summary



# Function for generating an analytical summary for 'Text' columns
def summarize_text(df, column_name):
    summary = {}
    return summary

# Function for generating an analytical summary for 'Identifiers (IDs)' columns
def summarize_identifiers(df, column_name):
    summary = {
        "Total Unique IDs": df[column_name].nunique(),
        "Duplicated IDs": df[column_name].duplicated().sum(),
        "First 5 IDs": df[column_name].head(5).tolist()
    }
    return summary

def summarize_financial(df, column_name):
    summary = {}
    
    # Compute boxplot statistics
    data = df[column_name].dropna()
    q1 = data.quantile(0.25)
    q3 = data.quantile(0.75)
    iqr = q3 - q1
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr
    
    # ECharts options for the boxplot
    chart_options = {
        "title": {
            # "text": f"Boxplot of {column_name}",
            "textStyle": {
                "fontSize": 14  # Smaller font size for the title
            },
            "left": 'center',
            "top": 10  # Add some top padding
        },
        "tooltip": {
            "trigger": "item",
            "formatter": "{b}: {c}",  # Display category, count, and percentage
            "position": 'top'  # Position tooltip above the mouse pointer
        },
        "grid": {
            "top": 60  # Add more space at the top to prevent overlap
        },
        "xAxis": {
            "type": "category",
            "data": [column_name],
            "axisLabel": {
                "show": False  # Hide x-axis labels
            },
            "axisTick": {
                "show": False  # Hide x-axis ticks
            }
        },
        "yAxis": {
            "type": "value",
            "name": column_name,
            "nameLocation": "middle",
            "nameGap": 35  # Increase the gap between the y-axis label and the axis
        },
        "series": [
            {
                "name": column_name,
                "type": "boxplot",
                "data": [
                    [
                        np.min(data),
                        q1,
                        data.median(),
                        q3,
                        np.max(data)
                    ]
                ],
                "itemStyle": {
                    "color": "orange"
                }
            }
        ]
    }
    
    # Include ECharts options in the summary
    summary['chart_options'] = chart_options
    
    return summary


def summarize_geospatial(df, column_name):
    # Summary statistics
    summary = {}
    
    # Top 5 locations
    top_locations = df[column_name].value_counts().head(5)
    locations = top_locations.index.tolist()
    frequencies = top_locations.values.tolist()
    
    # ECharts options for the bar chart
    chart_options = {
        "title": {
            # "text": f"Top 5 Locations of {column_name}",
            "textStyle": {
                "fontSize": 14  # Smaller font size for the title
            },
            "left": 'center',
            "top": 10  # Add some top padding
        },
        "tooltip": {
            "trigger": "item",
            "formatter": "{b}: {c}",  # Display category, count, and percentage
            "position": 'top'  # Position tooltip above the mouse pointer
        },
        "grid": {
            "top": 60  # Add more space at the top to prevent overlap
        },
        "xAxis": {
            "type": "category",
            "data": locations,
            "axisLabel": {
                "show": False  # Hide x-axis labels
            },
            "axisTick": {
                "show": False  # Hide x-axis ticks
            }
        },
        "yAxis": {
            "type": "value",
            "name": "Frequency",
            "nameLocation": "middle",
            "nameGap": 35  # Increase the gap between the y-axis label and the axis
        },
        "series": [
            {
                "name": column_name,
                "type": "bar",
                "data": frequencies,
                "color": "#118ab2"  # Use a color scheme appropriate for ECharts
            }
        ]
    }
    
    # Include ECharts options in the summary
    summary['chart_options'] = chart_options
    
    return summary


def summarize_boolean(df, column_name):
    # Normalize the column to boolean
    def normalize_to_bool(value):
        if pd.isnull(value):
            return False  # Consider NaN values as False
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            # Convert string representations to boolean
            return value.strip().lower() in ['true', '1', 'yes']
        if isinstance(value, (int, float)):
            # Consider non-zero numbers as True
            return bool(value)
        return False  # Default case if none of the above match

    # Apply the normalization to the column
    df[column_name] = df[column_name].apply(normalize_to_bool)

    # Summary statistics
    true_count = df[column_name].sum()
    false_count = df[column_name].count() - true_count  # Total count minus true_count

    summary = {}

    # ECharts options for the pie chart
    chart_options = {
        "title": {
            "textStyle": {
                "fontSize": 14  # Smaller font size for the title
            },
            "left": "center",
            "top": 10  # Add some top padding
        },
        "tooltip": {
            "trigger": "item",
            "formatter": "{b}: {c} ({d}%)",  # Display category, count, and percentage
            "position": 'top'  # Position tooltip above the mouse pointer
        },
        "legend": {
            "show": False,  # Hide the legend
        },
        "series": [
            {
                "name": column_name,
                "type": "pie",
                "radius": "50%",
                "data": [
                    {"value": int(true_count), "name": "True", "itemStyle": {"color": "#0496ff"}},
                    {"value": int(false_count), "name": "False", "itemStyle": {"color": "#ffbc42"}}
                ],
                "label": {
                    "show": False  # Hide labels on the pie slices
                },
                "emphasis": {  # Adjusted itemStyle format
                    "itemStyle": {
                        "shadowBlur": 10,
                        "shadowOffsetX": 0,
                        "shadowColor": "rgba(0, 0, 0, 0.5)"
                    }
                }
            }
        ]
    }

    # Include ECharts options in the summary
    summary['chart_options'] = chart_options

    return summary



# Function for generating an analytical summary for 'Binary' columns
def summarize_binary(df, column_name):
    summary = summarize_boolean(df, column_name)
    summary["Mode"] = df[column_name].mode()[0] if not df[column_name].mode().empty else None

    # Binary representation is already handled by the Boolean pie chart
    return summary

# Function for generating an analytical summary for 'Contact Information' columns
def summarize_contact_information(df, column_name):
    summary = {
        "Total Entries": df[column_name].count(),
        "Unique Entries": df[column_name].nunique(),
        "Most Common Domain": df[column_name].str.extract(r'@(\w+\.\w+)').mode()[0].values[0] if '@' in df[column_name].iloc[0] else None
    }
    return summary

# Function for generating an analytical summary for 'Aggregated/Mixed Data' columns
def summarize_aggregated_mixed(df, column_name):
    summary = {
        "Sample of 5 Entries": df[column_name].head(5).tolist(),
        "Total Unique Entries": df[column_name].nunique()
    }
    return summary

# Function for generating an analytical summary for 'Special Symbols' columns
def summarize_special_symbols(df, column_name):
    summary = {
        "Total Entries with Special Symbols": df[column_name].str.contains(r'[^a-zA-Z0-9\s]').sum(),
        "Most Common Special Symbol": df[column_name].str.findall(r'[^a-zA-Z0-9\s]').explode().mode()[0] if not df[column_name].empty else None
    }
    return summary

def summarize_ratings_scoring(df, column_name):
    summary = {}
    
    # Compute the distribution of scores
    score_counts = df[column_name].value_counts().sort_index()
    scores = score_counts.index.tolist()
    counts = score_counts.values.tolist()
    
    # ECharts options for the bar chart
    chart_options = {
        "title": {
            # "text": f"Distribution for {column_name}",
            "textStyle": {
                "fontSize": 14  # Smaller font size for the title
            },
            "left": 'center',
            "top": 10  # Add some top padding
        },
        "tooltip": {
            "trigger": "item",
            "formatter": "{b}: {c}",  # Display category, count, and percentage
            "position": 'top'  # Position tooltip above the mouse pointer
        },
        "grid": {
            "top": 60  # Add more space at the top to prevent overlap
        },
        "xAxis": {
            "type": "category",
            "data": scores,
            "axisLabel": {
                "show": False  # Hide x-axis labels
            },
            "axisTick": {
                "show": False  # Hide x-axis ticks
            }
        },
        "yAxis": {
            "type": "value",
            "name": "Frequency",
            "nameLocation": "middle",
            "nameGap": 35,  # Increase the gap between the y-axis label and the axis
            "axisLabel": {
                "show": False  # Hide x-axis labels
            },
            "axisTick": {
                "show": False  # Hide x-axis ticks
            }
        },
        "series": [
            {
                "name": column_name,
                "type": "bar",
                "data": counts,
                "color": "#d81159"
            }
        ]
    }
    
    # Include ECharts options in the summary
    summary['chart_options'] = chart_options
    
    return summary


import pandas as pd
import numpy as np

def summarize_duration(df, column_name):
    # Convert to timedelta and compute summary statistics
    duration_series = pd.to_timedelta(df[column_name], errors='coerce')
    summary = {}
    
    # Compute histogram data
    durations_seconds = duration_series.dropna().dt.total_seconds()
    hist, bin_edges = np.histogram(durations_seconds, bins=30)
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
    
    # ECharts options for the histogram
    chart_options = {
        "title": {
            # "text": f"Distribution of Duration in {column_name}",
            "textStyle": {
                "fontSize": 14  # Smaller font size for the title
            },
            "left": 'center',
            "top": 10  # Add some top padding
        },
        "tooltip": {
            "trigger": "axis",
            "formatter": "{b}: {c} occurrences"  # Display bin center and count
        },
        "grid": {
            "top": 60  # Add more space at the top to prevent overlap
        },
        "xAxis": {
            "type": "category",
            "data": [f"{round(center, 2)} s" for center in bin_centers],  # Format bin centers
            "axisLabel": {
                "rotate": 45,
                "show": True  # Show x-axis labels with rotation
            },
            "axisTick": {
                "show": False  # Hide x-axis ticks
            }
        },
        "yAxis": {
            "type": "value",
            "name": "Frequency",
            "nameLocation": "middle",
            "nameGap": 35  # Increase the gap between the y-axis label and the axis
        },
        "series": [
            {
                "name": column_name,
                "type": "bar",
                "data": hist.tolist(),
                "color": "#d81159"
            }
        ]
    }
    
    # Include ECharts options in the summary
    summary['chart_options'] = chart_options
    
    return summary



def summarize_survey_feedback(df, column_name):
    # Compute value counts
    value_counts = df[column_name].value_counts()
    summary = {}
    
    # Generate ECharts options for the top 5 responses
    top_responses = value_counts.head(5)
    chart_options = {
        "title": {
            # "text": f"Top 5 Survey/Feedback Responses for {column_name}",
            "textStyle": {
                "fontSize": 14  # Smaller font size for the title
            },
            "left": 'center',
            "top": 10  # Add some top padding
        },
        "tooltip": {
            "trigger": "item",
            "formatter": "{b}: {c} responses"  # Display category and count
        },
        "grid": {
            "top": 60  # Add more space at the top to prevent overlap
        },
        "xAxis": {
            "type": "category",
            "data": top_responses.index.tolist(),
            "axisLabel": {
                "rotate": 45,  # Rotate labels for better readability
                "formatter": "{value}"  # Format x-axis labels
            },
            "axisTick": {
                "show": False  # Hide x-axis ticks
            }
        },
        "yAxis": {
            "type": "value",
            "name": "Frequency",
            "nameLocation": "middle",
            "nameGap": 35  # Increase the gap between the y-axis label and the axis
        },
        "series": [
            {
                "name": column_name,
                "type": "bar",
                "data": top_responses.values.tolist(),
                "color": "#d81159"  # You may need to adjust this color depending on ECharts' color schemes
            }
        ]
    }
    
    # Include ECharts options in the summary
    summary['chart_options'] = chart_options
    
    return summary


# Function for generating an analytical summary for 'File References' columns
def summarize_file_references(df, column_name):
    summary = {
        "Total Entries": df[column_name].count(),
        "Unique References": df[column_name].nunique(),
        "Common File Extensions": df[column_name].str.extract(r'\.(\w+)$').value_counts().head(3).to_dict()
    }
    return summary

# Function for generating an analytical summary for 'Miscellaneous' columns
def summarize_miscellaneous(df, column_name):
    summary = {
        "Total Entries": df[column_name].count(),
        "Unique Entries": df[column_name].nunique(),
        "Sample of 5 Entries": df[column_name].head(5).tolist()
    }
    return summary

# Function for generating an analytical summary for 'Names' columns
def summarize_names(df, column_name):
    summary = {
        "Total Unique Names": df[column_name].nunique(),
        "Most Common Name": df[column_name].mode()[0] if not df[column_name].mode().empty else None,
        "Top 5 Names": df[column_name].value_counts().head(5).to_dict()
    }
    return summary