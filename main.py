from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date
from uuid import uuid4, UUID

app = FastAPI(
    title="Transport Maintenance Service",
    description="API для обработки заявок на техническое обслуживание подвижного состава (Вариант 1)",
    version="1.0.0"
)

class MaintenanceRequestCreate(BaseModel):
    train_number: str = Field(..., description="Номер и серия подвижного состава")
    maintenance_type: str = Field(..., description="Вид ТО (например, ТО-1, ТО-2)")
    desired_date: date = Field(..., description="Желаемая дата постановки на ТО")
    comments: Optional[str] = Field(None, description="Дополнительные замечания")

class MaintenanceRequestResponse(MaintenanceRequestCreate):
    id: UUID = Field(..., description="Уникальный идентификатор заявки")
    status: str = Field(..., description="Статус заявки (принята, запланирована и т.д.)")

db: List[MaintenanceRequestResponse] = []

@app.get("/api/v1/routes/", response_model=List[MaintenanceRequestResponse], status_code=status.HTTP_200_OK)
def get_all_requests():
    return db

@app.get("/api/v1/routes/{request_id}", response_model=MaintenanceRequestResponse, status_code=status.HTTP_200_OK)
def get_request_by_id(request_id: UUID):
    for req in db:
        if req.id == request_id:
            return req
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Заявка не найдена")

@app.post("/api/v1/routes/", response_model=MaintenanceRequestResponse, status_code=status.HTTP_201_CREATED)
def create_request(request: MaintenanceRequestCreate):
    if not request.train_number.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Номер подвижного состава не может быть пустым")
    new_request = MaintenanceRequestResponse(
        id=uuid4(),
        status="принята",
        **request.model_dump()
    )
    db.append(new_request)
    return new_request

@app.delete("/api/v1/routes/{request_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_request(request_id: UUID):
    global db
    for i, req in enumerate(db):
        if req.id == request_id:
            db.pop(i)
            return
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Заявка не найдена")