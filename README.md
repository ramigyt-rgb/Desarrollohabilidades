# Learning OS PRO

Sistema personal de aprendizaje en Streamlit.

## Incluye
- Login y usuarios locales seguros.
- Onboarding por habilidad.
- Piano, Programación, Inglés y Aviación.
- Ruta de aprendizaje por etapas.
- Dashboard con progreso, XP, nivel y streak.
- Check-in diario.
- Ejercicios y sesiones de práctica.
- Exámenes con corrección automática.
- Tutor IA contextual.
- Objetivos semanales.
- Biblioteca de módulos.
- Historial y analítica.
- Persistencia SQLite.

## Instalación en Windows

1. Abrí la carpeta del proyecto en VS Code.
2. Abrí Terminal > New Terminal.
3. Creá un entorno virtual:

```bash
python -m venv .venv
```

4. Activarlo:

```bash
.venv\Scripts\activate
```

5. Instalá dependencias:

```bash
pip install -r requirements.txt
```

6. Ejecutá:

```bash
streamlit run app.py
```

## Primer ingreso

La primera pantalla permite crear tu propia cuenta. No hay usuario ni contraseña predefinidos.

## Tutor IA real opcional

La app ya funciona sin API con un tutor pedagógico local.

Para conectar un LLM:
1. Creá `.streamlit/secrets.toml`
2. Agregá:

```toml
LLM_API_KEY = "tu_clave"
LLM_BASE_URL = "https://tu-endpoint/v1"
LLM_MODEL = "tu-modelo"
```

El endpoint debe aceptar `POST /chat/completions` con formato compatible con OpenAI.

## Datos

El archivo `learning_os.db` se crea automáticamente en la misma carpeta.


## Versión GitHub/iPhone

Esta edición no usa la carpeta `assets/`.
Las 24 figuras PPA están embebidas en `ppa_assets.py`, por lo que todos los
archivos necesarios pueden subirse directamente a la raíz del repositorio.
