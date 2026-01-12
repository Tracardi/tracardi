"""
Identity Resolution Service

This module provides external API interface for identity resolution.
When identity resolution is performed externally via API, the internal
automatic merging can be skipped by setting 'externalIdentityResolution': true
in tracker payload options.
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
