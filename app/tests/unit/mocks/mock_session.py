from .mock_storage import sessions


class SessionStorageMock:

    async def load(self, session_id):
        for item in sessions:
            if session_id in item:
                return item[session_id]
        return None

    async def create(self, data):
        for item in data:
            sessions.append({item['id']: item})
