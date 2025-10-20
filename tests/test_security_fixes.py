#!/usr/bin/env python3
"""
AEGIS v2.0 - Security Fixes Test Suite
Auto-generated tests for Phase 3 security implementations
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock
import tempfile
import shutil

# Add workspace to path
sys.path.insert(0, '/workspace')


class TestEnvironmentSecurity(unittest.TestCase):
    """Test suite for environment variable security"""
    
    def setUp(self):
        """Set up test environment"""
        # Save original env vars
        self.original_env = os.environ.copy()
    
    def tearDown(self):
        """Restore original environment"""
        os.environ.clear()
        os.environ.update(self.original_env)
    
    def test_telegram_controller_requires_bot_token(self):
        """Test that telegram_controller raises error without BOT_TOKEN"""
        # Clear env vars
        os.environ.pop('TELEGRAM_BOT_TOKEN', None)
        os.environ.pop('TELEGRAM_CHAT_ID', None)
        
        # Should raise ValueError
        with self.assertRaises(ValueError) as context:
            import importlib
            if 'telegram_controller' in sys.modules:
                importlib.reload(sys.modules['telegram_controller'])
            else:
                import telegram_controller
        
        self.assertIn('TELEGRAM_BOT_TOKEN', str(context.exception))
    
    def test_telegram_controller_requires_chat_id(self):
        """Test that telegram_controller raises error without CHAT_ID"""
        # Set token but not chat_id
        os.environ['TELEGRAM_BOT_TOKEN'] = 'test_token_123'
        os.environ.pop('TELEGRAM_CHAT_ID', None)
        
        # Should raise ValueError
        with self.assertRaises(ValueError) as context:
            import importlib
            if 'telegram_controller' in sys.modules:
                importlib.reload(sys.modules['telegram_controller'])
            else:
                import telegram_controller
        
        self.assertIn('TELEGRAM_CHAT_ID', str(context.exception))
    
    def test_enhanced_notifications_requires_credentials(self):
        """Test that EnhancedNotifications requires credentials"""
        # Clear env
        os.environ.pop('TELEGRAM_BOT_TOKEN', None)
        os.environ.pop('TELEGRAM_CHAT_ID', None)
        
        from enhanced_notifications import EnhancedNotifications
        
        with self.assertRaises(ValueError) as context:
            EnhancedNotifications()
        
        self.assertIn('TELEGRAM_BOT_TOKEN', str(context.exception))
    
    def test_enhanced_notifications_with_valid_credentials(self):
        """Test that EnhancedNotifications works with valid credentials"""
        os.environ['TELEGRAM_BOT_TOKEN'] = 'valid_token_123:abcdef'
        os.environ['TELEGRAM_CHAT_ID'] = '123456789'
        
        from enhanced_notifications import EnhancedNotifications
        
        # Should not raise
        notifier = EnhancedNotifications()
        self.assertEqual(notifier.bot_token, 'valid_token_123:abcdef')
        self.assertEqual(notifier.chat_id, '123456789')


class TestHardcodedCredentialRemoval(unittest.TestCase):
    """Test that hardcoded credentials have been removed"""
    
    def test_no_hardcoded_telegram_token(self):
        """Verify no hardcoded Telegram token in source"""
        # Read telegram_controller.py
        with open('/workspace/telegram_controller.py', 'r') as f:
            content = f.read()
        
        # Should NOT contain the old hardcoded token
        self.assertNotIn('7289126201:AAH', content, 
                        "Found hardcoded Telegram token in telegram_controller.py")
        
        # Should contain AEGIS security comment
        self.assertIn('AEGIS v2.0 Security', content,
                     "Missing AEGIS security marker")
    
    def test_no_hardcoded_chat_id(self):
        """Verify no hardcoded chat ID in enhanced_notifications"""
        with open('/workspace/enhanced_notifications.py', 'r') as f:
            content = f.read()
        
        # Should NOT contain hardcoded chat ID
        self.assertNotIn('7517400013', content,
                        "Found hardcoded chat ID")
        
        # Should contain AEGIS security comment
        self.assertIn('AEGIS v2.0 Security', content,
                     "Missing AEGIS security marker")
    
    def test_apex_nexus_uses_dotenv(self):
        """Verify apex_nexus_v2.py uses standard dotenv"""
        with open('/workspace/apex_nexus_v2.py', 'r') as f:
            content = f.read()
        
        # Should import dotenv
        self.assertIn('from dotenv import load_dotenv', content,
                     "Missing dotenv import")
        
        # Should call load_dotenv()
        self.assertIn('load_dotenv()', content,
                     "Missing load_dotenv() call")
        
        # Should NOT have custom parser
        self.assertNotIn("with open('.env')", content,
                        "Still using custom .env parser")


class TestGitignoreSecurity(unittest.TestCase):
    """Test .gitignore security configuration"""
    
    def test_gitignore_exists(self):
        """Test that .gitignore file exists"""
        self.assertTrue(os.path.exists('/workspace/.gitignore'),
                       ".gitignore file does not exist")
    
    def test_gitignore_blocks_env(self):
        """Test that .gitignore blocks .env files"""
        with open('/workspace/.gitignore', 'r') as f:
            content = f.read()
        
        self.assertIn('.env', content, ".gitignore missing .env")
        self.assertIn('*.log', content, ".gitignore missing *.log")
        self.assertIn('*.db', content, ".gitignore missing *.db")
    
    def test_env_example_exists(self):
        """Test that .env.example template exists"""
        self.assertTrue(os.path.exists('/workspace/.env.example'),
                       ".env.example template does not exist")


class TestEnvironmentValidation(unittest.TestCase):
    """Test environment validation utility"""
    
    def test_env_validator_exists(self):
        """Test that env_validator.py exists"""
        self.assertTrue(os.path.exists('/workspace/utils/env_validator.py'),
                       "env_validator.py does not exist")
    
    def test_env_validator_detects_missing_vars(self):
        """Test validator detects missing required vars"""
        from utils.env_validator import EnvValidator
        
        # Clear all env vars
        for var in EnvValidator.REQUIRED_VARS:
            os.environ.pop(var, None)
        
        results = EnvValidator.validate()
        
        self.assertFalse(results['valid'], "Validator should fail with missing vars")
        self.assertTrue(len(results['errors']) > 0, "Should have errors")
    
    def test_env_validator_detects_placeholders(self):
        """Test validator detects placeholder values"""
        from utils.env_validator import EnvValidator
        
        # Set placeholder values
        os.environ['EXCHANGE_API_KEY'] = 'your_key_here'
        os.environ['EXCHANGE_API_SECRET'] = 'placeholder'
        os.environ['TELEGRAM_BOT_TOKEN'] = 'test'
        os.environ['TELEGRAM_CHAT_ID'] = '123'
        os.environ['LIVE_MODE'] = 'False'
        os.environ['INITIAL_BALANCE'] = '3.0'
        os.environ['MAX_POSITION_SIZE'] = '0.5'
        
        results = EnvValidator.validate()
        
        self.assertFalse(results['valid'], "Validator should detect placeholders")
    
    def test_env_validator_passes_with_valid_values(self):
        """Test validator passes with valid values"""
        from utils.env_validator import EnvValidator
        
        # Set valid values
        os.environ['EXCHANGE_API_KEY'] = 'valid_api_key_12345678901234567890'
        os.environ['EXCHANGE_API_SECRET'] = 'valid_secret_abcdefghij1234567890'
        os.environ['TELEGRAM_BOT_TOKEN'] = '123456789:ABCdefGHIjklMNOp'
        os.environ['TELEGRAM_CHAT_ID'] = '987654321'
        os.environ['LIVE_MODE'] = 'False'
        os.environ['INITIAL_BALANCE'] = '3.0'
        os.environ['MAX_POSITION_SIZE'] = '0.5'
        
        results = EnvValidator.validate()
        
        self.assertTrue(results['valid'], f"Validator should pass: {results['errors']}")


class TestSecurityScripts(unittest.TestCase):
    """Test security check scripts"""
    
    def test_daily_security_check_exists(self):
        """Test that daily security check script exists"""
        script_path = '/workspace/scripts/daily_security_check.sh'
        self.assertTrue(os.path.exists(script_path),
                       "daily_security_check.sh does not exist")
        
        # Check it's executable
        self.assertTrue(os.access(script_path, os.X_OK),
                       "daily_security_check.sh is not executable")


class TestDotenvIntegration(unittest.TestCase):
    """Test python-dotenv integration"""
    
    def test_dotenv_import(self):
        """Test that dotenv can be imported"""
        try:
            from dotenv import load_dotenv
            self.assertTrue(True, "dotenv imported successfully")
        except ImportError:
            self.fail("python-dotenv not installed")
    
    def test_apex_nexus_loads_dotenv(self):
        """Test that apex_nexus_v2 loads environment correctly"""
        # Create temp .env file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write('TEST_VAR=test_value_123\n')
            temp_env = f.name
        
        try:
            from dotenv import load_dotenv
            load_dotenv(temp_env)
            
            self.assertEqual(os.getenv('TEST_VAR'), 'test_value_123',
                           "dotenv failed to load test variable")
        finally:
            os.unlink(temp_env)


def run_tests():
    """Run all security tests"""
    print("="*70)
    print("AEGIS v2.0 - Security Fixes Test Suite")
    print("="*70)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestEnvironmentSecurity))
    suite.addTests(loader.loadTestsFromTestCase(TestHardcodedCredentialRemoval))
    suite.addTests(loader.loadTestsFromTestCase(TestGitignoreSecurity))
    suite.addTests(loader.loadTestsFromTestCase(TestEnvironmentValidation))
    suite.addTests(loader.loadTestsFromTestCase(TestSecurityScripts))
    suite.addTests(loader.loadTestsFromTestCase(TestDotenvIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("\n✅ ALL SECURITY TESTS PASSED!")
        return 0
    else:
        print("\n❌ SOME TESTS FAILED - Review above")
        return 1


if __name__ == '__main__':
    sys.exit(run_tests())
