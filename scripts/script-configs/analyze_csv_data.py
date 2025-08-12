#!/usr/bin/env python3
"""
CSV Data Analysis Script for San Diego County Permit Data
Analyzes the downloaded CSV file to understand data structure and fields
"""

import pandas as pd
import json
import os
from pathlib import Path

def analyze_csv_file():
    """Analyze the downloaded CSV file structure"""
    
    # Look for the downloaded CSV file
    csv_files = [
        "RecordList20250811.csv",
        "C:/Users/Moussa/AppData/Local/Temp/playwright-mcp-output/2025-08-12T04-45-42.791Z/RecordList20250811.csv"
    ]
    
    csv_file = None
    for file_path in csv_files:
        if os.path.exists(file_path):
            csv_file = file_path
            break
    
    if not csv_file:
        print("❌ CSV file not found. Checking current directory...")
        # List all CSV files in current directory
        current_dir = Path(".")
        csv_files_found = list(current_dir.glob("*.csv"))
        if csv_files_found:
            print(f"📁 Found CSV files: {csv_files_found}")
            csv_file = str(csv_files_found[0])
        else:
            print("❌ No CSV files found in current directory")
            return None
    
    print(f"📊 Analyzing CSV file: {csv_file}")
    
    try:
        # Read the CSV file
        df = pd.read_csv(csv_file)
        
        print(f"\n✅ Successfully loaded CSV with {len(df)} rows and {len(df.columns)} columns")
        
        # Display basic information
        print("\n📋 Column Names and Data Types:")
        for i, (col, dtype) in enumerate(zip(df.columns, df.dtypes)):
            print(f"{i+1:2d}. {col:<30} ({dtype})")
        
        print(f"\n📊 Data Shape: {df.shape}")
        print(f"📊 Memory Usage: {df.memory_usage(deep=True).sum() / 1024:.2f} KB")
        
        # Display first few rows
        print("\n🔍 First 3 rows of data:")
        print(df.head(3).to_string())
        
        # Check for missing values
        print("\n❓ Missing Values Analysis:")
        missing_data = df.isnull().sum()
        for col, missing_count in missing_data.items():
            if missing_count > 0:
                percentage = (missing_count / len(df)) * 100
                print(f"   {col:<30}: {missing_count:3d} missing ({percentage:5.1f}%)")
        
        # Analyze unique values in key columns
        print("\n🔑 Unique Values in Key Columns:")
        key_columns = ['Record Type', 'Record Status', 'Short Notes']
        for col in key_columns:
            if col in df.columns:
                unique_vals = df[col].value_counts()
                print(f"\n   {col}:")
                for val, count in unique_vals.head(10).items():
                    print(f"      {val:<30}: {count:3d}")
        
        # Address analysis
        if 'Address' in df.columns:
            print("\n🏠 Address Analysis:")
            addresses_with_data = df['Address'].dropna()
            print(f"   Total addresses: {len(addresses_with_data)}")
            print(f"   Sample addresses:")
            for addr in addresses_with_data.head(5):
                print(f"      {addr}")
        
        # Export analysis results
        analysis_results = {
            'file_info': {
                'filename': csv_file,
                'rows': len(df),
                'columns': len(df.columns),
                'memory_usage_kb': df.memory_usage(deep=True).sum() / 1024
            },
            'columns': {
                'names': list(df.columns),
                'types': {col: str(dtype) for col, dtype in zip(df.columns, df.dtypes)}
            },
            'missing_data': {col: int(count) for col, count in df.isnull().sum().items()},
            'sample_data': df.head(3).to_dict('records'),
            'unique_values': {}
        }
        
        # Add unique values for key columns
        for col in key_columns:
            if col in df.columns:
                analysis_results['unique_values'][col] = df[col].value_counts().to_dict()
        
        # Save analysis results
        with open('csv_analysis_results.json', 'w') as f:
            json.dump(analysis_results, f, indent=2, default=str)
        
        print(f"\n💾 Analysis results saved to: csv_analysis_results.json")
        
        return analysis_results
        
    except Exception as e:
        print(f"❌ Error analyzing CSV file: {e}")
        return None

if __name__ == "__main__":
    print("🔍 San Diego County Permit CSV Data Analysis")
    print("=" * 50)
    
    results = analyze_csv_file()
    
    if results:
        print("\n✅ Analysis completed successfully!")
        print("\n📋 Summary:")
        print(f"   • File: {results['file_info']['filename']}")
        print(f"   • Rows: {results['file_info']['rows']}")
        print(f"   • Columns: {results['file_info']['columns']}")
        print(f"   • Available fields: {', '.join(results['columns']['names'])}")
    else:
        print("\n❌ Analysis failed!")
