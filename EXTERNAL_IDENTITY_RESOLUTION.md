# External Identity Resolution Service

This document explains how to use Tracardi's identity resolution (profile merging) feature through internal service layer.

**IMPORTANT**: This is an internal service - not exposed as public API endpoints. Use the service layer directly in your code with proper authentication and authorization.

## Overview

Tracardi automatically performs identity resolution (profile merging) when it detects profile changes. However, in some cases, you may want to control this process through an external system. This feature provides:

1. **External Control**: Perform identity resolution from your own systems via internal service
2. **Performance**: Gain performance by preventing unnecessary internal merging operations
3. **Customization**: Customize merging logic according to your business rules
4. **Flexibility**: Implement complex matching rules and validation logic before merging

## Flag Usage

If you've performed identity resolution externally, add the `externalIdentityResolution: true` flag when sending events to Tracardi. This way, Tracardi will skip internal merging.

### Example Tracker Payload

```json
POST /track
{
  "source": {
    "id": "source-123"
  },
  "session": {
    "id": "session-456"
  },
  "profile": {
    "id": "profile-789"
  },
  "events": [
    {
      "type": "page-view",
      "properties": {
        "url": "https://example.com"
      }
    }
  ],
  "options": {
    "externalIdentityResolution": true
  }
}
```

**Important**: The `options.externalIdentityResolution: true` setting prevents Tracardi from performing internal identity resolution.

## ⚠️ CRITICAL: Profile ID Validation

**IMPORTANT**: After external merge operations, merged profile IDs become invalid. You MUST use the returned `merged_profile_id` in tracker payloads.

### Why Validation Matters

```python
# ❌ WRONG - Using old profile ID after merge
merged_profile = await merge_profiles(primary="profile-123", additional=["profile-456"])
# profile-456 is now merged and deleted

await track_event(profile_id="profile-456")  # ❌ ERROR: Profile not found!
# Result: Creates duplicate profile or sends event to wrong profile
```

```python
# ✅ CORRECT - Using merged profile ID
merged_profile = await IdentityResolutionService.resolve_by_profile_ids(
    primary_profile_id="profile-123",
    additional_profile_ids=["profile-456"]
)
merged_id = merged_profile.id  # "profile-123"

await track_event(profile_id=merged_id)  # ✅ OK: Uses correct merged profile
```

### Profile Validation Method

Always validate profile IDs before tracking, especially after merge operations:

```python
from tracardi.service.identity_resolution_service import IdentityResolutionService

# Validate profile ID
is_valid, actual_id, error = await IdentityResolutionService.validate_profile_id(
    profile_id="profile-456"
)

if is_valid:
    print(f"Profile {actual_id} is valid and active")
else:
    if actual_id:
        print(f"Profile was merged into {actual_id}")
        print(f"Use {actual_id} in tracker payloads")
    else:
        print(f"Profile not found: {error}")
```

## Internal Service API

**IMPORTANT**: This is an internal service - not exposed as HTTP endpoints. Use the service layer directly in your code.

### 1. Merge by Profile IDs

```python
from tracardi.service.identity_resolution_service import IdentityResolutionService

# Merge specific profile IDs
merged_profile = await IdentityResolutionService.resolve_by_profile_ids(
    primary_profile_id="profile-123",
    additional_profile_ids=["profile-456", "profile-789"],
    validate_circular=True,      # Optional: detect circular merges
    validate_resurrection=True   # Optional: detect zombie profiles
)

if merged_profile:
    print(f"Merged profile ID: {merged_profile.id}")
    print(f"All merged IDs: {merged_profile.ids}")
```

### 2. Merge by Keys

```python
# Merge profiles by email
merged_profile = await IdentityResolutionService.resolve_by_merge_keys(
    profile_id="profile-123",
    merge_keys=[
        ("data.contact.email.main", "user@example.com")
    ]
)

# Multiple keys example
merged_profile = await IdentityResolutionService.resolve_by_merge_keys(
    profile_id="profile-123",
    merge_keys=[
        ("data.contact.email.main", "user@example.com"),
        ("data.contact.phone.main", "+1234567890")
    ]
)
```

### 3. Merge by Single Field (Convenience Method)

```python
# Merge by email (simple)
merged_profile = await IdentityResolutionService.resolve_by_field_value(
    field_name="data.contact.email.main",
    field_value="user@example.com",
    primary_profile_id="profile-123"  # Optional
)

# If primary_profile_id not specified, newest profile is used as primary
merged_profile = await IdentityResolutionService.resolve_by_field_value(
    field_name="data.contact.email.main",
    field_value="user@example.com"
)
```

### 4. Find Duplicates (Without Merging)

```python
# Find duplicates without merging (preview mode)
duplicate_profiles = await IdentityResolutionService.find_duplicate_profiles(
    merge_keys=[
        ("data.contact.email.main", "user@example.com")
    ],
    limit=100
)

print(f"Found {len(duplicate_profiles)} duplicate profiles")
for profile in duplicate_profiles:
    print(f"  - {profile.id}: {profile.traits.get('email')}")
```

### 5. Profile ID Validation

```python
# Validate if profile ID exists and is not merged
is_valid, actual_id, error = await IdentityResolutionService.validate_profile_id(
    profile_id="profile-456"
)

if not is_valid:
    print(f"Profile validation failed: {error}")
    if actual_id:
        print(f"Use this ID instead: {actual_id}")
```

### 6. Circular Merge Detection

```python
# Detect circular merge chains (A→B→C→A)
has_circle, chain = await IdentityResolutionService.detect_circular_merge(
    profile_id="profile-123",
    max_depth=10
)

if has_circle:
    print(f"Circular merge detected: {' → '.join(chain)}")
```

### 7. Profile Resurrection Check

```python
# Check if profile was previously merged (zombie detection)
is_resurrected, merged_into = await IdentityResolutionService.check_profile_resurrection(
    profile_id="profile-456"
)

if is_resurrected:
    print(f"WARNING: profile-456 was previously merged into {merged_into}")
    print(f"Do not create new profile with this ID!")
```

## Use Cases

### Use Case 1: Real-Time User Registration/Login (with Validation)

When a user registers or logs in, perform immediate identity resolution to merge anonymous browsing data with authenticated profile.

```python
from tracardi.service.identity_resolution_service import IdentityResolutionService

async def handle_user_login(email, anonymous_profile_id):
    """
    Merge anonymous profile with authenticated profile on login.
    INCLUDES PROFILE VALIDATION to prevent bugs.
    """
    # 1. VALIDATE anonymous profile ID first
    is_valid, actual_id, error = await IdentityResolutionService.validate_profile_id(
        anonymous_profile_id
    )
    
    if not is_valid:
        # Profile was merged or doesn't exist - use the actual ID
        anonymous_profile_id = actual_id or anonymous_profile_id
        print(f"Warning: Profile ID updated to {anonymous_profile_id}")
    
    # 2. Find duplicates by email
    duplicate_profiles = await IdentityResolutionService.find_duplicate_profiles(
        merge_keys=[
            ("data.contact.email.main", email)
        ]
    )
    
    # 3. If user has existing profile, merge with anonymous
    if len(duplicate_profiles) > 0:
        authenticated_profile_id = duplicate_profiles[0].id
        
        merged_profile = await IdentityResolutionService.resolve_by_profile_ids(
            primary_profile_id=authenticated_profile_id,
            additional_profile_ids=[anonymous_profile_id]
        )
        
        if not merged_profile:
            raise Exception("Merge failed")
        
        merged_profile_id = merged_profile.id
    else:
        # New user, use anonymous profile as base
        merged_profile_id = anonymous_profile_id
    
    # 4. VALIDATE merged profile before tracking
    is_valid, actual_id, error = await IdentityResolutionService.validate_profile_id(
        merged_profile_id
    )
    
    if not is_valid:
        raise Exception(f"Merged profile validation failed: {error}")
    
    # 5. Send login event with VALIDATED merged profile
    # (Use your tracking method here)
    await track_event(
        source_id="website",
        profile_id=merged_profile_id,
        events=[{
            "type": "user-login",
            "properties": {"email": email}
        }],
        options={
            "externalIdentityResolution": True  # Skip internal merge
        }
    )
    
    return merged_profile_id
```

### Use Case 2: Multi-Device User Tracking

Consolidate user profiles across different devices when they use the same credentials.

```python
from tracardi.service.identity_resolution_service import IdentityResolutionService

async def consolidate_cross_device_profiles(user_id, device_profile_ids):
    """
    Merge profiles from multiple devices for single user.
    """
    # Find primary profile by user_id
    profiles = await IdentityResolutionService.find_duplicate_profiles(
        merge_keys=[
            ("data.identifiers.user_id", user_id)
        ],
        limit=1
    )
    
    if not profiles:
        raise ValueError(f"No profile found for user_id {user_id}")
    
    primary_profile = profiles[0]
    
    # Merge all device profiles into primary
    merged_profile = await IdentityResolutionService.resolve_by_profile_ids(
        primary_profile_id=primary_profile.id,
        additional_profile_ids=device_profile_ids
    )
    
    return merged_profile.id if merged_profile else primary_profile.id
```

### Use Case 3: Batch Duplicate Cleanup

Perform scheduled batch processing to clean up duplicate profiles.

```python
from tracardi.service.identity_resolution_service import IdentityResolutionService

async def nightly_duplicate_cleanup():
    """
    Nightly job to clean up duplicate profiles across the system.
    """
    # Get unique emails from database
    unique_emails = get_all_unique_emails_from_database()
    
    merge_stats = {
        "processed": 0,
        "merged": 0,
        "errors": []
    }
    
    for email in unique_emails:
        try:
            # Find duplicates
            duplicates = await IdentityResolutionService.find_duplicate_profiles(
                merge_keys=[
                    ("data.contact.email.main", email)
                ]
            )
            
            # Only merge if there are actual duplicates
            if len(duplicates) > 1:
                merged_profile = await IdentityResolutionService.resolve_by_field_value(
                    field_name="data.contact.email.main",
                    field_value=email
                )
                
                if merged_profile:
                    merge_stats["merged"] += 1
                    print(f"Merged {len(duplicates)} profiles for {email}")
            
            merge_stats["processed"] += 1
            
        except Exception as e:
            merge_stats["errors"].append(f"{email}: {str(e)}")
            print(f"Error merging profiles for {email}: {str(e)}")
    
    # Log results
    print(f"Batch cleanup completed")
    print(f"Processed: {merge_stats['processed']}")
    print(f"Merged: {merge_stats['merged']}")
    print(f"Errors: {len(merge_stats['errors'])}")
    
    return merge_stats
```

### Use Case 4: CRM Integration

Sync profile merges from external CRM system.

```python
async def sync_crm_profile_merge(crm_master_id, crm_duplicate_ids):
    """
    When CRM merges records, mirror the merge in Tracardi.
    """
    # Map CRM IDs to Tracardi profile IDs
    master_profile = get_tracardi_profile_by_crm_id(crm_master_id)
    duplicate_profiles = [
        get_tracardi_profile_by_crm_id(crm_id) 
        for crm_id in crm_duplicate_ids
    ]
    
    # Merge in Tracardi
    merged_profile = await IdentityResolutionService.resolve_by_profile_ids(
        primary_profile_id=master_profile["id"],
        additional_profile_ids=[p["id"] for p in duplicate_profiles]
    )
    
    # Update CRM with merged Tracardi ID
    if merged_profile:
        update_crm_record(crm_master_id, {"tracardi_profile_id": merged_profile.id})
    
    return merged_profile
```

### Use Case 5: GDPR Data Consolidation

Consolidate all user data for GDPR data portability requests.

```python
async def consolidate_for_gdpr_request(user_email, additional_identifiers=None):
    """
    Find and merge all profiles for GDPR data export request.
    """
    all_profiles = []
    
    # Search by email
    email_profiles = await IdentityResolutionService.find_duplicate_profiles(
        merge_keys=[
            ("data.contact.email.main", user_email)
        ],
        limit=1000
    )
    all_profiles.extend(email_profiles)
    
    # Search by additional identifiers (phone, user_id, etc.)
    if additional_identifiers:
        for field, value in additional_identifiers.items():
            profiles = await IdentityResolutionService.find_duplicate_profiles(
                merge_keys=[(field, value)],
                limit=1000
            )
            all_profiles.extend(profiles)
    
    # Remove duplicates
    unique_profiles = {p.id: p for p in all_profiles}
    profile_ids = list(unique_profiles.keys())
    
    # Merge all profiles
    if len(profile_ids) > 1:
        merged_profile = await IdentityResolutionService.resolve_by_profile_ids(
            primary_profile_id=profile_ids[0],
            additional_profile_ids=profile_ids[1:]
        )
        
        consolidated_profile_id = merged_profile.id if merged_profile else profile_ids[0]
    else:
        consolidated_profile_id = profile_ids[0] if profile_ids else None
    
    # Export all data for GDPR request
    if consolidated_profile_id:
        full_profile = await load_full_profile_data(consolidated_profile_id)
        return full_profile
    
    return None
```

## Technical Details

### Internal Implementation

Flag check is performed in `tracardi/service/wf/workflow_manager_async.py`:

```python
skip_internal_merge = self.tracker_payload.options.get('externalIdentityResolution', False)

if self.profile is not None and self.profile.needs_merging() and not skip_internal_merge:
    self.profile = await self.merge_profile(self.profile)
```

### Service Layer

Identity resolution service is implemented in `tracardi/service/identity_resolution_service.py` and provides these methods:

- `resolve_by_profile_ids()`: Merge by explicit IDs
- `resolve_by_merge_keys()`: Merge by key-value matching
- `find_duplicate_profiles()`: Find duplicates (without merging)
- `resolve_by_field_value()`: Merge by single field
- `validate_profile_id()`: Validate profile ID and check if merged
- `detect_circular_merge()`: Detect circular merge chains
- `check_profile_resurrection()`: Check for zombie profiles
- `check_ids_overflow()`: Check profile.ids array size

### Data Models

Request/response models are defined in `tracardi/domain/identity_resolution_payload.py`.

## Best Practices

### 1. **CRITICAL: Always Validate Profile IDs After Merge**
```python
# After any merge operation
merged_profile = await IdentityResolutionService.resolve_by_profile_ids(...)
merged_id = merged_profile.id

# VALIDATE before using
is_valid, actual_id, error = await IdentityResolutionService.validate_profile_id(merged_id)
if not is_valid:
    raise Exception(f"Invalid profile ID: {error}")

# NOW safe to use
await track_event(profile_id=merged_id)
```

**Why**: Merged profile IDs become invalid. Using old IDs causes:
- Profile not found errors
- Duplicate profile creation
- Events going to wrong profiles
- Data inconsistency

### 2. **Always Use the Flag After External Merge**
```python
# After external merging, always use this flag
await track_event(
    profile_id=merged_id,
    options={"externalIdentityResolution": True}
)
```

### 3. **Store Merged Profile ID Mappings**
```python
# Keep track of old → new profile ID mappings
profile_merge_log = {
    "old_ids": ["profile-456", "profile-789"],
    "new_id": "profile-123",
    "merged_at": datetime.now(),
    "reason": "email match"
}
```

### 4. **Validate Before Every Track Call**
```python
async def safe_track_event(profile_id, events):
    # Always validate first
    is_valid, actual_id, error = await IdentityResolutionService.validate_profile_id(profile_id)
    if not is_valid:
        profile_id = actual_id  # Use corrected ID
    
    return await track_event(profile_id, events)
```

### 5. **Duplicate Check Before Merge**
Check with `find_duplicate_profiles()` method before merging to preview results.

### 6. **Error Handling & Retry Logic**
```python
async def merge_with_retry(primary_id, additional_ids, max_retries=3, backoff_base=2):
    """
    Retry merge with exponential backoff if failures occur.
    """
    for attempt in range(max_retries):
        try:
            return await IdentityResolutionService.resolve_by_profile_ids(
                primary_id, additional_ids
            )
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            
            wait_time = backoff_base ** attempt
            logger.warning(
                f"Merge failed (attempt {attempt + 1}/{max_retries}). "
                f"Retrying in {wait_time}s..."
            )
            await asyncio.sleep(wait_time)
```

### 7. **Monitoring & Alerting**
- Log all merge operations
- Monitor validation failure rates
- Alert on duplicate profile creation spikes
- Track merge success/failure metrics

### 8. **Transaction Safety**
Ensure transaction safety for critical merge operations - use database transactions where possible.

### 9. **Data Quality Validation**
Validate profile data quality before merging to prevent garbage data propagation.

### 10. **Audit Trail**
```python
audit_log = {
    "operation": "profile_merge",
    "user_id": "admin-123",
    "primary_profile": "profile-123",
    "merged_profiles": ["profile-456", "profile-789"],
    "timestamp": datetime.now(),
    "reason": "CRM sync",
    "validation_passed": True
}
```

## Troubleshooting

### Problem: "Profile not found" error after merge

**Symptom**: Getting 404 or profile not found errors when tracking events after merge.

**Cause**: Using old (merged) profile ID instead of the merged profile ID.

**Solution**:
```python
# ❌ WRONG
merged_profile = await IdentityResolutionService.resolve_by_profile_ids(
    primary_profile_id="A",
    additional_profile_ids=["B"]
)
await track_event(profile_id="B")  # B doesn't exist anymore!

# ✅ CORRECT
merged_profile = await IdentityResolutionService.resolve_by_profile_ids(
    primary_profile_id="A",
    additional_profile_ids=["B"]
)
merged_id = merged_profile.id  # Use this!
await track_event(profile_id=merged_id)
```

**Prevention**: Always validate profile IDs:
```python
is_valid, actual_id, error = await IdentityResolutionService.validate_profile_id(profile_id)
if not is_valid:
    profile_id = actual_id  # Use corrected ID
```

### Problem: Internal merge still running

**Symptom**: Seeing duplicate merge operations in logs.

**Solution**: Ensure `options.externalIdentityResolution: true` flag is present in tracker payload.

```python
# Correct usage
await track_event(
    profile_id=merged_id,
    options={"externalIdentityResolution": True}  # Don't forget this!
)
```

### Problem: Circular merge detected

**Symptom**: Error about circular merge chain (A→B→C→A).

**Solution**: This is a critical data integrity issue. Use circular merge detection:

```python
# Before merging, check for circular references
has_circle, chain = await IdentityResolutionService.detect_circular_merge(profile_id)
if has_circle:
    raise ValueError(f"Circular merge detected: {' → '.join(chain)}")
```

## Advanced Topics

### Edge Cases & Production Hardening

For production deployments, review the comprehensive edge cases document:

**[IDENTITY_RESOLUTION_EDGE_CASES.md](./IDENTITY_RESOLUTION_EDGE_CASES.md)**

Critical scenarios covered:
1. **Circular Merge Chains** - Detect A→B→C→A loops
2. **Concurrent Merge Operations** - Distributed locking strategies
3. **Profile Resurrection** - Zombie profile prevention
4. **Partial Merge Failures** - Transaction rollback
5. **IDs Field Overflow** - Performance optimization
6. **Session Orphaning** - Session migration
7. **Event Race Conditions** - Grace period handling
8. **Double Merge Prevention** - Idempotency keys
9. **Cross-Tenant Security** - Tenant isolation
10. **Merge Key Collisions** - Multi-factor matching

### Production Deployment Checklist

Before deploying to production:

- [ ] Review all edge cases in IDENTITY_RESOLUTION_EDGE_CASES.md
- [ ] Implement circular merge detection
- [ ] Add distributed locking for concurrent operations (if needed)
- [ ] Set up monitoring and alerting
- [ ] Test rollback procedures
- [ ] Implement idempotency for all operations
- [ ] Configure grace periods for race conditions
- [ ] Set up profile IDs overflow monitoring
- [ ] Document incident response procedures
- [ ] Load test merge operations
- [ ] Test with production-like data volumes
- [ ] Verify backup and recovery procedures
- [ ] Train operations team on troubleshooting

### When to Use External vs Internal Resolution

**Use External Resolution When:**
- You need custom merge logic
- CRM or external system drives merging
- Batch processing requirements
- Complex validation rules
- Multi-system coordination
- Audit trail requirements
- Manual review processes

**Use Internal Resolution When:**
- Real-time merging is sufficient
- Standard merge rules work
- Simple email/phone matching
- No external dependencies
- Lower latency requirements
- Automatic workflows preferred

## Support

For questions:
- GitHub Issues: https://github.com/Tracardi/tracardi
- Documentation: https://docs.tracardi.com
- Community: https://tracardi.com/community
- Edge Cases: See IDENTITY_RESOLUTION_EDGE_CASES.md
