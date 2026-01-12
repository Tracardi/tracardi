# External Identity Resolution API

Bu doküman, Tracardi'nin identity resolution (profil birleştirme) özelliğini harici API üzerinden nasıl kullanabileceğinizi açıklar.

## Genel Bakış

Tracardi, varsayılan olarak profil değişikliklerini tespit ettiğinde otomatik olarak identity resolution (profil birleştirme) yapar. Ancak bazı durumlarda bu işlemi harici bir sistem üzerinden kontrol etmek isteyebilirsiniz. Bu özellik size şunları sağlar:

1. **Harici Kontrol**: Identity resolution'ı kendi sistemlerinizden API ile yapabilirsiniz
2. **Performance**: Gereksiz internal merging işlemlerini engelleyerek performans kazanırsınız
3. **Özelleştirme**: Merging mantığını kendi iş kurallarınıza göre özelleştirebilirsiniz

## Flag Kullanımı

Identity resolution'ı harici olarak yaptıysanız, Tracardi'ye event gönderirken `externalIdentityResolution: true` flag'ini ekleyin. Bu sayede Tracardi internal merging yapmayı atlayacaktır.

### Örnek Tracker Payload

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

**Önemli**: `options.externalIdentityResolution: true` ayarı, Tracardi'nin internal identity resolution yapmasını engeller.

## API Endpoints

### 1. Profile ID'lere Göre Birleştirme

Belirli profile ID'lerini birleştirmek için:

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

### 2. Merge Key'lere Göre Birleştirme

Email, telefon veya özel bir alana göre profilleri birleştirmek için:

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

**Çoklu key örneği:**
```json
{
  "profile_id": "profile-123",
  "merge_keys": [
    ["data.contact.email.main", "user@example.com"],
    ["data.contact.phone.main", "+905551234567"]
  ]
}
```

### 3. Tek Alan ile Birleştirme (Kolaylık Endpoint'i)

```bash
POST /identity-resolution/merge-by-field
Content-Type: application/json

{
  "field_name": "data.contact.email.main",
  "field_value": "user@example.com",
  "primary_profile_id": "profile-123"  // Opsiyonel
}
```

`primary_profile_id` belirtilmezse, en yeni profil primary olarak kullanılır.

### 4. Duplicate Profilleri Bulma (Birleştirme Yapmadan)

Birleştirme yapmadan önce duplicate profilleri görmek için:

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

## Kullanım Senaryoları

### Senaryo 1: Email Değişikliğinde Manuel Birleştirme

```python
import requests

# 1. Yeni email ile duplicate profilleri bul
duplicates_response = requests.post(
    "http://tracardi-api/identity-resolution/find-duplicates",
    json={
        "merge_keys": [
            ["data.contact.email.main", "newemail@example.com"]
        ]
    }
)

duplicates = duplicates_response.json()

# 2. Duplicate varsa birleştir
if duplicates["count"] > 1:
    merge_response = requests.post(
        "http://tracardi-api/identity-resolution/merge-by-field",
        json={
            "field_name": "data.contact.email.main",
            "field_value": "newemail@example.com"
        }
    )
    
    merged_profile_id = merge_response.json()["merged_profile_id"]
    
    # 3. Tracardi'ye event gönder (internal merge skip edilsin)
    track_response = requests.post(
        "http://tracardi-api/track",
        json={
            "source": {"id": "source-123"},
            "profile": {"id": merged_profile_id},
            "events": [...],
            "options": {
                "externalIdentityResolution": True  # Internal merge'i atla
            }
        }
    )
```

### Senaryo 2: Periyodik Batch Birleştirme

```python
# Günde bir kez tüm email'lere göre duplicate temizliği
unique_emails = get_all_unique_emails_from_database()

for email in unique_emails:
    response = requests.post(
        "http://tracardi-api/identity-resolution/merge-by-field",
        json={
            "field_name": "data.contact.email.main",
            "field_value": email
        }
    )
    
    if response.json()["success"]:
        print(f"Merged profiles for {email}")
```

### Senaryo 3: CRM Entegrasyonu

```python
# CRM'den gelen merge isteği
crm_merge_request = {
    "master_profile": "profile-123",
    "merge_profiles": ["profile-456", "profile-789"]
}

# Tracardi'de birleştir
response = requests.post(
    "http://tracardi-api/identity-resolution/merge-by-ids",
    json={
        "primary_profile_id": crm_merge_request["master_profile"],
        "additional_profile_ids": crm_merge_request["merge_profiles"]
    }
)

# Tüm sonraki eventlerde flag kullan
# options: {"externalIdentityResolution": true}
```

## Teknik Detaylar

### Internal Implementation

Flag kontrolü `tracardi/service/wf/workflow_manager_async.py` içinde yapılır:

```python
skip_internal_merge = self.tracker_payload.options.get('externalIdentityResolution', False)

if self.profile is not None and self.profile.needs_merging() and not skip_internal_merge:
    self.profile = await self.merge_profile(self.profile)
```

### Service Layer

Identity resolution servisi `tracardi/service/identity_resolution_service.py` içinde implement edilmiştir ve şu metodları sağlar:

- `resolve_by_profile_ids()`: Explicit ID'lere göre birleştirme
- `resolve_by_merge_keys()`: Key-value eşleşmesine göre birleştirme
- `find_duplicate_profiles()`: Duplicate bulma (birleştirme yapmadan)
- `resolve_by_field_value()`: Tek alan ile birleştirme

### Data Models

Request/response modelleri `tracardi/domain/identity_resolution_payload.py` içinde tanımlanmıştır.

## Best Practices

1. **Flag'i Her Zaman Kullanın**: External merging yaptıktan sonra mutlaka `externalIdentityResolution: true` flag'ini kullanın
2. **Duplicate Kontrolü**: Birleştirme yapmadan önce `find-duplicates` endpoint'i ile kontrol edin
3. **Hata Yönetimi**: API çağrılarınızda hata yönetimi yapın ve retry logic ekleyin
4. **Monitoring**: External merge işlemlerini loglayin ve monitor edin
5. **Transaction Safety**: Kritik merge işlemlerinde transaction safety sağlayın

## Migration Guide

### Mevcut Sistemden External API'ye Geçiş

1. **API Endpoint'lerini Deploy Edin**
   - Endpoint'leri TracardAPI projesine ekleyin
   - Deploy ve test edin

2. **External Merge Logic Implement Edin**
   - Kendi merge logic'inizi yazın
   - Identity resolution service'i kullanın

3. **Tracker Payload'larını Güncelleyin**
   - `options.externalIdentityResolution: true` ekleyin
   - Test edin

4. **Monitor Edin**
   - Internal merge'lerin skip edildiğini kontrol edin
   - Performance metriklerini takip edin

## Troubleshooting

### Problem: Internal merge hala çalışıyor

**Çözüm**: Tracker payload'da `options.externalIdentityResolution: true` flag'inin olduğundan emin olun.

### Problem: Merge sonrası event'ler eski profile'a gidiyor

**Çözüm**: Merge'den sonra dönen `merged_profile_id`'yi kullandığınızdan emin olun.

### Problem: Duplicate bulunamıyor

**Çözüm**: 
- Merge key'lerin doğru olduğundan emin olun
- Trait alanları için `.keyword` suffix'i otomatik eklenir, manuel eklemeye gerek yok
- Field path'lerin doğru olduğunu kontrol edin

## Support

Sorularınız için:
- GitHub Issues: https://github.com/Tracardi/tracardi
- Documentation: https://docs.tracardi.com
