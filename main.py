import os
from typing import Optional

import firebase
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Request, Response, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from firebase_admin import auth, credentials, firestore, initialize_app
from pydantic import BaseModel, EmailStr

load_dotenv()
reusable_oauth2 = OAuth2PasswordBearer(tokenUrl="/login")

cred = credentials.Certificate(os.environ.get("FIREBASE_CREDENTIALS", ""))
firebase_app = initialize_app(cred)
f_app = firebase.initialize_app(
    {
        "apiKey": os.environ.get("API_KEY", ""),
        "authDomain": os.environ.get("AUTH_DOMAIN", ""),
        "databaseURL": os.environ.get("DATABASE_URL", ""),
        "projectId": os.environ.get("PROJECT_ID", ""),
        "storageBucket": os.environ.get("STORAGE_BUCKET", ""),
        "messagingSenderId": os.environ.get("MESSAGING_SENDER_ID", ""),
        "appId": os.environ.get("APP_ID", ""),
    }
)
f_auth = f_app.auth()
db = firestore.client()

app = FastAPI(
    title="Task API",
    description="Create, Read, Update, Delete, PATCH, HEAD, OPTIONS, TRACE -- Ever Alvarez 9A BIS",
    version="1.0.0",
    docs_url="/",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# _________________________________________________________________________________________


class Task(BaseModel):
    title: str
    description: str
    completed: bool


class UserRegistration(BaseModel):
    email: EmailStr
    password: str


class TaskInDb(Task):
    user_id: str
    id: str


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None


class RegResModel(BaseModel):
    message: Optional[str]
    user_uid: Optional[str]


class LoginResModel(BaseModel):
    access_token: Optional[str]
    token_type: Optional[str]


class GeneralResModel(BaseModel):
    message: Optional[str]
    task_id: Optional[str]


# _________________________________________________________________________________________


def create_user(email: str, password: str) -> str:
    user = auth.create_user(email=email, password=password)
    return user.uid


def authenticate_user(email: str, password: str) -> Optional[dict]:
    try:
        user = f_auth.sign_in_with_email_and_password(email, password)

        return {
            "access_token": user["idToken"],
            "token_type": "bearer",
        }
    except Exception:
        return None


def get_current_user(authorization: str = Depends(reusable_oauth2)):
    try:
        user = auth.verify_id_token(authorization)
        return user
    except auth.ExpiredIdTokenError:
        raise HTTPException(status_code=401, detail="Expired ID token")
    except auth.InvalidIdTokenError:
        raise HTTPException(status_code=401, detail="Invalid ID token")
    except Exception:
        raise HTTPException(
            status_code=401, detail="Invalid or missing Authorization header"
        )


# _________________________________________________________________________________________


@app.post("/register", response_model=RegResModel)
def register_user(user: UserRegistration):
    try:
        user_uid = create_user(user.email, user.password)
        return {"message": "User registered successfully", "user_uid": user_uid}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/login", response_model=LoginResModel)
def login_user(form_data: OAuth2PasswordRequestForm = Depends()):
    user_id = authenticate_user(form_data.username, form_data.password)
    if user_id:
        return user_id

    raise HTTPException(status_code=401, detail="Login failed")


# _________________________________________________________________________________________


# Get the list of tasks for the current user
@app.get("/tasks", response_model=list[TaskInDb])
def get_user_tasks(user: dict = Depends(get_current_user)):
    tasks = db.collection("tasks").where("user_id", "==", user["uid"]).stream()
    task_list = []
    for task in tasks:
        task_data = task.to_dict()
        task_list.append({**task_data, "id": task.id})
    return task_list


@app.post("/task", response_model=GeneralResModel)
def create_task(task: Task, user: dict = Depends(get_current_user)):
    task_ref = db.collection("tasks").document()
    task_ref.set({**task.dict(), "user_id": user["uid"]})

    return {"message": "Task created successfully", "task_id": task_ref.id}



@app.put("/task/{task_id}", response_model=GeneralResModel)
def update_task(task_id: str, task: TaskUpdate, user: dict = Depends(get_current_user)):
    task_ref = db.collection("tasks").document(task_id)

    if not task_ref.get().exists:
        raise HTTPException(status_code=404, detail="Task not found")

    task_data = task_ref.get().to_dict()

    if task_data["user_id"] != user["uid"]:
        raise HTTPException(status_code=403, detail="Access forbidden")

    data_to_update = {k: v for k, v in task.dict().items() if v is not None}
    task_ref.update(data_to_update)

    return {"message": "Task updated successfully", "task_id": task_id}


@app.delete("/task/{task_id}", response_model=GeneralResModel)
def delete_task(task_id: str, user: dict = Depends(get_current_user)):
    task_ref = db.collection("tasks").document(task_id)

    if not task_ref.get().exists:
        raise HTTPException(status_code=404, detail="Task not found")

    task_data = task_ref.get().to_dict()

    if task_data["user_id"] != user["uid"]:
        raise HTTPException(status_code=403, detail="Access forbidden")

    task_ref.delete()

    return {"message": "Task deleted successfully", "task_id": task_id}


@app.patch("/task/{task_id}/complete", response_model=GeneralResModel)
def complete_task(task_id: str, user: dict = Depends(get_current_user)):
    task_ref = db.collection("tasks").document(task_id)

    if not task_ref.get().exists:
        raise HTTPException(status_code=404, detail="Task not found")

    task_data = task_ref.get().to_dict()

    if task_data["user_id"] != user["uid"]:
        raise HTTPException(status_code=403, detail="Access forbidden")

    task_ref.update({"completed": True})

    return {"message": "Task completed successfully", "task_id": task_id}


# _________________________________________________________________________________________


@app.options("/options")
def get_options(response: Response):
    response.headers["Allow"] = "OPTIONS, GET, POST, PUT, DELETE, PATCH, HEAD, TRACE"
    response.status_code = status.HTTP_204_NO_CONTENT

    return


@app.head("/head")
def get_headers():
    return {}


# curl -v -X TRACE http://<host>/trace
@app.trace("/trace")
async def get_trace(request: Request, response: Response):
    request_body = await request.body()

    for k, v in request.headers.items():
        response.headers[k] = v
    response.headers["Content-Type"] = "message/http"  # RFC 7231
    response.status_code = 200  # RFC 7231

    return request_body.decode("utf-8")


# _________________________________________________________________________________________

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
