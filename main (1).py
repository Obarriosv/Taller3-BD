from fastapi import FastAPI, Body, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from bson import ObjectId
from datetime import datetime
import os

app = FastAPI(title="API Parranderos MongoDB")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



MONGO_URI = os.getenv("MONGO_URI", "mongodb://TU_USUARIO:TU_CONTRASEÑA@157.253.236.88:8087")
MONGO_DB = os.getenv("MONGO_DB", "NOMBRE_DE_TU_BASE")

comentarios_collection = db["comentarios_bares"]
eventos_collection = db["eventos"]

comentarios_collection = db["comentarios_bares"]
eventos_collection = db["eventos"]


def convertir_a_json(documento):
    """
    Convierte ObjectId y datetime para que FastAPI pueda devolverlos como JSON.
    """
    if documento is None:
        return None

    for clave, valor in documento.items():
        if isinstance(valor, ObjectId):
            documento[clave] = str(valor)
        elif isinstance(valor, datetime):
            documento[clave] = valor.isoformat()

    return documento


@app.get("/")
def inicio():
    return {
        "mensaje": "API de Parranderos funcionando correctamente",
        "endpoints": [
            "/bares/{bar_id}/comentarios",
            "/bares/{bar_id}/eventos"
        ]
    }


@app.get("/bares/{bar_id}/comentarios")
def obtener_comentarios(bar_id: int):
    """
    Retorna todos los comentarios asociados a un bar.
    La colección se llama comentarios_bares.
    El filtro se hace por bar_id.
    """
    try:
        comentarios = comentarios_collection.find({"bar_id": bar_id}).sort("fecha", -1)
        return [convertir_a_json(comentario) for comentario in comentarios]

    except PyMongoError as error:
        raise HTTPException(
            status_code=500,
            detail=f"Error consultando comentarios: {str(error)}"
        )


@app.post("/bares/{bar_id}/comentarios")
def crear_comentario(bar_id: int, datos: dict = Body(...)):
    """
    Inserta un comentario en la colección comentarios_bares.
    El bar_id se toma desde la URL.
    """
    try:
        if "texto" not in datos or not str(datos["texto"]).strip():
            raise HTTPException(
                status_code=400,
                detail="El campo texto es obligatorio."
            )

        fecha_actual = datetime.now().isoformat()

        comentario = {
            "bar_id": bar_id,
            "texto": datos.get("texto"),
            "autor": datos.get("autor", "Anónimo"),
            "calificacion": datos.get("calificacion"),
            "fecha": fecha_actual,
            "date": fecha_actual
        }

        resultado = comentarios_collection.insert_one(comentario)

        return {
            "mensaje": "Comentario creado correctamente",
            "id": str(resultado.inserted_id),
            "comentario": comentario
        }

    except PyMongoError as error:
        raise HTTPException(
            status_code=500,
            detail=f"Error creando comentario: {str(error)}"
        )


@app.get("/bares/{bar_id}/eventos")
def obtener_eventos(bar_id: int):
    """
    Retorna todos los eventos asociados a un bar.
    La colección se llama eventos.
    El filtro se hace por bar_id.
    """
    try:
        eventos = eventos_collection.find({"bar_id": bar_id}).sort("fecha_creacion", -1)
        return [convertir_a_json(evento) for evento in eventos]

    except PyMongoError as error:
        raise HTTPException(
            status_code=500,
            detail=f"Error consultando eventos: {str(error)}"
        )


@app.post("/bares/{bar_id}/eventos")
def crear_evento(bar_id: int, datos: dict = Body(...)):
    """
    Inserta un evento en la colección eventos.
    El evento puede tener campos distintos según su tipo.
    Por ejemplo:
    - Concierto: nombre, artista, cover, cupos
    - Happy hour: nombre, descuento, hora_inicio, hora_fin
    """
    try:
        if "nombre" not in datos or not str(datos["nombre"]).strip():
            raise HTTPException(
                status_code=400,
                detail="El campo nombre es obligatorio."
            )

        evento = {}

        for clave, valor in datos.items():
            if valor is not None and str(valor).strip() != "":
                evento[clave] = valor

        evento["bar_id"] = bar_id
        evento["fecha_creacion"] = datetime.now().isoformat()

        resultado = eventos_collection.insert_one(evento)

        return {
            "mensaje": "Evento creado correctamente",
            "id": str(resultado.inserted_id),
            "evento": evento
        }

    except PyMongoError as error:
        raise HTTPException(
            status_code=500,
            detail=f"Error creando evento: {str(error)}"
        )