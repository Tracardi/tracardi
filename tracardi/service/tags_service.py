from tracardi.event_server.utils.memory_cache import MemoryCache

# musi wczytywać do pamięci cache ustawienia z indeksu tag, użyj MemoryCache,
# service musi wyciągać event z bazy i zwracać go z wypełnionym "tags"