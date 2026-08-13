import os
import requests

def _secrets_value(name):
    try:
        import streamlit as st
        return st.secrets.get(name, "")
    except Exception:
        return ""

def get_llm_config():
    return {
        "key": _secrets_value("LLM_API_KEY") or os.getenv("LLM_API_KEY", ""),
        "base": (_secrets_value("LLM_BASE_URL") or os.getenv("LLM_BASE_URL", "")).rstrip("/"),
        "model": _secrets_value("LLM_MODEL") or os.getenv("LLM_MODEL", ""),
    }

def local_tutor(skill, question, context):
    q = question.lower()
    focus = context.get("focus", "tu próxima práctica")
    target = context.get("target", "")
    if any(k in q for k in ["plan", "hoy", "practico", "práctico", "sesión"]):
        return (
            f"Para **{skill}**, hoy haría una sesión corta y deliberada alrededor de **{focus}**.\n\n"
            "1. Recuperación activa: explicá de memoria lo último que aprendiste.\n"
            "2. Práctica enfocada: repetí el ejercicio lentamente hasta lograr 3 ejecuciones correctas.\n"
            "3. Variación: cambiá una condición para comprobar que realmente entendiste.\n"
            "4. Cierre: anotá un error recurrente y una mejora concreta para mañana.\n\n"
            f"Objetivo personal actual: **{target or 'seguir consolidando fundamentos'}**."
        )
    if any(k in q for k in ["error", "mal", "traba", "cuesta", "difícil", "dificil"]):
        return (
            "No intentes corregir todo a la vez. Aislá **una variable**: velocidad, precisión, memoria, "
            "coordinación o comprensión. Bajá la dificultad, conseguí 3 repeticiones limpias y recién ahí "
            "volvé a subirla. Si me describís exactamente dónde falla, te lo desarmo paso a paso."
        )
    if any(k in q for k in ["examen", "evalu", "test"]):
        return (
            f"Te evaluaría en {skill} con tres capas: **recuerdo sin ayuda**, **aplicación en un caso nuevo** "
            "y **explicación con tus propias palabras**. Si dominás las tres, el conocimiento está mucho más consolidado."
        )
    return (
        f"Estoy siguiendo tu progreso en **{skill}**. Tu foco actual es **{focus}**. "
        "Respondeme con qué querés lograr, qué intentaste y dónde se rompe; con eso puedo darte una corrección "
        "mucho más precisa. Como regla: priorizá práctica activa, feedback rápido y dificultad apenas por encima "
        "de tu nivel cómodo."
    )

def ask_tutor(skill, question, context, history):
    cfg = get_llm_config()
    if not all([cfg["key"], cfg["base"], cfg["model"]]):
        return local_tutor(skill, question, context), "Tutor Smart local"

    system = f"""Sos el Tutor IA de Learning OS.
Habilidad activa: {skill}.
Objetivo: {context.get('target','')}.
Experiencia: {context.get('experience','')}.
Foco actual: {context.get('focus','')}.
Progreso: {context.get('progress','')}.
Sé exigente pero claro. No inventes datos. Enseñá con recuperación activa,
práctica deliberada, ejemplos y preguntas socráticas. Priorizá seguridad si el tema es aviación.
Respondé en español salvo que la habilidad sea Inglés y practicar inglés sea útil.
"""
    messages = [{"role":"system","content":system}]
    messages += [{"role": m["role"], "content": m["content"]} for m in history[-10:]]
    messages.append({"role":"user","content":question})
    try:
        r = requests.post(
            f"{cfg['base']}/chat/completions",
            headers={"Authorization": f"Bearer {cfg['key']}", "Content-Type":"application/json"},
            json={"model": cfg["model"], "messages": messages, "temperature": 0.45},
            timeout=40
        )
        r.raise_for_status()
        data = r.json()
        return data["choices"][0]["message"]["content"], cfg["model"]
    except Exception as e:
        fallback = local_tutor(skill, question, context)
        return fallback + f"\n\n_El proveedor externo no respondió; usé el Tutor Smart local._", "Fallback local"
