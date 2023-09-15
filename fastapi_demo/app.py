from fastapi import FastAPI, HTTPException
from typing import Any
from mongita import MongitaClientDisk
from pydantic import BaseModel

class Shape(BaseModel):
    name:str
    no_of_sides: int
    id: int

app = FastAPI()

client = MongitaClientDisk()
db = client.db
shapes = db.shapes

@app.get("/")
async def root():
    return {"message": "Hello world"}


@app.get("/shapes")
async def get_shapes():
    exisisting_shapes = shapes.find({})
    return [
        {key:shape[key] for key in shape if key != "_id"}
        for shape in exisisting_shapes
    ]


@app.get("/shapes/{shape_id}")
async def get_shape_by_id(shape_id: int):
    if shapes.count_documents({'id':shape_id}) > 0:
        shape = shapes.find_one({'id':shape_id})
        return {key:shape[key] for key in shape if key != "_id"}
    raise HTTPException(status_code=404, detail=f"no shape with id {shape_id} found")

@app.post('/shapes')
async def post_shape(shape: Shape):
    shapes.insert_one(shape.model_dump())
    return shape

@app.put('/shapes/{shape_id}')
async def update_shape(shape_id:int, shape:Shape):
    if shapes.count_documents({'id':shape_id}) > 0:
        shapes.replace_one({'id':shape_id}, shape.model_dump())
        return shape
    raise HTTPException(status_code=404, detail=f"No shape with ID {shape_id}")

@app.put('/shapes/upsert/{shape_id}')
async def update_shape_upsert(shape_id:int, shape:Shape):
    if shapes.count_documents({'id':shape_id}) > 0:
        shapes.replace_one({'id':shape_id}, shape.model_dump(), upsert=True)
        return {'message': 'Shape deleted'}
    raise HTTPException(status_code=404, detail=f"No shape with ID {shape_id}")

@app.delete('/shapes/{shape_id}')
async def delete_shape(shape_id:int):
    if shapes.count_documents({'id':shape_id}) > 0:
        shapes.delete_one({'id':shape_id})
        return shapes
    raise HTTPException(status_code=404, detail=f"No shape with ID {shape_id}")
