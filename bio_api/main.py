from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from . import models, schemas, crud, database
import csv
import io
from datetime import datetime


# generate tables
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="BioTrack API", version="1.0")


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/observacoes/", response_model=schemas.ObservacaoResponse)
def create_observacao(observacao: schemas.ObservacaoCreate, db: Session = Depends(get_db)):
    return crud.create_observacao(db=db, observacao=observacao)

@app.get("/observacoes/", response_model=list[schemas.ObservacaoResponse])
def listar_observacoes(db: Session = Depends(get_db)):
    return crud.get_observacoes(db)

@app.get("/observacoes/{observacao_id}", response_model=schemas.ObservacaoResponse)
def get_observacao(observacao_id: int, db: Session = Depends(get_db)):
    db_observacao = crud.get_observacao(db, observacao_id=observacao_id)
    if not db_observacao:
        raise HTTPException(status_code=404, detail="Note not found")
    return db_observacao

@app.post("/import")
async def importar_observacoes(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Import observation records from a CSV file.
    The CSV file must contain the following columns:
    species, type, location, datetime, temperature, humidity, observer
    """

    content = await file.read()
    decoded = content.decode("utf-8")
    csv_reader = csv.DictReader(io.StringIO(decoded))

    imported = 0
    for row in csv_reader:
        try:
            observacao_data = schemas.ObservacaoCreate(
                especie=row["especie"],
                tipo=row["tipo"],
                localizacao=row["localizacao"],
                data_hora=datetime.fromisoformat(row["data_hora"]),
                condicoes={
                    "temperatura": float(row.get("temperatura", 0)),
                    "umidade": float(row.get("umidade", 0))
                },
                observador=row["observador"]
            )

            crud.create_observacao(db=db, observacao=observacao_data)
            imported += 1

        except Exception as e:
            print(f"Error importing line: {row} → {e}")

    return {"message": f"{imported} observations imported successfully."}