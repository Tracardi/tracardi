"""
Identity Resolution API Payload Models

Request and response models for external identity resolution API.
"""

from typing import List, Optional, Tuple
from pydantic import BaseModel, Field


class IdentityResolutionByIdsRequest(BaseModel):
    """Request to merge profiles by explicit profile IDs"""
    
    primary_profile_id: str = Field(
        description="Primary profile ID to merge others into"
    )
    additional_profile_ids: List[str] = Field(
        description="List of profile IDs to merge with the primary profile"
    )


class IdentityResolutionByKeysRequest(BaseModel):
    """Request to merge profiles by matching key-value pairs"""
    
    profile_id: str = Field(
        description="Primary profile ID"
    )
    merge_keys: List[Tuple[str, str]] = Field(
        description="List of (field, value) tuples to identify duplicate profiles. "
                    "Example: [('data.contact.email.main', 'user@example.com')]"
    )


class IdentityResolutionByFieldRequest(BaseModel):
    """Request to merge profiles by a single field value"""
    
    field_name: str = Field(
        description="Profile field name to match. "
                    "Example: 'data.contact.email.main'"
    )
    field_value: str = Field(
        description="Field value to match"
    )
    primary_profile_id: Optional[str] = Field(
        default=None,
        description="Optional primary profile ID. If not provided, "
                    "the newest profile will be used as primary."
    )


class FindDuplicatesRequest(BaseModel):
    """Request to find duplicate profiles without merging"""
    
    merge_keys: List[Tuple[str, str]] = Field(
        description="List of (field, value) tuples to find duplicate profiles"
    )
    limit: int = Field(
        default=1000,
        description="Maximum number of profiles to return"
    )


class ProfileSummary(BaseModel):
    """Summary of a profile for API responses"""
    
    id: str
    ids: List[str] = []
    traits: Optional[dict] = {}
    created: Optional[str] = None
    updated: Optional[str] = None
    segments: Optional[List[str]] = []


class IdentityResolutionResponse(BaseModel):
    """Response from identity resolution operation"""
    
    success: bool
    merged_profile_id: Optional[str] = None
    merged_profile_ids: List[str] = Field(
        default=[],
        description="List of all profile IDs that were merged"
    )
    message: str
    profile: Optional[ProfileSummary] = None


class FindDuplicatesResponse(BaseModel):
    """Response with list of duplicate profiles"""
    
    success: bool
    count: int
    profiles: List[ProfileSummary]
    message: str
