"""
Unit tests for Message Broker implementations
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock

from tracardi.service.message_broker.broker_config import MessageBrokerConfig
from tracardi.service.message_broker.broker_factory import get_message_broker, reset_broker_instance
from tracardi.service.message_broker.base_broker import MessageBroker


class TestMessageBrokerConfig:
    """Test MessageBrokerConfig"""
    
    def test_default_config(self):
        """Test default configuration"""
        config = MessageBrokerConfig()
        assert config.broker_type == 'rabbitmq'
        assert config.topic == 'tracardi-events'
        assert config.timeout == 30
    
    def test_invalid_broker_type(self):
        """Test invalid broker type raises error"""
        with pytest.raises(ValueError, match="Invalid broker_type"):
            MessageBrokerConfig(broker_type='invalid')
    
    def test_rabbitmq_specific_config(self):
        """Test RabbitMQ specific configuration"""
        config = MessageBrokerConfig(
            broker_type='rabbitmq',
            broker_url='amqp://localhost:5672',
            virtual_host='/test',
            exchange_type='topic'
        )
        assert config.broker_type == 'rabbitmq'
        assert config.virtual_host == '/test'
        assert config.exchange_type == 'topic'
    
    def test_kafka_specific_config(self):
        """Test Kafka specific configuration"""
        config = MessageBrokerConfig(
            broker_type='kafka',
            broker_url='localhost:9092',
            group_id='test-group'
        )
        assert config.broker_type == 'kafka'
        assert config.group_id == 'test-group'
    
    @patch.dict('os.environ', {
        'TRACARDI_MESSAGE_BROKER': 'rabbitmq',
        'TRACARDI_BROKER_URL': 'amqp://test:5672',
        'TRACARDI_BROKER_TOPIC': 'test-topic',
        'TRACARDI_BROKER_USERNAME': 'admin',
        'TRACARDI_BROKER_PASSWORD': 'secret'
    })
    def test_from_env(self):
        """Test loading configuration from environment"""
        config = MessageBrokerConfig.from_env()
        assert config.broker_type == 'rabbitmq'
        assert config.broker_url == 'amqp://test:5672'
        assert config.topic == 'test-topic'
        assert config.username == 'admin'
        assert config.password == 'secret'


class TestBrokerFactory:
    """Test Broker Factory"""
    
    def setup_method(self):
        """Reset broker instance before each test"""
        reset_broker_instance()
    
    @patch('tracardi.service.message_broker.broker_config.message_broker_config')
    def test_get_rabbitmq_broker(self, mock_config):
        """Test getting RabbitMQ broker instance"""
        mock_config.broker_type = 'rabbitmq'
        broker = get_message_broker()
        
        from tracardi.service.message_broker.implementations.rabbitmq_broker import RabbitMQBroker
        assert isinstance(broker, RabbitMQBroker)
    
    @patch('tracardi.service.message_broker.broker_config.message_broker_config')
    def test_get_kafka_broker(self, mock_config):
        """Test getting Kafka broker instance"""
        mock_config.broker_type = 'kafka'
        broker = get_message_broker()
        
        from tracardi.service.message_broker.implementations.kafka_broker import KafkaBroker
        assert isinstance(broker, KafkaBroker)
    
    @patch('tracardi.service.message_broker.broker_config.message_broker_config')
    @patch('tracardi.service.license.License.has_license', return_value=False)
    def test_pulsar_requires_license(self, mock_license, mock_config):
        """Test Pulsar requires commercial license"""
        mock_config.broker_type = 'pulsar'
        
        with pytest.raises(ValueError, match="requires Tracardi commercial license"):
            get_message_broker()
    
    @patch('tracardi.service.message_broker.broker_config.message_broker_config')
    def test_unknown_broker_type(self, mock_config):
        """Test unknown broker type raises error"""
        mock_config.broker_type = 'unknown'
        
        with pytest.raises(ValueError, match="Unknown broker type"):
            get_message_broker()
    
    @patch('tracardi.service.message_broker.broker_config.message_broker_config')
    def test_singleton_pattern(self, mock_config):
        """Test broker factory returns singleton instance"""
        mock_config.broker_type = 'rabbitmq'
        
        broker1 = get_message_broker()
        broker2 = get_message_broker()
        
        assert broker1 is broker2  # Same instance


class TestRabbitMQBroker:
    """Test RabbitMQ Broker"""
    
    def setup_method(self):
        """Setup test config"""
        self.config = MessageBrokerConfig(
            broker_type='rabbitmq',
            broker_url='amqp://localhost:5672',
            topic='test-topic'
        )
    
    @pytest.mark.asyncio
    @patch('tracardi.service.message_broker.implementations.rabbitmq_broker.Connection')
    async def test_connect(self, mock_connection_class):
        """Test RabbitMQ connection"""
        from tracardi.service.message_broker.implementations.rabbitmq_broker import RabbitMQBroker
        
        # Mock connection
        mock_conn = MagicMock()
        mock_channel = MagicMock()
        mock_conn.channel.return_value = mock_channel
        mock_connection_class.return_value = mock_conn
        
        broker = RabbitMQBroker(self.config)
        await broker.connect()
        
        assert broker.is_connected()
        mock_connection_class.assert_called_once()
        mock_conn.connect.assert_called_once()
    
    @pytest.mark.asyncio
    @patch('tracardi.service.message_broker.implementations.rabbitmq_broker.Connection')
    async def test_publish(self, mock_connection_class):
        """Test message publishing"""
        from tracardi.service.message_broker.implementations.rabbitmq_broker import RabbitMQBroker
        
        # Mock connection and producer
        mock_conn = MagicMock()
        mock_channel = MagicMock()
        mock_producer = MagicMock()
        mock_conn.channel.return_value = mock_channel
        mock_connection_class.return_value = mock_conn
        
        broker = RabbitMQBroker(self.config)
        await broker.connect()
        broker._producer = mock_producer
        
        # Publish message
        message = {'event': 'test', 'data': {}}
        await broker.publish(message)
        
        mock_producer.publish.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_publish_without_connection_fails(self):
        """Test publishing without connection raises error"""
        from tracardi.service.message_broker.implementations.rabbitmq_broker import RabbitMQBroker
        
        broker = RabbitMQBroker(self.config)
        
        with pytest.raises(RuntimeError, match="Not connected"):
            await broker.publish({'test': 'data'})
    
    @pytest.mark.asyncio
    @patch('tracardi.service.message_broker.implementations.rabbitmq_broker.Connection')
    async def test_disconnect(self, mock_connection_class):
        """Test RabbitMQ disconnection"""
        from tracardi.service.message_broker.implementations.rabbitmq_broker import RabbitMQBroker
        
        mock_conn = MagicMock()
        mock_channel = MagicMock()
        mock_conn.channel.return_value = mock_channel
        mock_connection_class.return_value = mock_conn
        
        broker = RabbitMQBroker(self.config)
        await broker.connect()
        await broker.disconnect()
        
        assert not broker.is_connected()
        mock_conn.release.assert_called_once()
    
    @pytest.mark.asyncio
    @patch('tracardi.service.message_broker.implementations.rabbitmq_broker.Connection')
    async def test_health_check(self, mock_connection_class):
        """Test health check"""
        from tracardi.service.message_broker.implementations.rabbitmq_broker import RabbitMQBroker
        
        mock_conn = MagicMock()
        mock_channel = MagicMock()
        mock_conn.channel.return_value = mock_channel
        mock_conn.connected = True
        mock_connection_class.return_value = mock_conn
        
        broker = RabbitMQBroker(self.config)
        await broker.connect()
        
        assert await broker.health_check() == True


class TestKafkaBroker:
    """Test Kafka Broker"""
    
    def setup_method(self):
        """Setup test config"""
        self.config = MessageBrokerConfig(
            broker_type='kafka',
            broker_url='localhost:9092',
            topic='test-topic'
        )
    
    @pytest.mark.asyncio
    @patch('tracardi.service.message_broker.implementations.kafka_broker.AIOKafkaProducer')
    async def test_connect(self, mock_producer_class):
        """Test Kafka connection"""
        from tracardi.service.message_broker.implementations.kafka_broker import KafkaBroker
        
        # Mock producer
        mock_producer = AsyncMock()
        mock_producer_class.return_value = mock_producer
        
        broker = KafkaBroker(self.config)
        await broker.connect()
        
        assert broker.is_connected()
        mock_producer.start.assert_called_once()
    
    @pytest.mark.asyncio
    @patch('tracardi.service.message_broker.implementations.kafka_broker.AIOKafkaProducer')
    async def test_publish(self, mock_producer_class):
        """Test message publishing"""
        from tracardi.service.message_broker.implementations.kafka_broker import KafkaBroker
        
        # Mock producer
        mock_producer = AsyncMock()
        mock_producer_class.return_value = mock_producer
        
        broker = KafkaBroker(self.config)
        await broker.connect()
        
        # Publish message
        message = {'event': 'test', 'data': {}}
        await broker.publish(message)
        
        mock_producer.send_and_wait.assert_called_once_with(
            self.config.topic,
            value=message
        )
    
    @pytest.mark.asyncio
    async def test_publish_without_connection_fails(self):
        """Test publishing without connection raises error"""
        from tracardi.service.message_broker.implementations.kafka_broker import KafkaBroker
        
        broker = KafkaBroker(self.config)
        
        with pytest.raises(RuntimeError, match="Not connected"):
            await broker.publish({'test': 'data'})
    
    @pytest.mark.asyncio
    @patch('tracardi.service.message_broker.implementations.kafka_broker.AIOKafkaProducer')
    async def test_disconnect(self, mock_producer_class):
        """Test Kafka disconnection"""
        from tracardi.service.message_broker.implementations.kafka_broker import KafkaBroker
        
        mock_producer = AsyncMock()
        mock_producer_class.return_value = mock_producer
        
        broker = KafkaBroker(self.config)
        await broker.connect()
        await broker.disconnect()
        
        assert not broker.is_connected()
        mock_producer.stop.assert_called_once()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
