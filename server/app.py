from fastapi import FastAPI
import uvicorn

from my_env.env import EmailEnv
from my_env.models import EmailAction

app = FastAPI()
env = EmailEnv()


# ✅ NEW: Home route (add here)
@app.get("/")
def home():
    return {
        "message": "Email OpenEnv API is running 🚀",
        "endpoints": {
            "/reset": "POST → Get a new email task",
            "/step": "POST → Send response and get reward"
        }
    }


@app.post("/reset")
def reset():
    obs = env.reset()
    return {
        "email_text": obs.email_text,
        "task_type": obs.task_type
    }


@app.post("/step")
def step(action: dict):
    act = EmailAction(**action)
    result = env.step(act)

    return {
        "observation": {
            "email_text": result.observation.email_text,
            "task_type": result.observation.task_type
        },
        "reward": result.reward,
        "done": result.done,
        "info": result.info
    }


# REQUIRED main() function
def main():
    uvicorn.run(app, host="0.0.0.0", port=8000)


# REQUIRED for validation
if __name__ == "__main__":
    main()