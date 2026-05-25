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
    async def detect_circular_merge(profile_id: str, max_depth: int = 10) -> Tuple[bool, List[str]]:
        """
        Detect circular merge chains before they cause issues.
        
        Example circular chain: A→B→C→A
        
        Args:
            profile_id: Starting profile ID to check
            max_depth: Maximum chain depth to check (prevents infinite loops)
            
        Returns:
            Tuple of (has_circle, chain_path)
            - has_circle: True if circular reference detected
            - chain_path: List of profile IDs in the chain
            
        CRITICAL: Always call this before merge operations to prevent data corruption.
        """
        visited = set()
        chain = []
        current_id = profile_id
        
        for _ in range(max_depth):
            if current_id in visited:
                # Circular reference detected!
                logger.error(
                    f"Circular merge detected: {' → '.join(chain)} → {current_id}"
                )
                return True, chain
            
            visited.add(current_id)
            chain.append(current_id)
            
            # Check if current ID was merged into another
            is_valid, next_id, _ = await IdentityResolutionService.validate_profile_id(current_id)
            
            if is_valid or next_id is None:
                # End of chain - no circle
                return False, chain
            
            current_id = next_id
        
        # Max depth exceeded - assume circular to be safe
        logger.warning(
            f"Max depth ({max_depth}) exceeded checking {profile_id}. "
            f"Assuming circular reference."
        )
        return True, chain

    @staticmethod
    async def validate_no_circular_merges(profile_ids: List[str]) -> None:
        """
        Validate no circular merges exist in list of profiles.
        
        Raises ValueError if circular merge detected.
        
        Args:
            profile_ids: List of profile IDs to check
            
        Raises:
            ValueError: If circular merge chain detected
        """
        for profile_id in profile_ids:
            has_circle, chain = await IdentityResolutionService.detect_circular_merge(profile_id)
            if has_circle:
                raise ValueError(
                    f"Circular merge detected starting at {profile_id}: "
                    f"{' → '.join(chain)}. Cannot proceed with merge operation."
                )

    @staticmethod
    async def check_profile_resurrection(profile_id: str) -> Tuple[bool, Optional[str]]:
        """
        Check if profile ID was previously used and merged (zombie profile detection).
        
        This prevents accidentally creating a new profile with an ID that was
        previously merged, which would create duplicate/inconsistent data.
        
        Args:
            profile_id: Profile ID to check
            
        Returns:
            Tuple of (is_resurrected, merged_into_id):
            - is_resurrected: True if this ID was previously merged
            - merged_into_id: The profile ID this was merged into (if applicable)
            
        Example:
            >>> is_resurrected, merged_into = await check_profile_resurrection("profile-456")
            >>> if is_resurrected:
            >>>     print(f"ERROR: profile-456 was merged into {merged_into}!")
            >>>     print(f"Use {merged_into} instead of creating new profile-456")
        """
        # Check if this ID exists in any profile's IDs list (meaning it was merged)
        similar_profiles = await profile_db.load_profiles_to_merge(
            merge_by=[("ids", profile_id)],
            condition='must',
            limit=1
        )
        
        if similar_profiles:
            # This ID was used before and merged
            existing_profile = similar_profiles[0]
            
            # Check if a NEW profile with this ID also exists
            current_profile = await profile_db.load(profile_id)
            
            if current_profile and current_profile.id != existing_profile.id:
                # RESURRECTION DETECTED!
                logger.error(
                    f"Profile resurrection detected! {profile_id} was previously "
                    f"merged into {existing_profile.id} but a new profile with "
                    f"ID {profile_id} exists. This is a data inconsistency."
                )
                return True, existing_profile.id
        
        return False, None

    @staticmethod
    def check_ids_overflow(profile: Profile, max_ids: int = 1000) -> Tuple[bool, int]:
        """
        Check if profile.ids array is becoming too large.
        
        Large IDs arrays can cause:
        - Database performance issues
        - Memory problems
        - Slow query performance
        
        Args:
            profile: Profile to check
            max_ids: Maximum recommended IDs count
            
        Returns:
            Tuple of (is_overflow, current_count)
            
        Recommendation: If overflow detected, implement ID compaction or archival.
        """
        current_count = len(profile.ids) if profile.ids else 0
        
        if current_count > max_ids:
            logger.warning(
                f"Profile {profile.id} has {current_count} IDs (max recommended: {max_ids}). "
                f"Consider implementing ID compaction."
            )
            return True, current_count
        
        return False, current_count

    @staticmethod
    async def resolve_by_profile_ids(
        primary_profile_id: str,
        additional_profile_ids: List[str],
        validate_circular: bool = True,
        validate_resurrection: bool = True
    ) -> Optional[Profile]:
        """
        Merge profiles by explicit profile IDs with safety validations.
        
        Args:
            primary_profile_id: The main profile ID to merge others into
            additional_profile_ids: List of profile IDs to merge with primary
            validate_circular: Check for circular merge chains (recommended: True)
            validate_resurrection: Check for profile resurrection (recommended: True)
            
        Returns:
            Merged profile or None if no merge was performed
            
        Raises:
            ValueError: If circular merge detected or validation fails
            
        CRITICAL Safety Checks:
        - Circular merge detection
        - Profile resurrection check
        - Profile IDs overflow warning
        """
        logger.info(
            f"External identity resolution: Merging profile {primary_profile_id} "
            f"with {len(additional_profile_ids)} additional profiles"
        )
        
        # Safety check: Detect circular merges
        if validate_circular:
            all_ids = [primary_profile_id] + additional_profile_ids
            await IdentityResolutionService.validate_no_circular_merges(all_ids)
        
        # Safety check: Detect profile resurrection
        if validate_resurrection:
            for profile_id in [primary_profile_id] + additional_profile_ids:
                is_resurrected, merged_into = await IdentityResolutionService.check_profile_resurrection(profile_id)
                if is_resurrected:
                    raise ValueError(
                        f"Profile resurrection detected: {profile_id} was previously "
                        f"merged into {merged_into}. This indicates a data inconsistency. "
                        f"Use {merged_into} instead."
                    )
        
        # Perform merge
        merged_profile = await deduplicate_profile(
            profile_id=primary_profile_id,
            profile_ids=additional_profile_ids
        )
        
        # Post-merge validation: Check for IDs overflow
        if merged_profile:
            is_overflow, count = IdentityResolutionService.check_ids_overflow(merged_profile)
            if is_overflow:
                logger.warning(
                    f"Merged profile {merged_profile.id} has {count} IDs. "
                    f"Consider implementing ID compaction strategy."
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
