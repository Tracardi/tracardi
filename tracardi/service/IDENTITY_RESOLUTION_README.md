# Identity Resolution Service

This module provides identity resolution (profile merging) functionality for internal use within your applications.

**IMPORTANT**: This is an internal-only service. No public API endpoints are exposed. Use the service layer directly in your code.

## Files

### Core Service
- **`identity_resolution_service.py`**: Identity resolution service layer
  - `resolve_by_profile_ids()`: Merge by profile IDs
  - `resolve_by_merge_keys()`: Merge by key-value pairs
  - `find_duplicate_profiles()`: Find duplicates without merging
  - `resolve_by_field_value()`: Merge by single field value
  - `validate_profile_id()`: Validate profile ID and check if merged
  - `detect_circular_merge()`: Detect circular merge chains
  - `check_profile_resurrection()`: Check for zombie profiles

### Data Models
- **`tracardi/domain/identity_resolution_payload.py`**: Request/Response models
  - `IdentityResolutionByIdsRequest`
  - `IdentityResolutionByKeysRequest`
  - `IdentityResolutionByFieldRequest`
  - `FindDuplicatesRequest`
  - `IdentityResolutionResponse`
  - `FindDuplicatesResponse`
  - `ProfileSummary`

## Features

### External Identity Resolution Flag

The `externalIdentityResolution` flag has been added to tracker payload options. When this flag is `true`, Tracardi skips internal identity resolution.

**Implementation**: `tracardi/service/wf/workflow_manager_async.py`

```python
skip_internal_merge = self.tracker_payload.options.get('externalIdentityResolution', False)

if self.profile is not None and self.profile.needs_merging() and not skip_internal_merge:
    self.profile = await self.merge_profile(self.profile)
```

## Usage

### 1. Internal Service Usage

```python
from tracardi.service.identity_resolution_service import IdentityResolutionService

# Merge by email
merged_profile = await IdentityResolutionService.resolve_by_field_value(
    field_name="data.contact.email.main",
    field_value="user@example.com"
)

# Validate profile ID (checks if merged)
is_valid, actual_id, error = await IdentityResolutionService.validate_profile_id(
    profile_id="profile-456"
)

# Detect circular merges
has_circle, chain = await IdentityResolutionService.detect_circular_merge(
    profile_id="profile-123"
)

# Check for zombie profiles
is_resurrected, merged_into = await IdentityResolutionService.check_profile_resurrection(
    profile_id="profile-456"
)
```

### 2. Tracker Payload Flag Usage

```json
{
  "source": {"id": "source-123"},
  "profile": {"id": "profile-456"},
  "events": [...],
  "options": {
    "externalIdentityResolution": true
  }
}
```

### 3. Safe Merge with Validations

```python
# Merge with automatic safety checks
merged_profile = await IdentityResolutionService.resolve_by_profile_ids(
    primary_profile_id="profile-123",
    additional_profile_ids=["profile-456", "profile-789"],
    validate_circular=True,      # Detect circular merge chains
    validate_resurrection=True   # Detect zombie profiles
)
```

## Integration Patterns

### Pattern 1: Custom Application Integration

Build your own API with authentication and use the service internally:

```python
from fastapi import FastAPI, Depends
from tracardi.service.identity_resolution_service import IdentityResolutionService

app = FastAPI()

@app.post("/my-api/merge-profiles")
async def merge_profiles(
    primary_id: str,
    additional_ids: List[str],
    current_user = Depends(get_current_user)  # Your auth
):
    # Validate permissions
    if not current_user.has_permission("merge_profiles"):
        raise HTTPException(403, "Not authorized")
    
    # Use internal service
    result = await IdentityResolutionService.resolve_by_profile_ids(
        primary_id, additional_ids
    )
    
    return result
```

### Pattern 2: Background Job Integration

```python
# Celery/Huey task
@task
async def batch_merge_duplicates():
    emails = get_unique_emails()
    
    for email in emails:
        duplicates = await IdentityResolutionService.find_duplicate_profiles(
            merge_keys=[("data.contact.email.main", email)]
        )
        
        if len(duplicates) > 1:
            await IdentityResolutionService.resolve_by_profile_ids(
                primary_profile_id=duplicates[0].id,
                additional_profile_ids=[p.id for p in duplicates[1:]]
            )
```

### Pattern 3: CRM Webhook Integration

```python
# CRM webhook handler
@app.post("/webhooks/crm/contact-merged")
async def handle_crm_merge(webhook_data: dict):
    master_id = webhook_data["master_contact_id"]
    merged_ids = webhook_data["merged_contact_ids"]
    
    # Map CRM IDs to Tracardi profile IDs
    tracardi_master = get_tracardi_profile_id(master_id)
    tracardi_merged = [get_tracardi_profile_id(id) for id in merged_ids]
    
    # Perform merge in Tracardi
    await IdentityResolutionService.resolve_by_profile_ids(
        tracardi_master, tracardi_merged
    )
```

## Documentation

For detailed usage guide, see `EXTERNAL_IDENTITY_RESOLUTION.md` in the root directory.

For production edge cases and safety considerations, see `IDENTITY_RESOLUTION_EDGE_CASES.md`.

## Benefits

1. **Performance**: Prevent unnecessary internal merging for better performance
2. **Control**: Full control over identity resolution logic
3. **Integration**: Integrate with external systems (CRM, etc.)
4. **Batch Processing**: Support for scheduled batch merge operations
5. **Preview**: Find duplicates before merging
6. **Safety**: Built-in circular merge detection and validation
7. **Security**: Keep merge operations internal to your application

## Security Considerations

Since this is an internal service:

1. **Never expose directly** - Always wrap in your own authenticated API
2. **Validate permissions** - Check user permissions before merge operations
3. **Audit logging** - Log all merge operations with user/system information
4. **Tenant isolation** - Ensure profiles belong to correct tenant
5. **Rate limiting** - Implement rate limits in your wrapper API
6. **Input validation** - Validate all inputs before calling service methods

## Next Steps

1. Review `EXTERNAL_IDENTITY_RESOLUTION.md` for comprehensive documentation
2. Review `IDENTITY_RESOLUTION_EDGE_CASES.md` for production considerations
3. Implement your own authenticated API wrapper if needed
4. Set up monitoring and alerting for merge operations
5. Test thoroughly in staging environment
