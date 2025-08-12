#!/usr/bin/env python3
"""
CSV Data Processor for Municipal Permit Data
Processes actual CSV structure: Record Number, Type, Address, Date Opened, Status
"""

import pandas as pd
import json
import logging
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CSVDataProcessor:
    """Process CSV data from municipal portals with actual column structure"""
    
    def __init__(self):
        self.expected_columns = ['Record Number', 'Type', 'Address', 'Date Opened', 'Status']
        
    def analyze_csv_structure(self, csv_path):
        """Analyze CSV file structure and data quality"""
        logger.info(f"📊 Analyzing CSV structure: {csv_path}")
        
        try:
            df = pd.read_csv(csv_path)
            
            analysis = {
                'file_path': str(csv_path),
                'total_records': len(df),
                'total_columns': len(df.columns),
                'columns': list(df.columns),
                'data_types': df.dtypes.to_dict(),
                'missing_expected_columns': [],
                'data_completeness': {},
                'sample_data': {},
                'unique_values': {}
            }
            
            # Check for expected columns
            for col in self.expected_columns:
                if col not in df.columns:
                    analysis['missing_expected_columns'].append(col)
            
            # Analyze data completeness
            for col in df.columns:
                non_null = df[col].notna().sum()
                percentage = (non_null / len(df)) * 100
                analysis['data_completeness'][col] = {
                    'non_null_count': int(non_null),
                    'total_count': len(df),
                    'percentage': round(percentage, 1)
                }
            
            # Sample data for each column
            for col in df.columns:
                sample_values = df[col].dropna().head(5).tolist()
                analysis['sample_data'][col] = [str(val) for val in sample_values]
            
            # Unique values for categorical columns
            categorical_columns = ['Type', 'Status']
            for col in categorical_columns:
                if col in df.columns:
                    unique_values = df[col].value_counts().head(10).to_dict()
                    analysis['unique_values'][col] = {str(k): int(v) for k, v in unique_values.items()}
            
            # Address analysis
            if 'Address' in df.columns:
                addresses = df['Address'].dropna()
                analysis['address_analysis'] = {
                    'total_addresses': len(addresses),
                    'unique_addresses': len(addresses.unique()),
                    'sample_addresses': addresses.head(10).tolist(),
                    'address_patterns': self.analyze_address_patterns(addresses)
                }
            
            logger.info(f"✅ Analysis complete: {analysis['total_records']} records, {analysis['total_columns']} columns")
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Error analyzing CSV: {e}")
            return None
    
    def analyze_address_patterns(self, addresses):
        """Analyze address patterns for geocoding optimization"""
        patterns = {
            'with_state': 0,
            'with_zip': 0,
            'with_ca': 0,
            'avg_length': 0,
            'common_cities': {}
        }
        
        total_length = 0
        for addr in addresses:
            addr_str = str(addr).upper()
            total_length += len(addr_str)
            
            if ' CA ' in addr_str or addr_str.endswith(' CA'):
                patterns['with_ca'] += 1
            
            if any(state in addr_str for state in [' CA ', ' AZ ', ' NV ']):
                patterns['with_state'] += 1
            
            # Check for ZIP codes (5 digits at end)
            if addr_str.split()[-1].isdigit() and len(addr_str.split()[-1]) == 5:
                patterns['with_zip'] += 1
        
        patterns['avg_length'] = round(total_length / len(addresses), 1)
        
        return patterns
    
    def process_csv_to_permits(self, csv_path):
        """Convert CSV data to standardized permit format"""
        logger.info(f"🔄 Processing CSV to permit format: {csv_path}")
        
        try:
            df = pd.read_csv(csv_path)
            
            permits = []
            for _, row in df.iterrows():
                permit = {
                    # Core fields from CSV
                    'site_number': str(row.get('Record Number', '')).strip(),
                    'record_type': str(row.get('Type', '')).strip(),
                    'address': str(row.get('Address', '')).strip(),
                    'date_opened': str(row.get('Date Opened', '')).strip(),
                    'status': str(row.get('Status', '')).strip(),
                    
                    # Derived fields
                    'project_city': 'San Diego County',
                    'source_portal': 'San Diego County',
                    
                    # Placeholder fields for future enhancement
                    'project_company': None,
                    'project_contact': None,
                    'project_phone': None,
                    'project_email': None,
                    'quantity': None,
                    'material_description': None,
                    'notes': None,
                    
                    # Pricing fields (to be calculated)
                    'dump_fee': 0.0,
                    'ldp_fee': 0.0,
                    'trucking_price_per_load': None,
                    'total_price_per_load': None,
                    'roundtrip_minutes': None,
                    'added_minutes': 0,
                    
                    # Geocoding fields (to be populated)
                    'coordinates': None,
                    'geocoding_accuracy': None,
                    'geocoding_confidence': None,
                    'geocoding_source': None,
                    'formatted_address': None,
                    
                    # Metadata
                    'raw_csv_data': row.to_dict(),
                    'processed_at': datetime.now().isoformat(),
                    'scraped_at': datetime.now().isoformat()
                }
                
                # Clean empty strings to None
                for key, value in permit.items():
                    if isinstance(value, str) and value.strip() == '':
                        permit[key] = None
                
                permits.append(permit)
            
            logger.info(f"✅ Processed {len(permits)} permits from CSV")
            return permits
            
        except Exception as e:
            logger.error(f"❌ Error processing CSV: {e}")
            return []
    
    def validate_permit_data(self, permits_data):
        """Validate processed permit data"""
        logger.info(f"🔍 Validating {len(permits_data)} permits...")
        
        validation_results = {
            'total_permits': len(permits_data),
            'valid_permits': 0,
            'issues': [],
            'statistics': {
                'with_site_number': 0,
                'with_address': 0,
                'with_record_type': 0,
                'with_status': 0,
                'with_date_opened': 0
            }
        }
        
        for i, permit in enumerate(permits_data):
            issues = []
            
            # Check required fields
            if not permit.get('site_number'):
                issues.append(f"Missing site_number")
            else:
                validation_results['statistics']['with_site_number'] += 1
            
            if not permit.get('address'):
                issues.append(f"Missing address")
            else:
                validation_results['statistics']['with_address'] += 1
            
            if not permit.get('record_type'):
                issues.append(f"Missing record_type")
            else:
                validation_results['statistics']['with_record_type'] += 1
            
            if not permit.get('status'):
                issues.append(f"Missing status")
            else:
                validation_results['statistics']['with_status'] += 1
            
            if not permit.get('date_opened'):
                issues.append(f"Missing date_opened")
            else:
                validation_results['statistics']['with_date_opened'] += 1
            
            if issues:
                validation_results['issues'].append({
                    'permit_index': i,
                    'site_number': permit.get('site_number', 'Unknown'),
                    'issues': issues
                })
            else:
                validation_results['valid_permits'] += 1
        
        # Calculate percentages
        total = validation_results['total_permits']
        for key, count in validation_results['statistics'].items():
            percentage = (count / total) * 100 if total > 0 else 0
            validation_results['statistics'][f'{key}_percentage'] = round(percentage, 1)
        
        logger.info(f"✅ Validation complete: {validation_results['valid_permits']}/{total} permits valid")
        return validation_results
    
    def save_analysis_report(self, analysis, validation, output_path):
        """Save comprehensive analysis report"""
        report = {
            'generated_at': datetime.now().isoformat(),
            'csv_analysis': analysis,
            'validation_results': validation,
            'summary': {
                'total_records': analysis['total_records'] if analysis else 0,
                'data_completeness_score': self.calculate_completeness_score(analysis) if analysis else 0,
                'validation_score': (validation['valid_permits'] / validation['total_permits'] * 100) if validation and validation['total_permits'] > 0 else 0,
                'ready_for_geocoding': validation['statistics']['with_address'] if validation else 0
            }
        }
        
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        logger.info(f"📄 Analysis report saved: {output_path}")
        return report
    
    def calculate_completeness_score(self, analysis):
        """Calculate overall data completeness score"""
        if not analysis or 'data_completeness' not in analysis:
            return 0
        
        important_fields = ['Record Number', 'Type', 'Address', 'Status']
        total_score = 0
        field_count = 0
        
        for field in important_fields:
            if field in analysis['data_completeness']:
                total_score += analysis['data_completeness'][field]['percentage']
                field_count += 1
        
        return round(total_score / field_count, 1) if field_count > 0 else 0

def main():
    """Test the CSV data processor"""
    processor = CSVDataProcessor()
    
    # Test with reference CSV file
    csv_path = Path("data-example/RecordList20250811.csv")
    
    if csv_path.exists():
        logger.info(f"🧪 Testing CSV processor with: {csv_path}")
        
        # Analyze CSV structure
        analysis = processor.analyze_csv_structure(csv_path)
        
        # Process to permit format
        permits = processor.process_csv_to_permits(csv_path)
        
        # Validate data
        validation = processor.validate_permit_data(permits)
        
        # Save analysis report
        report_path = "csv_analysis_report.json"
        report = processor.save_analysis_report(analysis, validation, report_path)
        
        # Save processed permits
        permits_path = "processed_permits.json"
        with open(permits_path, 'w') as f:
            json.dump(permits, f, indent=2, default=str)
        
        logger.info(f"✅ Processing complete!")
        logger.info(f"📊 Summary: {report['summary']}")
        
    else:
        logger.error(f"❌ CSV file not found: {csv_path}")

if __name__ == "__main__":
    main()
