from pydantic import BaseModel


class ProfileStats(BaseModel):
    visits: int = 0
    views: int = 0

    def merge(self, stats: 'ProfileStats') -> 'ProfileStats':
        views = self.visits + stats.views
        visits = self.visits + stats.visits
        data = {
            'views': views,
            'visits': visits
        }
        return ProfileStats(**data)
