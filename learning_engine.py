from datetime import date, timedelta

LEVELS = [
    (0, "Explorador", 1),
    (250, "Aprendiz", 2),
    (650, "Practicante", 3),
    (1200, "Competente", 4),
    (2000, "Avanzado", 5),
    (3200, "Especialista", 6),
    (5000, "Maestro", 7),
]

def total_xp(session_rows, exam_rows, completed_lessons=0):
    return sum(r["xp"] for r in session_rows) + sum(r["xp"] for r in exam_rows) + completed_lessons * 35

def level_for_xp(xp):
    current = LEVELS[0]
    next_threshold = None
    for i, item in enumerate(LEVELS):
        if xp >= item[0]:
            current = item
            next_threshold = LEVELS[i+1][0] if i+1 < len(LEVELS) else None
    return {"name": current[1], "level": current[2], "floor": current[0], "next": next_threshold}

def level_progress(xp):
    info = level_for_xp(xp)
    if info["next"] is None:
        return 1.0, 0
    span = info["next"] - info["floor"]
    return max(0.0, min(1.0, (xp-info["floor"])/span)), info["next"]-xp

def streak(checkin_rows, session_rows):
    days = {r["day"] for r in checkin_rows}
    days |= {r["created_at"][:10] for r in session_rows}
    if not days:
        return 0
    d = date.today()
    if d.isoformat() not in days:
        d = d - timedelta(days=1)
        if d.isoformat() not in days:
            return 0
    count = 0
    while d.isoformat() in days:
        count += 1
        d -= timedelta(days=1)
    return count

def weekly_minutes(session_rows):
    cutoff = date.today() - timedelta(days=6)
    return sum(r["minutes"] for r in session_rows if date.fromisoformat(r["created_at"][:10]) >= cutoff)

def roadmap_progress(skill_data, lesson_rows):
    total = sum(len(m["lessons"]) for m in skill_data["modules"])
    completed = sum(1 for r in lesson_rows if r["completed"])
    return completed, total, (completed/total if total else 0)

def module_progress(module_idx, module, lesson_rows):
    done_set = {(r["module_idx"], r["lesson_idx"]) for r in lesson_rows if r["completed"]}
    done = sum((module_idx, i) in done_set for i in range(len(module["lessons"])))
    return done, len(module["lessons"]), done / len(module["lessons"])

def current_module_index(skill_data, lesson_rows):
    for mi, module in enumerate(skill_data["modules"]):
        done, total, _ = module_progress(mi, module, lesson_rows)
        if done < total:
            return mi
    return len(skill_data["modules"]) - 1

def recommended_session(skill_data, lesson_rows, daily_minutes):
    mi = current_module_index(skill_data, lesson_rows)
    module = skill_data["modules"][mi]
    done_set = {(r["module_idx"], r["lesson_idx"]) for r in lesson_rows if r["completed"]}
    li = next((i for i in range(len(module["lessons"])) if (mi, i) not in done_set), len(module["lessons"])-1)
    title, concept, exercise = module["lessons"][li]
    warm = max(3, round(daily_minutes*0.15))
    learn = max(5, round(daily_minutes*0.25))
    practice = max(8, daily_minutes-warm-learn-3)
    return {
        "module_idx": mi, "lesson_idx": li, "title": title, "concept": concept,
        "exercise": exercise, "blocks": [
            ("Activación", warm, "Repaso sin mirar apuntes."),
            ("Concepto", learn, concept),
            ("Práctica deliberada", practice, exercise),
            ("Cierre", 3, "Anotá qué salió mejor y cuál será tu foco siguiente."),
        ]
    }
