from pydantic import BaseModel


class ProfileStats(BaseModel):
    visits: int = 0
    views: int = 0

    def merge(self, stats: 'ProfileStats'):
        self.views += stats.views
        self.visits += stats.visits
