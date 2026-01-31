import os
import jwt
from fastapi import Header, HTTPException, status
from typing import Optional
import structlog
from dotenv import load_dotenv

load_dotenv()
logger = structlog.get_logger()

# Get the PEM Public Key from Clerk Dashboard -> API Keys -> Advanced -> PEM Public Key
# It should be set as an environment variable: CLERK_PEM_PUBLIC_KEY
CLERK_PEM_PUBLIC_KEY = os.getenv("CLERK_PEM_PUBLIC_KEY")
if CLERK_PEM_PUBLIC_KEY:
    logger.info("CLERK_PEM_PUBLIC_KEY loaded successfully", length=len(CLERK_PEM_PUBLIC_KEY))
else:
    logger.error("CLERK_PEM_PUBLIC_KEY is MISSING or Empty")


async def get_current_user(authorization: Optional[str] = Header(None)) -> str:
    """
    Verifies the Clerk JWT from the Authorization header.
    Returns the user_id (sub) if valid.
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization Header",
        )
    
    try:
        scheme,token = authorization.split()
        if scheme.lower() != "bearer":
             raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Authorization Scheme",
            )
            
        if not CLERK_PEM_PUBLIC_KEY:
             # Dev mode fallback: If no key set, warn but maybe allow if explicitly in DEV? 
             # No, better securely fail or check for a DEV_bypass env.
             # For now, let's log error and fail safe.
             logger.error("CLERK_PEM_PUBLIC_KEY not set in backend environment.")
             raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Authentication configuration missing on server.",
            )

        # decode and verify
        payload = jwt.decode(
            token, 
            CLERK_PEM_PUBLIC_KEY, 
            algorithms=["RS256"],
            # You might want to verify audience/issuer too if needed
            # audience="...", 
            # issuer="https://clerk.your-app.com"
            options={"verify_aud": False} 
        )
        
        user_id = payload.get("sub")
        if not user_id:
             raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token missing user_id",
            )
            
        return user_id

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
        )
    except jwt.InvalidTokenError as e:
        logger.warning("Invalid Token", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
    except Exception as e:
        logger.error("Authentication Error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
        )
