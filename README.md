# Sistema de Gestión de Cotizaciones Quirúrgicas

## Estructura del Proyecto

```
backend/
├── app/
│   ├── api/
│   │   └── endpoints.py      # Rutas de la API
│   ├── core/
│   │   └── config.py        # Configuración de la aplicación
│   ├── models/
│   │   └── quote.py         # Modelos Pydantic
│   ├── services/
│   │   ├── database_service.py  # Servicios de base de datos
│   │   └── pdf_service.py       # Servicios de procesamiento PDF
│   └── main.py              # Punto de entrada de la aplicación
├── requirements.txt         # Dependencias
└── .env                    # Variables de entorno

frontend/
├── public/                 # Archivos estáticos
├── src/
│   ├── components/         # Componentes React
│   │   └── ui/            # Componentes de UI reutilizables
│   ├── hooks/             # Hooks personalizados
│   ├── lib/               # Utilidades y funciones auxiliares
│   ├── services/          # Servicios de API
│   ├── App.jsx           # Componente principal
│   └── index.jsx         # Punto de entrada
├── package.json          # Dependencias y scripts
└── vite.config.js       # Configuración de Vite
```

## Características Principales

### Backend (FastAPI)

1. API RESTful para la gestión de cotizaciones quirúrgicas
2. Procesamiento automático de PDFs para extraer información
3. Integración con MongoDB para almacenamiento de datos
4. Sugerencias de precios basadas en datos históricos
5. Dashboard con estadísticas y métricas

### Frontend (React + Vite)

1. Interfaz moderna y responsive
2. Componentes UI reutilizables
3. Gestión de estado eficiente
4. Integración con la API del backend
5. Visualización de datos y estadísticas

## Configuración del Entorno

### Backend

#### Desarrollo Local

1. Crear un entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

2. Instalar dependencias:
```bash
pip install -r requirements.txt
```

3. Copiar `.env.example` a `.env` y configurar las variables:
```bash
cp .env.example .env
```

4. Ejecutar el servidor:
```bash
uvicorn main:app --reload
```

#### Usando Docker

1. Construir la imagen:
```bash
docker build -t zafir-api .
```

2. Ejecutar el contenedor:
```bash
docker run -p 8000:8000 --env-file .env zafir-api
```

### Despliegue en Render.com

1. Crear una nueva Web Service en Render.com
2. Conectar con el repositorio de GitHub
3. Configurar las variables de entorno:
   - `PORT`: 8000
   - `ENVIRONMENT`: production
   - `DATABASE_URL`: URL de tu base de datos
   - `FRONTEND_URL`: URL de tu frontend en producción
   - `SECRET_KEY`: Clave secreta para JWT
4. Configurar el build command:
   ```bash
   pip install -r requirements.txt
   ```
5. Configurar el start command:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port $PORT
   ```

### Frontend

1. Instalar dependencias:
```bash
cd frontend
npm install
```

2. Ejecutar en modo desarrollo:
```bash
npm run dev
```

## API Endpoints

- `GET /api/` - Información del sistema
- `POST /api/upload-pdf` - Procesar cotización desde PDF
- `POST /api/quotes` - Crear nueva cotización
- `GET /api/quotes` - Listar cotizaciones
- `GET /api/quotes/{id}` - Obtener cotización específica
- `PUT /api/quotes/{id}` - Actualizar cotización
- `DELETE /api/quotes/{id}` - Eliminar cotización
- `GET /api/pricing-suggestions/{procedure}` - Obtener sugerencias de precios
- `GET /api/procedures` - Listar procedimientos únicos
- `GET /api/surgeons` - Listar cirujanos únicos
- `GET /api/dashboard` - Estadísticas del dashboard
