import streamlit as st
import pandas as pd
import plotly.express as px
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
    data=SKILLS[skill]
    rows=db.lesson_rows(user["id"],skill)
    hero("MASTERY CHECK", f"Exámenes · {data['icon']} {skill}", "No alcanza con reconocer la respuesta: buscamos recuperar, aplicar y explicar.")
    mi=st.selectbox("Módulo a evaluar",range(len(data["modules"])),format_func=lambda i:f"{i+1:02d} · {data['modules'][i]['title']}")
    module=data["modules"][mi]
    d,t,p=module_progress(mi,module,rows)
    st.caption(f"Preparación estimada: {d}/{t} lecciones completadas")
    with st.form(f"exam_{mi}"):
        answers=[]
        for qi,(q,opts,correct) in enumerate(module["exam"]):
            answers.append(st.radio(f"{qi+1}. {q}",opts,index=None,key=f"q_{mi}_{qi}"))
        reflection=st.text_area("Explicación / reflexión",placeholder="Explicá con tus palabras qué entendiste mejor en este módulo.")
        submit=st.form_submit_button("Corregir examen",type="primary",use_container_width=True)
        if submit:
            if any(a is None for a in answers):
                st.warning("Respondé todas las preguntas.")
            else:
                correct_n=sum(ans==opts[correct] for ans,(_,opts,correct) in zip(answers,module["exam"]))
                score=correct_n/len(module["exam"])*100
                xp=int(30+score*0.8)
                db.save_exam(user["id"],skill,mi,score,xp)
                st.session_state.exam_result=(score,xp,correct_n,len(module["exam"]))
    if st.session_state.exam_result:
        score,xp,c,n=st.session_state.exam_result
        cls="exam-ok" if score>=70 else "exam-bad"
        msg="Dominio aprobado" if score>=70 else "Todavía conviene reforzar"
        st.markdown(f'<div class="{cls}"><b>{msg}</b><br>Resultado: {score:.0f}% · {c}/{n} correctas · +{xp} XP</div>',unsafe_allow_html=True)

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
