# FastAPI + MongoDB Atlas CRUD

## Panoramica del progetto

Questo progetto implementa una CRUD completa per la gestione di utenti utilizzando FastAPI come framework backend, MongoDB Atlas come database cloud, PyMongo come driver Python per la connessione a MongoDB e MongoDB Compass come interfaccia grafica per l’ispezione e la gestione dei dati.

L’obiettivo del progetto non è soltanto fornire un insieme di endpoint funzionanti, ma anche definire una struttura ordinata e professionale che possa essere compresa, estesa e mantenuta facilmente da un team di sviluppo. Il progetto è stato organizzato separando chiaramente configurazione, accesso al database, serializzazione dei documenti, repository e router HTTP.

In questo scenario il database non gira in locale. Il database è ospitato su MongoDB Atlas, quindi tutti i componenti del sistema, compresi Compass e l’applicazione FastAPI, si collegano a un cluster remoto tramite connection string.

---

## Obiettivi didattici e tecnici

Questo progetto permette di comprendere:

- come creare e configurare un cluster MongoDB Atlas
- come autorizzare gli accessi tramite IP access list
- come creare un database user per autenticare applicazioni e client
- come utilizzare MongoDB Compass per creare database, collection e documenti
- come configurare un backend Python con FastAPI
- come connettere FastAPI a MongoDB Atlas tramite PyMongo
- come organizzare una CRUD secondo una struttura di progetto pulita
- come testare gli endpoint tramite Swagger UI
- come osservare in Compass gli effetti delle operazioni CRUD eseguite dall’API

---

## Stack tecnologico

Il progetto utilizza i seguenti strumenti:

- Python
- FastAPI
- Uvicorn
- PyMongo
- MongoDB Atlas
- MongoDB Compass
- python-dotenv
- Pydantic

MongoDB documenta PyMongo come driver ufficiale Python e pubblica anche guide dedicate all’integrazione con FastAPI. Compass è la GUI ufficiale per l’esplorazione e la manipolazione dei dati MongoDB. 

---

## Architettura logica del progetto

L’applicazione segue una separazione delle responsabilità semplice ma efficace.

La configurazione è centralizzata in un modulo dedicato.  
La connessione al database è definita in un punto unico.  
Gli schemi di input e output sono definiti separatamente tramite Pydantic.  
L’accesso ai dati è incapsulato in un repository.  
Gli endpoint HTTP sono raccolti in router modulari.

Questa suddivisione permette di evitare codice disperso e di mantenere il progetto facilmente evolvibile.

---

## Struttura delle cartelle

```text
fastapi-mongo-atlas-crud/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py
│   ├── db/
│   │   ├── __init__.py
│   │   └── mongodb.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── serializers.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── user_schema.py
│   ├── repositories/
│   │   ├── __init__.py
│   │   └── user_repository.py
│   └── routers/
│       ├── __init__.py
│       └── user_router.py
│
├── .env
├── .gitignore
└── requirements.txt
Prerequisiti

Prima di avviare il progetto è necessario disporre di:

Python installato sulla macchina
un account MongoDB Atlas
un cluster MongoDB Atlas attivo
un database user creato su Atlas
l’IP del proprio ambiente autorizzato nella IP access list del cluster
MongoDB Compass installato in locale

Per collegarsi a un cluster Atlas non basta conoscere l’URI: Atlas richiede che sia presente un database user e che l’IP client sia autorizzato nella IP access list. La connection string si recupera dal pannello Connect del cluster.

1. Creazione e configurazione del cluster MongoDB Atlas
1.1 Creazione account e project

Accedere a MongoDB Atlas e creare un account. Una volta effettuato l’accesso, creare un nuovo project che conterrà il cluster del progetto.

1.2 Creazione del cluster

All’interno del project, creare un cluster Atlas. Per un ambiente di studio o sviluppo iniziale è sufficiente un cluster base.

1.3 Creazione del database user

Dal pannello di sicurezza di Atlas, creare un database user. Questo utente sarà usato da:

MongoDB Compass
applicazione FastAPI
eventuali altri client applicativi

È importante conservare username e password, perché saranno necessari nella connection string.

1.4 Configurazione IP access list

Dal pannello Network Access aggiungere l’IP pubblico della macchina da cui ci si collega. Senza questo passaggio il cluster rifiuterà le connessioni.

1.5 Recupero connection string

Aprire il cluster e premere su Connect. Da lì copiare la connection string di tipo mongodb+srv://....

Esempio generico:

mongodb+srv://USERNAME:PASSWORD@CLUSTER_URL/?retryWrites=true&w=majority&appName=Cluster0
2. Installazione e utilizzo di MongoDB Compass

MongoDB Compass è la GUI ufficiale di MongoDB e permette di collegarsi al cluster, creare database e collection, esplorare documenti, eseguire query e osservare gli effetti delle operazioni CRUD. La documentazione ufficiale distingue anche le edizioni full, read-only e isolated; per sviluppo ordinario va usata la full edition.

2.1 Installazione

Scaricare e installare MongoDB Compass dal sito ufficiale MongoDB, scegliendo la versione adatta al proprio sistema operativo.

2.2 Connessione al cluster Atlas

Aprire Compass e incollare la connection string copiata da Atlas. Sostituire, se necessario, username e password con le credenziali corrette del database user.

2.3 Creazione del database e della collection

Una volta connessi:

creare il database school_db
creare la collection users
2.4 Inserimento di un documento manuale di prova

All’interno della collection users è possibile inserire un documento iniziale, ad esempio:

{
  "name": "Fabio",
  "email": "fabio@example.com",
  "age": 30
}

Questo passaggio è utile per familiarizzare con la struttura documentale di MongoDB prima ancora di usare l’API.

3. Clonazione o creazione del progetto

Se il repository esiste già:

git clone <url-del-repository>
cd fastapi-mongo-atlas-crud

Se invece si vuole creare il progetto da zero:

mkdir fastapi-mongo-atlas-crud
cd fastapi-mongo-atlas-crud
4. Creazione dell’ambiente virtuale Python

È consigliato usare un ambiente virtuale per isolare le dipendenze del progetto.

Su macOS e Linux:

python3 -m venv .venv
source .venv/bin/activate

Su Windows:

python -m venv .venv
.venv\Scripts\activate
5. Installazione delle dipendenze

Installare i pacchetti necessari:

pip install fastapi "uvicorn[standard]" pymongo python-dotenv email-validator

Poi generare il file requirements.txt:

pip freeze > requirements.txt

FastAPI genera automaticamente la documentazione OpenAPI e Swagger UI; PyMongo è il driver che consente all’applicazione Python di interagire con il cluster MongoDB.

6. Configurazione del file .env

Creare nella root del progetto un file .env con questo contenuto:

MONGO_URI=mongodb+srv://USERNAME:PASSWORD@CLUSTER_URL/?retryWrites=true&w=majority&appName=Cluster0
MONGO_DB=school_db
MONGO_COLLECTION_USERS=users
Significato delle variabili

MONGO_URI
Contiene la connection string completa del cluster Atlas.

MONGO_DB
Indica il nome del database a cui collegarsi. In questo progetto è school_db.

MONGO_COLLECTION_USERS
Indica il nome della collection usata dal repository utenti. In questo progetto è users.

Nota importante

Il file .env contiene dati sensibili e non deve essere versionato nel repository.

7. File .gitignore

Creare il file .gitignore con il seguente contenuto:

.venv/
__pycache__/
*.pyc
.env

In questo modo si evitano commit accidentali di file temporanei, bytecode Python e configurazione sensibile.

8. Spiegazione dei file del progetto
8.1 app/core/config.py

Questo file centralizza la lettura delle variabili di ambiente e rende disponibile la configurazione al resto del progetto.

import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB", "school_db")
MONGO_COLLECTION_USERS = os.getenv("MONGO_COLLECTION_USERS", "users")

if not MONGO_URI:
    raise ValueError("MONGO_URI non configurata nel file .env")

La sua funzione è evitare di duplicare valori di configurazione in più punti del codice.

8.2 app/db/mongodb.py

Questo modulo definisce la connessione a MongoDB Atlas tramite MongoClient e rende disponibile il database selezionato.

from pymongo import MongoClient
from app.core.config import MONGO_URI, MONGO_DB

client = MongoClient(MONGO_URI)
database = client[MONGO_DB]

def get_database():
    return database

Il MongoClient è il punto di ingresso standard del driver PyMongo.

8.3 app/schemas/user_schema.py

Questo file contiene gli schemi Pydantic utilizzati da FastAPI per validare i dati in ingresso e definire i modelli di output.

from pydantic import BaseModel, EmailStr
from typing import Optional

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    age: int

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    age: Optional[int] = None

class UserResponse(BaseModel):
    id: str
    name: str
    email: EmailStr
    age: int

Questa separazione permette di distinguere chiaramente il payload di creazione, quello di aggiornamento e la struttura restituita dall’API.

8.4 app/models/serializers.py

MongoDB salva gli identificativi nel campo _id e li rappresenta come ObjectId. Questo serializer converte il documento MongoDB in un dizionario più adatto all’esposizione HTTP.

def user_serializer(user: dict) -> dict:
    return {
        "id": str(user["_id"]),
        "name": user["name"],
        "email": user["email"],
        "age": user["age"]
    }
8.5 app/repositories/user_repository.py

Il repository incapsula tutte le operazioni CRUD sulla collection users.

from bson import ObjectId
from app.db.mongodb import get_database
from app.core.config import MONGO_COLLECTION_USERS

class UserRepository:
    def __init__(self):
        self.collection = get_database()[MONGO_COLLECTION_USERS]

    def create_user(self, user_data: dict) -> str:
        result = self.collection.insert_one(user_data)
        return str(result.inserted_id)

    def get_all_users(self):
        return list(self.collection.find())

    def get_user_by_id(self, user_id: str):
        return self.collection.find_one({"_id": ObjectId(user_id)})

    def update_user(self, user_id: str, update_data: dict) -> int:
        result = self.collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": update_data}
        )
        return result.modified_count

    def delete_user(self, user_id: str) -> int:
        result = self.collection.delete_one({"_id": ObjectId(user_id)})
        return result.deleted_count

Qui avviene il dialogo effettivo con MongoDB tramite PyMongo. Le primitive usate sono quelle standard del driver: insert_one, find, find_one, update_one, delete_one.

8.6 app/routers/user_router.py

Il router espone i metodi del repository come endpoint HTTP.

from fastapi import APIRouter, HTTPException
from app.schemas.user_schema import UserCreate, UserUpdate
from app.repositories.user_repository import UserRepository
from app.models.serializers import user_serializer

router = APIRouter(prefix="/users", tags=["users"])
repo = UserRepository()

@router.post("/")
def create_user(payload: UserCreate):
    user_id = repo.create_user(payload.model_dump())
    user = repo.get_user_by_id(user_id)
    return user_serializer(user)

@router.get("/")
def get_users():
    users = repo.get_all_users()
    return [user_serializer(user) for user in users]

@router.get("/{user_id}")
def get_user(user_id: str):
    user = repo.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user_serializer(user)

@router.put("/{user_id}")
def update_user(user_id: str, payload: UserUpdate):
    update_data = {k: v for k, v in payload.model_dump().items() if v is not None}
    user = repo.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    repo.update_user(user_id, update_data)
    updated_user = repo.get_user_by_id(user_id)
    return user_serializer(updated_user)

@router.delete("/{user_id}")
def delete_user(user_id: str):
    deleted = repo.delete_user(user_id)
    if deleted == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}
8.7 app/main.py

Questo file è il punto di ingresso dell’applicazione FastAPI.

from fastapi import FastAPI
from app.routers.user_router import router as user_router

app = FastAPI(
    title="FastAPI MongoDB Atlas CRUD",
    version="1.0.0"
)

app.include_router(user_router)

@app.get("/")
def root():
    return {"message": "API attiva"}
9. Avvio del progetto

Una volta creati i file e configurato il .env, avviare il server di sviluppo:

uvicorn app.main:app --reload

L’opzione --reload permette il riavvio automatico del server a ogni modifica del codice, utile durante lo sviluppo.

10. Documentazione interattiva

FastAPI genera automaticamente la documentazione Swagger UI.

Una volta avviato il server, aprire:

http://127.0.0.1:8000/docs

Da questa interfaccia è possibile testare tutti gli endpoint senza usare strumenti esterni. FastAPI documenta nativamente la generazione automatica di OpenAPI e Swagger UI.

11. Endpoint disponibili
GET /

Endpoint di controllo base per verificare che l’applicazione sia attiva.

Risposta tipica:

{
  "message": "API attiva"
}
POST /users/

Crea un nuovo utente.

Esempio payload:

{
  "name": "Fabio",
  "email": "fabio@example.com",
  "age": 30
}
GET /users/

Restituisce tutti gli utenti presenti nella collection.

GET /users/{user_id}

Restituisce un singolo utente identificato dal suo id.

PUT /users/{user_id}

Aggiorna parzialmente o totalmente i dati di un utente.

Esempio payload:

{
  "email": "fabio.dev@example.com"
}
DELETE /users/{user_id}

Elimina l’utente identificato dal relativo id.

12. Flusso completo di lavoro

Il flusso corretto di utilizzo del progetto è il seguente.

Per prima cosa si configura MongoDB Atlas creando cluster, database user e accesso IP.
Successivamente si collega MongoDB Compass al cluster per creare database e collection.
Poi si configura il backend tramite file .env, che contiene la connection string.
Infine si avvia FastAPI, si testano gli endpoint tramite /docs e si osservano in Compass le modifiche ai documenti effettuate dall’API.

Questo approccio permette di lavorare in modo trasparente su tutti i livelli del sistema: GUI, codice backend e database remoto.

13. Come osservare i dati in Compass

Dopo aver eseguito operazioni tramite gli endpoint FastAPI, aprire Compass e navigare su:

cluster Atlas
database school_db
collection users

Qui sarà possibile vedere in tempo reale i documenti creati, aggiornati o rimossi dall’API.

Questo passaggio è fondamentale per comprendere la relazione tra chiamata HTTP e persistenza dei dati nel database.

14. Problemi comuni
Errore di connessione al cluster

Le cause più frequenti sono:

IP non autorizzato nella IP access list
username o password errati del database user
connection string copiata male
cluster non disponibile
Compass non si connette

Verificare:

correttezza della connection string
presenza dell’IP nella access list
credenziali del database user
stato del cluster
L’API parte ma le query falliscono

Verificare:

variabili nel .env
nome del database
nome della collection
correttezza del serializer o dell’ObjectId
Errore su ObjectId

Se l’id passato negli endpoint non è un ObjectId valido, il repository può generare un errore. In una versione evoluta del progetto si può aggiungere una validazione preventiva.

15. Miglioramenti consigliati

Questa base è volutamente semplice, ma può essere estesa in molti modi.

Una prima estensione utile consiste nel creare un indice univoco sul campo email, così da impedire duplicati. Questo può essere fatto sia da Compass sia via codice PyMongo.

Esempio:

from app.db.mongodb import get_database
from app.core.config import MONGO_COLLECTION_USERS

db = get_database()
db[MONGO_COLLECTION_USERS].create_index("email", unique=True)

Si potrebbero poi aggiungere:

gestione degli errori PyMongo
validazione più robusta degli id
livello services separato dal repository
logging strutturato
test automatici
Dockerizzazione
autenticazione JWT
environment multipli
16. Motivi della struttura adottata

La struttura scelta non è casuale.
Mettere tutto in un singolo file renderebbe il progetto più corto, ma molto meno chiaro.
Separare responsabilità e livelli applicativi rende più semplice capire dove intervenire:

se cambia la configurazione si tocca config.py
se cambia la connessione si tocca mongodb.py
se cambia la validazione si toccano gli schema Pydantic
se cambia la logica dati si tocca il repository
se cambiano gli endpoint si toccano i router

Questa impostazione è consigliata per il lavoro in team, perché riduce confusione e conflitti.

17. Esempio di sessione di test
avviare l’applicazione con uvicorn app.main:app --reload
aprire http://127.0.0.1:8000/docs
eseguire il POST /users/
copiare l’id restituito
eseguire il GET /users/{user_id}
eseguire il PUT /users/{user_id}
eseguire il DELETE /users/{user_id}
verificare in Compass le variazioni della collection

Questo ciclo permette di verificare tutta la CRUD end-to-end.