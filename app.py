import streamlit as st
import pandas as pd
import plotly.express as px
import random
from pathlib import Path
from datetime import datetime, date, timedelta

from seed_content import SKILLS
import database as db
from auth import hash_password, verify_password
from learning_engine import (
    total_xp, level_for_xp, level_progress, streak, weekly_minutes,
    roadmap_progress, module_progress, recommended_session, current_module_index
)
from ai_tutor import ask_tutor
from ui import inject_css, hero, metric_card
from ppa_bank import PPA_BANK

st.set_page_config(
    page_title="Learning OS",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)
db.init_db()
inject_css()

def rerun():
    st.rerun()

def init_state():
    st.session_state.setdefault("user", None)
    st.session_state.setdefault("nav", "Inicio")
    st.session_state.setdefault("exam_result", None)
init_state()

def login_screen():
    c1, c2, c3 = st.columns([1.15, 1.4, 1.15])
    with c2:
        st.markdown("<div style='height:7vh'></div>", unsafe_allow_html=True)
        hero("PERSONAL LEARNING SYSTEM", "Learning OS ✦", "Tu sistema operativo para aprender habilidades complejas con estructura, práctica y feedback.")
        t1, t2 = st.tabs(["Ingresar", "Crear cuenta"])
        with t1:
            with st.form("login"):
                username = st.text_input("Usuario")
                password = st.text_input("Contraseña", type="password")
                ok = st.form_submit_button("Entrar a Learning OS", use_container_width=True)
                if ok:
                    user = db.get_user(username)
                    if user and verify_password(password, user["password_hash"]):
                        st.session_state.user = user
                        st.session_state.nav = "Inicio"
                        rerun()
                    st.error("Usuario o contraseña incorrectos.")
        with t2:
            with st.form("register"):
                name = st.text_input("Tu nombre")
                username = st.text_input("Elegí un usuario")
                p1 = st.text_input("Contraseña", type="password")
                p2 = st.text_input("Repetí la contraseña", type="password")
                create = st.form_submit_button("Crear mi espacio", use_container_width=True)
                if create:
                    if len(username.strip()) < 3 or len(p1) < 6:
                        st.error("Usá un usuario de al menos 3 caracteres y contraseña de al menos 6.")
                    elif p1 != p2:
                        st.error("Las contraseñas no coinciden.")
                    else:
                        uid = db.create_user(username, name or username, hash_password(p1))
                        if not uid:
                            st.error("Ese usuario ya existe.")
                        else:
                            st.session_state.user = db.get_user(username)
                            rerun()

def onboarding(user):
    hero("SETUP INICIAL", "Construí tu sistema de aprendizaje", "Elegí una habilidad, tu nivel y cuánto tiempo real podés sostener. Learning OS organiza el resto.")
    cols = st.columns(4)
    selected = st.session_state.get("onboard_skill", "Programación")
    for i, (skill, data) in enumerate(SKILLS.items()):
        with cols[i]:
            st.markdown(f"""
            <div class="glass">
              <div style="font-size:2rem">{data['icon']}</div>
              <div style="font-size:1.1rem;font-weight:800;margin-top:7px">{skill}</div>
              <div class="tiny">{data['tagline']}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Elegir", key=f"pick_{skill}", use_container_width=True):
                st.session_state.onboard_skill = skill
                selected = skill
    st.divider()
    with st.form("onboarding"):
        c1,c2 = st.columns(2)
        with c1:
            skill = st.selectbox("Habilidad principal", list(SKILLS.keys()), index=list(SKILLS.keys()).index(selected))
            experience = st.select_slider("Tu punto de partida", ["Cero", "Principiante", "Intermedio", "Avanzado"])
        with c2:
            minutes = st.slider("Minutos por día", 10, 120, 30, 5)
            target = st.text_input("Objetivo", placeholder="Ej: tocar 5 canciones de memoria / construir apps sin tutoriales")
        if st.form_submit_button("Crear mi Learning OS", use_container_width=True):
            db.save_profile(user["id"], skill, minutes, target, experience)
            rerun()

def sidebar(user, profile):
    with st.sidebar:
        st.markdown("## ✦ Learning OS")
        st.caption("Personal Learning System")
        st.divider()
        if profile.get("active_skill"):
            skill = profile["active_skill"]
            data = SKILLS[skill]
            st.markdown(f"### {data['icon']} {skill}")
            if len(SKILLS) > 1:
                new_skill = st.selectbox("Cambiar habilidad", list(SKILLS.keys()), index=list(SKILLS.keys()).index(skill), label_visibility="collapsed")
                if new_skill != skill:
                    db.set_active_skill(user["id"], new_skill)
                    st.session_state.nav = "Inicio"
                    rerun()
        st.divider()
        items = [
            ("Inicio","⌂"), ("Ruta","◈"), ("Práctica","▶"), ("Exámenes","✓"),
            ("Tutor IA","✦"), ("Analítica","⌁"), ("Objetivos","◎"), ("Ajustes","⚙")
        ]
        for label, icon in items:
            active = st.session_state.nav == label
            if st.button(f"{icon}  {label}", key=f"nav_{label}", use_container_width=True, type="primary" if active else "secondary"):
                st.session_state.nav = label
                rerun()
        st.divider()
        st.caption(f"Conectado como **{user['display_name']}**")
        if st.button("Cerrar sesión", use_container_width=True):
            st.session_state.user = None
            rerun()

def get_stats(uid, skill):
    lesson_rows = db.lesson_rows(uid, skill)
    sess = db.sessions(uid, skill)
    exams = db.exams(uid, skill)
    checks = db.checkins(uid, skill)
    completed = sum(1 for r in lesson_rows if r["completed"])
    xp = total_xp(sess, exams, completed)
    return lesson_rows, sess, exams, checks, completed, xp

def page_home(user, profile, skill):
    data = SKILLS[skill]
    lesson_rows, sess, exam_rows, checks, completed, xp = get_stats(user["id"], skill)
    level = level_for_xp(xp)
    lp, remain = level_progress(xp)
    done, total, rp = roadmap_progress(data, lesson_rows)
    stk = streak(checks, sess)
    weekly = weekly_minutes(sess)
    rec = recommended_session(data, lesson_rows, profile["daily_minutes"])

    hero(f"{data['icon']} {skill.upper()} · LEARNING OS", f"Buenos días, {user['display_name']}.", f"Tu próxima mejora no necesita motivación infinita: necesita una sesión clara. Hoy el foco es {rec['title']}.")
    cols = st.columns(4)
    with cols[0]: metric_card("Nivel", f"{level['level']} · {level['name']}", f"{xp:,} XP acumulados".replace(",", "."))
    with cols[1]: metric_card("Streak", f"{stk} días", "Constancia activa")
    with cols[2]: metric_card("Ruta", f"{round(rp*100)}%", f"{done}/{total} lecciones")
    with cols[3]: metric_card("Esta semana", f"{weekly} min", f"Meta diaria: {profile['daily_minutes']} min")

    st.markdown("### Tu sesión de hoy")
    a,b = st.columns([1.65,1])
    with a:
        st.markdown(f"""
        <div class="module-card">
          <div class="eyebrow">NEXT BEST ACTION</div>
          <div style="font-size:1.55rem;font-weight:850;margin:.35rem 0">{rec['title']}</div>
          <div style="color:#B6B6C2">{rec['concept']}</div>
          <div class="accent-line" style="background:{data['accent']}"></div>
          <div style="font-weight:750">Ejercicio clave</div>
          <div class="tiny" style="font-size:.88rem;margin-top:5px">{rec['exercise']}</div>
        </div>
        """, unsafe_allow_html=True)
        for name, mins, desc in rec["blocks"]:
            st.write(f"**{mins} min · {name}** — {desc}")
        if st.button("Empezar práctica", type="primary", use_container_width=True):
            st.session_state.nav = "Práctica"; rerun()
    with b:
        st.markdown("#### Progreso de nivel")
        st.progress(lp)
        st.caption("Nivel máximo alcanzado." if remain == 0 else f"Faltan {remain} XP para el próximo nivel.")
        st.markdown("#### Check-in rápido")
        with st.form("quick_check"):
            energy = st.slider("Energía",1,5,3)
            focus = st.slider("Foco",1,5,3)
            intention = st.text_input("Intención", placeholder="Una cosa que quiero hacer bien hoy")
            if st.form_submit_button("Registrar check-in", use_container_width=True):
                db.upsert_checkin(user["id"], skill, energy, focus, intention)
                st.success("Check-in registrado.")
                rerun()

    st.markdown("### Radar de progreso")
    mcols = st.columns(len(data["modules"]))
    for mi, module in enumerate(data["modules"]):
        d,t,p = module_progress(mi,module,lesson_rows)
        with mcols[mi]:
            st.markdown(f"**{mi+1:02d}. {module['level']}**")
            st.progress(p)
            st.caption(f"{d}/{t} · {module['title']}")

def page_roadmap(user, profile, skill):
    data = SKILLS[skill]
    rows = db.lesson_rows(user["id"], skill)
    hero("ADAPTIVE ROADMAP", f"Ruta · {data['icon']} {skill}", "Cada etapa desbloquea dificultad. Marcá como completado solo lo que realmente podés recuperar y aplicar.")
    if data.get("disclaimer"): st.info(data["disclaimer"])
    for mi, module in enumerate(data["modules"]):
        d,t,p = module_progress(mi,module,rows)
        status = "Completado" if d==t else ("En curso" if d else "Pendiente")
        with st.expander(f"{mi+1:02d} · {module['title']} — {status} · {round(p*100)}%", expanded=(0 < p < 1) or (mi==current_module_index(data,rows))):
            st.caption(f"{module['level']} · {module['xp']} XP de referencia")
            st.progress(p)
            done_set = {(r["module_idx"],r["lesson_idx"]) for r in rows if r["completed"]}
            for li,(title,concept,exercise) in enumerate(module["lessons"]):
                checked=(mi,li) in done_set
                c1,c2=st.columns([.08,.92])
                with c1:
                    new = st.checkbox("", value=checked, key=f"lesson_{mi}_{li}", label_visibility="collapsed")
                    if new != checked:
                        db.set_lesson_completed(user["id"], skill, mi, li, new)
                        rerun()
                with c2:
                    st.markdown(f"**{title}**")
                    st.caption(concept)
                    st.write(f"↳ {exercise}")

def page_practice(user, profile, skill):
    data=SKILLS[skill]
    rows=db.lesson_rows(user["id"],skill)
    rec=recommended_session(data,rows,profile["daily_minutes"])
    hero("DELIBERATE PRACTICE", f"Práctica · {rec['title']}", "Una sesión gana valor cuando tiene foco, feedback y un cierre medible.")
    c1,c2=st.columns([1.2,1])
    with c1:
        st.markdown("### Protocolo recomendado")
        for i,(name,mins,desc) in enumerate(rec["blocks"],1):
            st.markdown(f"""
            <div class="module-card">
              <div class="eyebrow">BLOQUE {i} · {mins} MIN</div>
              <div style="font-size:1.1rem;font-weight:800">{name}</div>
              <div class="tiny">{desc}</div>
            </div>""", unsafe_allow_html=True)
        st.info(f"Ejercicio principal: {rec['exercise']}")
    with c2:
        st.markdown("### Cerrar sesión")
        with st.form("practice_log"):
            minutes=st.number_input("Minutos reales",5,300,int(profile["daily_minutes"]),5)
            quality=st.slider("Calidad de la práctica",1,5,3)
            notes=st.text_area("Bitácora",placeholder="Qué mejoró, qué falló, qué repetir...")
            complete=st.checkbox("También completar la lección recomendada")
            if st.form_submit_button("Guardar sesión + XP",type="primary",use_container_width=True):
                xp=int(minutes*1.4 + quality*8)
                db.add_session(user["id"],skill,minutes,quality,notes,xp)
                if complete:
                    db.set_lesson_completed(user["id"],skill,rec["module_idx"],rec["lesson_idx"],True)
                st.success(f"Sesión guardada · +{xp} XP")
                rerun()
        st.markdown("### Técnica de calidad")
        st.write("**1.** Trabajá lento. **2.** Identificá el error exacto. **3.** Corregí una variable. **4.** Repetí limpio. **5.** Subí dificultad.")

def page_exams(user, profile, skill):
    data = SKILLS[skill]
    rows = db.lesson_rows(user["id"], skill)

    if skill != "Aviación":
        hero("MASTERY CHECK", f"Exámenes · {data['icon']} {skill}", "No alcanza con reconocer la respuesta: buscamos recuperar, aplicar y explicar.")
        mi = st.selectbox("Módulo a evaluar", range(len(data["modules"])), format_func=lambda i: f"{i+1:02d} · {data['modules'][i]['title']}")
        module = data["modules"][mi]
        d, t, p = module_progress(mi, module, rows)
        st.caption(f"Preparación estimada: {d}/{t} lecciones completadas")
        with st.form(f"exam_{mi}"):
            answers = []
            for qi, (q, opts, correct) in enumerate(module["exam"]):
                answers.append(st.radio(f"{qi+1}. {q}", opts, index=None, key=f"q_{mi}_{qi}"))
            st.text_area("Explicación / reflexión", placeholder="Explicá con tus palabras qué entendiste mejor en este módulo.")
            submit = st.form_submit_button("Corregir examen", type="primary", use_container_width=True)
            if submit:
                if any(a is None for a in answers):
                    st.warning("Respondé todas las preguntas.")
                else:
                    correct_n = sum(ans == opts[correct] for ans, (_, opts, correct) in zip(answers, module["exam"]))
                    score = correct_n / len(module["exam"]) * 100
                    xp = int(30 + score * 0.8)
                    db.save_exam(user["id"], skill, mi, score, xp)
                    st.session_state.exam_result = (score, xp, correct_n, len(module["exam"]))
        if st.session_state.get("exam_result"):
            score, xp, c, n = st.session_state.exam_result
            cls = "exam-ok" if score >= 70 else "exam-bad"
            msg = "Dominio aprobado" if score >= 70 else "Todavía conviene reforzar"
            st.markdown(f'<div class="{cls}"><b>{msg}</b><br>Resultado: {score:.0f}% · {c}/{n} correctas · +{xp} XP</div>', unsafe_allow_html=True)
        return

    hero("ANAC EXAM LAB", "Exámenes · ✈️ Aviación", "Banco PPA integrado: práctica por capítulo, simulacro aleatorio, revisión de errores y análisis oficial cuando está disponible.")
    st.info("Banco cargado desde el material ANAC aportado. Las preguntas se preservan según la fuente. El PDF de preguntas no trae una clave separada; la autocorrección usa únicamente claves que pudieron derivarse de forma inequívoca del documento oficial 'Teoría y análisis de respuestas'. Las restantes se muestran como revisión manual para no inventar respuestas.")

    meta = PPA_BANK["meta"]
    all_questions = PPA_BANK["questions"]
    keyed = [q for q in all_questions if q.get("answer")]
    chapters = sorted({q["chapter"] for q in all_questions})
    chapter_names = {q["chapter"]: q["chapter_title"] for q in all_questions}

    c1, c2, c3, c4 = st.columns(4)
    with c1: metric_card("Banco PPA", meta["question_count"], "preguntas cargadas")
    with c2: metric_card("Capítulos", len(chapters), "temario ANAC")
    with c3: metric_card("Autocorregibles", meta["autograded_count"], "clave derivada del análisis")
    with c4: metric_card("Con figura", sum(1 for q in all_questions if q.get("figure")), "anexo integrado")

    tabs = st.tabs(["Simulacro ANAC", "Práctica por capítulo", "Banco completo", "Historial"])

    def show_figure(q):
        fig = q.get("figure")
        if not fig:
            return
        page = PPA_BANK.get("figure_pages", {}).get(fig)
        if page:
            img = Path(__file__).with_name("assets") / "ppa_figures" / f"page-{page:02d}.png"
            if img.exists():
                with st.expander(f"Ver Figura {fig} · Anexo ANAC", expanded=True):
                    st.image(str(img), use_container_width=True)

    def render_result(quiz, answers, title="Resultado"):
        gradable = [q for q in quiz if q.get("answer")]
        correct = 0
        answered_gradable = 0
        for i, q in enumerate(quiz):
            ans = answers.get(str(i))
            if q.get("answer") and ans:
                answered_gradable += 1
                chosen_letter = q["letters"][q["options"].index(ans)] if ans in q["options"] else None
                if chosen_letter == q["answer"]:
                    correct += 1
        score = (correct / len(gradable) * 100) if gradable else 0
        st.markdown(f"### {title}")
        rc1, rc2, rc3 = st.columns(3)
        with rc1: metric_card("Nota autocorregible", f"{score:.0f}%" if gradable else "—", f"{correct}/{len(gradable)} correctas")
        with rc2: metric_card("Respondidas", sum(bool(v) for v in answers.values()), f"de {len(quiz)}")
        with rc3: metric_card("Revisión manual", sum(1 for q in quiz if not q.get("answer")), "sin clave inequívoca")
        if gradable:
            xp = int(20 + score * 0.65)
            db.save_exam(user["id"], skill, 100, score, xp)
            st.caption(f"Intento registrado · +{xp} XP")
        for i, q in enumerate(quiz):
            ans = answers.get(str(i))
            with st.expander(f"{i+1}. Cap. {q['chapter']} · Pregunta {q['number']}" + (" ✓" if q.get("answer") and ans and q["letters"][q["options"].index(ans)] == q["answer"] else "")):
                st.write(q["question"])
                st.write(f"**Tu respuesta:** {ans or 'Sin responder'}")
                if q.get("answer"):
                    idx = q["letters"].index(q["answer"])
                    st.success(f"Clave: {q['answer'].upper()}) {q['options'][idx]}")
                else:
                    st.warning("Esta pregunta queda como revisión manual: la fuente de preguntas no incluye una clave explícita y no se fuerza una respuesta.")
                if q.get("analysis"):
                    st.markdown("**Análisis oficial asociado**")
                    st.write(q["analysis"])

    with tabs[0]:
        st.markdown("### Simulacro aleatorio")
        a, b, c = st.columns(3)
        with a:
            n = st.selectbox("Cantidad", [10, 20, 30, 40], index=1, key="ppa_n")
        with b:
            chapter_choice = st.selectbox("Temario", ["Todos"] + [f"{x}. {chapter_names[x]}" for x in chapters], key="ppa_ch")
        with c:
            only_keyed = st.toggle("Solo autocorregibles", value=True, key="ppa_only_keyed")
        pool = keyed if only_keyed else all_questions
        if chapter_choice != "Todos":
            ch = int(chapter_choice.split(".")[0])
            pool = [q for q in pool if q["chapter"] == ch]
        if st.button("Generar nuevo simulacro", type="primary", use_container_width=True, key="make_ppa_exam"):
            st.session_state.ppa_quiz = random.sample(pool, min(n, len(pool)))
            st.session_state.ppa_answers = {}
            st.session_state.ppa_finished = False
            rerun()
        quiz = st.session_state.get("ppa_quiz", [])
        if quiz and not st.session_state.get("ppa_finished", False):
            st.progress(sum(bool(v) for v in st.session_state.get("ppa_answers", {}).values()) / len(quiz))
            with st.form("ppa_exam_form"):
                answers = {}
                for i, q in enumerate(quiz):
                    st.markdown(f"#### {i+1}. {q['question']}")
                    show_figure(q)
                    answers[str(i)] = st.radio("Elegí una opción", q["options"], index=None, key=f"ppa_exam_{i}", label_visibility="collapsed")
                    st.caption(f"Capítulo {q['chapter']} · {q['chapter_title']} · Pregunta {q['number']}")
                    st.divider()
                if st.form_submit_button("Finalizar y corregir", type="primary", use_container_width=True):
                    st.session_state.ppa_answers = answers
                    st.session_state.ppa_finished = True
                    rerun()
        elif quiz and st.session_state.get("ppa_finished"):
            render_result(quiz, st.session_state.get("ppa_answers", {}), "Resultado del simulacro")
            if st.button("Nuevo intento", use_container_width=True):
                st.session_state.pop("ppa_quiz", None); st.session_state.pop("ppa_answers", None); st.session_state.ppa_finished=False; rerun()

    with tabs[1]:
        chapter = st.selectbox("Capítulo", chapters, format_func=lambda x: f"{x}. {chapter_names[x]}", key="practice_chapter")
        cp = [q for q in all_questions if q["chapter"] == chapter]
        st.caption(f"{len(cp)} preguntas disponibles")
        qnum = st.selectbox("Pregunta", range(len(cp)), format_func=lambda i: f"{cp[i]['number']}. {cp[i]['question'][:85]}…" if len(cp[i]['question']) > 85 else f"{cp[i]['number']}. {cp[i]['question']}")
        q = cp[qnum]
        st.markdown(f"### {q['question']}")
        show_figure(q)
        answer = st.radio("Respuesta", q["options"], index=None, key=f"practice_answer_{chapter}_{qnum}")
        if st.button("Revisar respuesta", use_container_width=True, key="review_practice"):
            if not answer:
                st.warning("Elegí una opción primero.")
            elif q.get("answer"):
                chosen = q["letters"][q["options"].index(answer)]
                idx = q["letters"].index(q["answer"])
                if chosen == q["answer"]:
                    st.success("Correcta.")
                else:
                    st.error(f"Incorrecta. Clave: {q['answer'].upper()}) {q['options'][idx]}")
            else:
                st.warning("Sin clave inequívoca en la fuente cargada: revisión manual.")
            if q.get("analysis"):
                st.markdown("#### Análisis oficial")
                st.write(q["analysis"])

    with tabs[2]:
        search = st.text_input("Buscar", placeholder="Ej: pérdida, altímetro, VOR, combustible…")
        filter_ch = st.selectbox("Filtrar capítulo", [0] + chapters, format_func=lambda x: "Todos" if x == 0 else f"{x}. {chapter_names[x]}", key="bank_ch")
        view = all_questions
        if filter_ch:
            view = [q for q in view if q["chapter"] == filter_ch]
        if search.strip():
            term = search.lower().strip()
            view = [q for q in view if term in q["question"].lower() or any(term in o.lower() for o in q["options"])]
        st.caption(f"{len(view)} resultados")
        for q in view[:100]:
            icon = "●" if q.get("answer") else "○"
            with st.expander(f"{icon} C{q['chapter']} · {q['number']} · {q['question'][:95]}"):
                st.write(q["question"])
                for letter, opt in zip(q["letters"], q["options"]):
                    st.write(f"**{letter.upper()})** {opt}")
                show_figure(q)
                st.caption("● autocorregible · ○ revisión manual")
        if len(view) > 100:
            st.caption("Mostrando los primeros 100 resultados; usá búsqueda o capítulo para acotar.")
        fig_pdf = Path(__file__).with_name("assets") / "anexo_figuras_ppa.pdf"
        if fig_pdf.exists():
            st.download_button("Descargar anexo de figuras ANAC", data=fig_pdf.read_bytes(), file_name="anexo_figuras_ppa.pdf", mime="application/pdf", use_container_width=True)

    with tabs[3]:
        hist = db.exams(user["id"], skill)
        if not hist:
            st.info("Todavía no hay intentos registrados.")
        else:
            hdf = pd.DataFrame(hist)
            hdf["fecha"] = pd.to_datetime(hdf["created_at"]).dt.strftime("%d/%m/%Y %H:%M")
            hdf["nota"] = hdf["score"].round(1).astype(str) + "%"
            st.dataframe(hdf[["fecha", "nota", "xp"]], use_container_width=True, hide_index=True)

def page_tutor(user, profile, skill):
    data=SKILLS[skill]
    rows=db.lesson_rows(user["id"],skill)
    done,total,rp=roadmap_progress(data,rows)
    rec=recommended_session(data,rows,profile["daily_minutes"])
    hero("AI MENTOR", f"Tutor IA · {data['icon']} {skill}", "Conoce tu objetivo, ruta y progreso. Pedile explicaciones, ejercicios, correcciones o una sesión adaptada.")
    hist=db.tutor_history(user["id"],skill,20)
    if not hist:
        st.markdown("""
        <div class="glass">
          <b>Probá preguntando:</b><br><br>
          “¿Qué debería practicar hoy?” · “Tomame un mini examen” ·
          “No entiendo este concepto” · “Dame una práctica de 20 minutos” ·
          “¿Cómo sé si realmente lo dominé?”
        </div>""",unsafe_allow_html=True)
    for m in hist:
        with st.chat_message("assistant" if m["role"]=="assistant" else "user"):
            st.markdown(m["content"])
    q=st.chat_input(f"Preguntale algo sobre {skill}…")
    if q:
        db.save_tutor_message(user["id"],skill,"user",q)
        context={
            "target":profile.get("target",""),
            "experience":profile.get("experience",""),
            "focus":rec["title"],
            "progress":f"{done}/{total} lecciones ({round(rp*100)}%)"
        }
        ans,provider=ask_tutor(skill,q,context,hist)
        db.save_tutor_message(user["id"],skill,"assistant",ans)
        st.session_state["_provider"]=provider
        rerun()
    if st.session_state.get("_provider"):
        st.caption(f"Motor: {st.session_state['_provider']}")

def page_analytics(user, profile, skill):
    hero("LEARNING INTELLIGENCE", f"Analítica · {skill}", "Usá datos para ajustar el sistema, no para castigarte.")
    rows=db.sessions(user["id"],skill)
    checks=db.checkins(user["id"],skill)
    exams=db.exams(user["id"],skill)
    lesson_rows=db.lesson_rows(user["id"],skill)
    completed=sum(1 for r in lesson_rows if r["completed"])
    xp=total_xp(rows,exams,completed)
    c=st.columns(4)
    vals=[
        ("XP total",xp),("Horas",round(sum(r["minutes"] for r in rows)/60,1)),
        ("Sesiones",len(rows)),("Nota media",f"{(sum(r['score'] for r in exams)/len(exams)):.0f}%" if exams else "—")
    ]
    for col,(k,v) in zip(c,vals):
        with col: metric_card(k,v)
    if rows:
        df=pd.DataFrame(rows)
        df["date"]=pd.to_datetime(df["created_at"]).dt.date
        daily=df.groupby("date",as_index=False).agg(minutes=("minutes","sum"),quality=("quality","mean"),xp=("xp","sum"))
        fig=px.bar(daily,x="date",y="minutes",title="Minutos de práctica por día")
        fig.update_layout(height=340,margin=dict(l=10,r=10,t=50,b=10),paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig,use_container_width=True)
        if len(daily)>=2:
            fig2=px.scatter(daily,x="minutes",y="quality",size="xp",title="Tiempo vs calidad percibida")
            fig2.update_layout(height=330,margin=dict(l=10,r=10,t=50,b=10),paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig2,use_container_width=True)
        with st.expander("Historial de sesiones"):
            show=df[["created_at","minutes","quality","xp","notes"]].copy()
            show["created_at"]=pd.to_datetime(show["created_at"]).dt.strftime("%d/%m/%Y %H:%M")
            st.dataframe(show,use_container_width=True,hide_index=True)
    else:
        st.info("Todavía no hay sesiones. Registrá tu primera práctica para activar la analítica.")

def page_goals(user, profile, skill):
    hero("WEEKLY EXECUTION", f"Objetivos · {skill}", "Pocas metas, visibles y accionables. El objetivo es reducir fricción.")
    with st.form("new_goal"):
        text=st.text_input("Nuevo objetivo",placeholder="Ej: completar módulo 1 esta semana")
        if st.form_submit_button("Agregar objetivo",use_container_width=True):
            if text.strip():
                db.add_goal(user["id"],skill,text); rerun()
    goals=db.goals(user["id"],skill)
    if not goals:
        st.info("No tenés objetivos activos.")
    for g in goals:
        checked=st.checkbox(g["text"],value=bool(g["done"]),key=f"goal_{g['id']}")
        if checked != bool(g["done"]):
            db.toggle_goal(g["id"],checked); rerun()

def page_settings(user, profile, skill):
    hero("SYSTEM SETTINGS","Ajustes","Configurá el sistema alrededor de tu realidad, no de una rutina ideal.")
    with st.form("settings"):
        active=st.selectbox("Habilidad activa",list(SKILLS.keys()),index=list(SKILLS.keys()).index(skill))
        exp=st.select_slider("Experiencia",["Cero","Principiante","Intermedio","Avanzado"],value=profile.get("experience","Principiante"))
        mins=st.slider("Minutos diarios",10,120,int(profile.get("daily_minutes",30)),5)
        target=st.text_input("Objetivo principal",value=profile.get("target",""))
        if st.form_submit_button("Guardar cambios",type="primary",use_container_width=True):
            db.save_profile(user["id"],active,mins,target,exp)
            st.success("Configuración guardada.")
            rerun()
    st.markdown("### Tutor IA")
    st.write("Funciona siempre con **Tutor Smart local**. Si configurás `LLM_API_KEY`, `LLM_BASE_URL` y `LLM_MODEL`, usa automáticamente tu proveedor externo compatible.")

user=st.session_state.user
if not user:
    login_screen()
    st.stop()

profile=db.get_profile(user["id"])
if not profile.get("active_skill"):
    onboarding(user)
    st.stop()

skill=profile["active_skill"]
sidebar(user,profile)

pages={
    "Inicio":page_home,"Ruta":page_roadmap,"Práctica":page_practice,"Exámenes":page_exams,
    "Tutor IA":page_tutor,"Analítica":page_analytics,"Objetivos":page_goals,"Ajustes":page_settings
}
pages[st.session_state.nav](user,profile,skill)
