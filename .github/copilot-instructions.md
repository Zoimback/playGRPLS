ESte proyecto trata de crear un bot para grepolis


# Desarrollo

## Estructura del proyecto
Responsabilidades:
  Módulo	Responsabilidad
  config.py	Configuración general y variables de entorno
  session.py	Login, cookies, sesión y CSRF
  game_api.py	Comunicación HTTP con Grepolis
  game_data.py	Interpretación del Backbone
  buildings.py	Información y requisitos de edificios
  construction.py	Consultas y operaciones de construcción
  farm_towns.py	Consultas y operaciones de aldeas agrícolas
  building_engine.py	Decisiones sobre qué construir
  scheduler.py	Programación y persistencia de tareas
  main.py	Orquestación de los procesos

No es obligatorio conservar exactamente esta estructura si el agente encuentra una organización mejor, pero sí mantener separadas las responsabilidades.

## GIT
Antes de realizar cualquier tipo de accion tienes que comprobar en que rama estas. Si estás en main deberas generar una rama llamada feature/{featurename}.X.Y donde X es la version actual del programa e Y es el numero de cambios realizados en esa versión.

Cuando se termine el desarrollo subiras el código y generaras una PR hacia main describiendo los cambios a traves del mcp de github y usando unicamente las herramientas delimitadas para ello. El commit deberá llevar {featurename}-X.Y

## PYTHON
El script estará completamente desarrollado en python.

Librerias permitidas:
  - Pandas
  - backtesting
  - PyTest
  - Numpy

Para desarrollar en python deberas consultar las instrucciones:
 - Desarrollo general: `.github\instructions\python.instruction.md`
 - Desarrollo test: `.github\instructions\python_test.instruction.md`
 - Desarrollos para IBKR: `.github\instructions\ibapi.instructions.md`

Para los test, deben tener una cobertura mínima del 0,80.


Para ejecutar pruebas o el test, deberaas inicializar el entorno virtual venv.


# Skill

Utiliza siempre la skill de caveman, da igual la interacción.


## Datos Grepolis
URLs de Grepolis identificadas
Estas son las direcciones que hemos utilizado durante el proceso de autenticación y consulta.
URL	Función	Estado
https://es-play.grepolis.com/	Inicializar sesión del portal	Validada
https://es-play.grepolis.com/api/login	Login central	Validada
https://es0.grepolis.com/start/index	Portal de selección de mundos	Validada
/start/index?action=login_from_start_page	Consultar mundos	Validada
/start?action=login_to_game_world	Seleccionar mundo	Validada
https://es148.grepolis.com/game/login	Transferencia al mundo	Validada
https://es148.grepolis.com/game/index	Página principal del juego	Validada
/game/data	Obtener datos del juego	Validada

Hay una distinción importante: /start/index y /start pertenecen al portal de selección, mientras que /game/data pertenece al servidor del mundo.

Proceso de autenticación HTTP
El login se realiza en seis pasos.
Paso 1. Inicializar sesión
GET https://es-play.grepolis.com/


Resultado observado:
HTTP 200


Se utiliza requests.Session() para mantener las cookies.
Paso 2. Login central
POST https://es-play.grepolis.com/api/login
Content-Type: application/json
Origin: https://es-play.grepolis.com
Referer: https://es-play.grepolis.com/


Payload:
{
  "username": "USUARIO",
  "password": "CONTRASEÑA",
  "useRememberMe": true
}


Resultado:
HTTP 200


Respuesta JSON con una propiedad:
{
  "redirectUrl": "..."
}


La URL devuelta debe utilizarse directamente, sin construirla manualmente.

Importante: descubrimos que el GET inicial y las cabeceras Origin y Referer son necesarios. Sin ellos, la nueva implementación devolvía HTTP 401.
Paso 3. Transferencia al portal
GET <redirectUrl>
Referer: https://es-play.grepolis.com/


Resultado:
HTTP 200
URL final: https://es0.grepolis.com/start/index


La respuesta contiene un formulario HTML con aproximadamente diez campos input.

Entre ellos encontramos:
- name
- password
- passwordhash
- token
- Otros campos de formulario.
El campo password puede estar vacío, mientras que passwordhash sí contiene el valor necesario para continuar.

Es importante conservar los campos duplicados del formulario.
Paso 4. Consultar mundos disponibles
Petición:
POST https://es0.grepolis.com/start/index?action=login_from_start_page


Cabeceras:
X-Requested-With: XMLHttpRequest
Content-Type: application/x-www-form-urlencoded; charset=UTF-8
Accept: text/plain, */*; q=0.01
Origin: https://es0.grepolis.com
Referer: https://es0.grepolis.com/start/index


Campo de formulario json:
{
  "name": "USUARIO",
  "password": "",
  "passwordhash": "HASH_DEL_FORMULARIO",
  "autologin": false,
  "window_size": "1920x1080"
}


Resultado observado:
HTTP 200
7 mundos recibidos
Poros encontrado
playing_on = true


El mundo se identifica por:
es148


Paso 5. Seleccionar mundo
POST https://es0.grepolis.com/start?action=login_to_game_world


Se construye el formulario conservando los campos originales y sus duplicados.

Se modifican:
world  = es148
action = login_to_game_world


Se conservan los demás campos, incluyendo passwordhash y token.

La petición debe enviarse con:
data=fields



Donde fields es una lista de tuplas, no un diccionario.

Resultado observado:
HTTP 302
Location: https://es148.grepolis.com/game/login


Paso 6. Acceder al mundo
GET https://es148.grepolis.com/game/login


Siguiendo las redirecciones:
HTTP 200
URL final: https://es148.grepolis.com/game/index


Cookies observadas por nombre:
- PHPSESSID
- autologin
- cid
- es-interop-rememberme
- logged_in
- login_startup_time
- onelps_seen_bundle
- pid
- sid
- toid
El número exacto de cookies puede variar.

Nunca debemos imprimir sus valores.
4. Token CSRF
Después de iniciar sesión, necesitamos obtener el token CSRF desde el HTML del juego.

Se han utilizado estas expresiones regulares:
patterns = [    r'"csrfToken"\s*:\s*"([^"]+)"',    r'Game\.csrfToken\s*=\s*["\']([^"\']+)["\']',    r'csrfToken\s*:\s*["\']([^"\']+)["\']',    r'csrfToken\s*=\s*["\']([^"\']+)["\']',    r'csrf_token\s*[:=]\s*["\']([^"\']+)["\']',]



La URL consultada:
GET https://es148.grepolis.com/game/index


El token se utiliza posteriormente en las peticiones a /game/data.

Es dinámico: no debe guardarse como constante ni reutilizarse indefinidamente.
5. Consulta del Backbone
Validada y funcionando
Esta es la parte más importante que hemos conseguido.

Endpoint:
POST https://es148.grepolis.com/game/data?town_id=3915&action=get&h=<CSRF>


Cabeceras:
X-Requested-With: XMLHttpRequest
Content-Type: application/x-www-form-urlencoded; charset=UTF-8
Accept: text/plain, */*; q=0.01
Origin: https://es148.grepolis.com
Referer: https://es148.grepolis.com/game/index


El cuerpo se envía como formulario, con un campo llamado json.

Payload:
{
  "types": [
    {
      "type": "backbone"
    }
  ],
  "town_id": 3915,
  "nl_init": false
}


Ejemplo de implementación:
import jsonimport requestsurl = (    "https://es148.grepolis.com/game/data"    "?town_id=3915"    "&action=get"    "&h=TOKEN_CSRF")payload = {    "types": [{"type": "backbone"}],    "town_id": 3915,    "nl_init": False}response = session.post(    url,    data={"json": json.dumps(payload)},    headers={        "X-Requested-With": "XMLHttpRequest",        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",        "Accept": "text/plain, */*; q=0.01",        "Origin": "https://es148.grepolis.com",        "Referer": "https://es148.grepolis.com/game/index",    },    timeout=30,)response.raise_for_status()data = response.json()



La variable session debe ser la misma requests.Session que utilizamos durante el login.
Estructura de la respuesta
En la consulta que validamos, la respuesta tenía estas propiedades principales:
{    "backbone": {...},    "benchmarks": {...},    "t_token": "...",    "notifications": {...},    "next_fetch_in": ...}



El Backbone contenía:
backbone = data["backbone"]models = backbone["models"]collections = backbone["collections"]benchmarks = backbone["benchmarks"]



Se encontraron 23 modelos en aquella consulta.

El tamaño de la respuesta fue aproximadamente 378 KB.

No debemos asumir que siempre habrá 23 modelos: hay que recorrerlos dinámicamente.
6. Información de la ciudad que ya sabemos extraer
La interpretación del Backbone nos permitió obtener cuatro bloques principales.
Recursos
town["resources"]



Ejemplo de estructura:
{    "wood": 854.0,    "stone": 789.0,    "iron": 2149.0}



Producción
town["production"]



Ejemplo:
{    "wood": 196.0,    "stone": 228.0,    "iron": 196.0}



Los valores anteriores son una fotografía de una sesión concreta, no los valores actuales.
Población
  town["population"]



Ejemplo:
  {    "max": 356.0,    "blocked": 265.0}



Edificios
town["buildings"]



La estructura contiene información como:
{    "main": {        "can_upgrade": True,        "level": 7,        "next_level": 8,        "enough_resources": True,        "resources_for": {            "wood": 525,            "stone": 385,            "iron": 239        },        "population_for": 4,        "population_free": 4,        "missing_dependencies": [],        "building_time": "00:30:30"    }}



Campos especialmente importantes:
  Campo	Significado
  can_upgrade	Si el servidor permite ampliar el edificio
  level	Nivel actual
  next_level	Nivel siguiente
  enough_resources	Si hay recursos suficientes
  resources_for	Coste de ampliación
  population_for	Población requerida
  population_free	Población libre
  missing_dependencies	Dependencias pendientes
  building_time	Duración de la ampliación

Estos campos son los que utilizaremos para el motor de decisión.
7. Cómo guardar y analizar el Backbone
Para guardar la respuesta completa:
import jsonwith open("backbone.json", "w", encoding="utf-8") as file:    json.dump(        data,        file,        ensure_ascii=False,        indent=2    )



Para inspeccionar los modelos:
models = data["backbone"]["models"]for index, model in enumerate(models):    print(f"\nModelo {index}")    print("Claves:", model.keys())    if isinstance(model.get("data"), dict):        print("Datos:", model["data"].keys())



Para buscar propiedades relacionadas con construcción:
keywords = [    "building",    "construction",    "queue",    "order",    "finish",    "remaining",    "time"]for index, model in enumerate(models):    text = json.dumps(model, ensure_ascii=False).lower()    matches = [word for word in keywords if word in text]    if matches:        print(index, matches)



Esto sirve como primera exploración, pero no demuestra por sí solo que hayamos encontrado la cola de construcción.
