"""
File Utilities

This module contains utility functions for file operations.
"""

import os
import csv
from datetime import datetime

def ensure_dir(directory):
    """Ensure that a directory exists, create it if it doesn't.
    
    Args:
        directory (str): Path to the directory
    """
    if not os.path.exists(directory):
        os.makedirs(directory)

def save_workout_data(data, filename=None, directory='workout_data'):
    """Save workout data to a CSV file.
    
    Args:
        data (dict): Dictionary containing workout data
        filename (str, optional): Output filename. If None, generates a timestamped filename.
        directory (str, optional): Directory to save the file in. Defaults to 'workout_data'.
        
    Returns:
        str: Path to the saved file
    """
    # Ensure directory exists
    ensure_dir(directory)
    
    # Generate filename if not provided
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"workout_{timestamp}.csv"
    
    filepath = os.path.join(directory, filename)
    
    # Prepare data for CSV
    fieldnames = data.keys()
    
    # Write to CSV
    with open(filepath, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow(data)
    
    return filepath

def load_workout_data(filepath):
    """Load workout data from a CSV file.
    
    Args:
        filepath (str): Path to the CSV file
        
    Returns:
        dict: Dictionary containing the workout data
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")
    
    with open(filepath, 'r') as f:
        reader = csv.DictReader(f)
        data = next(reader)  # Get the first row
    
    return data

def get_latest_workout_data(directory='workout_data'):
    """Get the most recent workout data file.
    
    Args:
        directory (str, optional): Directory to search in. Defaults to 'workout_data'.
        
    Returns:
        dict: Dictionary containing the most recent workout data, or None if no files found
    """
    if not os.path.exists(directory):
        return None
        
    # Get all CSV files in the directory
    files = [f for f in os.listdir(directory) if f.endswith('.csv')]
    
    if not files:
        return None
    
    # Sort by modification time (newest first)
    files.sort(key=lambda x: os.path.getmtime(os.path.join(directory, x)), reverse=True)
    
    # Load the most recent file
    latest_file = os.path.join(directory, files[0])
    return load_workout_data(latest_file)
