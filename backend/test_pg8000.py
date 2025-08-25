import os
from pg8000 import dbapi
print('env:', os.getenv('POSTGRES_HOST'), os.getenv('POSTGRES_PORT'), os.getenv('POSTGRES_DB'))
try:
    conn = dbapi.connect(host=os.getenv('POSTGRES_HOST') or 'localhost', port=int(os.getenv('POSTGRES_PORT') or 5432), database=os.getenv('POSTGRES_DB') or 'zafir_db', user=os.getenv('POSTGRES_USER') or 'postgres', password=os.getenv('POSTGRES_PASSWORD') or '')
    print('pg8000 connected')
    conn.close()
except Exception as e:
    print('pg8000 error:', e)
