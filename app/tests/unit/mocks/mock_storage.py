sessions = [{
    "1": {
        "type": "session",
        "source": {"id": "scope"},
        "id": "1",
        'profile': {"id": "1"}
    }
}]

profiles = [
    {"1": {'id': "1", "traits": {}}},
    {"2": {'id': "2", "traits": {}}},
]


class MockStorageCrud:

    def __init__(self, index, domain_class_ref, entity):
        self.index = index
        self.domain_class_ref = domain_class_ref
        self.entity = entity
        if index == 'session':
            self.data = sessions
        elif index == 'profile':
            self.data = profiles

    async def load(self):

        for item in self.data:
            if self.entity.id in item:
                return self.domain_class_ref(**item[self.entity.id])
        return None

    async def save(self):
        self.data.append({self.entity.id: self.entity.dict(exclude_unset=True)})

    async def delete(self):
        del(self.data[self.entity.id])


class EntityStorageCrud:

    def __init__(self, index, entity):
        self.index = index
        self.entity = entity
        if index == 'session':
            self.data = sessions
        elif index == 'profile':
            self.data = profiles

    async def load(self, domain_class_ref):

        for item in self.data:
            if self.entity.id in item:
                return domain_class_ref(**item[self.entity.id])
        return None

    async def save(self):
        self.data.append({self.entity.id: self.entity.dict(exclude_unset=True)})

    async def delete(self):
        del(self.data[self.entity.id])

