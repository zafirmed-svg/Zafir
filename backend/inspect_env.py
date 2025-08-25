import os,traceback
from dotenv import load_dotenv

# load .env in case script is run directly (PowerShell doesn't auto-load .env)
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

print('ENV POSTGRES_HOST:', repr(os.getenv('POSTGRES_HOST')))
print('ENV POSTGRES_PORT:', repr(os.getenv('POSTGRES_PORT')))
print('ENV POSTGRES_DB:', repr(os.getenv('POSTGRES_DB')))
print('ENV POSTGRES_USER:', repr(os.getenv('POSTGRES_USER')))
pw = os.getenv('POSTGRES_PASSWORD')
print('ENV POSTGRES_PASSWORD repr:', repr(pw))
try:
    print('PW bytes:', pw.encode('utf-8'))
except Exception as e:
    print('encode error:', e)

try:
    import psycopg2
    # ensure libpq returns UTF-8 encoded messages
    os.environ.setdefault('PGCLIENTENCODING', 'UTF8')
    conn = psycopg2.connect(host=os.getenv('POSTGRES_HOST'), port=os.getenv('POSTGRES_PORT'), dbname=os.getenv('POSTGRES_DB'), user=os.getenv('POSTGRES_USER'), password=pw)
    print('CONNECTED OK')
    conn.close()
except Exception:
    traceback.print_exc()
