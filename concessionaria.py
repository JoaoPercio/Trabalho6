from fastapi import FastAPI, HTTPException, Depends
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError 
from bson import ObjectId
from pydantic import BaseModel
from typing import List
from typing import Optional

app = FastAPI()

#configuracao do MongoDB
client = MongoClient("mongodb://localhost:27017")
db = client["trabalho6"]

#modelos
class Marca(BaseModel): #marca create e put
    nome: str

class MarcaList(Marca): #lista com id
    id: str

class Modelo(BaseModel): #modelo create e put
    id_marca: str
    nome: str

class ModeloList(Modelo): #lista com id
    id: str
    
class ModeloResponse(BaseModel): # junta as informaçoes da marca
    id: str
    id_marca: str
    nome: str
    marca_info: Optional[Marca]

class Carro(BaseModel):
    id_modelo: str
    nome: str
    renavam: int
    placa: str
    valor: float
    ano: int

class CarroList(Carro):
    id: str


class CarroResponse(BaseModel):
    id: str
    id_modelo: str
    nome: str
    renavam: int
    placa: str
    valor: float
    ano: int
    modelo_info: Optional[Modelo]
    marca_info: Optional[Marca]


#MARCA
@app.post("/marca/", response_model=MarcaList)
def create_marca(marca: Marca):
    result = db.marca.insert_one(marca.dict())
    inserted_id = str(result.inserted_id)
    return MarcaList(
        id=inserted_id,
        nome=marca.nome,
    )

@app.get("/marca/{marca_id}", response_model=MarcaList)
def get_marca(marca_id: str):
    marca = db.marca.find_one({"_id": ObjectId(marca_id)})

    if marca is None:
        raise HTTPException(status_code=404, detail="Marca not found")

    return MarcaList(id=str(marca["_id"]), nome=marca["nome"])

@app.get("/marca/", response_model=List[MarcaList])
def get_all_marcas():
    marcas = list(db.marca.find())
    marcas_response = []
    for marca in marcas:
        marcas_response.append(MarcaList(
            id=str(marca["_id"]),
            nome=marca["nome"]
        ))
    return marcas_response

@app.put("/marca/{marca_id}", response_model=Marca)
def update_marca(marca_id: str, updated_marca: Marca):
    db.marca.update_one({"_id": ObjectId(marca_id)}, {"$set": updated_marca.dict()})
    return updated_marca

@app.delete("/marca/{marca_id}")
def delete_marca(marca_id: str):
    marca = db.marca.find_one({"_id": ObjectId(marca_id)})
    if marca is None:
        raise HTTPException(status_code=404, detail="Marca not found")
    db.marca.delete_one({"_id": ObjectId(marca_id)})
    return 0

#MODELO
@app.get("/modelos/", response_model=List[ModeloResponse])
def get_all_modelos():
    modelos = list(db.modelo.find())

    modelos_response = []
    for modelo in modelos:
        id_marca = modelo.get("id_marca")
        marca_info = None

        if id_marca:
            marca_info = db.marca.find_one({"_id": ObjectId(id_marca)})

        modelos_response.append(ModeloResponse(
            id=str(modelo["_id"]),
            id_marca=modelo["id_marca"],
            nome=modelo["nome"],
            marca_info=Marca(**marca_info) if marca_info else None
        ))

    return modelos_response

@app.post("/modelo/", response_model=ModeloList)
def create_modelo(modelo: Modelo):
    result = db.modelo.insert_one(modelo.dict())
    inserted_id = str(result.inserted_id)

    return ModeloList(
        id=inserted_id,
        id_marca=modelo.id_marca,
        nome=modelo.nome,
    )

@app.get("/modelo/{modelo_id}", response_model=ModeloResponse)
def get_modelo(modelo_id: str):
    modelo = db.modelo.find_one({"_id": ObjectId(modelo_id)})

    if not modelo:
        raise HTTPException(status_code=404, detail=f"Modelo with ID {modelo_id} not found")

    # Obter informações da marca associada ao modelo
    id_marca = modelo.get("id_marca")
    marca_info = None

    if id_marca:
        marca_info = db.marca.find_one({"_id": ObjectId(id_marca)})

    return ModeloResponse(
        id=str(modelo["_id"]),
        id_marca=modelo["id_marca"],
        nome=modelo["nome"],
        marca_info=Marca(**marca_info) if marca_info else None
    )

@app.put("/modelo/{modelo_id}", response_model=Modelo)
def update_modelo(modelo_id: str, updated_modelo: Modelo):
    db.modelo.update_one({"_id": ObjectId(modelo_id)}, {"$set": updated_modelo.dict()})
    return updated_modelo

@app.delete("/modelo/{modelo_id}")
def delete_modelo(modelo_id: str):
    modelo = db.modelo.find_one({"_id": ObjectId(modelo_id)})
    if modelo is None:
        raise HTTPException(status_code=404, detail="Modelo not found")
    db.modelo.delete_one({"_id": ObjectId(modelo_id)})
    return 0

#CARRO
@app.post("/carro/", response_model=CarroList)
def create_carro(carro: Carro):
    result = db.carro.insert_one(carro.dict())
    inserted_id = str(result.inserted_id)

    return CarroList(
        id=inserted_id,
        id_modelo = carro.id_modelo,
        nome=carro.nome,
        renavam = carro.renavam,
        placa = carro.placa,
        valor = carro.valor,
        ano = carro.ano,   
    )

@app.get("/carro/{carro_id}", response_model=CarroResponse)
def get_carro(carro_id: str):
    carro = db.carro.find_one({"_id": ObjectId(carro_id)})
    if carro is None:
        raise HTTPException(status_code=404, detail="Carro not found")

    id_modelo = carro.get("id_modelo")
    modelo_info = None
    marca_info = None

    if id_modelo:
        modelo_info = db.modelo.find_one({"_id": ObjectId(id_modelo)})
        if modelo_info:
            id_marca = modelo_info.get("id_marca")
            marca_info = db.marca.find_one({"_id": ObjectId(id_marca)})

    return CarroResponse(
        id=str(carro["_id"]),
        id_modelo=carro["id_modelo"],
        nome=carro["nome"],
        renavam=carro["renavam"],
        placa=carro["placa"],
        valor=carro["valor"],
        ano=carro["ano"],
        modelo_info=Modelo(**modelo_info) if modelo_info else None,
        marca_info=Marca(**marca_info) if marca_info else None
    )

@app.get("/carro/", response_model=List[CarroResponse])
def get_all_carros():
    carros = list(db.carro.find())
    carros_response = []

    for carro in carros:
        id_modelo = carro.get("id_modelo")
        modelo_info = None
        marca_info = None

        if id_modelo:
            modelo_info = db.modelo.find_one({"_id": ObjectId(id_modelo)})
            if modelo_info:
                id_marca = modelo_info.get("id_marca")
                marca_info = db.marca.find_one({"_id": ObjectId(id_marca)})

        carros_response.append(CarroResponse(
            id=str(carro["_id"]),
            id_modelo=carro["id_modelo"],
            nome=carro["nome"],
            renavam=carro["renavam"],
            placa=carro["placa"],
            valor=carro["valor"],
            ano=carro["ano"],
            modelo_info=Modelo(**modelo_info) if modelo_info else None,
            marca_info=Marca(**marca_info) if marca_info else None
        ))

    return carros_response

@app.put("/carro/{carro_id}", response_model=Carro)
def update_carro(carro_id: str, updated_carro: Carro):
    db.carro.update_one({"_id": ObjectId(carro_id)}, {"$set": updated_carro.dict()})
    return updated_carro

@app.delete("/carro/{carro_id}")
def delete_carro(carro_id: str):
    carro = db.carro.find_one({"_id": ObjectId(carro_id)})
    if carro is None:
        raise HTTPException(status_code=404, detail="Carro not found")
    db.carro.delete_one({"_id": ObjectId(carro_id)})
    return 0