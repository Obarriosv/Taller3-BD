from fastapi import FastAPI, Body, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
import os

app = FastAPI(title="API Taller 3 MongoDB APEX")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB")

if not MONGO_URI:
    raise RuntimeError("Falta la variable de entorno MONGO_URI")

if not MONGO_DB:
    raise RuntimeError("Falta la variable de entorno MONGO_DB")

client = MongoClient(MONGO_URI)
db = client[MONGO_DB]

comentarios_collection = db["comentarios_bares"]
eventos_collection = db["eventos"]


def convertir_documento(doc):
    doc["_id"] = str(doc["_id"])
    return doc


@app.get("/")
def index():
    return {
        "mensaje": "API funcionando correctamente",
        "base_datos": MONGO_DB
    }


@app.get("/bares/{bar_id}/comentarios")
def obtener_comentarios(bar_id: int):
    comentarios = comentarios_collection.find({"bar_id": bar_id}).sort("fecha", -1)
    return [convertir_documento(c) for c in comentarios]


@app.post("/bares/{bar_id}/comentarios")
def crear_comentario(bar_id: int, datos: dict = Body(...)):
    texto = datos.get("texto")

    if not texto or not str(texto).strip():
        raise HTTPException(status_code=400, detail="El comentario no puede estar vacío")

    comentario = {
        "bar_id": bar_id,
        "texto": texto,
        "autor": datos.get("autor", "Anónimo"),
        "calificacion": datos.get("calificacion"),
        "fecha": datetime.now().isoformat()
    }

    resultado = comentarios_collection.insert_one(comentario)

    return {
        "mensaje": "Comentario creado correctamente",
        "id": str(resultado.inserted_id)
    }


@app.get("/bares/{bar_id}/eventos")
def obtener_eventos(bar_id: int):
    eventos = eventos_collection.find({"bar_id": bar_id}).sort("fecha_creacion", -1)
    return [convertir_documento(e) for e in eventos]


@app.post("/bares/{bar_id}/eventos")
def crear_evento(bar_id: int, datos: dict = Body(...)):
    nombre = datos.get("nombre")

    if not nombre or not str(nombre).strip():
        raise HTTPException(status_code=400, detail="El nombre del evento es obligatorio")

    evento = {}

    for clave, valor in datos.items():
        if valor is not None and str(valor).strip() != "":
            evento[clave] = valor

    evento["bar_id"] = bar_id
    evento["fecha_creacion"] = datetime.now().isoformat()

    resultado = eventos_collection.insert_one(evento)

    return {
        "mensaje": "Evento creado correctamente",
        "id": str(resultado.inserted_id)
    }
