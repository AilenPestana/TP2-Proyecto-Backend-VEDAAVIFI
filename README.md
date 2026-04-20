# Proyecto Backend — Fixture Mundial 2026
 
## Integrantes
 
- Ailen Pestaña
- Valentina Huerta
- Valentina Ruffa
- Delfina Rodriguez
- Ignacio Ayala
- Ignacio Zamparolo
- Emilia Arroyo
- Franco Requejo
- Abril Yebara
## Requisitos
 
- Python >= 3.10
- MySQL
- pip

## Cómo ejecutar
 
1. Clonar el repositorio
```bash
git clone https://github.com/AilenPestana/TP2-Proyecto-Backend-VEDAAVIFI.git
cd TP2-Proyecto-Backend-VEDAAVIFI
```
 
2. Crear entorno virtual
```bash
python3 -m venv .venv
```
 
3. Activar entorno virtual
```bash
# Linux / Mac
source .venv/bin/activate
```
 
4. Instalar dependencias
```bash
pip install -r requirements.txt
```
 
5. Crear la base de datos y correr el SQL
```bash
mysql -u root -p < mysql_db.sql
```
 
6. Configurar `database.py` con tus credenciales
```python
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "tu_password",
    "database": "mundial2026"
}
```
 
7. Ejecutar la aplicación
```bash
python3 app.py
```
 
La API queda disponible en: `http://localhost:5000`
 
## Ejemplos de uso (Postman)
 
### Crear partido
 
```
POST /partidos
Body: { "equipo_local": "Argentina", "equipo_visitante": "Brasil", "fecha": "2026-06-15", "fase": "grupos" }
```
 
### Listar partidos con filtros
 
```
GET /partidos?equipo=Argentina&fase=grupos&_limit=10&_offset=0
```
 
### Obtener detalle de un partido
 
```
GET /partidos/1
```
 
### Eliminar un partido
 
```
DELETE /partidos/1
```
 
### Modificar parcialmente un partido
 
```
PATCH /partidos/1
Body: { "fecha": "2026-06-20" }
```
 
### Cargar resultado
 
```
PUT /partidos/1/resultado
Body: { "goles_local": 2, "goles_visitante": 1 }
```
 
### Crear usuario
 
```
POST /usuarios
Body: { "nombre": "Juan Pérez", "email": "juan@example.com" }
```
 
### Listar usuarios
 
```
GET /usuarios?_limit=10&_offset=0
```
 
### Registrar predicción
 
```
POST /partidos/1/prediccion
Body: { "usuario_id": 1, "goles_local": 2, "goles_visitante": 0 }
```
 
### Consultar ranking
 
```
GET /ranking?_limit=10&_offset=0
```
 
Ejemplo de respuesta:
 
```json
{
  "ranking": [
    { "id_usuario": 1, "puntos": 6 },
    { "id_usuario": 2, "puntos": 3 }
  ],
  "_links": {
    "_first": { "href": "..." },
    "_prev": null,
    "_next": null,
    "_last": { "href": "..." }
  }
}
```
 
## Códigos de respuesta
 
- `200 OK` — respuesta exitosa
- `201 Created` — recurso creado
- `204 No Content` — operación exitosa sin contenido
- `400 Bad Request` — parámetros inválidos
- `404 Not Found` — recurso no encontrado
- `500 Internal Server Error` — error del servidor
## Supuestos
 
- Los resultados se guardan en una tabla separada (`resultados`). Si un partido no tiene fila en esa tabla, se considera que todavía no fue jugado.
- Las fases válidas son: `grupos`, `dieciseisavos`, `octavos`, `cuartos`, `semis` y `final`. Cualquier otro valor es rechazado con error 400. Se almacenan en minúsculas.
- Un usuario solo puede hacer una predicción por partido. Esto se refuerza a nivel de base de datos con una restricción `UNIQUE (partido_id, usuario_id)`.
- No se puede registrar una predicción si el partido ya tiene resultado cargado.
- El ranking se calcula comparando las predicciones con los resultados reales ya cargados. El criterio de puntaje es:
  - Resultado exacto → 3 puntos
  - Ganador o empate correcto (marcador distinto) → 1 punto
  - Resultado incorrecto → 0 puntos
- Si no hay predicciones con resultados disponibles, el endpoint `/ranking` devuelve `204 No Content`.
- No se implementó autenticación. Todos los endpoints son de acceso libre.
