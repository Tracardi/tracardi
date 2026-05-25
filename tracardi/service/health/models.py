"""
Data models for health check responses.
"""
from enum import Enum
from typing import Dict, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class HealthStatus(str, Enum):
    """Health status enumeration"""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"
    UNKNOWN = "unknown"


class ComponentHealth(BaseModel):
    """Health status of a single component"""
    status: HealthStatus = Field(..., description="Component health status")
    message: Optional[str] = Field(None, description="Additional information")
    response_time_ms: Optional[float] = Field(None, description="Response time in milliseconds")
    details: Optional[Dict] = Field(None, description="Additional details")
    
    class Config:
        use_enum_values = True


class HealthCheckResponse(BaseModel):
    """Complete health check response"""
    status: HealthStatus = Field(..., description="Overall health status")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Check timestamp")
    version: Optional[str] = Field(None, description="Application version")
    components: Dict[str, ComponentHealth] = Field(default_factory=dict, description="Component health statuses")
    
    class Config:
        use_enum_values = True
    
    def is_healthy(self) -> bool:
        """Check if system is healthy"""
        return self.status == HealthStatus.HEALTHY
    
    def is_ready(self) -> bool:
        """Check if system is ready to serve traffic"""
        # System is ready if all critical components are healthy
        critical_components = ["elasticsearch", "mysql", "redis"]
        for comp in critical_components:
            if comp in self.components:
                if self.components[comp].status != HealthStatus.HEALTHY:
                    return False
        return True
