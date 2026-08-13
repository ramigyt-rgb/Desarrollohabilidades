SKILLS = {
    "Piano": {
        "icon": "🎹",
        "tagline": "De tocar notas a pensar música.",
        "accent": "#D8B4FE",
        "modules": [
            {
                "title": "Fundamentos & mapa del teclado",
                "level": "Base",
                "xp": 120,
                "lessons": [
                    ("Orientación del teclado", "Ubicá Do central, grupos de 2/3 negras y nombres de notas.", "Tocá y nombrá 20 notas aleatorias sin mirar una guía."),
                    ("Postura y relajación", "Alineación, muñeca neutra, hombros relajados y digitación 1–5.", "2 minutos de cinco dedos por mano a tempo cómodo."),
                    ("Pulso y metrónomo", "Negras, blancas y corcheas con pulso estable.", "60 segundos a 60 BPM sin cortar."),
                ],
                "exam": [
                    ("¿Qué número corresponde al pulgar?", ["1", "2", "3", "5"], 0),
                    ("¿Qué ayuda principalmente a estabilizar el pulso?", ["Pedal", "Metrónomo", "Sostenido", "Arpegio"], 1),
                ],
            },
            {
                "title": "Escalas, acordes y coordinación",
                "level": "Inicial",
                "xp": 180,
                "lessons": [
                    ("Do mayor", "Digitación, paso de pulgar y sonido parejo.", "Escala ascendente y descendente, manos separadas."),
                    ("Triadas mayores y menores", "Construcción 1–3–5 y reconocimiento auditivo.", "C, F, G, Am, Dm, Em en posición fundamental."),
                    ("Independencia de manos", "Patrón de bajo simple + acordes.", "8 compases sin detenerte."),
                ],
                "exam": [
                    ("La triada de Do mayor es…", ["C-D-E", "C-E-G", "C-F-G", "C-E-A"], 1),
                    ("La escala de Do mayor tiene…", ["1 sostenido", "1 bemol", "ninguna alteración", "2 sostenidos"], 2),
                ],
            },
            {
                "title": "Repertorio & fluidez",
                "level": "Intermedio",
                "xp": 260,
                "lessons": [
                    ("Lectura por intervalos", "Leé distancia y dirección, no nota por nota.", "Lectura a primera vista de 8 compases."),
                    ("Voicings y acompañamiento", "Inversiones, conducción de voces y patrones.", "Tocá una progresión I–V–vi–IV con 3 patrones."),
                    ("Interpretación", "Dinámica, fraseo, pedal y respiración musical.", "Grabá una pieza completa y autoevaluá 3 aspectos."),
                ],
                "exam": [
                    ("Una inversión sirve para…", ["Cambiar de tonalidad", "Reordenar notas del acorde", "Duplicar tempo", "Eliminar el bajo"], 1),
                    ("El fraseo musical se relaciona con…", ["La intención y dirección", "Solo velocidad", "Solo volumen", "La afinación del piano"], 0),
                ],
            },
            {
                "title": "Improvisación & lenguaje",
                "level": "Avanzado",
                "xp": 360,
                "lessons": [
                    ("Motivos", "Crear, repetir y variar ideas breves.", "Improvisá 2 minutos usando solo 3 notas."),
                    ("Armonía funcional", "Tensión, resolución y funciones tonales.", "Analizá una progresión y marcá T-S-D."),
                    ("Performance", "Preparación mental, continuidad y recuperación de errores.", "Tocá una toma completa sin reiniciar."),
                ],
                "exam": [
                    ("Un motivo es…", ["Una idea musical breve", "Un pedal", "Una escala", "Un silencio largo"], 0),
                    ("En performance conviene…", ["Reiniciar ante cada error", "Mantener continuidad", "Acelerar", "Evitar respirar"], 1),
                ],
            },
        ],
    },
    "Programación": {
        "icon": "💻",
        "tagline": "De escribir código a construir sistemas.",
        "accent": "#7DD3FC",
        "modules": [
            {
                "title": "Pensamiento computacional",
                "level": "Base",
                "xp": 120,
                "lessons": [
                    ("Variables y tipos", "Representación de datos y operaciones.", "Creá variables de texto, entero, decimal y booleano."),
                    ("Condiciones", "Tomar decisiones con if/elif/else.", "Clasificá una nota en aprobado/desaprobado."),
                    ("Bucles", "Automatizar repeticiones.", "Recorré una lista y calculá un total."),
                ],
                "exam": [
                    ("¿Qué estructura toma decisiones?", ["for", "if", "import", "print"], 1),
                    ("¿Qué hace un bucle?", ["Repite lógica", "Encripta", "Instala Python", "Diseña UI"], 0),
                ],
            },
            {
                "title": "Python práctico",
                "level": "Inicial",
                "xp": 190,
                "lessons": [
                    ("Funciones", "Entradas, salidas, scope y reutilización.", "Escribí una función que calcule un promedio."),
                    ("Colecciones", "Listas, dicts, sets y tuplas.", "Modelá 5 productos con nombre y precio."),
                    ("Errores", "Excepciones y debugging sistemático.", "Capturá un ValueError y mostrá un mensaje útil."),
                ],
                "exam": [
                    ("Una función ayuda a…", ["Reutilizar lógica", "Borrar Python", "Evitar variables", "Crear internet"], 0),
                    ("Un dict almacena…", ["Solo números", "Clave-valor", "Solo texto", "Solo funciones"], 1),
                ],
            },
            {
                "title": "Apps & datos",
                "level": "Intermedio",
                "xp": 280,
                "lessons": [
                    ("Pandas", "Carga, limpieza, filtros y agregaciones.", "Analizá un CSV y calculá 3 KPIs."),
                    ("Streamlit", "Interfaces reactivas y estado.", "Construí una app con filtros y métricas."),
                    ("Persistencia", "SQLite y CRUD.", "Guardá y recuperá registros."),
                ],
                "exam": [
                    ("Pandas se usa principalmente para…", ["Datos tabulares", "Editar video", "DNS", "Audio"], 0),
                    ("CRUD significa…", ["Create Read Update Delete", "Compile Run Upload Deploy", "Copy Restore User Data", "Ninguna"], 0),
                ],
            },
            {
                "title": "Arquitectura & producto",
                "level": "Avanzado",
                "xp": 380,
                "lessons": [
                    ("Diseño modular", "Separación de responsabilidades.", "Refactorizá una app monolítica en módulos."),
                    ("APIs", "Contratos, autenticación y errores.", "Consumí una API y manejá timeouts."),
                    ("Testing", "Pruebas unitarias e integración.", "Escribí tests para lógica crítica."),
                ],
                "exam": [
                    ("Separar responsabilidades mejora…", ["Mantenibilidad", "Latencia de internet siempre", "Tamaño de pantalla", "Voltaje"], 0),
                    ("Un test unitario verifica…", ["Una unidad de lógica", "Todo internet", "Solo CSS", "Un usuario real"], 0),
                ],
            },
        ],
    },
    "Inglés": {
        "icon": "🇬🇧",
        "tagline": "De traducir mentalmente a pensar y responder.",
        "accent": "#F9A8D4",
        "modules": [
            {
                "title": "Core English",
                "level": "Base",
                "xp": 120,
                "lessons": [
                    ("Present simple", "Rutinas, hechos y frecuencia.", "Describí tu día en 8 oraciones."),
                    ("Preguntas", "Do/does, be y question words.", "Creá 10 preguntas reales."),
                    ("Vocabulario activo", "Aprender por contexto y recuperación.", "Usá 15 palabras nuevas en frases propias."),
                ],
                "exam": [
                    ("Correcto: She ___ every day.", ["study", "studies", "studying", "studied"], 1),
                    ("Pregunta correcta:", ["You work here?", "Do you work here?", "Does you work here?", "Are work here?"], 1),
                ],
            },
            {
                "title": "Conversación funcional",
                "level": "Inicial",
                "xp": 180,
                "lessons": [
                    ("Past simple", "Relatar hechos terminados.", "Contá qué hiciste ayer durante 90 segundos."),
                    ("Future forms", "Will, going to y present continuous.", "Explicá tres planes futuros."),
                    ("Listening chunks", "Reconocer grupos de palabras.", "Escuchá 5 minutos y anotá chunks, no palabras sueltas."),
                ],
                "exam": [
                    ("I ___ him yesterday.", ["see", "saw", "seen", "seeing"], 1),
                    ("Plan decidido: I am ___ visit London.", ["go", "going to", "will to", "gone"], 1),
                ],
            },
            {
                "title": "Fluidez & precisión",
                "level": "Intermedio",
                "xp": 270,
                "lessons": [
                    ("Conditionals", "Hipótesis, posibilidades y consecuencias.", "Escribí 10 ejemplos 0/1/2 conditional."),
                    ("Storytelling", "Conectores, tensión y cierre.", "Contá una historia de 2 minutos."),
                    ("Pronunciation", "Stress, linking y reducción.", "Shadowing de 3 minutos."),
                ],
                "exam": [
                    ("If I had more time, I ___ more.", ["travel", "would travel", "traveled", "will travel"], 1),
                    ("Linking ayuda a…", ["Sonar más natural", "Escribir más lento", "Eliminar vocabulario", "Cambiar gramática"], 0),
                ],
            },
            {
                "title": "Dominio aplicado",
                "level": "Avanzado",
                "xp": 360,
                "lessons": [
                    ("Debate", "Argumentar, matizar y responder objeciones.", "Defendé una posición durante 3 minutos."),
                    ("Professional English", "Reuniones, emails y presentaciones.", "Presentá un proyecto en 5 minutos."),
                    ("Immersion", "Consumo activo sin traducción constante.", "30 minutos de inmersión + resumen en inglés."),
                ],
                "exam": [
                    ("To hedge an opinion means…", ["Matizarla", "Gritarla", "Traducirla", "Negarla"], 0),
                    ("Fluency is best described as…", ["Comunicación continua y efectiva", "Cero errores", "Acento nativo obligatorio", "Solo vocabulario"], 0),
                ],
            },
        ],
    },
    "Aviación": {
        "icon": "✈️",
        "tagline": "Estudiá con criterio operacional, no de memoria.",
        "accent": "#A7F3D0",
        "modules": [
            {
                "title": "Principios de vuelo",
                "level": "Base",
                "xp": 140,
                "lessons": [
                    ("Cuatro fuerzas", "Sustentación, peso, empuje y resistencia.", "Explicá cómo cambia cada fuerza en vuelo recto y nivelado."),
                    ("Controles primarios", "Alerones, elevador y timón.", "Asociá cada control con su eje."),
                    ("Ángulo de ataque", "Relación con sustentación y pérdida.", "Explicá una pérdida sin usar la frase 'falta de velocidad'."),
                ],
                "exam": [
                    ("El timón controla principalmente…", ["Pitch", "Yaw", "Roll", "Potencia"], 1),
                    ("Una pérdida ocurre al exceder…", ["Altitud crítica", "Ángulo de ataque crítico", "RPM crítica", "Temperatura crítica"], 1),
                ],
            },
            {
                "title": "Operación & procedimientos",
                "level": "Inicial",
                "xp": 210,
                "lessons": [
                    ("Checklist", "Disciplina de cabina y flujo.", "Simulá before start, taxi y before takeoff."),
                    ("Circuito de tránsito", "Secuencia, referencias y comunicaciones.", "Dibujá el circuito y explicá cada tramo."),
                    ("Aproximación estabilizada", "Velocidad, senda, configuración y energía.", "Definí criterios personales de estabilización."),
                ],
                "exam": [
                    ("Una checklist sirve para…", ["Reducir omisiones", "Reemplazar entrenamiento", "Aumentar velocidad", "Evitar radio"], 0),
                    ("Una aproximación estable requiere…", ["Parámetros controlados", "Cambios grandes continuos", "Ignorar viento", "No usar referencias"], 0),
                ],
            },
            {
                "title": "Meteorología & navegación",
                "level": "Intermedio",
                "xp": 300,
                "lessons": [
                    ("Viento y presión", "Efectos operacionales.", "Interpretá un escenario de viento cruzado."),
                    ("Planificación", "Rumbo, tiempo, combustible y alternativos.", "Armá una navegación simulada completa."),
                    ("Toma de decisiones", "Riesgo, márgenes y alternativas.", "Analizá un caso go/no-go."),
                ],
                "exam": [
                    ("Mayor densidad del aire suele favorecer…", ["Performance", "Resistencia cero", "Pérdida inmediata", "Ningún efecto"], 0),
                    ("Go/no-go debe considerar…", ["Riesgo total y márgenes", "Solo ganas de volar", "Solo hora", "Solo combustible"], 0),
                ],
            },
            {
                "title": "Criterio de piloto",
                "level": "Avanzado",
                "xp": 420,
                "lessons": [
                    ("ADM", "Aeronautical decision-making y amenazas.", "Aplicá PAVE a un vuelo simulado."),
                    ("Emergencias", "Prioridades y memoria operativa.", "Aviate, navigate, communicate en 3 escenarios."),
                    ("Briefing", "Anticipación y plan B.", "Hacé briefing completo de salida y llegada."),
                ],
                "exam": [
                    ("Primera prioridad ante una emergencia:", ["Aviate", "Llamar por radio", "Buscar el celular", "Cambiar destino"], 0),
                    ("PAVE organiza…", ["Factores de riesgo", "Tipos de motor", "Solo clima", "Frecuencias"], 0),
                ],
            },
        ],
        "disclaimer": "Contenido educativo general. Para vuelo real prevalecen tu instructor, POH/AFM, reglamentación y procedimientos aprobados.",
    },
}
