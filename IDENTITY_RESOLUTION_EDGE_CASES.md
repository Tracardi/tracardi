# Identity Resolution: Critical Edge Cases & Solutions

This document covers advanced edge cases, race conditions, and failure scenarios for external identity resolution.

## Table of Contents
1. [Circular Merge Chains](#circular-merge-chains)
2. [Concurrent Merge Operations](#concurrent-merge-operations)
3. [Profile Resurrection](#profile-resurrection)
4. [Partial Merge Failures](#partial-merge-failures)
5. [IDs Field Overflow](#ids-field-overflow)
6. [Session Orphaning](#session-orphaning)
7. [Event Race Conditions](#event-race-conditions)
8. [Double Merge Prevention](#double-merge-prevention)
9. [Cross-Tenant Security](#cross-tenant-security)
10. [Merge Key Collisions](#merge-key-collisions)
11. [Validation Cache Staleness](#validation-cache-staleness)
12. [Profile Data Corruption](#profile-data-corruption)
13. [Eventual Consistency](#eventual-consistency)
14. [Memory & Performance](#memory--performance)
15. [APM Hash Integrity](#apm-hash-integrity)

---

## 1. Circular Merge Chains

### Problem
```
Profile A merges into B
Profile B merges into C
Profile C merges into A (circular!)
```

**Result**: Validation fails, infinite loops, data loss.

### Detection
```python
async def detect_circular_merge(profile_id: str, max_depth: int = 10) -> Tuple[bool, List[str]]:
    """
    Detect circular merge chains before they cause issues.
    
    Returns: (has_circle, chain_path)
    """
    visited = set()
    chain = []
    current_id = profile_id
    
    for _ in range(max_depth):
        if current_id in visited:
            # Circular reference detected!
            return True, chain
        
        visited.add(current_id)
        chain.append(current_id)
        
        # Check if current ID was merged into another
        is_valid, next_id, _ = await validate_profile_id(current_id)
        
        if is_valid or next_id is None:
            # End of chain
            return False, chain
        
        current_id = next_id
    
    # Max depth exceeded - assume circular
    return True, chain
```

### Prevention
```python
async def safe_merge_with_circle_detection(primary_id, additional_ids):
    """
    Merge with circular reference protection.
    """
    # 1. Check all profiles for circular references
    all_ids = [primary_id] + additional_ids
    
    for profile_id in all_ids:
        has_circle, chain = await detect_circular_merge(profile_id)
        if has_circle:
            raise ValueError(
                f"Circular merge detected: {' -> '.join(chain)}. "
                f"Cannot proceed with merge."
            )
    
    # 2. Safe to merge
    return await merge_profiles(primary_id, additional_ids)
```

---

## 2. Concurrent Merge Operations

### Problem
```
Time    System A                    System B
0ms     Load profile-456            Load profile-456  
10ms    Merge 456→123              Merge 456→789
20ms    Save merged-123             Save merged-789
```

**Result**: Data inconsistency, duplicate merges, event split.

### Solution: Distributed Locking
```python
from tracardi.service.tracking.locking import Lock, async_mutex
from tracardi.service.storage.redis.driver.redis_client import RedisClient

async def merge_with_lock(primary_id, additional_ids, timeout=30):
    """
    Merge with distributed lock to prevent concurrent modifications.
    """
    redis = RedisClient()
    
    # Create locks for all profiles involved
    all_ids = sorted([primary_id] + additional_ids)  # Sort for deadlock prevention
    locks = []
    
    try:
        # Acquire locks in sorted order (prevents deadlock)
        for profile_id in all_ids:
            lock_key = f"profile:merge:{profile_id}"
            lock = Lock(redis, lock_key, default_lock_ttl=timeout)
            
            # Use async mutex
            async with async_mutex(lock, f"merge-{profile_id}", 
                                  break_after_time=timeout):
                locks.append(lock)
        
        # All locks acquired - safe to merge
        logger.info(f"Acquired locks for {len(all_ids)} profiles")
        
        # Perform merge
        result = await merge_profiles(primary_id, additional_ids)
        
        return result
        
    except BlockingIOError as e:
        # Lock acquisition failed
        logger.error(f"Could not acquire lock for merge: {e}")
        raise ValueError(
            f"Merge operation is already in progress for one of these profiles. "
            f"Please wait and retry."
        )
    finally:
        # Locks auto-release via context manager
        pass
```

### Lock Timeout Handling
```python
class MergeLockTimeout(Exception):
    """Raised when merge lock cannot be acquired within timeout."""
    pass

async def merge_with_retry(primary_id, additional_ids, 
                           max_retries=3, backoff_base=2):
    """
    Retry merge with exponential backoff if locks are unavailable.
    """
    for attempt in range(max_retries):
        try:
            return await merge_with_lock(primary_id, additional_ids)
        except (BlockingIOError, MergeLockTimeout) as e:
            if attempt == max_retries - 1:
                raise
            
            wait_time = backoff_base ** attempt
            logger.warning(
                f"Merge lock unavailable (attempt {attempt + 1}/{max_retries}). "
                f"Retrying in {wait_time}s..."
            )
            await asyncio.sleep(wait_time)
```

---

## 3. Profile Resurrection

### Problem
```
1. Profile-456 merges into Profile-123
2. System mistakenly creates new Profile-456
3. Now we have duplicate: original merged + new resurrected
```

**Result**: Zombie profiles, data inconsistency.

### Detection
```python
async def check_profile_resurrection(profile_id: str) -> Tuple[bool, Optional[str]]:
    """
    Check if profile ID was previously used and merged.
    
    Returns: (is_resurrected, merged_into_id)
    """
    # Check if this ID exists in any profile's IDs list
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
            return True, existing_profile.id
    
    return False, None
```

### Prevention
```python
async def safe_profile_creation(profile_id: str, profile_data: dict):
    """
    Create profile with resurrection check.
    """
    # Check for resurrection
    is_resurrected, merged_into = await check_profile_resurrection(profile_id)
    
    if is_resurrected:
        logger.error(
            f"Profile resurrection detected! {profile_id} was previously "
            f"merged into {merged_into}. Redirecting to merged profile."
        )
        
        # Option 1: Use merged profile instead
        return merged_into
        
        # Option 2: Create with different ID
        # new_id = f"{profile_id}-{uuid4().hex[:8]}"
        # return await create_profile(new_id, profile_data)
    
    # Safe to create
    return await create_profile(profile_id, profile_data)
```

---

## 4. Partial Merge Failures

### Problem
```
Merge Operation Steps:
1. ✅ Copy profile data
2. ✅ Move events (50% done...)
3. ❌ DATABASE ERROR
4. ❌ Move sessions (NOT DONE)
5. ❌ Delete old profiles (NOT DONE)
```

**Result**: Half-merged profiles, orphaned data, inconsistent state.

### Solution: Transactional Merge
```python
class MergeTransaction:
    """
    Pseudo-transactional merge with rollback capability.
    """
    
    def __init__(self, primary_id, additional_ids):
        self.primary_id = primary_id
        self.additional_ids = additional_ids
        self.rollback_data = {}
        self.completed_steps = []
    
    async def execute(self):
        """
        Execute merge with step tracking for rollback.
        """
        try:
            # Step 1: Backup current state
            await self.backup_profiles()
            self.completed_steps.append('backup')
            
            # Step 2: Merge profile data
            merged_profile = await self.merge_profile_data()
            self.completed_steps.append('merge_data')
            
            # Step 3: Move events (with checkpoint)
            await self.move_events_with_checkpoint()
            self.completed_steps.append('move_events')
            
            # Step 4: Move sessions (with checkpoint)
            await self.move_sessions_with_checkpoint()
            self.completed_steps.append('move_sessions')
            
            # Step 5: Update profile IDs list
            await self.update_profile_ids()
            self.completed_steps.append('update_ids')
            
            # Step 6: Mark old profiles as merged
            await self.mark_old_profiles_merged()
            self.completed_steps.append('mark_merged')
            
            # Step 7: Commit - point of no return
            await self.commit_merge()
            self.completed_steps.append('committed')
            
            return merged_profile
            
        except Exception as e:
            logger.error(f"Merge failed at step: {self.completed_steps[-1] if self.completed_steps else 'start'}")
            await self.rollback()
            raise
    
    async def rollback(self):
        """
        Rollback partial merge.
        """
        logger.warning(f"Rolling back merge. Completed steps: {self.completed_steps}")
        
        # Rollback in reverse order
        for step in reversed(self.completed_steps):
            try:
                if step == 'move_events':
                    await self.rollback_events()
                elif step == 'move_sessions':
                    await self.rollback_sessions()
                elif step == 'update_ids':
                    await self.rollback_ids()
                # ... etc
            except Exception as e:
                logger.error(f"Rollback failed for step {step}: {e}")
    
    async def move_events_with_checkpoint(self):
        """
        Move events in batches with checkpoints.
        """
        batch_size = 1000
        for old_profile_id in self.additional_ids:
            offset = 0
            
            while True:
                # Move batch
                events = await load_events_batch(old_profile_id, offset, batch_size)
                if not events:
                    break
                
                await update_events_profile_id(events, self.primary_id)
                
                # Checkpoint
                await self.save_checkpoint(
                    'move_events',
                    {'profile_id': old_profile_id, 'offset': offset}
                )
                
                offset += batch_size
```

### Partial Failure Recovery
```python
async def recover_partial_merge(transaction_id: str):
    """
    Recover from partial merge failure.
    """
    # Load transaction state
    state = await load_merge_transaction_state(transaction_id)
    
    if state['status'] == 'partial':
        logger.info(f"Recovering partial merge: {transaction_id}")
        
        # Resume from last checkpoint
        last_step = state['last_completed_step']
        
        if last_step == 'move_events':
            # Resume from events
            await resume_move_events(state)
        elif last_step == 'move_sessions':
            # Continue with sessions
            await resume_move_sessions(state)
        # ... etc
```

---

## 5. IDs Field Overflow

### Problem
```
Profile merged 1000 times
profile.ids = [id1, id2, id3, ..., id1000]  # 50KB+ array!
```

**Result**: Database performance issues, memory problems, slow queries.

### Detection
```python
def check_ids_overflow(profile: Profile, max_ids: int = 1000) -> bool:
    """
    Check if profile.ids is becoming too large.
    """
    if len(profile.ids) > max_ids:
        logger.warning(
            f"Profile {profile.id} has {len(profile.ids)} IDs (max: {max_ids}). "
            f"Consider ID compaction."
        )
        return True
    return False
```

### Solution: ID Compaction
```python
async def compact_profile_ids(profile_id: str, keep_recent: int = 100):
    """
    Compact profile IDs to prevent overflow.
    
    Strategy:
    1. Keep most recent N IDs in profile.ids
    2. Move older IDs to separate archive table
    3. Maintain reverse lookup capability
    """
    profile = await profile_db.load(profile_id)
    
    if len(profile.ids) <= keep_recent:
        return  # No compaction needed
    
    # Sort IDs by age (assuming timestamp-based IDs or metadata)
    sorted_ids = await sort_ids_by_age(profile.ids)
    
    # Keep recent IDs
    recent_ids = sorted_ids[-keep_recent:]
    archived_ids = sorted_ids[:-keep_recent]
    
    # Archive old IDs to separate table
    await archive_old_profile_ids(profile_id, archived_ids)
    
    # Update profile with compacted IDs
    profile.ids = recent_ids
    await profile_db.save(profile)
    
    logger.info(
        f"Compacted profile {profile_id} IDs: "
        f"{len(sorted_ids)} → {len(recent_ids)} (archived {len(archived_ids)})"
    )
```

### Archived IDs Lookup
```python
async def find_profile_by_id_with_archive(profile_id: str) -> Optional[str]:
    """
    Find profile even if ID is archived.
    """
    # 1. Try current profile.ids
    is_valid, actual_id, _ = await validate_profile_id(profile_id)
    if is_valid or actual_id:
        return actual_id
    
    # 2. Check archived IDs
    archived_profile_id = await lookup_archived_profile_id(profile_id)
    if archived_profile_id:
        logger.info(f"Found {profile_id} in archive, points to {archived_profile_id}")
        return archived_profile_id
    
    return None
```

---

## 6. Session Orphaning

### Problem
```
Profile-456 has Session-A
Profile-456 merges into Profile-123
Session-A still points to Profile-456 (orphaned!)
```

**Result**: Session data lost, analytics broken, tracking errors.

### Solution: Session Migration
```python
async def migrate_sessions_after_merge(
    old_profile_ids: List[str], 
    new_profile_id: str
):
    """
    Migrate all sessions from old profiles to new profile.
    """
    for old_id in old_profile_ids:
        # Find all sessions for old profile
        sessions = await session_db.load_by_profile_id(old_id)
        
        for session in sessions:
            # Update session to point to new profile
            session.profile.id = new_profile_id
            
            # Maintain history
            if not hasattr(session, 'merged_from'):
                session.merged_from = []
            session.merged_from.append(old_id)
            
            await session_db.save(session)
            
        logger.info(f"Migrated {len(sessions)} sessions from {old_id} to {new_profile_id}")
```

### Session Lookup with Fallback
```python
async def load_session_safe(session_id: str, profile_id: str) -> Optional[Session]:
    """
    Load session with profile ID validation.
    """
    session = await session_db.load(session_id)
    
    if session is None:
        return None
    
    # Check if session profile matches
    if session.profile.id != profile_id:
        # Profile might have been merged
        actual_profile_id = await get_active_profile_id(profile_id)
        
        if actual_profile_id and session.profile.id == actual_profile_id:
            # Session is valid, just update local reference
            profile_id = actual_profile_id
        else:
            logger.warning(
                f"Session {session_id} profile mismatch: "
                f"expected {profile_id}, got {session.profile.id}"
            )
    
    return session
```

---

## 7. Event Race Conditions

### Problem
```
Time    Merge Thread            Track Thread
0ms     Start merge             -
10ms    Move events             -
15ms    -                       New event arrives for old profile
20ms    Delete old profile      -
25ms    -                       Event saved to DELETED profile!
```

**Result**: Events go to deleted profile, data loss.

### Solution: Grace Period
```python
async def merge_with_grace_period(primary_id, additional_ids, 
                                  grace_period_seconds=30):
    """
    Merge with grace period to catch in-flight events.
    """
    # 1. Mark profiles as "merging" (soft lock)
    for profile_id in additional_ids:
        await mark_profile_status(profile_id, status='merging', 
                                  merge_into=primary_id)
    
    # 2. Perform merge
    merged_profile = await merge_profiles(primary_id, additional_ids)
    
    # 3. Wait grace period for in-flight events
    logger.info(f"Merge complete. Waiting {grace_period_seconds}s grace period...")
    await asyncio.sleep(grace_period_seconds)
    
    # 4. Move any straggler events that arrived during grace period
    for profile_id in additional_ids:
        straggler_events = await load_events_since(
            profile_id, 
            since=datetime.now() - timedelta(seconds=grace_period_seconds)
        )
        
        if straggler_events:
            logger.warning(f"Found {len(straggler_events)} straggler events")
            await move_events(straggler_events, merged_profile.id)
    
    # 5. Now safe to mark old profiles as fully merged
    for profile_id in additional_ids:
        await mark_profile_status(profile_id, status='merged', 
                                  merged_into=primary_id)
    
    return merged_profile
```

### Tracking Intercept
```python
async def safe_track_event(profile_id, event_data):
    """
    Track event with merge-in-progress check.
    """
    # Check if profile is being merged
    profile_status = await get_profile_status(profile_id)
    
    if profile_status == 'merging':
        # Profile merge in progress - use target profile
        target_profile_id = await get_merge_target(profile_id)
        
        logger.info(
            f"Profile {profile_id} is being merged into {target_profile_id}. "
            f"Redirecting event."
        )
        
        profile_id = target_profile_id
    
    # Track to correct profile
    return await track_event(profile_id, event_data)
```

---

## 8. Double Merge Prevention

### Problem
```
Request 1: Merge profile-456 into profile-123
Request 2: Merge profile-456 into profile-123 (duplicate!)
```

**Result**: Duplicate operations, wasted resources, potential errors.

### Solution: Idempotency Keys
```python
import hashlib

def generate_merge_idempotency_key(primary_id, additional_ids):
    """
    Generate unique idempotency key for merge operation.
    """
    # Sort IDs for consistent key regardless of order
    all_ids = sorted([primary_id] + additional_ids)
    key_string = ':'.join(all_ids)
    
    return hashlib.sha256(key_string.encode()).hexdigest()

async def idempotent_merge(primary_id, additional_ids, ttl_seconds=3600):
    """
    Merge with idempotency protection.
    """
    # Generate idempotency key
    idempotency_key = generate_merge_idempotency_key(primary_id, additional_ids)
    redis_key = f"merge:idempotency:{idempotency_key}"
    
    # Check if already processed
    existing_result = await redis_client.get(redis_key)
    if existing_result:
        logger.info(f"Merge already processed: {idempotency_key}")
        return json.loads(existing_result)
    
    # Process merge
    result = await merge_profiles(primary_id, additional_ids)
    
    # Cache result
    await redis_client.set(
        redis_key,
        json.dumps({
            'merged_profile_id': result.id,
            'timestamp': datetime.now().isoformat()
        }),
        ex=ttl_seconds
    )
    
    return result
```

---

## 9. Cross-Tenant Security

### Problem
```
Tenant A: Merge profile-A-123 with profile-B-456
Profile-B-456 belongs to Tenant B!
```

**Result**: SECURITY BREACH! Data leak between tenants.

### Solution: Tenant Validation
```python
async def validate_tenant_ownership(profile_ids: List[str], 
                                    tenant_id: str) -> Tuple[bool, List[str]]:
    """
    Validate all profiles belong to same tenant.
    """
    invalid_profiles = []
    
    for profile_id in profile_ids:
        profile = await profile_db.load(profile_id)
        
        if profile is None:
            invalid_profiles.append(f"{profile_id}: not found")
            continue
        
        if profile.metadata.tenant != tenant_id:
            invalid_profiles.append(
                f"{profile_id}: belongs to tenant {profile.metadata.tenant}, "
                f"not {tenant_id}"
            )
    
    return len(invalid_profiles) == 0, invalid_profiles

async def secure_merge(primary_id, additional_ids, tenant_id: str):
    """
    Merge with tenant security validation.
    """
    # Validate all profiles belong to same tenant
    all_ids = [primary_id] + additional_ids
    is_valid, errors = await validate_tenant_ownership(all_ids, tenant_id)
    
    if not is_valid:
        raise SecurityError(
            f"Cross-tenant merge attempt detected! Errors:\n" +
            '\n'.join(errors)
        )
    
    # Safe to proceed
    return await merge_profiles(primary_id, additional_ids)
```

---

## 10. Merge Key Collisions

### Problem
```
User A: john@example.com (legitimate)
User B: john@example.com (typo or fraud)
Merge by email → Both profiles merged!
```

**Result**: Wrong users merged, privacy violation, data contamination.

### Solution: Multi-Factor Matching
```python
async def safe_merge_with_confirmation(
    field_name: str,
    field_value: str,
    confirmation_fields: List[Tuple[str, str]]
):
    """
    Merge with additional confirmation fields.
    
    Example:
        Merge by email, but also confirm:
        - Phone number matches
        - Name matches
        - Device ID overlaps
    """
    # Find duplicates by primary field
    duplicates = await find_duplicates(field_name, field_value)
    
    if len(duplicates) <= 1:
        return None  # No merge needed
    
    # Group profiles by confirmation field matches
    groups = []
    for profile in duplicates:
        matched_group = None
        
        for group in groups:
            # Check if profile matches any in this group
            match_score = calculate_match_score(
                profile, 
                group[0],
                confirmation_fields
            )
            
            if match_score >= 0.7:  # 70% match threshold
                matched_group = group
                break
        
        if matched_group:
            matched_group.append(profile)
        else:
            groups.append([profile])
    
    # Only merge profiles in same group
    merge_results = []
    for group in groups:
        if len(group) > 1:
            result = await merge_profiles(
                primary_id=group[0].id,
                additional_ids=[p.id for p in group[1:]]
            )
            merge_results.append(result)
    
    return merge_results

def calculate_match_score(profile1, profile2, fields):
    """
    Calculate similarity score between profiles.
    """
    score = 0
    total_weight = 0
    
    for field, weight in fields:
        val1 = get_field_value(profile1, field)
        val2 = get_field_value(profile2, field)
        
        if val1 and val2:
            total_weight += weight
            if val1 == val2:
                score += weight
            elif is_similar(val1, val2):  # Fuzzy match
                score += weight * 0.5
    
    return score / total_weight if total_weight > 0 else 0
```

---

## Summary: Critical Safeguards Checklist

Before deploying external identity resolution:

- [ ] **Implement distributed locking** for concurrent merge protection
- [ ] **Add circular reference detection** before merges
- [ ] **Validate tenant ownership** for security
- [ ] **Use idempotency keys** to prevent double merges
- [ ] **Implement grace periods** for event race conditions
- [ ] **Monitor profile.ids size** and implement compaction
- [ ] **Migrate sessions** during merge operations
- [ ] **Add multi-factor matching** for collision prevention
- [ ] **Implement transactional merge** with rollback capability
- [ ] **Check for profile resurrection** before creation
- [ ] **Add validation caching** with proper TTL
- [ ] **Monitor and alert** on merge failures and anomalies
- [ ] **Test rollback procedures** regularly
- [ ] **Document incident response** procedures
- [ ] **Implement audit logging** for all merge operations

## Monitoring & Alerts

### Key Metrics to Track
```python
# Merge operation metrics
- merge_duration_seconds
- merge_failure_rate
- merge_lock_wait_time
- merge_rollback_count
- circular_merge_detections

# Data integrity metrics
- orphaned_sessions_count
- orphaned_events_count
- profile_ids_overflow_count
- resurrection_detections
- cross_tenant_attempts

# Performance metrics
- validation_cache_hit_rate
- merge_queue_depth
- concurrent_merge_conflicts
- idempotency_cache_hits
```

### Alert Thresholds
- Merge failure rate > 5%
- Rollback count > 10/hour
- Circular merge detected
- Cross-tenant attempt (any)
- profile.ids > 500
- Orphaned data > 1000 records

## Further Reading
- [Distributed Systems Consistency](https://jepsen.io/)
- [Database Transaction Patterns](https://martinfowler.com/eaaCatalog/)
- [Identity Resolution Best Practices](https://www.oreilly.com/library/view/practical-data-science/9781449320638/)
