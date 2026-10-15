"""
Abstract Base Class for Message Brokers

Defines the interface that all broker implementations must follow.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict


class MessageBroker(ABC):
    """
    Abstract base class for message broker implementations.
    
    All broker implementations (RabbitMQ, Kafka, Pulsar) must inherit
    from this class and implement the required methods.
    """
    
    def __init__(self, config):
        """
        Initialize broker with configuration.
        
        Args:
            config: MessageBrokerConfig instance
        """
        self.config = config
        self._client = None
        self._producer = None
    
    @abstractmethod
    async def connect(self) -> None:
        """
        Establish connection to the message broker.
        
        Raises:
            ConnectionError: If connection fails
        """
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """
        Close connection to the message broker.
        """
        pass
    
    @abstractmethod
    async def publish(self, message: Dict[str, Any]) -> None:
        """
        Publish a message to the broker.
        
        Args:
            message: Dictionary containing the message payload
            
        Raises:
            PublishError: If publishing fails
        """
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """
        Check if broker connection is healthy.
        
        Returns:
            bool: True if healthy, False otherwise
        """
        pass
    
    def is_connected(self) -> bool:
        """
        Check if currently connected to broker.
        
        Returns:
            bool: True if connected, False otherwise
        """
        return self._client is not None
