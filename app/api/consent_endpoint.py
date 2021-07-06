# from fastapi import APIRouter
# from fastapi import HTTPException, Depends
#
# from .auth.authentication import get_current_user
# from ..domain.consent import Consent
#
# router = APIRouter(
#     dependencies=[Depends(get_current_user)]
# )
#
#
# @router.get("/consent")
# async def get_consent(id: str):
#     try:
#         consent = Consent(id=id)
#         return await consent.storage().load()
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
#
#
# @router.post("/consent")
# async def add_consent(consent: Consent):
#     try:
#         return await consent.storage().save()
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
#
#
# @router.put("/consent")
# async def update_consent(consent: Consent):
#     try:
#         return await consent.storage().save()
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
#
#
# @router.delete("/consent")
# async def delete_consent(id: str):
#     try:
#         consent = Consent(id=id)
#         return await consent.storage().delete()
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
