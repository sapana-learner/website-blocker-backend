from fastapi import FastAPI, HTTPException
from database import engine, SessionLocal
from schemas import UserCreate, LoginRequest, WebsiteCreate, FocusCreate
import models

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# ------------------
# Home
# ------------------

@app.get("/")
def home():
    return {"message": "Backend Working"}


# ------------------
# Register
# ------------------

@app.post("/register")
def register(user: UserCreate):
    db = SessionLocal()

    existing_user = db.query(models.User).filter(
        models.User.email == user.email
    ).first()

    if existing_user:
        db.close()
        raise HTTPException(status_code=409, detail="Email already registered")

    new_user = models.User(
        name=user.name,
        email=user.email,
        password=user.password
    )

    db.add(new_user)
    db.commit()
    db.close()

    return {"message": "User Registered Successfully"}


# ------------------
# Login
# ------------------

@app.post("/login")
def login(user: LoginRequest):
    db = SessionLocal()

    existing_user = db.query(models.User).filter(
        models.User.email == user.email
    ).first()

    if not existing_user:
        db.close()
        raise HTTPException(status_code=401, detail="Invalid Email or Password")

    if existing_user.password != user.password:
        db.close()
        raise HTTPException(status_code=401, detail="Invalid Email or Password")

    user_id = existing_user.id
    db.close()

    return {"message": "Login Successful", "user_id": user_id}


# ------------------
# Add Website
# ------------------

@app.post("/add-website")
def add_website(data: WebsiteCreate):
    db = SessionLocal()

    user = db.query(models.User).filter(models.User.id == data.user_id).first()

    if not user:
        db.close()
        raise HTTPException(status_code=404, detail="User not found")

    website = models.BlockedWebsite(
        website=data.website,
        user_id=data.user_id
    )

    db.add(website)
    db.commit()
    db.close()

    return {"message": "Website Added Successfully"}


# ------------------
# Delete Website
# ------------------

@app.delete("/website/{website_id}")
def delete_website(website_id: int):
    db = SessionLocal()

    website = db.query(models.BlockedWebsite).filter(
        models.BlockedWebsite.id == website_id
    ).first()

    if not website:
        db.close()
        raise HTTPException(status_code=404, detail="Website not found")

    db.delete(website)
    db.commit()
    db.close()

    return {"message": "Website deleted successfully"}


# ------------------
# Start Focus
# ------------------

@app.post("/start-focus")
def start_focus(data: FocusCreate):
    db = SessionLocal()

    user = db.query(models.User).filter(models.User.id == data.user_id).first()

    if not user:
        db.close()
        raise HTTPException(status_code=404, detail="User not found")

    session = models.FocusSession(
        status="ACTIVE",
        user_id=data.user_id
    )

    db.add(session)
    db.commit()
    db.close()

    return {"message": "Focus Session Started"}


# ------------------
# Stop Focus
# ------------------

@app.post("/stop-focus")
def stop_focus(user_id: int):
    db = SessionLocal()

    session = db.query(models.FocusSession).filter(
        models.FocusSession.user_id == user_id,
        models.FocusSession.status == "ACTIVE"
    ).first()

    if not session:
        db.close()
        raise HTTPException(status_code=404, detail="No active focus session")

    session.status = "STOPPED"
    db.commit()
    db.close()

    return {"message": "Focus Session Stopped"}


# ------------------
# Get Users
# ------------------

@app.get("/users")
def get_users():
    db = SessionLocal()
    users = db.query(models.User).all()
    db.close()
    return users


# ------------------
# Get User Websites
# ------------------

@app.get("/websites/{user_id}")
def get_websites(user_id: int):
    db = SessionLocal()
    websites = db.query(models.BlockedWebsite).filter(
        models.BlockedWebsite.user_id == user_id
    ).all()
    db.close()
    return websites


# ------------------
# Get User Focus History
# ------------------

@app.get("/focus-sessions/{user_id}")
def get_focus_sessions(user_id: int):
    db = SessionLocal()
    sessions = db.query(models.FocusSession).filter(
        models.FocusSession.user_id == user_id
    ).all()
    db.close()
    return sessions
