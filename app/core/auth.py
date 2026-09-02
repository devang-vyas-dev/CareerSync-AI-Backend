from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.supabase_client import supabase

security = HTTPBearer()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        # Let Supabase itself verify the ES256 token - works for both old and new projects
        user_response = supabase.auth.get_user(token)

        if not user_response.user:
            raise HTTPException(status_code=401, detail="Invalid token - user not found")

        # Return in format our routes expect
        user = user_response.user
        return {
            "sub": user.id,
            "email": user.email,
            "role": "authenticated",
            "raw": user
        }
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")