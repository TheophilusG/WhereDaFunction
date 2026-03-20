from fastapi import APIRouter, Depends

from core.deps import get_current_user


router = APIRouter(prefix="/vendors", tags=["vendors"])


@router.get("/me")
def get_vendor_dashboard(current_user=Depends(get_current_user)):
    return {
        "data": {
            "user_id": current_user.id,
            "is_vendor": current_user.is_vendor,
            "message": "Vendor dashboard endpoints will be added in phase 4",
        },
        "error": None,
        "meta": None,
    }
