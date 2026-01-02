from fastapi import FastAPI
import os

app = FastAPI(title="Pronoscore API")

@app.get("/")
def read_root():
    return {
        "status": "online",
        "message": "Bienvenue sur l'API Pronoscore 2026",
        "version": "1.0.0"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}
