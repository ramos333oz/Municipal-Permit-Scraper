#!/usr/bin/env python3
"""
Environment Setup for Database Integration
Sets up environment variables and validates configuration
"""

import os
import sys

def setup_environment():
    """Set up environment variables for database integration"""
    
    # Supabase configuration
    os.environ['SUPABASE_URL'] = 'https://tellxlrnkwooikljwlhc.supabase.co'
    os.environ['SUPABASE_ANON_KEY'] = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRlbGx4bHJua3dvb2lrbGp3bGhjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQ4OTYyNzQsImV4cCI6MjA3MDQ3MjI3NH0.8qHGO5Iew5qL9-npMJNNdRZklZBJQPwEiDLuPZH7Nsk'
    
    # Geocoding API key (if available)
    if not os.getenv('GEOCODIO_API_KEY'):
        os.environ['GEOCODIO_API_KEY'] = '806d6c98688b022ff79c7dc6d08b662c897bfdb'
    
    print("✅ Environment variables configured")
    print(f"   SUPABASE_URL: {os.environ['SUPABASE_URL']}")
    print(f"   SUPABASE_ANON_KEY: {os.environ['SUPABASE_ANON_KEY'][:20]}...")
    print(f"   GEOCODIO_API_KEY: {os.environ.get('GEOCODIO_API_KEY', 'Not set')[:20]}...")

if __name__ == "__main__":
    setup_environment()
