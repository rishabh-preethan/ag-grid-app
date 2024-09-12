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


def save_plot(fig, column_name):
    """Save a matplotlib figure to the images directory and return the file path."""
    # Ensure the images directory exists
    os.makedirs('images', exist_ok=True)
    
    # Generate a unique filename using the current date and time
    filename = f"{column_name}_plot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    filepath = os.path.join('images', filename)
    
    # Save the figure
    fig.savefig(filepath, format='png', bbox_inches='tight')
    
    return filepath

def summarize_date_time(df, column_name):
    date_format = "%Y-%m-%d"  # Adjust to match the format in your CSV
    try:
        date_series = pd.to_datetime(df[column_name], format=date_format, errors='coerce')
    except ValueError:
        date_series = df[column_name].apply(lambda x: pd.to_datetime(x, errors='coerce') if pd.notnull(x) else pd.NaT)

    # Convert dates to strings for ECharts
    date_series_str = date_series.dropna().dt.strftime(date_format)
    
    # Get date counts
    date_counts = Counter(date_series_str)
    sorted_dates = sorted(date_counts.keys())
    sorted_counts = [date_counts[date] for date in sorted_dates]

    # Generate ECharts options for date distribution
    chart_options = {
        "title": {
            "text": f"Distribution of {column_name}"
        },
        "tooltip": {
            "trigger": "axis"
        },
        "xAxis": {
            "type": "category",
            "data": sorted_dates,
            "axisLabel": {
                "rotate": 45
            }
        },
        "yAxis": {
            "type": "value"
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
        'min_date': date_series.min().strftime(date_format),
        'max_date': date_series.max().strftime(date_format),
        'unique_dates': date_series.nunique(),
        'null_count': date_series.isnull().sum(),
        'chart_options': chart_options  # Include ECharts options in the summary
    }
    
    return date_summary

def summarize_numeric(df, column_name):
    # Calculate summary statistics
    summary = {
        "Mean": df[column_name].mean(),
        "Median": df[column_name].median(),
        "Standard Deviation": df[column_name].std(),
        "Min": df[column_name].min(),
        "Max": df[column_name].max(),
        "25th Percentile": df[column_name].quantile(0.25),
        "75th Percentile": df[column_name].quantile(0.75),
        "Unique Values": df[column_name].nunique()
    }

    # Drop NA values
    data = df[column_name].dropna()
    
    # Calculate histogram data
    counts, bin_edges = np.histogram(data, bins=30)
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
    
    # Convert histogram data to ECharts format
    chart_options = {
        "title": {
            "text": f"Distribution of {column_name}"
        },
        "tooltip": {
            "trigger": "axis"
        },
        "xAxis": {
            "type": "category",
            "data": [f"{round(edge, 2)}" for edge in bin_centers],
            "axisLabel": {
                "rotate": 45
            }
        },
        "yAxis": {
            "type": "value"
        },
        "series": [
            {
                "name": column_name,
                "type": "bar",
                "data": counts.tolist(),
                "color": "lightgreen"
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
    summary = {
        "Most Frequent Value": value_counts.idxmax(),
        "Frequency of Most Frequent Value": value_counts.max(),
        "Unique Categories": value_counts.shape[0],
        "Top 5 Categories": value_counts.head(5).to_dict()
    }
    
    # Top 5 categories and frequencies
    top_categories = value_counts.head(5)
    categories = top_categories.index.tolist()
    frequencies = top_categories.values.tolist()
    
    # Generate ECharts options
    chart_options = {
        "title": {
            "text": f"Top 5 Categories of {column_name}"
        },
        "tooltip": {
            "trigger": "axis"
        },
        "xAxis": {
            "type": "category",
            "data": categories,
            "axisLabel": {
                "rotate": 45
            }
        },
        "yAxis": {
            "type": "value"
        },
        "series": [
            {
                "name": column_name,
                "type": "bar",
                "data": frequencies,
                "color": "pastel"
            }
        ]
    }
    
    # Include ECharts options in the summary
    summary['chart_options'] = chart_options
    
    return summary

# Function for generating an analytical summary for 'Text' columns
def summarize_text(df, column_name):
    summary = {
        "Total Text Length": df[column_name].str.len().sum(),
        "Average Text Length": df[column_name].str.len().mean(),
        "Number of Unique Entries": df[column_name].nunique(),
        "Most Frequent Text": df[column_name].mode()[0] if not df[column_name].mode().empty else None,
        "Top 5 Most Frequent Texts": df[column_name].value_counts().head(5).to_dict()
    }
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
    # Use summarize_numeric to get basic statistics
    summary = summarize_numeric(df, column_name)
    
    # Add financial specific statistics
    summary["Total Sum"] = df[column_name].sum()
    summary["Currency Format Detected"] = any(df[column_name].astype(str).str.contains(r'[\$\€\¥]'))
    
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
            "text": f"Boxplot of {column_name}"
        },
        "tooltip": {
            "trigger": "item",
            "formatter": "{a} <br/>{b} : {c}"
        },
        "xAxis": {
            "type": "category",
            "data": [column_name]
        },
        "yAxis": {
            "type": "value"
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
    summary = {
        "Total Unique Locations": df[column_name].nunique(),
        "Most Frequent Location": df[column_name].mode()[0] if not df[column_name].mode().empty else None,
        "Geospatial Coverage": f"{df[column_name].min()} to {df[column_name].max()} (approximation)"
    }
    
    # Top 5 locations
    top_locations = df[column_name].value_counts().head(5)
    locations = top_locations.index.tolist()
    frequencies = top_locations.values.tolist()
    
    # ECharts options for the bar chart
    chart_options = {
        "title": {
            "text": f"Top 5 Locations of {column_name}"
        },
        "tooltip": {
            "trigger": "axis"
        },
        "xAxis": {
            "type": "category",
            "data": locations,
            "axisLabel": {
                "rotate": 45
            }
        },
        "yAxis": {
            "type": "value"
        },
        "series": [
            {
                "name": column_name,
                "type": "bar",
                "data": frequencies,
                "color": "coolwarm"
            }
        ]
    }
    
    # Include ECharts options in the summary
    summary['chart_options'] = chart_options
    
    return summary

def summarize_boolean(df, column_name):
    # Summary statistics
    true_count = df[column_name].sum()
    false_count = df[column_name].count() - true_count
    summary = {
        "Count of True": true_count,
        "Count of False": false_count,
        "Percentage True": df[column_name].mean() * 100
    }
    
    # ECharts options for the pie chart
    chart_options = {
        "title": {
            "text": f"Distribution of {column_name}",
            "left": "center"
        },
        "tooltip": {
            "trigger": "item",
            "formatter": "{a} <br/>{b}: {c} ({d}%)"
        },
        "legend": {
            "orient": "vertical",
            "left": "left",
            "data": ["True", "False"]
        },
        "series": [
            {
                "name": column_name,
                "type": "pie",
                "radius": "50%",
                "data": [
                    {"value": true_count, "name": "True"},
                    {"value": false_count, "name": "False"}
                ],
                "itemStyle": {
                    "emphasis": {
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
    # Summary statistics from the numeric function
    summary = summarize_numeric(df, column_name)
    summary["Most Common Score"] = df[column_name].mode()[0] if not df[column_name].mode().empty else None
    
    # Compute the distribution of scores
    score_counts = df[column_name].value_counts().sort_index()
    scores = score_counts.index.tolist()
    counts = score_counts.values.tolist()
    
    # ECharts options for the bar chart
    chart_options = {
        "title": {
            "text": f"Ratings/Scoring Distribution for {column_name}"
        },
        "tooltip": {
            "trigger": "axis"
        },
        "xAxis": {
            "type": "category",
            "data": scores,
            "axisLabel": {
                "rotate": 45
            }
        },
        "yAxis": {
            "type": "value"
        },
        "series": [
            {
                "name": column_name,
                "type": "bar",
                "data": counts,
                "color": "magma"
            }
        ]
    }
    
    # Include ECharts options in the summary
    summary['chart_options'] = chart_options
    
    return summary

def summarize_duration(df, column_name):
    # Convert to timedelta and compute summary statistics
    duration_series = pd.to_timedelta(df[column_name], errors='coerce')
    summary = {
        "Total Duration": duration_series.sum(),
        "Average Duration": duration_series.mean(),
        "Shortest Duration": duration_series.min(),
        "Longest Duration": duration_series.max()
    }
    
    # Compute histogram data
    durations_seconds = duration_series.dropna().dt.total_seconds()
    hist, bin_edges = np.histogram(durations_seconds, bins=30)
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
    
    # ECharts options for the histogram
    chart_options = {
        "title": {
            "text": f"Distribution of Duration in {column_name}"
        },
        "tooltip": {
            "trigger": "axis"
        },
        "xAxis": {
            "type": "category",
            "data": bin_centers.tolist(),
            "axisLabel": {
                "formatter": "{value} s"
            }
        },
        "yAxis": {
            "type": "value"
        },
        "series": [
            {
                "name": column_name,
                "type": "bar",
                "data": hist.tolist(),
                "color": "darkblue"
            }
        ]
    }
    
    # Include ECharts options in the summary
    summary['chart_options'] = chart_options
    
    return summary


def summarize_survey_feedback(df, column_name):
    # Compute value counts
    value_counts = df[column_name].value_counts()
    summary = {
        "Most Common Response": value_counts.idxmax(),
        "Top 5 Responses": value_counts.head(5).to_dict(),
        "Unique Responses": df[column_name].nunique()
    }
    
    # Generate ECharts options for the top 5 responses
    top_responses = value_counts.head(5)
    chart_options = {
        "title": {
            "text": f"Top 5 Survey/Feedback Responses for {column_name}"
        },
        "tooltip": {
            "trigger": "item"
        },
        "xAxis": {
            "type": "category",
            "data": top_responses.index.tolist(),
            "axisLabel": {
                "rotate": 45  # Rotate labels for better readability
            }
        },
        "yAxis": {
            "type": "value"
        },
        "series": [
            {
                "name": column_name,
                "type": "bar",
                "data": top_responses.values.tolist(),
                "color": "viridis"
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