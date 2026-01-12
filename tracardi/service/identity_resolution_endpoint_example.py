"""
Identity Resolution API Endpoints Example

This is an example implementation for TracardAPI.
Copy these endpoints to TracardAPI project.

Usage in tracker payload:
    POST /track
    {
        "source": {...},
        "events": [...],
        "options": {
            "externalIdentityResolution": true  // Skip internal merging
        }
    }
"""

from fastapi import APIRouter, HTTPException
from typing import List

from tracardi.domain.identity_resolution_payload import (
    IdentityResolutionByIdsRequest,
    IdentityResolutionByKeysRequest,
    IdentityResolutionByFieldRequest,
    FindDuplicatesRequest,
    IdentityResolutionResponse,
    FindDuplicatesResponse,
    ProfileSummary
)
from tracardi.service.identity_resolution_service import IdentityResolutionService
from tracardi.domain.profile import Profile

# Create router for identity resolution endpoints
router = APIRouter(
    prefix="/identity-resolution",
    tags=["Identity Resolution"]
)


def _profile_to_summary(profile: Profile) -> ProfileSummary:
    """Convert Profile to ProfileSummary for API response"""
    return ProfileSummary(
        id=profile.id,
        ids=profile.ids,
        traits=profile.traits,
        created=str(profile.metadata.time.insert) if profile.metadata.time.insert else None,
        updated=str(profile.metadata.time.update) if profile.metadata.time.update else None,
        segments=profile.segments
    )


@router.post(
    "/validate-profile",
    response_model=dict,
    summary="Validate profile ID before tracking"
)
async def validate_profile(profile_id: str):
    """
    Validate if a profile ID exists and is usable.
    
    Use this endpoint before sending events to ensure you're using the correct profile ID.
    If the profile was merged, this will return the current active profile ID.
    
    **Important**: Always validate profile IDs after external merge operations.
    
    Example request:
    ```
    GET /identity-resolution/validate-profile?profile_id=profile-456
    ```
    
    Example response (profile is valid):
    ```json
    {
        "is_valid": true,
        "profile_id": "profile-456",
        "message": "Profile is valid and active"
    }
    ```
    
    Example response (profile was merged):
    ```json
    {
        "is_valid": false,
        "profile_id": "profile-123",
        "error": "Profile profile-456 was merged into profile-123",
        "message": "Use profile-123 in tracker payloads"
    }
    ```
    """
    try:
        is_valid, actual_id, error = await IdentityResolutionService.validate_profile_id(profile_id)
        
        if is_valid:
            return {
                "is_valid": True,
                "profile_id": actual_id,
                "message": "Profile is valid and active"
            }
        else:
            return {
                "is_valid": False,
                "profile_id": actual_id,
                "error": error,
                "message": f"Use {actual_id} in tracker payloads" if actual_id else "Profile not found"
            }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Validation failed: {str(e)}"
        )


@router.post(
    "/merge-by-ids",
    response_model=IdentityResolutionResponse,
    summary="Merge profiles by profile IDs"
)
async def merge_profiles_by_ids(request: IdentityResolutionByIdsRequest):
    """
    Merge multiple profiles by their IDs.
    
    This endpoint merges specified profiles into a primary profile.
    All events and sessions from additional profiles will be moved to the primary profile.
    
    **CRITICAL**: After using this API:
    1. Use the returned `merged_profile_id` in all subsequent tracker payloads
    2. Set `externalIdentityResolution: true` in tracker payload options
    3. Validate profile IDs with `/validate-profile` endpoint before tracking
    
    **DO NOT** use old profile IDs after merge - they will not be found!
    
    Example request:
    ```json
    {
        "primary_profile_id": "profile-123",
        "additional_profile_ids": ["profile-456", "profile-789"]
    }
    ```
    """
    try:
        # Validate primary profile exists
        is_valid, actual_id, error = await IdentityResolutionService.validate_profile_id(
            request.primary_profile_id
        )
        
        if not is_valid:
            raise HTTPException(
                status_code=400,
                detail=f"Primary profile validation failed: {error}. " +
                       (f"Use {actual_id} instead" if actual_id else "Profile not found")
            )
        merged_profile = await IdentityResolutionService.resolve_by_profile_ids(
            primary_profile_id=request.primary_profile_id,
            additional_profile_ids=request.additional_profile_ids
        )
        
        if merged_profile:
            return IdentityResolutionResponse(
                success=True,
                merged_profile_id=merged_profile.id,
                merged_profile_ids=merged_profile.ids,
                message=f"Successfully merged {len(merged_profile.ids)} profiles",
                profile=_profile_to_summary(merged_profile)
            )
        else:
            return IdentityResolutionResponse(
                success=False,
                message="No profiles to merge or merge not needed"
            )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Identity resolution failed: {str(e)}"
        )


@router.post(
    "/merge-by-keys",
    response_model=IdentityResolutionResponse,
    summary="Merge profiles by matching keys"
)
async def merge_profiles_by_keys(request: IdentityResolutionByKeysRequest):
    """
    Merge profiles by matching key-value pairs.
    
    This endpoint finds and merges profiles that match the specified field values.
    Common use cases: merge by email, phone number, or custom identifier.
    
    **Note**: After using this API, set `externalIdentityResolution: true` in tracker 
    payload options to prevent internal automatic merging.
    
    Example request:
    ```json
    {
        "profile_id": "profile-123",
        "merge_keys": [
            ["data.contact.email.main", "user@example.com"]
        ]
    }
    ```
    """
    try:
        merged_profile = await IdentityResolutionService.resolve_by_merge_keys(
            profile_id=request.profile_id,
            merge_keys=request.merge_keys
        )
        
        if merged_profile:
            return IdentityResolutionResponse(
                success=True,
                merged_profile_id=merged_profile.id,
                merged_profile_ids=merged_profile.ids,
                message=f"Successfully merged {len(merged_profile.ids)} profiles",
                profile=_profile_to_summary(merged_profile)
            )
        else:
            return IdentityResolutionResponse(
                success=False,
                message="No profiles to merge or merge not needed"
            )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Identity resolution failed: {str(e)}"
        )


@router.post(
    "/merge-by-field",
    response_model=IdentityResolutionResponse,
    summary="Merge profiles by single field"
)
async def merge_profiles_by_field(request: IdentityResolutionByFieldRequest):
    """
    Convenience endpoint to merge profiles by a single field value.
    
    This is a simplified version of merge-by-keys for single field matching.
    
    **Note**: After using this API, set `externalIdentityResolution: true` in tracker 
    payload options to prevent internal automatic merging.
    
    Example request:
    ```json
    {
        "field_name": "data.contact.email.main",
        "field_value": "user@example.com",
        "primary_profile_id": "profile-123"
    }
    ```
    """
    try:
        merged_profile = await IdentityResolutionService.resolve_by_field_value(
            field_name=request.field_name,
            field_value=request.field_value,
            primary_profile_id=request.primary_profile_id
        )
        
        if merged_profile:
            return IdentityResolutionResponse(
                success=True,
                merged_profile_id=merged_profile.id,
                merged_profile_ids=merged_profile.ids,
                message=f"Successfully merged {len(merged_profile.ids)} profiles",
                profile=_profile_to_summary(merged_profile)
            )
        else:
            return IdentityResolutionResponse(
                success=False,
                message="No profiles to merge or merge not needed"
            )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Identity resolution failed: {str(e)}"
        )


@router.post(
    "/find-duplicates",
    response_model=FindDuplicatesResponse,
    summary="Find duplicate profiles without merging"
)
async def find_duplicate_profiles(request: FindDuplicatesRequest):
    """
    Find duplicate profiles matching the given keys without performing merge.
    
    This is useful for preview/analysis before performing actual merge.
    You can review the duplicate profiles and then decide whether to merge them.
    
    Example request:
    ```json
    {
        "merge_keys": [
            ["data.contact.email.main", "user@example.com"]
        ],
        "limit": 100
    }
    ```
    """
    try:
        profiles = await IdentityResolutionService.find_duplicate_profiles(
            merge_keys=request.merge_keys,
            limit=request.limit
        )
        
        profile_summaries = [_profile_to_summary(p) for p in profiles]
        
        return FindDuplicatesResponse(
            success=True,
            count=len(profiles),
            profiles=profile_summaries,
            message=f"Found {len(profiles)} duplicate profiles"
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to find duplicates: {str(e)}"
        )


# Example: How to include this router in your main FastAPI app
# 
# from fastapi import FastAPI
# from tracardi.service.identity_resolution_endpoint_example import router as identity_router
# 
# app = FastAPI()
# app.include_router(identity_router)
