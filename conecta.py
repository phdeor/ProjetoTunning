import psycopg2
import redis
from pymongo import MongoClient

def conectar_postgres():
    try:
        return psycopg2.connect(
            host="localhost",
            database="supermercado_db",
            user="postgres",
            password="sua_senha_aqui",
            port="5432"
        )
    except Exception as e:
        print(f"Erro no Postgres: {e}")
        return None

def conectar_mongo():
    try:
        uri = "mongodb+srv://admin_fei:grupofoda123@cluster0.ytfqci2.mongodb.net/?appName=Cluster0"
        cliente = MongoClient(uri) 
        
        # O teste visual para você ter certeza que plugou no Atlas
        db = cliente.supermercado_db
        print("Conectado ao MongoDB! Coleções disponíveis:", db.list_collection_names())
        
        # Devolvemos a conexão bruta, mantendo o mesmo estilo do Redis
        return cliente 
        
    except Exception as e:
        print(f"Erro no Mongo: {e}")
        return None

def conectar_redis():
    try:
        # Conectando no seu Redis Cloud
        r = redis.Redis(
            host='redis-13656.crce196.sa-east-1-2.ec2.cloud.redislabs.com',
            port=13656, 
            password='V2ND0fxW3ulJfhkZV2ByAsYnr5ZM9s0g', 
            decode_responses=True
        )
        print("Deu certo a conexão com o Redis Cloud!")
        return r # O return SEMPRE fica por último
    except Exception as e:
        print(f"Erro no Redis: {e}")
        return None