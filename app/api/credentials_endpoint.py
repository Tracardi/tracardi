from collections import defaultdict

from fastapi import APIRouter
from fastapi import HTTPException, Depends
from .auth.authentication import get_current_user
from .grouper import search
from ..domain.source import SourceRecord, Source
from ..domain.sources import Sources

router = APIRouter(
    dependencies=[Depends(get_current_user)]
)


@router.get("/credentials/by_type", tags=["credential"])
async def get_credentials(query: str = None):
    try:
        sources = Sources()
        result = await sources.bulk().load()
        total = result.total
        result = [SourceRecord.construct(Source.__fields_set__, **r).decode() for r in result]

        # Filtering
        if query is not None and len(query) > 0:
            query = query.lower()
            if query:
                result = [r for r in result if query in r.name.lower() or search(query, r.type)]

        # Grouping
        groups = defaultdict(list)
        for source in result:  # type: Source
            if isinstance(source.type, list):
                for group in source.type:
                    groups[group].append(source)
            elif isinstance(source.type, str):
                groups[source.type].append(source)

        # Sort
        groups = {k: sorted(v, key=lambda r: r.name, reverse=False) for k, v in groups.items()}

        return {
            "total": total,
            "grouped": groups
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
