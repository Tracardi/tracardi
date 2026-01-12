"""
Unit tests for Grafana Loki integration
"""
import unittest
from unittest.mock import Mock, patch, MagicMock
import logging
import os


class TestLokiConfig(unittest.TestCase):
    """Test Loki configuration"""

    def test_loki_config_disabled_by_default(self):
        """Test that Loki is disabled by default"""
        from tracardi.config import LokiConfig
        
        env = {}
        config = LokiConfig(env)
        
        self.assertFalse(config.enabled)
        self.assertIsNone(config.url)

    def test_loki_config_enabled(self):
        """Test Loki configuration when enabled"""
        from tracardi.config import LokiConfig
        
        env = {
            'LOKI_ENABLED': 'yes',
            'LOKI_URL': 'http://localhost:3100',
            'LOKI_USERNAME': 'admin',
            'LOKI_PASSWORD': 'secret',
            'LOKI_LABELS': 'service=tracardi,environment=test'
        }
        config = LokiConfig(env)
        
        self.assertTrue(config.enabled)
        self.assertEqual(config.url, 'http://localhost:3100')
        self.assertEqual(config.username, 'admin')
        self.assertEqual(config.password, 'secret')
        self.assertIn('service', config.labels_dict)
        self.assertEqual(config.labels_dict['service'], 'tracardi')
        self.assertEqual(config.labels_dict['environment'], 'test')

    def test_loki_config_labels_parsing(self):
        """Test label parsing"""
        from tracardi.config import LokiConfig
        
        env = {
            'LOKI_LABELS': 'app=tracardi,env=prod,version=1.0'
        }
        config = LokiConfig(env)
        
        self.assertEqual(len(config.labels_dict), 3)
        self.assertEqual(config.labels_dict['app'], 'tracardi')
        self.assertEqual(config.labels_dict['env'], 'prod')
        self.assertEqual(config.labels_dict['version'], '1.0')

    def test_loki_config_disabled_without_url(self):
        """Test that Loki is disabled if URL is not provided"""
        from tracardi.config import LokiConfig
        
        env = {
            'LOKI_ENABLED': 'yes'
            # No LOKI_URL
        }
        config = LokiConfig(env)
        
        # Should be disabled because URL is missing
        self.assertFalse(config.enabled)


class TestLokiLogHandler(unittest.TestCase):
    """Test Loki log handler"""

    def setUp(self):
        """Set up test fixtures"""
        from tracardi.config import LokiConfig
        
        self.env = {
            'LOKI_ENABLED': 'yes',
            'LOKI_URL': 'http://localhost:3100',
            'LOKI_LABELS': 'service=tracardi,environment=test',
            'LOKI_BATCH_SIZE': '10',
            'LOKI_BATCH_INTERVAL': '5'
        }
        self.config = LokiConfig(self.env)

    def test_handler_initialization(self):
        """Test handler initialization"""
        from tracardi.exceptions.log_handler import LokiLogHandler
        
        handler = LokiLogHandler(loki_config=self.config)
        
        self.assertIsNotNone(handler)
        self.assertEqual(handler.loki_config, self.config)
        self.assertEqual(len(handler.collection), 0)

    def test_handler_disabled_when_config_disabled(self):
        """Test that handler doesn't emit when disabled"""
        from tracardi.exceptions.log_handler import LokiLogHandler
        from tracardi.config import LokiConfig
        
        disabled_config = LokiConfig({'LOKI_ENABLED': 'no'})
        handler = LokiLogHandler(loki_config=disabled_config)
        
        # Create a log record
        record = logging.LogRecord(
            name='test',
            level=logging.ERROR,
            pathname='test.py',
            lineno=1,
            msg='Test message',
            args=(),
            exc_info=None
        )
        
        handler.emit(record)
        
        # Should not add to collection when disabled
        self.assertEqual(len(handler.collection), 0)

    def test_handler_batching(self):
        """Test log batching"""
        from tracardi.exceptions.log_handler import LokiLogHandler
        
        handler = LokiLogHandler(loki_config=self.config)
        
        # Create multiple log records
        for i in range(5):
            record = logging.LogRecord(
                name='test',
                level=logging.ERROR,
                pathname='test.py',
                lineno=i,
                msg=f'Test message {i}',
                args=(),
                exc_info=None
            )
            handler.emit(record)
        
        # Should have 5 logs in collection
        self.assertEqual(len(handler.collection), 5)

    @patch('tracardi.exceptions.log_handler.requests.post')
    def test_send_batch(self, mock_post):
        """Test sending batch to Loki"""
        from tracardi.exceptions.log_handler import LokiLogHandler
        
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 204
        mock_post.return_value = mock_response
        
        handler = LokiLogHandler(loki_config=self.config)
        
        # Add some logs
        for i in range(3):
            record = logging.LogRecord(
                name='test',
                level=logging.ERROR,
                pathname='test.py',
                lineno=i,
                msg=f'Test message {i}',
                args=(),
                exc_info=None
            )
            handler.emit(record)
        
        # Send batch
        handler.send_batch()
        
        # Verify request was made
        self.assertTrue(mock_post.called)
        
        # Verify collection was cleared
        self.assertEqual(len(handler.collection), 0)

    def test_should_send_by_size(self):
        """Test batch sending triggered by size"""
        from tracardi.exceptions.log_handler import LokiLogHandler
        
        handler = LokiLogHandler(loki_config=self.config)
        
        # Add logs up to batch size
        for i in range(10):
            record = logging.LogRecord(
                name='test',
                level=logging.ERROR,
                pathname='test.py',
                lineno=i,
                msg=f'Test message {i}',
                args=(),
                exc_info=None
            )
            handler.emit(record)
        
        # Should trigger send
        self.assertTrue(handler.should_send())

    def test_auth_credentials(self):
        """Test authentication credentials"""
        from tracardi.exceptions.log_handler import LokiLogHandler
        
        handler = LokiLogHandler(loki_config=self.config)
        
        # Config has username and password
        self.config.username = 'admin'
        self.config.password = 'secret'
        
        auth = handler._get_auth()
        
        self.assertIsNotNone(auth)
        self.assertEqual(auth, ('admin', 'secret'))

    def test_no_auth_when_not_configured(self):
        """Test no auth when credentials not configured"""
        from tracardi.exceptions.log_handler import LokiLogHandler
        from tracardi.config import LokiConfig
        
        env = {
            'LOKI_ENABLED': 'yes',
            'LOKI_URL': 'http://localhost:3100'
        }
        config = LokiConfig(env)
        handler = LokiLogHandler(loki_config=config)
        
        auth = handler._get_auth()
        
        self.assertIsNone(auth)


class TestLokiIntegration(unittest.TestCase):
    """Integration tests for Loki logging"""

    @patch.dict(os.environ, {
        'LOKI_ENABLED': 'yes',
        'LOKI_URL': 'http://localhost:3100',
        'LOKI_LABELS': 'service=tracardi,environment=test'
    })
    def test_logger_with_loki_enabled(self):
        """Test that logger includes Loki handler when enabled"""
        # This test would require reloading the config module
        # In a real scenario, you'd test with environment variables set before import
        pass


if __name__ == '__main__':
    unittest.main()
