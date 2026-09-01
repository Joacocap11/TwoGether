# TwoGether

Registro privado y compartido de experiencias de Joaquín (Joaco) y Selena. El MVP permite guardar visitas a lugares de comida, puntuaciones individuales, platos, tests con capturas y un dashboard resumido.

## Arquitectura

Monorepo con una API FastAPI, frontend React + TypeScript y PostgreSQL, orquestados por Docker Compose. La API está versionada bajo `/api/v1`, usa SQLAlchemy/Alembic y JWT. Los archivos se almacenan en un volumen Docker local; no se usa S3 ni WireGuard dentro de la aplicación.

## Requisitos

- Docker Desktop con Compose v2
- Para desarrollo separado: Python 3.12+, Node.js 20+

## Inicio rápido con Docker

```bash
copy .env.example .env
# Edita .env y cambia POSTGRES_PASSWORD y JWT_SECRET_KEY
docker compose up -d --build
```

- Frontend: http://localhost:5173
- API y Swagger: http://localhost:8000/docs
- Health: http://localhost:8000/health

El contenedor de API ejecuta `alembic upgrade head` antes de arrancar. PostgreSQL y uploads sobreviven mediante volúmenes (`postgres_data` y `uploads`).

## Configuración

Variables principales en `.env`:

| Variable | Uso |
| --- | --- |
| `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_HOST`, `POSTGRES_PORT` | Componentes de conexión PostgreSQL; la API construye `DATABASE_URL` y codifica la contraseña |
| `JWT_SECRET_KEY` | Secreto para firmar tokens; usar uno aleatorio en despliegue |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | Duración del access token |
| `CORS_ORIGINS` | Orígenes permitidos separados por coma |
| `VITE_API_URL` | URL pública de la API para el frontend |
| `API_PORT`, `FRONTEND_PORT` | Puertos publicados localmente |
| `UPLOAD_MAX_SIZE_BYTES` | Tamaño máximo de imágenes |

`.env` y secretos no se versionan. Usa `.env.example` como plantilla.

## Usuarios iniciales

Crear las dos cuentas con el comando de seed documentado por la API:

```bash
docker compose exec api python seed.py
```

El seed es idempotente. Usa `INITIAL_JOACO_EMAIL`, `INITIAL_JOACO_PASSWORD`, `INITIAL_SELENA_EMAIL` e `INITIAL_SELENA_PASSWORD` únicamente desde `.env` privado. Informa qué usuarios creó y cuáles ya existían. El registro HTTP está deshabilitado por defecto (`REGISTRATION_ENABLED=false`).


## Backup básico

Realiza copias periódicas de la base de datos y del volumen de uploads:

```bash
docker compose run --rm -e TESTING=true -e DATABASE_URL=sqlite:///./test_twogether.db -e REGISTRATION_ENABLED=true api pytest
```

Restaura ambos elementos únicamente con los servicios detenidos o siguiendo el procedimiento de mantenimiento de tu servidor. WireGuard y el acceso desde Proxmox son responsabilidad de la infraestructura externa.

La interfaz web cubre login, dashboard con datos reales, formulario único de salida compartida con datos de Joaco y Selena, puntuaciones de plato y lugar, opiniones, fotos independientes y collages CSS. Tests usan un único formulario con nombre, fecha, dos capturas y notas opcionales; no requieren resultados textuales. Los promedios de plato y lugar se calculan dinámicamente. No se incluyen funcionalidades fuera del MVP.
## Desarrollo

Backend separado:

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

Frontend separado:

```bash
cd frontend
npm install
npm run dev
```

El frontend usa `VITE_API_URL` y por defecto apunta a `http://localhost:8000/api/v1`.

Migraciones:

```bash
alembic revision --autogenerate -m "describe change"
alembic upgrade head
```

Calidad:

```bash
cd backend && pytest
cd backend && ruff check .
cd frontend && npm run lint
cd frontend && npm run build
```

## Despliegue básico

En la VM/LXC de aplicaciones, copia el repositorio y un `.env` privado, configura un dominio/reverse proxy externo si corresponde y ejecuta `docker compose up -d --build`. Publica únicamente el frontend y la API necesarios; no publiques PostgreSQL. Usa secretos largos y backups de los volúmenes de PostgreSQL/uploads.

## Modelo y reglas

Una visita (`PlaceVisit`) tiene muchos platos (`Dish`) y ratings (`UserRating`) relacionados con los dos usuarios compartidos. `UserRating.comment` es la única opinión libre por persona. `TestOutcome` guarda una captura opcional por usuario; los campos textuales de resultado se mantienen nullable únicamente para compatibilidad histórica y ya no se usan en el flujo actual. Los promedios de plato y lugar se calculan dinámicamente y nunca se persisten.

## Fuera del alcance

No incluye app móvil, notificaciones, mapas avanzados/geolocalización, redes sociales/chat, IA/OCR, importación/exportación masiva, gamificación, reservas, recomendaciones ni estadísticas avanzadas/ Wrapped.

## Branding

Los assets oficiales de TwoGether viven en `frontend/public/branding/`. El símbolo y sus derivados se sirven desde rutas públicas de Vite/Nginx; no dependen de la carpeta Descargas. La paleta principal es crema `#F7F3EA`, azul `#284B63` y amarillo `#E7B84B`.
