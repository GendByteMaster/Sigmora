from fastapi import APIRouter, Depends, HTTPException, status
from models import User, Token
from auth import get_current_user, get_password_hash, create_access_token, verify_password
from fastapi.security import OAuth2PasswordRequestForm
from database import db
from bson import ObjectId
from datetime import timedelta

router = APIRouter()

@router.post("/subscribe")
async def subscribe(user: User):
    if await db.users.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="User already exists")
    user.password = get_password_hash(user.password)
    user.subscribed = True
    await db.users.insert_one(user.dict())
    return {"message": "Subscribed successfully"}

@router.post("/unsubscribe")
async def unsubscribe(current_user: dict = Depends(get_current_user)):
    await db.users.update_one(
        {"_id": ObjectId(current_user["_id"])}, 
        {"$set": {"subscribed": False}}
    )
    return {"message": "Unsubscribed successfully"}

@router.get("/stats")
async def stats():
    count = await db.users.count_documents({"subscribed": True})
    return {"subscribers": count}

@router.post("/preferences")
async def update_preferences(preferences: dict, current_user: dict = Depends(get_current_user)):
    await db.users.update_one(
        {"_id": ObjectId(current_user["_id"])}, 
        {"$set": {"preferences": preferences}}
    )
    return {"message": "Preferences updated successfully"}

@router.get("/notifications")
async def get_notifications(current_user: dict = Depends(get_current_user)):
    notifications = await db.notifications.find({"sent_to": current_user["_id"]}).to_list(length=100)
    return notifications

@router.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await db.users.find_one({"email": form_data.username})
    if not user or not verify_password(form_data.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        data={"sub": user["email"]}, 
        expires_delta=timedelta(minutes=30)
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/get-token")
async def get_token(current_user: dict = Depends(get_current_user)):
    return {"access_token": current_user["access_token"], "token_type": "bearer"}
