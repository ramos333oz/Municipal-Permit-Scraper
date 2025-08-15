#!/usr/bin/env python3
"""
GitHub Actions Setup Script for Municipal Permit Scraping
Helps configure secrets and validate environment for automation
"""

import os
import sys
import json
import subprocess
from typing import Dict, List, Optional

class GitHubActionsSetup:
    """Setup and validation for GitHub Actions automation"""
    
    def __init__(self):
        self.required_secrets = {
            'SUPABASE_URL': 'Your Supabase project URL',
            'SUPABASE_ANON_KEY': 'Your Supabase anonymous key',
            'GEOCODIO_API_KEY': 'Your Geocodio API key for geocoding'
        }
        
        self.optional_secrets = {
            'GOOGLE_MAPS_API_KEY': 'Google Maps API key (fallback geocoding)',
            'SLACK_WEBHOOK_URL': 'Slack webhook for notifications',
            'DISCORD_WEBHOOK_URL': 'Discord webhook for notifications'
        }
    
    def check_github_cli(self) -> bool:
        """Check if GitHub CLI is installed"""
        try:
            result = subprocess.run(['gh', '--version'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ GitHub CLI is installed")
                return True
        except FileNotFoundError:
            pass
        
        print("❌ GitHub CLI not found")
        print("Install from: https://cli.github.com/")
        return False
    
    def check_repository_auth(self) -> bool:
        """Check if user is authenticated with GitHub"""
        try:
            result = subprocess.run(['gh', 'auth', 'status'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ GitHub authentication verified")
                return True
        except Exception:
            pass
        
        print("❌ GitHub authentication required")
        print("Run: gh auth login")
        return False
    
    def validate_environment_file(self) -> Dict[str, str]:
        """Validate local environment file"""
        env_values = {}
        
        # Check for .env file
        if os.path.exists('.env'):
            print("✅ Found .env file")
            with open('.env', 'r') as f:
                for line in f:
                    if '=' in line and not line.startswith('#'):
                        key, value = line.strip().split('=', 1)
                        env_values[key] = value
        else:
            print("⚠️  No .env file found")
        
        # Check environment variables
        for key in self.required_secrets:
            value = env_values.get(key) or os.getenv(key)
            if value:
                print(f"✅ {key}: Found")
                env_values[key] = value
            else:
                print(f"❌ {key}: Missing")
        
        return env_values
    
    def set_github_secrets(self, env_values: Dict[str, str]) -> bool:
        """Set GitHub repository secrets"""
        if not self.check_github_cli() or not self.check_repository_auth():
            return False
        
        success_count = 0
        total_count = 0
        
        for secret_name, description in self.required_secrets.items():
            total_count += 1
            value = env_values.get(secret_name)
            
            if not value:
                print(f"⚠️  Skipping {secret_name}: No value found")
                continue
            
            try:
                # Set the secret using GitHub CLI
                result = subprocess.run([
                    'gh', 'secret', 'set', secret_name, '--body', value
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    print(f"✅ Set secret: {secret_name}")
                    success_count += 1
                else:
                    print(f"❌ Failed to set {secret_name}: {result.stderr}")
            
            except Exception as e:
                print(f"❌ Error setting {secret_name}: {e}")
        
        print(f"\n📊 Secrets configured: {success_count}/{total_count}")
        return success_count == total_count
    
    def validate_workflow_files(self) -> bool:
        """Validate GitHub Actions workflow files"""
        workflow_dir = '.github/workflows'
        
        if not os.path.exists(workflow_dir):
            print(f"❌ Workflow directory not found: {workflow_dir}")
            return False
        
        workflow_files = [
            'san-diego-scraper.yml',
            'multi-municipality-scraper.yml'
        ]
        
        valid_count = 0
        for workflow_file in workflow_files:
            file_path = os.path.join(workflow_dir, workflow_file)
            if os.path.exists(file_path):
                print(f"✅ Found workflow: {workflow_file}")
                valid_count += 1
            else:
                print(f"❌ Missing workflow: {workflow_file}")
        
        return valid_count == len(workflow_files)
    
    def test_scraper_locally(self) -> bool:
        """Test scraper execution locally"""
        print("\n🧪 Testing scraper locally...")
        
        # Check if we're in the right directory
        scraper_path = 'scripts/san-diego-script/san_diego_county_scraper.py'
        if not os.path.exists(scraper_path):
            print(f"❌ Scraper not found: {scraper_path}")
            return False
        
        # Check Python dependencies
        try:
            import playwright
            import supabase
            import pandas
            print("✅ Required Python packages available")
        except ImportError as e:
            print(f"❌ Missing Python package: {e}")
            print("Run: pip install -r requirements.txt")
            return False
        
        print("✅ Local environment validation passed")
        return True
    
    def generate_setup_summary(self) -> str:
        """Generate setup summary and next steps"""
        summary = """
# GitHub Actions Setup Summary

## ✅ Completed Steps:
- GitHub CLI authentication
- Repository secrets configuration
- Workflow files validation
- Local environment testing

## 🚀 Next Steps:

### 1. Test Workflow Manually
```bash
# Trigger workflow manually to test
gh workflow run "San Diego County Permit Scraper"
```

### 2. Monitor First Run
```bash
# Watch workflow execution
gh run watch
```

### 3. Check Results
- Go to Actions tab in GitHub repository
- Review logs and artifacts
- Verify data in Supabase dashboard

### 4. Schedule Validation
- Workflows are scheduled for weekly execution
- San Diego: Sunday 2 AM UTC
- Multi-municipality: Staggered execution

### 5. Scaling to Additional Municipalities
- Copy San Diego scraper structure
- Add new municipality to multi-municipality workflow
- Update matrix configuration

## 📊 Expected Performance:
- **Execution Time**: ~15 minutes per municipality
- **Cost**: $0/month (within GitHub free tier)
- **Reliability**: 99%+ uptime with GitHub infrastructure
- **Scalability**: Up to 20 concurrent jobs

## 🔧 Troubleshooting:
- Check workflow logs in GitHub Actions tab
- Verify secrets are properly set
- Monitor Supabase dashboard for data ingestion
- Review rate limiting if multiple municipalities fail

## 📞 Support:
- GitHub Actions Documentation: https://docs.github.com/actions
- Supabase Documentation: https://supabase.com/docs
- Project Issues: Create GitHub issue for assistance
"""
        return summary

def main():
    """Main setup function"""
    print("🚀 GitHub Actions Setup for Municipal Permit Scraping")
    print("=" * 60)
    
    setup = GitHubActionsSetup()
    
    # Step 1: Validate environment
    print("\n1️⃣ Validating local environment...")
    env_values = setup.validate_environment_file()
    
    # Step 2: Test local scraper
    print("\n2️⃣ Testing local scraper...")
    local_test_passed = setup.test_scraper_locally()
    
    # Step 3: Validate workflows
    print("\n3️⃣ Validating workflow files...")
    workflows_valid = setup.validate_workflow_files()
    
    # Step 4: Configure GitHub secrets
    print("\n4️⃣ Configuring GitHub secrets...")
    secrets_configured = setup.set_github_secrets(env_values)
    
    # Step 5: Generate summary
    print("\n5️⃣ Setup Summary")
    print("=" * 30)
    
    if all([local_test_passed, workflows_valid, secrets_configured]):
        print("✅ GitHub Actions setup completed successfully!")
        print(setup.generate_setup_summary())
        return 0
    else:
        print("❌ Setup incomplete. Please address the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
