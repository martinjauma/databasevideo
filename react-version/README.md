# Guía de Inicio - Data App v2 (React + FastAPI)

Esta carpeta contiene la nueva versión de la aplicación. Se ha separado en un **Frontend** (React) y un **Backend** (FastAPI) para asegurar la máxima estabilidad y rendimiento.

---

## 🚀 Paso 1: Configuración del Backend (FastAPI)

El backend maneja la lógica de las herramientas, la conexión a MongoDB y la autenticación.

1.  **Navegar a la carpeta:**
    ```bash
    cd react-version/backend
    ```
2.  **Crear y activar un entorno virtual (Recomendado):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # En Mac/Linux
    ```
3.  **Instalar dependencias:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Configurar Variables de Entorno:**
    Crea un archivo `.env` en `react-version/backend/` con lo siguiente:
    ```env
    MONGO_URI=tu_uri_de_mongodb
    GOOGLE_CLIENT_ID=tu_google_client_id
    SECRET_KEY=una_clave_secreta_para_jwt
    ADMINS=tu_email@gmail.com,otro_admin@gmail.com
    ```
5.  **Iniciar el servidor:**
    ```bash
    uvicorn main:app --reload
    ```
    *El backend estará disponible en `http://localhost:8000`*

---

## 💻 Paso 2: Configuración del Frontend (React)

El frontend es la interfaz de usuario moderna.

1.  **Navegar a la carpeta:**
    ```bash
    cd react-version/frontend
    ```
2.  **Instalar dependencias:**
    ```bash
    npm install
    ```
3.  **Iniciar el modo desarrollo:**
    ```bash
    npm run dev
    ```
    *La aplicación estará disponible en `http://localhost:3000`*

---

## 🛠 Estructura del Proyecto

*   `react-version/frontend/src/pages/`: Aquí se encuentran las vistas de las herramientas (ej. `LongoMatchPage.tsx`).
*   `react-version/backend/routers/`: Aquí se definen los endpoints de la API (rutas).
*   `react-version/backend/services/`: Aquí reside la lógica de negocio pura (conversiones de archivos, etc.).

---

> [!IMPORTANT]
> Asegúrate de tener el backend corriendo antes de usar las herramientas en el frontend, ya que se comunican a través de una API.
