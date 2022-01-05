from pydantic import BaseModel
from tracardi.domain.named_entity import NamedEntity


class Configuration(BaseModel):
    source: NamedEntity
    url: str = "https://api2.amplitude.com/2/httpapi"
    timeout: int = 15
    event_type: str = None
    event_properties: str = None
    user_properties: str = None
    groups: str = None
    ip: str = None
    location_lat: str = None
    location_lng: str = None
    revenueType: str = None
    productId: str = None
    revenue: str = None
    quantity: str = None
    price: str = None
    language: str = None
    dma: str = None
    city: str = None
    region: str = None
    country: str = None
    carrier: str = None
    device_model: str = None
    device_manufacturer: str = None
    device_brand: str = None
    os_version: str = None
    os_name: str = None
    platform: str = None
