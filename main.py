from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from uuid import uuid4
from threading import Lock

app = FastAPI()

# Modelo para representar a un cliente en la cola
class Client(BaseModel):
    id: str
    name: str
    priority: Optional[int] = 0  # Prioridad opcional, por defecto 0

# Cola en memoria
queue: List[Client] = []
lock = Lock()  # Para evitar conflictos en accesos concurrentes

@app.post("/join_queue/", response_model=Client)
def join_queue(name: str, priority: Optional[int] = 0):
    """Agregar un cliente a la cola."""
    with lock:
        client = Client(id=str(uuid4()), name=name, priority=priority)
        queue.append(client)
        # Ordenar por prioridad (opcional)
        queue.sort(key=lambda x: x.priority, reverse=True)
    return client

@app.get("/get_queue/", response_model=List[Client])
def get_queue():
    """Obtener el estado actual de la cola."""
    return queue

@app.post("/process_next/")
def process_next():
    """Procesar el siguiente cliente en la cola."""
    with lock:
        if not queue:
            raise HTTPException(status_code=404, detail="No hay clientes en la cola.")
        client = queue.pop(0)  # Tomar al primer cliente
    return {"message": f"Cliente {client.name} procesado.", "client": client}

@app.delete("/remove_client/{client_id}")
def remove_client(client_id: str):
    """Eliminar un cliente específico de la cola."""
    with lock:
        global queue
        queue = [client for client in queue if client.id != client_id]
    return {"message": f"Cliente con ID {client_id} eliminado."}

@app.get("/queue_size/")
def queue_size():
    """Obtener el tamaño de la cola."""
    return {"size": len(queue)}
