from fastapi import APIRouter, Depends
from app.core.auth import get_current_user
from app.core.supabase_client import supabase
from app.models.schemas import UserSyncRequest

router = APIRouter()

@router.post("/sync")
def sync_user(data: UserSyncRequest, user=Depends(get_current_user)):
    try:
        existing = supabase.table("profiles").select("*").eq("id", data.supabase_id).execute()

        if not existing.data:
            supabase.table("profiles").insert({
                "id": data.supabase_id,
                "email": data.email,
                "full_name": data.full_name
            }).execute()
        else:
            # UPDATE if exists - THIS IS THE FIX!
            supabase.table("profiles").update({
                "email": data.email,
                "full_name": data.full_name
            }).eq("id", data.supabase_id).execute()
        return {"message": "User synced successfully", "user_id": data.supabase_id}
    except Exception as e:
        print(f"SYNC ERROR: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/me")
def get_me(user=Depends(get_current_user)):
    try:
        result = supabase.table("profiles").select("*").eq("id", user["sub"]).execute()
        if result.data:
            return result.data[0]
        return {"supabase_user": user, "profile": "Not synced yet, call /sync"}
    except Exception as e:
        return {"error": str(e), "supabase_user": user}