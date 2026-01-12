# Identity Resolution Service

Bu modül, Tracardi'nin identity resolution (profil birleştirme) özelliğini harici API olarak kullanılabilir hale getirir.

## Dosyalar

### Core Service
- **`identity_resolution_service.py`**: Identity resolution için servis katmanı
  - `resolve_by_profile_ids()`: ID'lere göre birleştirme
  - `resolve_by_merge_keys()`: Key'lere göre birleştirme
  - `find_duplicate_profiles()`: Duplicate bulma
  - `resolve_by_field_value()`: Tek alan ile birleştirme

### API Layer
- **`identity_resolution_endpoint_example.py`**: FastAPI endpoint örnekleri (TracardAPI için)
  - `/identity-resolution/merge-by-ids`
  - `/identity-resolution/merge-by-keys`
  - `/identity-resolution/merge-by-field`
  - `/identity-resolution/find-duplicates`

### Data Models
- **`tracardi/domain/identity_resolution_payload.py`**: Request/Response modelleri
  - `IdentityResolutionByIdsRequest`
  - `IdentityResolutionByKeysRequest`
  - `IdentityResolutionByFieldRequest`
  - `FindDuplicatesRequest`
  - `IdentityResolutionResponse`
  - `FindDuplicatesResponse`
  - `ProfileSummary`

## Özellikler

### External Identity Resolution Flag

Tracker payload'a `externalIdentityResolution` flag'i eklendi. Bu flag `true` olduğunda, Tracardi internal identity resolution'ı skip eder.

**Değişiklik**: `tracardi/service/wf/workflow_manager_async.py`

```python
skip_internal_merge = self.tracker_payload.options.get('externalIdentityResolution', False)

if self.profile is not None and self.profile.needs_merging() and not skip_internal_merge:
    self.profile = await self.merge_profile(self.profile)
```

## Kullanım

### 1. API Üzerinden Identity Resolution

```python
from tracardi.service.identity_resolution_service import IdentityResolutionService

# Email'e göre birleştir
merged_profile = await IdentityResolutionService.resolve_by_field_value(
    field_name="data.contact.email.main",
    field_value="user@example.com"
)
```

### 2. Tracker Payload'da Flag Kullanımı

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

## TracardAPI'ye Entegrasyon

`identity_resolution_endpoint_example.py` dosyasındaki endpoint'leri TracardAPI projesine ekleyin:

```python
from tracardi.service.identity_resolution_endpoint_example import router as identity_router

app = FastAPI()
app.include_router(identity_router)
```

## Dokümantasyon

Detaylı kullanım kılavuzu için root dizindeki `EXTERNAL_IDENTITY_RESOLUTION.md` dosyasına bakın.

## Benefits

1. **Performans**: Gereksiz internal merging'i engelleyerek daha hızlı işlem
2. **Kontrol**: Identity resolution'ı kendi mantığınıza göre kontrol edin
3. **Entegrasyon**: Harici sistemlerden (CRM, vb.) identity resolution yapın
4. **Batch Processing**: Periyodik batch merge işlemleri yapın
5. **Preview**: Merge'den önce duplicate'leri görün
