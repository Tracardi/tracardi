"""
Identity Resolution Service

This module provides external API interface for identity resolution.
When identity resolution is performed externally via API, the internal
automatic merging can be skipped by setting 'externalIdentityResolution': true
in tracker payload options.

IMPORTANT: After external merge, always use the returned merged_profile_id 
in subsequent tracker payloads. Using old (merged) profile IDs will cause 
profile not found errors or duplicate profile creation.
"""

from typing import List, Optional, Tuple
from tracardi.domain.profile import Profile
from tracardi.service.merging.facade_old import deduplicate_profile, merge_profile_by_merging_keys
from tracardi.service.storage.elastic.interface import profile as profile_db
from tracardi.service.profile_merger import ProfileMerger
from tracardi.exceptions.log_handler import get_logger

logger = get_logger(__name__)


class IdentityResolutionService:
    """
    Service for external identity resolution API.
    
    This service allows external systems to perform identity resolution
    without triggering internal automatic merging.
    """

    @staticmethod
    async def validate_profile_id(profile_id: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Validate if a profile ID exists and check if it was merged.
        
        This is critical when using external identity resolution to ensure
        you're using the correct (merged) profile ID in tracker payloads.
        
        Args:
            profile_id: Profile ID to validate
            
        Returns:
            Tuple of (is_valid, actual_profile_id, error_message):
            - is_valid: True if profile exists and is usable
            - actual_profile_id: The current valid profile ID (may differ if merged)
            - error_message: Error description if not valid
            
        Examples:
            >>> is_valid, actual_id, error = await validate_profile_id("profile-456")
            >>> if not is_valid:
            >>>     print(f"Error: {error}")
            >>>     print(f"Use this ID instead: {actual_id}")
        """
        try:
            # Try to load the profile
            profile = await profile_db.load(profile_id)
            
            if profile is None:
                # Profile doesn't exist - check if it was merged
                # Try to find if this ID exists in any profile's ids list
                similar_profiles = await profile_db.load_profiles_to_merge(
                    merge_by=[("ids", profile_id)],
                    condition='must',
                    limit=1
                )
                
                if similar_profiles and len(similar_profiles) > 0:
                    # Found! This profile was merged into another
                    merged_into = similar_profiles[0]
                    logger.warning(
                        f"Profile {profile_id} was merged into {merged_into.id}. "
                        f"Use {merged_into.id} instead."
                    )
                    return False, merged_into.id, f"Profile {profile_id} was merged into {merged_into.id}"
                else:
                    # Profile truly doesn't exist
                    return False, None, f"Profile {profile_id} not found"
            
            # Profile exists and is valid
            return True, profile.id, None
            
        except Exception as e:
            logger.error(f"Error validating profile ID {profile_id}: {str(e)}")
            return False, None, f"Validation error: {str(e)}"

    @staticmethod
    async def get_active_profile_id(profile_id: str) -> Optional[str]:
        """
        Get the active (non-merged) profile ID for a given profile ID.
        
        If the profile was merged, returns the merged profile ID.
        If the profile is active, returns the same ID.
        If the profile doesn't exist, returns None.
        
        Args:
            profile_id: Profile ID to check
            
        Returns:
            Active profile ID or None
            
        Usage:
            >>> active_id = await get_active_profile_id("profile-456")
            >>> if active_id and active_id != "profile-456":
            >>>     print(f"Profile was merged, use {active_id}")
        """
        is_valid, actual_id, _ = await IdentityResolutionService.validate_profile_id(profile_id)
        return actual_id if actual_id else None

    @staticmethod
    async def resolve_by_profile_ids(
        primary_profile_id: str,
        additional_profile_ids: List[str]
    ) -> Optional[Profile]:
        """
        Merge profiles by explicit profile IDs.
        
        Args:
            primary_profile_id: The main profile ID to merge others into
            additional_profile_ids: List of profile IDs to merge with primary
            
        Returns:
            Merged profile or None if no merge was performed
        """
        logger.info(
            f"External identity resolution: Merging profile {primary_profile_id} "
            f"with {len(additional_profile_ids)} additional profiles"
        )
        
        merged_profile = await deduplicate_profile(
            profile_id=primary_profile_id,
            profile_ids=additional_profile_ids
        )
        
        return merged_profile

    @staticmethod
    async def resolve_by_merge_keys(
        profile_id: str,
        merge_keys: List[Tuple[str, str]]
    ) -> Optional[Profile]:
        """
        Merge profiles by matching key-value pairs.
        
        Args:
            profile_id: Primary profile ID
            merge_keys: List of (field, value) tuples to match profiles
                       Example: [('data.contact.email.main', 'user@example.com')]
            
        Returns:
            Merged profile or None if no merge was performed
        """
        logger.info(
            f"External identity resolution: Merging profile {profile_id} "
            f"using {len(merge_keys)} merge keys"
        )
        
        # Load the primary profile
        profile = await profile_db.load(profile_id)
        
        if profile is None:
            raise ValueError(f"Profile with ID {profile_id} not found")
        
        # Perform merge
        merged_profile = await merge_profile_by_merging_keys(
            profile=profile,
            merge_by=merge_keys
        )
        
        return merged_profile

    @staticmethod
    async def find_duplicate_profiles(
        merge_keys: List[Tuple[str, str]],
        limit: int = 1000
    ) -> List[Profile]:
        """
        Find duplicate profiles matching the given keys without merging.
        
        This is useful for preview/analysis before performing actual merge.
        
        Args:
            merge_keys: List of (field, value) tuples to match profiles
            limit: Maximum number of profiles to return
            
        Returns:
            List of matching profiles
        """
        logger.info(
            f"External identity resolution: Finding duplicates "
            f"using {len(merge_keys)} merge keys"
        )
        
        # Add keywords for trait fields
        merge_keys_with_keywords = ProfileMerger.add_keywords(merge_keys)
        
        # Load matching profiles
        similar_profiles = await profile_db.load_profiles_to_merge(
            merge_keys_with_keywords,
            condition='must',
            limit=limit
        )
        
        logger.info(f"Found {len(similar_profiles)} duplicate profiles")
        
        return similar_profiles

    @staticmethod
    async def resolve_by_field_value(
        field_name: str,
        field_value: str,
        primary_profile_id: Optional[str] = None
    ) -> Optional[Profile]:
        """
        Convenience method to merge profiles by a single field value.
        
        Args:
            field_name: Profile field name (e.g., 'data.contact.email.main')
            field_value: Value to match
            primary_profile_id: Optional primary profile ID. If not provided,
                              the newest profile will be used as primary.
            
        Returns:
            Merged profile or None if no merge was performed
        """
        merge_keys = [(field_name, field_value)]
        
        # Find all matching profiles
        duplicates = await IdentityResolutionService.find_duplicate_profiles(
            merge_keys=merge_keys
        )
        
        if len(duplicates) <= 1:
            logger.info("No duplicates found for merging")
            return None
        
        # Use provided primary or the first (newest) profile
        if primary_profile_id:
            primary_profile = await profile_db.load(primary_profile_id)
            if primary_profile is None:
                raise ValueError(f"Primary profile {primary_profile_id} not found")
        else:
            primary_profile = duplicates[0]
            primary_profile_id = primary_profile.id
        
        # Merge using the profile IDs
        additional_ids = [p.id for p in duplicates if p.id != primary_profile_id]
        
        return await IdentityResolutionService.resolve_by_profile_ids(
            primary_profile_id=primary_profile_id,
            additional_profile_ids=additional_ids
        )
