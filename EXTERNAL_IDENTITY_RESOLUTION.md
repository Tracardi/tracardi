# External Identity Resolution API

This document explains how to use Tracardi's identity resolution (profile merging) feature through external API.

## Overview

Tracardi automatically performs identity resolution (profile merging) when it detects profile changes. However, in some cases, you may want to control this process through an external system. This feature provides:

1. **External Control**: Perform identity resolution from your own systems via API
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
merge_response = merge_profiles(primary="profile-123", additional=["profile-456"])
# profile-456 is now merged and deleted

track_event(profile_id="profile-456")  # ❌ ERROR: Profile not found!
# Result: Creates duplicate profile or sends event to wrong profile
```

```python
# ✅ CORRECT - Using merged profile ID
merge_response = merge_profiles(primary="profile-123", additional=["profile-456"])
merged_id = merge_response["merged_profile_id"]  # "profile-123"

track_event(profile_id=merged_id)  # ✅ OK: Uses correct merged profile
```

### Profile Validation Endpoint

Always validate profile IDs before tracking, especially after merge operations:

```bash
GET /identity-resolution/validate-profile?profile_id=profile-456
```

**Response (profile is valid):**
```json
{
  "is_valid": true,
  "profile_id": "profile-456",
  "message": "Profile is valid and active"
}
```

**Response (profile was merged):**
```json
{
  "is_valid": false,
  "profile_id": "profile-123",
  "error": "Profile profile-456 was merged into profile-123",
  "message": "Use profile-123 in tracker payloads"
}
```

## API Endpoints

### 1. Merge by Profile IDs

To merge specific profile IDs:

```bash
POST /identity-resolution/merge-by-ids
Content-Type: application/json

{
  "primary_profile_id": "profile-123",
  "additional_profile_ids": ["profile-456", "profile-789"]
}
```

**Response:**
```json
{
  "success": true,
  "merged_profile_id": "profile-123",
  "merged_profile_ids": ["profile-123", "profile-456", "profile-789"],
  "message": "Successfully merged 3 profiles",
  "profile": {
    "id": "profile-123",
    "ids": ["profile-123", "profile-456", "profile-789"],
    "traits": {...},
    "segments": ["segment-1", "segment-2"]
  }
}
```

### 2. Merge by Keys

To merge profiles by email, phone, or custom field:

```bash
POST /identity-resolution/merge-by-keys
Content-Type: application/json

{
  "profile_id": "profile-123",
  "merge_keys": [
    ["data.contact.email.main", "user@example.com"]
  ]
}
```

**Multiple keys example:**
```json
{
  "profile_id": "profile-123",
  "merge_keys": [
    ["data.contact.email.main", "user@example.com"],
    ["data.contact.phone.main", "+1234567890"]
  ]
}
```

### 3. Merge by Single Field (Convenience Endpoint)

```bash
POST /identity-resolution/merge-by-field
Content-Type: application/json

{
  "field_name": "data.contact.email.main",
  "field_value": "user@example.com",
  "primary_profile_id": "profile-123"  // Optional
}
```

If `primary_profile_id` is not specified, the newest profile will be used as primary.

### 4. Find Duplicates (Without Merging)

To preview duplicate profiles before merging:

```bash
POST /identity-resolution/find-duplicates
Content-Type: application/json

{
  "merge_keys": [
    ["data.contact.email.main", "user@example.com"]
  ],
  "limit": 100
}
```

**Response:**
```json
{
  "success": true,
  "count": 3,
  "profiles": [
    {
      "id": "profile-123",
      "ids": ["profile-123"],
      "traits": {...},
      "created": "2024-01-15T10:30:00Z",
      "updated": "2024-01-20T15:45:00Z"
    },
    {
      "id": "profile-456",
      "ids": ["profile-456"],
      "traits": {...},
      "created": "2024-01-10T08:20:00Z",
      "updated": "2024-01-18T12:30:00Z"
    }
  ],
  "message": "Found 3 duplicate profiles"
}
```

## Use Cases

### Use Case 1: Real-Time User Registration/Login (with Validation)

When a user registers or logs in, perform immediate identity resolution to merge anonymous browsing data with authenticated profile.

```python
import requests

def handle_user_login(email, anonymous_profile_id):
    """
    Merge anonymous profile with authenticated profile on login.
    INCLUDES PROFILE VALIDATION to prevent bugs.
    """
    # 1. VALIDATE anonymous profile ID first
    validation = requests.get(
        f"http://tracardi-api/identity-resolution/validate-profile",
        params={"profile_id": anonymous_profile_id}
    ).json()
    
    if not validation["is_valid"]:
        # Profile was merged or doesn't exist - use the actual ID
        anonymous_profile_id = validation["profile_id"]
        print(f"Warning: Profile ID updated to {anonymous_profile_id}")
    
    # 2. Find duplicates by email
    duplicates_response = requests.post(
        "http://tracardi-api/identity-resolution/find-duplicates",
        json={
            "merge_keys": [
                ["data.contact.email.main", email]
            ]
        }
    )
    
    duplicates = duplicates_response.json()
    
    # 3. If user has existing profile, merge with anonymous
    if duplicates["count"] > 0:
        authenticated_profile_id = duplicates["profiles"][0]["id"]
        
        merge_response = requests.post(
            "http://tracardi-api/identity-resolution/merge-by-ids",
            json={
                "primary_profile_id": authenticated_profile_id,
                "additional_profile_ids": [anonymous_profile_id]
            }
        )
        
        if not merge_response.json()["success"]:
            raise Exception(f"Merge failed: {merge_response.json()['message']}")
        
        merged_profile_id = merge_response.json()["merged_profile_id"]
    else:
        # New user, use anonymous profile as base
        merged_profile_id = anonymous_profile_id
    
    # 4. VALIDATE merged profile before tracking
    final_validation = requests.get(
        f"http://tracardi-api/identity-resolution/validate-profile",
        params={"profile_id": merged_profile_id}
    ).json()
    
    if not final_validation["is_valid"]:
        raise Exception(f"Merged profile validation failed: {final_validation['error']}")
    
    # 5. Send login event with VALIDATED merged profile
    track_response = requests.post(
        "http://tracardi-api/track",
        json={
            "source": {"id": "website"},
            "profile": {"id": merged_profile_id},
            "events": [{
                "type": "user-login",
                "properties": {"email": email}
            }],
            "options": {
                "externalIdentityResolution": True  # Skip internal merge
            }
        }
    )
    
    return merged_profile_id
```

### Use Case 2: Multi-Device User Tracking

Consolidate user profiles across different devices when they use the same credentials.

```python
def consolidate_cross_device_profiles(user_id, device_profile_ids):
    """
    Merge profiles from multiple devices for single user.
    
    Args:
        user_id: Unique user identifier
        device_profile_ids: List of profile IDs from different devices
    """
    # Find primary profile by user_id
    primary_profile_response = requests.post(
        "http://tracardi-api/identity-resolution/find-duplicates",
        json={
            "merge_keys": [
                ["data.identifiers.user_id", user_id]
            ],
            "limit": 1
        }
    )
    
    primary_profile = primary_profile_response.json()["profiles"][0]
    
    # Merge all device profiles into primary
    merge_response = requests.post(
        "http://tracardi-api/identity-resolution/merge-by-ids",
        json={
            "primary_profile_id": primary_profile["id"],
            "additional_profile_ids": device_profile_ids
        }
    )
    
    return merge_response.json()["merged_profile_id"]
```

### Use Case 3: Social Login Consolidation

Merge profiles when users authenticate via different social providers (Google, Facebook, etc.).

```python
def handle_social_login(provider, social_email, profile_id):
    """
    Consolidate profiles from different social login providers.
    """
    # 1. Check if email exists in any profile
    duplicates = requests.post(
        "http://tracardi-api/identity-resolution/find-duplicates",
        json={
            "merge_keys": [
                ["data.contact.email.main", social_email]
            ]
        }
    ).json()
    
    # 2. If exists, merge with current profile
    if duplicates["count"] > 1:
        # Find the main profile (oldest or with most data)
        profiles = sorted(
            duplicates["profiles"], 
            key=lambda x: x["created"]
        )
        main_profile_id = profiles[0]["id"]
        other_profile_ids = [p["id"] for p in profiles[1:]]
        
        merge_response = requests.post(
            "http://tracardi-api/identity-resolution/merge-by-ids",
            json={
                "primary_profile_id": main_profile_id,
                "additional_profile_ids": other_profile_ids
            }
        )
        
        merged_id = merge_response.json()["merged_profile_id"]
    else:
        merged_id = profile_id
    
    # 3. Track social login event
    requests.post(
        "http://tracardi-api/track",
        json={
            "source": {"id": "social-login"},
            "profile": {"id": merged_id},
            "events": [{
                "type": "social-login",
                "properties": {
                    "provider": provider,
                    "email": social_email
                }
            }],
            "options": {"externalIdentityResolution": True}
        }
    )
    
    return merged_id
```

### Use Case 4: B2B Account Consolidation

Merge multiple employee profiles under a single company account.

```python
def consolidate_company_employees(company_domain, employee_emails):
    """
    Consolidate all employee profiles for a company.
    """
    company_profiles = []
    
    # Find all profiles with company email domain
    for email in employee_emails:
        response = requests.post(
            "http://tracardi-api/identity-resolution/find-duplicates",
            json={
                "merge_keys": [
                    ["data.contact.email.main", email]
                ]
            }
        )
        
        profiles = response.json()["profiles"]
        if profiles:
            company_profiles.extend(profiles)
    
    # Merge all under company account
    if company_profiles:
        primary = company_profiles[0]["id"]
        others = [p["id"] for p in company_profiles[1:]]
        
        if others:
            requests.post(
                "http://tracardi-api/identity-resolution/merge-by-ids",
                json={
                    "primary_profile_id": primary,
                    "additional_profile_ids": others
                }
            )
    
    return primary
```

### Use Case 5: Email Change Handling

Handle email address changes while maintaining profile history.

```python
def handle_email_change(old_email, new_email, current_profile_id):
    """
    Merge profiles when user changes email address.
    """
    # 1. Find profiles with new email
    new_email_profiles = requests.post(
        "http://tracardi-api/identity-resolution/find-duplicates",
        json={
            "merge_keys": [
                ["data.contact.email.main", new_email]
            ]
        }
    ).json()
    
    # 2. Find profiles with old email
    old_email_profiles = requests.post(
        "http://tracardi-api/identity-resolution/find-duplicates",
        json={
            "merge_keys": [
                ["data.contact.email.main", old_email]
            ]
        }
    ).json()
    
    # 3. Merge all profiles
    all_profile_ids = set()
    all_profile_ids.add(current_profile_id)
    
    for profile in new_email_profiles["profiles"]:
        all_profile_ids.add(profile["id"])
    
    for profile in old_email_profiles["profiles"]:
        all_profile_ids.add(profile["id"])
    
    profile_ids = list(all_profile_ids)
    
    if len(profile_ids) > 1:
        merge_response = requests.post(
            "http://tracardi-api/identity-resolution/merge-by-ids",
            json={
                "primary_profile_id": current_profile_id,
                "additional_profile_ids": [
                    pid for pid in profile_ids if pid != current_profile_id
                ]
            }
        )
        
        return merge_response.json()["merged_profile_id"]
    
    return current_profile_id
```

### Use Case 6: Batch Duplicate Cleanup

Perform scheduled batch processing to clean up duplicate profiles.

```python
import asyncio
from datetime import datetime

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
            response = requests.post(
                "http://tracardi-api/identity-resolution/find-duplicates",
                json={
                    "merge_keys": [
                        ["data.contact.email.main", email]
                    ]
                }
            )
            
            duplicates = response.json()
            
            # Only merge if there are actual duplicates
            if duplicates["count"] > 1:
                merge_response = requests.post(
                    "http://tracardi-api/identity-resolution/merge-by-field",
                    json={
                        "field_name": "data.contact.email.main",
                        "field_value": email
                    }
                )
                
                if merge_response.json()["success"]:
                    merge_stats["merged"] += 1
                    print(f"Merged {duplicates['count']} profiles for {email}")
            
            merge_stats["processed"] += 1
            
        except Exception as e:
            merge_stats["errors"].append(f"{email}: {str(e)}")
            print(f"Error merging profiles for {email}: {str(e)}")
    
    # Log results
    print(f"Batch cleanup completed at {datetime.now()}")
    print(f"Processed: {merge_stats['processed']}")
    print(f"Merged: {merge_stats['merged']}")
    print(f"Errors: {len(merge_stats['errors'])}")
    
    return merge_stats
```

### Use Case 7: CRM Integration

Sync profile merges from external CRM system.

```python
def sync_crm_profile_merge(crm_master_id, crm_duplicate_ids):
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
    response = requests.post(
        "http://tracardi-api/identity-resolution/merge-by-ids",
        json={
            "primary_profile_id": master_profile["id"],
            "additional_profile_ids": [p["id"] for p in duplicate_profiles]
        }
    )
    
    # Update CRM with merged Tracardi ID
    if response.json()["success"]:
        merged_id = response.json()["merged_profile_id"]
        update_crm_record(crm_master_id, {"tracardi_profile_id": merged_id})
    
    return response.json()
```

### Use Case 8: Customer Support Ticket Consolidation

Merge profiles when customer support identifies the same user.

```python
def merge_support_tickets(support_agent_id, ticket_profile_ids, reason):
    """
    Support agent manually merges profiles after verifying same customer.
    """
    # 1. Preview profiles before merge
    profiles = []
    for profile_id in ticket_profile_ids:
        profile = requests.get(
            f"http://tracardi-api/profile/{profile_id}"
        ).json()
        profiles.append(profile)
    
    # 2. Log merge decision
    log_support_action({
        "agent_id": support_agent_id,
        "action": "profile_merge",
        "profiles": ticket_profile_ids,
        "reason": reason,
        "timestamp": datetime.now().isoformat()
    })
    
    # 3. Perform merge
    merge_response = requests.post(
        "http://tracardi-api/identity-resolution/merge-by-ids",
        json={
            "primary_profile_id": ticket_profile_ids[0],
            "additional_profile_ids": ticket_profile_ids[1:]
        }
    )
    
    # 4. Update all tickets with merged profile ID
    if merge_response.json()["success"]:
        merged_id = merge_response.json()["merged_profile_id"]
        update_support_tickets(ticket_profile_ids, merged_id)
    
    return merge_response.json()
```

### Use Case 9: E-commerce Cart Recovery

Merge guest checkout with registered user profile for cart recovery.

```python
def merge_guest_checkout(guest_email, guest_profile_id, cart_items):
    """
    When guest checks out, merge with existing customer profile.
    """
    # 1. Check if email exists
    existing_customer = requests.post(
        "http://tracardi-api/identity-resolution/find-duplicates",
        json={
            "merge_keys": [
                ["data.contact.email.main", guest_email]
            ]
        }
    ).json()
    
    if existing_customer["count"] > 0:
        # Existing customer
        customer_profile_id = existing_customer["profiles"][0]["id"]
        
        # Merge guest profile into customer profile
        merge_response = requests.post(
            "http://tracardi-api/identity-resolution/merge-by-ids",
            json={
                "primary_profile_id": customer_profile_id,
                "additional_profile_ids": [guest_profile_id]
            }
        )
        
        profile_id = merge_response.json()["merged_profile_id"]
    else:
        # New customer
        profile_id = guest_profile_id
    
    # Track purchase with merged profile
    requests.post(
        "http://tracardi-api/track",
        json={
            "source": {"id": "e-commerce"},
            "profile": {"id": profile_id},
            "events": [{
                "type": "purchase",
                "properties": {
                    "email": guest_email,
                    "items": cart_items,
                    "guest_checkout": True
                }
            }],
            "options": {"externalIdentityResolution": True}
        }
    )
    
    return profile_id
```

### Use Case 10: GDPR Data Consolidation

Consolidate all user data for GDPR data portability requests.

```python
def consolidate_for_gdpr_request(user_email, additional_identifiers=None):
    """
    Find and merge all profiles for GDPR data export request.
    """
    all_profiles = []
    
    # Search by email
    email_profiles = requests.post(
        "http://tracardi-api/identity-resolution/find-duplicates",
        json={
            "merge_keys": [
                ["data.contact.email.main", user_email]
            ],
            "limit": 1000
        }
    ).json()
    
    all_profiles.extend(email_profiles["profiles"])
    
    # Search by additional identifiers (phone, user_id, etc.)
    if additional_identifiers:
        for field, value in additional_identifiers.items():
            response = requests.post(
                "http://tracardi-api/identity-resolution/find-duplicates",
                json={
                    "merge_keys": [[field, value]],
                    "limit": 1000
                }
            ).json()
            all_profiles.extend(response["profiles"])
    
    # Remove duplicates
    unique_profiles = {p["id"]: p for p in all_profiles}
    profile_ids = list(unique_profiles.keys())
    
    # Merge all profiles
    if len(profile_ids) > 1:
        merge_response = requests.post(
            "http://tracardi-api/identity-resolution/merge-by-ids",
            json={
                "primary_profile_id": profile_ids[0],
                "additional_profile_ids": profile_ids[1:]
            }
        )
        
        consolidated_profile_id = merge_response.json()["merged_profile_id"]
    else:
        consolidated_profile_id = profile_ids[0] if profile_ids else None
    
    # Export all data for GDPR request
    if consolidated_profile_id:
        full_profile = requests.get(
            f"http://tracardi-api/profile/{consolidated_profile_id}/export"
        ).json()
        
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

### Data Models

Request/response models are defined in `tracardi/domain/identity_resolution_payload.py`.

## Best Practices

### 1. **CRITICAL: Always Validate Profile IDs After Merge**
```python
# After any merge operation
merge_response = merge_profiles(...)
merged_id = merge_response["merged_profile_id"]

# VALIDATE before using
validation = validate_profile(merged_id)
if not validation["is_valid"]:
    raise Exception(f"Invalid profile ID: {validation['error']}")

# NOW safe to use
track_event(profile_id=merged_id)
```

**Why**: Merged profile IDs become invalid. Using old IDs causes:
- Profile not found errors
- Duplicate profile creation
- Events going to wrong profiles
- Data inconsistency

### 2. **Always Use the Flag After External Merge**
```python
# After external merging, always use this flag
track_event(
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
def safe_track_event(profile_id, events):
    # Always validate first
    validation = validate_profile(profile_id)
    if not validation["is_valid"]:
        profile_id = validation["profile_id"]  # Use corrected ID
    
    return track_event(profile_id, events)
```

### 5. **Duplicate Check Before Merge**
Check with `find-duplicates` endpoint before merging to preview results.

### 6. **Error Handling & Retry Logic**
```python
def merge_with_retry(primary_id, additional_ids, max_retries=3):
    for attempt in range(max_retries):
        try:
            return merge_profiles(primary_id, additional_ids)
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            time.sleep(2 ** attempt)  # Exponential backoff
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

### 11. **Rate Limiting for Batch Operations**
Implement rate limiting to prevent system overload during batch processing.

### 12. **Testing in Staging**
Test merge logic thoroughly in staging before production deployment.

### 13. **Rollback Strategy**
Have a plan for incorrect merges (though profile merges are generally not reversible).

## Migration Guide

### Migrating from Internal to External API

1. **Deploy API Endpoints**
   - Add endpoints to TracardAPI project
   - Deploy and test

2. **Implement External Merge Logic**
   - Write your merge logic
   - Use identity resolution service

3. **Update Tracker Payloads**
   - Add `options.externalIdentityResolution: true`
   - Test thoroughly

4. **Monitor**
   - Verify internal merges are being skipped
   - Track performance metrics

## Troubleshooting

### Problem: "Profile not found" error after merge

**Symptom**: Getting 404 or profile not found errors when tracking events after merge.

**Cause**: Using old (merged) profile ID instead of the merged profile ID.

**Solution**:
```python
# ❌ WRONG
merge_response = merge_profiles(primary="A", additional=["B"])
track_event(profile_id="B")  # B doesn't exist anymore!

# ✅ CORRECT
merge_response = merge_profiles(primary="A", additional=["B"])
merged_id = merge_response["merged_profile_id"]  # Use this!
track_event(profile_id=merged_id)
```

**Prevention**: Always validate profile IDs:
```python
validation = validate_profile(profile_id)
if not validation["is_valid"]:
    profile_id = validation["profile_id"]  # Use corrected ID
```

### Problem: Duplicate profiles being created after external merge

**Symptom**: Multiple profiles with same email/phone after using external merge.

**Cause**: Using invalid profile ID in tracker payload causes Tracardi to create new profile.

**Solution**:
1. Validate profile ID before every track call:
```python
validation = validate_profile(profile_id)
if not validation["is_valid"]:
    profile_id = validation.get("profile_id") or create_new_profile()
```

2. Check merge actually succeeded:
```python
merge_response = merge_profiles(...)
if not merge_response["success"]:
    raise Exception("Merge failed!")
```

### Problem: Internal merge still running

**Symptom**: Seeing duplicate merge operations in logs.

**Solution**: Ensure `options.externalIdentityResolution: true` flag is present in tracker payload.

```python
# Correct usage
track_event(
    profile_id=merged_id,
    options={"externalIdentityResolution": True}  # Don't forget this!
)
```

### Problem: Events going to wrong profile after merge

**Symptom**: Events appearing on incorrect profile after merge operation.

**Root Causes**:
1. Using old profile ID
2. Not validating merged profile ID
3. Race condition between merge and track

**Solution**:
```python
# 1. Perform merge
merge_response = merge_profiles(...)
merged_id = merge_response["merged_profile_id"]

# 2. WAIT and validate (important for eventual consistency)
import time
time.sleep(0.5)  # Wait for DB sync

validation = validate_profile(merged_id)
if not validation["is_valid"]:
    raise Exception(f"Merged profile invalid: {validation['error']}")

# 3. Now safe to track
track_event(profile_id=merged_id, options={"externalIdentityResolution": True})
```

### Problem: Duplicates not found

**Symptom**: `find-duplicates` returns 0 results when duplicates should exist.

**Solution**: 
- Verify merge keys are correct
- `.keyword` suffix is automatically added for trait fields, no need to add manually
- Check field paths are correct: use `data.contact.email.main` not `traits.email`
- Ensure profiles exist in the database
- Check case sensitivity (email matching is case-sensitive)

### Problem: Merge operation too slow

**Symptom**: Merge taking >5 seconds, timeouts occurring.

**Solution**:
- Reduce the number of profiles being merged at once (max 10-20 at a time)
- Use batch processing for large-scale merges
- Optimize database indexes on merge key fields
- Consider async processing for non-critical merges
- Check database performance and connection pool

### Problem: Profile data lost after merge

**Symptom**: Some profile traits or data missing after merge.

**Solution**:
- Check merge strategy configuration in `ProfileMerger`
- Verify data models are compatible
- Review merge conflict resolution logic
- Enable detailed logging for merge operations:
```python
import logging
logging.getLogger('tracardi.service.profile_merger').setLevel(logging.DEBUG)
```

### Problem: Validation endpoint returns wrong profile ID

**Symptom**: Validation returning unexpected profile ID.

**Possible Causes**:
1. Profile was merged multiple times (chain merge)
2. Profile IDs field not properly maintained

**Solution**:
```python
# Always use the validation endpoint result
validation = validate_profile(original_id)
actual_id = validation.get("profile_id")

if actual_id != original_id:
    logger.warning(f"Profile {original_id} redirects to {actual_id}")
    # Update your local profile ID mapping
    update_profile_id_mapping(original_id, actual_id)
```

### Problem: Race conditions during concurrent merges

**Symptom**: Multiple merge operations on same profiles causing conflicts.

**Solution**:
- Implement distributed locking for merge operations
- Use profile ID as lock key
- Add retry logic with exponential backoff
```python
import redis
from contextlib import contextmanager

@contextmanager
def profile_merge_lock(profile_id, timeout=10):
    lock = redis_client.lock(f"merge:{profile_id}", timeout=timeout)
    acquired = lock.acquire(blocking=True, blocking_timeout=timeout)
    try:
        yield acquired
    finally:
        if acquired:
            lock.release()

# Usage
with profile_merge_lock(profile_id):
    merge_profiles(...)
```

## Performance Considerations

1. **Batch Operations**: Process large numbers of merges in batches during off-peak hours
2. **Caching**: Cache duplicate lookup results when appropriate
3. **Async Processing**: Use async processing for non-time-critical merges
4. **Database Optimization**: Ensure proper indexes on merge key fields
5. **Rate Limiting**: Implement rate limiting to prevent system overload

## Security Considerations

1. **Authentication**: Secure API endpoints with proper authentication
2. **Authorization**: Implement role-based access control for merge operations
3. **Audit Logging**: Log all merge operations with user/system information
4. **Data Validation**: Validate all input data before processing
5. **GDPR Compliance**: Ensure merge operations comply with data protection regulations

## Support

For questions:
- GitHub Issues: https://github.com/Tracardi/tracardi
- Documentation: https://docs.tracardi.com
- Community: https://tracardi.com/community
