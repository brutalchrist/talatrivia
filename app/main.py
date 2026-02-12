from fastapi import FastAPI

from app.api.routes import health, users, questions

app = FastAPI(title="TalaTrivia API")

app.include_router(health.router)
app.include_router(users.router)
app.include_router(questions.router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
