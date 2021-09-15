from .mock_storage import profiles


class ProfileStorageMock:

    async def load(self, profile_id):
        for item in profiles:
            if profile_id in item:
                return item[profile_id]
        return None

    async def create(self, data):
        for item in data:
            profiles.append({item['id']: item})
