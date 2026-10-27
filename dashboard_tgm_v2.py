"""
Dashboard TGM (Transvisa EIRL) - Baja eficacia del cumplimiento de mantenimiento preventivo
Versión 2: panel lateral de navegación + filtros dinámicos (meses y As-Is / To-Be) interconectados.
Ejecutar con: Streamlit Run Dashboard_tgm_v2.py
"""
importar pandas como pd
import plotly.express as px
import plotly.graph_objects as go
importar streamlit como st

st.set_page_config(page_title="TGM | Mantenimiento preventivo", page_icon="🚛", diseño="wide")

# ======================= DATOS (del Excel del equipo) ========================
SEMANAL = [['S01-02', 15, 10, 14747.8, 19894.03], ['S03-04', 8, 5, 3347.84, 8468.14], ['S04-05', 11, 6, 10635.51, 4471.74], ['S06-07', 11, 7, 18621.93, 1407.28], ['S08-09', 12, 8, 5261.22, 18017.83], ['S10-11', 14, 9, 11229.77, 29989.02], ['T12-13', 14, 10, 13467.64, 17211.7], ['S14-15', 8, 8, 18270.01, 3658.39], ['S16-17', 2, 2, 5066.83, 192.66], ['S18-19', 5, 4, 3133.43, 5416.55], ['S20-21', 7, 4, 8958.43, 2817.64], ['S22-23', 7, 4, 695.32, 134.08], ['S24-25', 4, 1, 1888.82, 560.2], ['S26-27', 18, 12, 12858.83, 7151.18], ['S28-29', 17, 12, 14418.1, 9635.9], ['S30-31', 15, 11, 7220.69, 8395.15], ['S32-33', 10, 8, 4846.09, 56401.09], ['S34-35', 7, 7, 4219.55, 2183.42], ['S36-37', 5, 3, 18895.25, 6572.13], ['S38-39', 14, 10, 21726.35, 4019.43], ['S40-41', 11, 11, 19618.58, 10931.71], ['S42-43', 7, 4, 20759.2, 1042.59], ['S44-45', 10, 8, 5648.05, 7963.19], ['S46-47', 10, 8, 11969.78, 2604.7], ['S48-49', 9, 9, 15490.3, 5380.88], ['S50-51', 11, 9, 0.0, 0.0]]
MESES = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
ABREV = [m[:3].upper() para m en MESES]
ASIS_MENSUAL = {
    'capacitación': [66.7, 58.3, 75.0, 50.0, 41.7, 66.7, 75.0, 58.3, 58.3, 50.0, 75.0, 66.7],
    'tiempo_muerto': [11.67, 15.0, 10.83, 3.33, 5.83, 7.0, 2.0, 8.33, 3.67, 8.67, 2.08, 1.33],
    'disponibilidad': [88.9, 83.7, 92.3, 78.3, 87.0, 82.4, 78.4, 74.2, 89.4, 86.3, 85.1, 93.3],
    'reprocesos': [22.2, 33.3, 10.0, 14.3, 12.5, 22.2, 28.6, 40.0, 10.0, 25.0, 11.1, 9.1],
    'setup': [520.0, 580.0, 470.0, 180.0, 310.0, 390.0, 100.0, 450.0, 200.0, 470.0, 110.0, 80.0],
}
# Capacitación: To-Be mensual tomado de tu Power BI (simulación ADDIE) y asistentes por mes
CAP_TOBE = [92,8, 91,1, 94,6, 89,3, 87,5, 92,8, 94,6, 91,1, 91,1, 89,3, 94,6, 92,8]
CAP_ASIST_ASIS = [8, 7, 9, 6, 5, 8, 9, 7, 7, 6, 9, 8]
CAP_ASIST_TOBE = [11.1, 10.9, 11.4, 10.7, 10.5, 11.1, 11.4, 10.9, 10.9, 10.7, 11.4, 11.1]
TOTAL_COLAB = 12

META_OT = 90.0
FACTURACIÓN_ANUAL = 2_585_000

ROJO, VERDE, AZUL, ROSA, MORADO, NARANJA, CIAN, AMBAR, NAVY = (
    "#FF3D5A", "#00D68F", "#2F80FF", "#FF2D87", "#7C3AED", "#FF7A00", "#00B8D9", "#FFC400", "#16163A")

MOTIVOS = [
    dict(id="C1", icono="🎓", color=MORADO, nombre="Capacitación", col="capacitacion",
         ind="% de asistencia a capacitaciones", unidad="%", as_is=61.8, to_be=91.8, estandar=90.0, mejor="mayor",
         metodo="ADDIE", metodo_det="ADDIE (Análisis, Diseño, Desarrollo, Implementación, Evaluación) · Luo et al. (2024)",
         formula="C(asist) = (N° de colaboradores que asistieron / Total de colaboradores del área) × 100",
         causa="Ausencia de un programa de capacitación continua en mantenimiento preventivo y autónomo."),
    dict(id="C2", icono="⏱️", color=NARANJA, nombre="Tiempos muertos", col="tiempo_muerto",
         ind="Tiempo muerto mensual", unidad="horas", as_is=6.65, to_be=3.18, estandar=3.42, mejor="menor",
         metodo="Sistema de optimización de programación inteligente",
         metodo_det="Sistema inteligente de optimización de programación (programación inteligente de recursos)",
         formula="Horas muertas por mes = Σ horas sin actividad productiva durante el servicio",
         causa="Ausencia de un procedimiento para asegurar oportunamente los recursos requeridos para el mantenimiento."),
    dict(id="C3", icono="🛠️", color=CIAN, nombre="Disponibilidad", col="disponibilidad",
         ind="Disponibilidad de equipos", unidad="%", as_is=84.9, to_be=95.3, estandar=95.0, mejor="mayor",
         metodo="TPM", metodo_det="TPM (Mantenimiento Productivo Total)",
         formula="Disponibilidad = MTBF / (MTBF + MTTR) × 100",
         causa="Averías recurrentes por mantenimiento correctivo no programado que reducen las ventanas de tiempo para el preventivo."),
    dict(id="C4", icono="🔁", color=ROSA, nombre="Reprocesos", col="reprocesos",
         ind="% de equipos con segundo mantenimiento", unidad="%", as_is=19.9, to_be=3.4, estandar=5.0, mejor="menor",
         metodo="DMAIC", metodo_det="DMAIC (Definir, Medir, Analizar, Mejorar, Controlar) · Six Sigma",
         formula="Reprocesos = (N° equipos con segundo mantenimiento / Total de equipos atendidos) × 100",
         causa="Ausencia de un protocolo de verificación de conformidad al finalizar el mantenimiento preventivo."),
    dict(id="C5", icono="⚙️", color=AMBAR, nombre="Configuración", col="configuración",
         ind="Tiempo de setup mensual", unidad="minutos", as_is=321.7, to_be=166.1, estandar=140.4, mejor="menor",
         metodo="SMED", metodo_det="SMED (Cambio rápido de herramientas / preparación)",
         formula="Setup mensual = Σ minutos de preparación previa al servicio de mantenimiento",
         causa="Ausencia de un procedimiento estandarizado para la preparación previa del servicio de mantenimiento."),
]

# ---------- DataFrames ----------
semanal = pd.DataFrame(SEMANAL, columns=["semana", "programados", "ejecutados", "costo_tracto", "costo_tolva"])
semanal["cumplimiento"] = semanal["ejecutados"] / semanal["programados"] * 100
semanal["costo_total"] = semanal["costo_tracto"] + semanal["costo_tolva"]


def serie_a_ser(m):
    """To-Be mensual: C1 usa tus valores del Power BI; el resto es una simulación coherente
    (misma forma del As-Is, promedio igual al To-Be del Excel)."""
    if m["col"] == "capacitacion":
        devolver CAP_TOBE
    base = ASIS_MENSUAL[m["col"]]
    promesa = suma(base) / longitud(base)
    si m["mejor"] == "mayor":
        return [round(min(100, m["to_be"] + (v - prom) * 0.35), 1) for v in base]
    devolver [round(v * m["to_be"] / prom, 2) para v en base]


mensual = pd.DataFrame({"mes": MESES, "abrev": ABREV})
para m en MOTIVOS:
    mensual[m["col"] + "_asis"] = ASIS_MENSUAL[m["col"]]
    mensual[m["col"] + "_tobe"] = serie_tobe(m)

resumen = pd.DataFrame(MOTIVOS)


def mejora(as_is, to_be, mejor):
    devolver (to_be - as_is) / as_is * 100 si mejor == "mayor" sino (as_is - to_be) / as_is * 100


def cumple(valor, est, mejor):
    return valor >= est if mejor == "mayor" else valor <= est


# ======================= ESTILOS ========================
st.markdown(f"""
<style>
.stApp {{ background: linear-gradient(135deg,#F4F7FF 0%,#FFF4FA 50%,#F0FFF9 100%); }}
sección[data-testid="stSidebar"] > div {{ background: linear-gradient(180deg,#0A2A7A 0%,#1456D6 55%,#2F9BFF 100%); }}
sección[data-testid="stSidebar"] * {{ color: #FFFFFF; }}
sección[data-testid="stSidebar"] .stButton > botón {{
    ancho:100%; alineación de texto:izquierda; radio de borde:12px; borde:1px sólido rgba(255,255,255,.25);
    fondo: rgba(255,255,255,.08); peso de fuente:700; relleno:.55rem .8rem; transición:all .2s; }}
sección[data-testid="stSidebar"] .stButton > botón:hover {{ background: rgba(255,255,255,.25); transform: translateX(4px); }}
sección[data-testid="stSidebar"] .stButton > botón[kind="primary"] {{
    fondo: gradiente-lineal(90deg,#E5173F,#FF3D5A); color:#FFFFFF !importante; borde:ninguno; }}
sección[data-testid="stSidebar"] .stButton > botón[kind="primary"] p {{ color:#FFFFFF !important; }}
.banner {{ border-radius:18px; padding:18px 26px; color:#fff; box-shadow:0 8px 22px rgba(0,0,0,.18); margin-bottom:14px; }}
.banner h1 {{ margin:0; font-size:1.9rem; color:#fff; }}
.banner p {{ margin:4px 0 0 0; opacity:.95; font-size:.95rem; }}
.chip {{ display:inline-block; padding:5px 12px; border-radius:999px; background:rgba(255,255,255,.22);
        font-size:.82rem; font-weight:700; margin:8px 8px 0 0; border:1px solid rgba(255,255,255,.4); }}
.kpi {{ border-radius:16px; padding:14px 16px; color:#fff; box-shadow:0 6px 16px rgba(0,0,0,.15); min-height:120px; }}
.kpi .t {{ font-size:.72rem; font-weight:800; letter-spacing:.6px; text-transform:uppercase; opacity:.92; }}
.kpi .s {{ font-size:.78rem; opacity:.9; }}
.kpi .v {{ font-size:2.1rem; font-weight:900; line-height:1.15; margin:4px 0; }}
.panel {{ background:#fff; border-radius:16px; padding:6px 10px; box-shadow:0 4px 14px rgba(0,0,0,.08); }}
.empresa {{ text-align:center; padding:6px 0 2px 0; }}
.empresa h2 {{ margin:0; font-size:1.55rem; letter-spacing:1px; color:#fff; }}
.servicio {{ background:rgba(255,255,255,.12); border-left:5px solid {AMBAR}; border-radius:10px;
             relleno: 7px 10px; margen: 6px 0; tamaño de fuente: 0.88rem; peso de fuente: 600; }}
.sección {{ font-size:.78rem; font-weight:800; letter-spacing:1.5px; margin:14px 0 4px 0; color:{AMBAR}; }}
</style>
"", unsafe_allow_html=True)


def kpi(titulo, valor, sub, color, color2=Ninguno):
    color2 = color2 o color
    st.markdown(f"""<div class="kpi" style="background:linear-gradient(135deg,{color},{color2});">
        <div class="t">{titulo}</div><div class="v">{valor}</div><div class="s">{sub}</div></div>""",
                unsafe_allow_html=True)


def banner(título, subtítulo, color, color2, chips=()):
    ch = "".join(f'<span class="chip">{c}</span>' para c en chips)
    st.markdown(f"""<div class="banner" style="background:linear-gradient(110deg,{color},{color2});">
        <h1>{título}</h1><p>{sub}</p>{ch}</div>""", unsafe_allow_html=True)


# ======================= ESTADO (interconexión) ========================
Si "pagina" no está en st.session_state:
    st.session_state.pagina = "resumen"
Si "meses_sel" no está en st.session_state:
    st.session_state.meses_sel = [] # vacío = todos los meses
Si "escenario" no está en st.session_state:
    st.session_state.escenario = "Ambos"


def ir(p):
    st.session_state.pagina = p


# ======================= PANEL IZQUIERDO ========================
con st.sidebar:
    st.markdown("""<div class="empresa"><div style="font-size:2.6rem">🚛</div>
        <h2>TRANSVISA EIRL</h2><div style="font-size:.8rem;opacity:.85">TGM · Año 2025</div></div>""",
                unsafe_allow_html=True)
    st.markdown('<div class="seccion">SERVICIOS</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="servicio">🚚 Transporte de carga pesada</div>
    <div class="servicio" style="border-left-color:#00D68F">🛢️ Fabricación de cisternas</div>
    <div class="servicio" style="border-left-color:#FF2D87">🔧 Mantenimiento</div>""", unsafe_allow_html=True)

    st.markdown('<div class="seccion">PANEL</div>', unsafe_allow_html=True)
    st.button("📋 Resumen ejecutivo", on_click=ir, args=("resumen",), key="b_res",
              type="primary" if st.session_state.pagina == "resumen" else "secondary")
    st.button("🚨 Problema general", on_click=ir, args=("general",), key="b_gen",
              type="primary" if st.session_state.pagina == "general" else "secondary")

    st.markdown('<div class="seccion">LAS 5 CAUSAS</div>', unsafe_allow_html=True)
    puntos = {"C1": "🟣", "C2": "🟠", "C3": "🔵", "C4": "🌸", "C5": "🟡"}
    para m en MOTIVOS:
        st.button(f"{puntos[m['id']]} {m['icono']} {m['id']} · {m['nombre']}", on_click=ir, args=(m["id"],),
                  clave="b_" + m["id"], tipo="primario" si st.session_state.pagina == m["id"] sino "secundario")
    st.caption("Fuente: Excel del equipo (hojas Ficha Técnica y Planteamiento)")

pagina = st.session_state.pagina

# ======================= PÁGINA: RESUMEN EJECUTIVO ========================
si pagina == "resumen":
    banner("📋 RESUMEN EJECUTIVO", "Baja eficacia del cumplimiento de mantenimiento preventivo · TGM / Transvisa EIRL",
           AZUL, MORADO, ["🎯 5 causas raíz", "📈 As-Is vs To-Be", "🧰 5 metodologías"])
    cumpl = semanal["cumplimiento"].mean()
    costo = semanal["costo_total"].sum()
    ok = suma(cumple(m["to_be"], m["estandar"], m["mejor"]) for m in MOTIVOS)

    c1, c2, c3, c4 = st.columns(4)
    con c1: kpi("✅ Cumplimiento OT (As-Is)", f"{cumpl:.1f}%", f"Meta {META_OT:.0f}% · {cumpl - META_OT:.1f} pp", ROJO, "#FF7A00")
    con c2: kpi("💰 Impacto económico", f"S/ {costo:,.0f}", "Costo tracto + tolva/cisterna", AZUL, CIAN)
    con c3: kpi("📉 % facturación anual", f"{costo / FACTURACION_ANUAL * 100:.1f}%", f"Facturación S/ {FACTURACION_ANUAL:,.0f}", MORADO, ROSA)
    with c4: kpi("🏆 To-Be cumple estándar", f"{ok} de {len(MOTIVOS)}", "Causas que alcanzan su estándar", "#00A878", VERDE)

    st.markdown("### 🎯 Las 5 causas de un vistazo")
    columnas = st.columns(5)
    para col, m en zip(cols, MOTIVOS):
        u = "%" if m["unidad"] == "%" else f" {m['unidad'][:3]}."
        mj = mejora(m["as_is"], m["to_be"], m["mejor"])
        c = cumple(m["to_be"], m["estandar"], m["mejor"])
        con col:
            kpi(f"{m['icono']} {m['id']} · {m['nombre']}", f"{m['to_be']:,.1f}{u}",
                f"Tal cual {m['as_is']:,.1f}{u} · ▲ {mj:.0f}% · {'✔ cumple' si c sino '✖ no cumple'}", m["color"], NAVY)

    resumen["mejora_pct"] = resumen.apply(lambda r: mejora(r.as_is, r.to_be, r.mejor), axis=1)
    resumen["etiqueta"] = resumen["id"] + " · " + resumen["nombre"]
    fig = px.bar(resumen, x="etiqueta", y="mejora_pct", color="etiqueta",
                 color_discrete_sequence=[m["color"] para m en MOTIVOS],
                 text=resumen["mejora_pct"].round(1).astype(str) + "%",
                 title="📈 Mejora esperada por causa (To-Be vs As-Is)", etiquetas={"mejora_pct": "% de mejora", "etiqueta": ""})
    fig.update_traces(textposition="outside")
    fig.update_layout(showlegend=False, plot_bgcolor="white", paper_bgcolor="white")
    st.plotly_chart(fig)

    tabla = resumen[["id", "nombre", "unidad", "as_is", "to_be", "estandar", "metodo"]].copy()
    tabla["Cumple"] = [("✅ Sí" if cumple(r.to_be, r.estandar, r.mejor) else "❌ No") for r in resumen.itertuples()]
    tabla.columns = ["ID", "Causa", "Unidad", "As-Is", "To-Be", "Estándar", "Metodología", "To-Be cumple estándar"]
    st.dataframe(tabla, hide_index=True)

# ======================= PÁGINA: PROBLEMA GENERAL =======================
elif pagina == "general":
    banner("🚨 PROBLEMA GENERAL", "Baja eficacia del cumplimiento de mantenimiento preventivo", ROJO, NARANJA,
           ["📅 Periodos quincenales 2025", f"🎯 Meta {META_OT:.0f}% de cumplimiento de OT"])
    prog, ejec = semanal["programados"].sum(), semanal["ejecutados"].sum()
    cumpl = semanal["cumplimiento"].mean()
    costo = semanal["costo_total"].sum()
    c1, c2, c3, c4 = st.columns(4)
    con c1: kpi("✅ Cumplimiento OT", f"{cumpl:.1f}%", f"{cumpl - META_OT:.1f} pp vs meta {META_OT:.0f}%", ROJO, NARANJA)
    con c2: kpi("📝 OT ejecutadas / programadas", f"{ejec} / {prog}", "Total del año", AZUL, CIAN)
    con c3: kpi("💰 Impacto económico", f"S/ {costo:,.0f}", "Tracto + tolva/cisterna", MORADO, ROSA)
    con c4: kpi("📉 % facturación anual", f"{costo / FACTURACION_ANUAL * 100:.1f}%", "Sobre ingresos anuales", "#00A878", VERDE)

    fig = px.line(semanal, x="semana", y="cumplimiento", marcadores=True,
                  title="📈 % de cumplimiento de órdenes de trabajo por quincena")
    fig.update_traces(line_color=ROSA, line_width=3, marker=dict(size=9, color=AZUL))
    fig.add_hline(y=META_OT, line_dash="dash", line_color=ROJO, annotation_text=f"Meta {META_OT:.0f}%",
                  posición_de_anotación="superior izquierda")
    fig.update_layout(yaxis_title="% cumplimiento", xaxis_title="", yaxis_range=[0, 110],
                      plot_bgcolor="white", paper_bgcolor="white")
    st.plotly_chart(fig)

    costos = semanal.melt(id_vars="semana", value_vars=["costo_tracto", "costo_tolva"], var_name="tipo", value_name="costo")
    costos["tipo"] = costos["tipo"].map({"costo_tracto": "🚛 Tracto", "costo_tolva": "🛢️ Tolva / cisterna"})
    fig2 = px.bar(costos, x="semana", y="costo", color="tipo", title="💸 Costo por periodo (S/)",
                  color_discrete_map={"🚛 Tracto": AZUL, "🛢️ Tolva/cisterna": NARANJA},
                  etiquetas={"costo": "S/", "semana": "", "tipo": ""})
    fig2.update_layout(plot_bgcolor="white", paper_bgcolor="white")
    st.plotly_chart(fig2)

    con st.expander("📑 Ver datos del cumplimiento semanal"):
        st.dataframe(semanal, hide_index=True)

# ======================= PÁGINAS: CAUSAS C1..C5 ========================
demás:
    m = next(x para x en MOTIVOS si x["id"] == pagina)
    color = m["color"]
    u = "%" if m["unidad"] == "%" else f" {m['unidad']}"

    banner(f"{m['icono']} CAUSA {m['id'][1]} · {m['nombre'].upper()}",
           f"Causa raíz: {m['causa']}", color, MARINO,
           [f"📐 Indicador: {m['ind']}", f"🧰 Metodología: {m['metodo']}",
            f"📏 Parámetro (estándar): {m['estándar']:,.1f}{u}"])
    con st.expander("🔎 Fórmula y herramienta / metodología aplicada", expandido=False):
        st.markdown(f"**📐 Indicador:** {m['fórmula']}")
        st.markdown(f"**🧰 Herramienta / metodología:** {m['metodo_det']}")
        st.markdown(f"**📏 Parámetro (estándar):** {m['estandar']:,.1f}{u} "
                    f"({'mayor es mejor' if m['mejor'] == 'mayor' else 'menor es mejor'})")

    # ---------- Filtros interconectados (botones de mes + As-Is / To-Be) ----------
    f1, f2 = st.columns([4, 1.4])
    con f1:
        st.markdown("**📅 Meses** (sin selección = todo el año)")
        si hasattr(st, "píldoras"):
            sel = st.pills("Meses", ABREV, selection_mode="multi", key="meses_sel", label_visibility="collapsed")
        demás:
            sel = st.multiselect("Meses", ABREV, key="meses_sel", label_visibility="collapsed")
    con f2:
        st.markdown("**🔀 Escenario**")
        st.radio("Escenario", ["Ambos", "Tal como está", "Futura"], key="escenario", horizontal=True,
                 label_visibility="collapsed")
    sel = sel o ABREV
    esc = st.session_state.escenario
    df = mensual[mensual["abrev"].isin(sel)].reset_index(drop=True)
    a_col, t_col = m["col"] + "_asis", m["col"] + "_tobe"

    val_asis, val_tobe = df[a_col].mean(), df[t_col].mean()
    mj = mejora(val_asis, val_tobe, m["mejor"])
    cumple_tobe = cumple(val_tobe, m["estandar"], m["mejor"])
    meses_txt = "Todo el año" if len(sel) == 12 else ", ".join(sel)

    k = st.columns(5)
    with k[0]: kpi("🔴 As-Is · Situación actual", f"{val_asis:,.1f}{u}", f"Promedio · {meses_txt}", ROJO, "#C21F3A")
    with k[1]: kpi("🟢 To-Be · Simulación", f"{val_tobe:,.1f}{u}", f"Aplicando {m['metodo']}", "#00A878", VERDE)
    with k[2]: kpi("🎯 Estándar / Meta", f"{m['estandar']:,.1f}{u}", "Valor de referencia (parámetro)", NAVY, "#3B3B7A")
    con k[3]: kpi("🚀 Mejora esperada", f"{'▲' if mj >= 0 else '▼'} {abs(mj):.1f}%", "Frente al As-Is", AZUL, CIAN)
    con k[4]:
        kpi("🏁 Estado del To-Be", "CUMPLE ✔" if cumple_tobe else "NO CUMPLE ✖", "Comparado con el estándar",
            "#00A878" if cumple_tobe else ROJO, VERDE if cumple_tobe else NARANJA)

    g1, g2 = st.columns([1.6, 1])
    # ---------- Evolución mensual ----------
    con g1:
        fig = ir.Figura()
        Si esc en ("Ambos", "Tal cual"):
            fig.add_trace(go.Scatter(x=df["abrev"], y=df[a_col], mode="lines+markers+text", name="As-Is",
                                     texto=[f"{v:,.1f}" para v en df[a_col]], posición del texto="centro inferior",
                                     línea=dict(color=ROJO, ancho=3), marcador=dict(tamaño=10)))
        Si esc en ("Ambos", "To-Be"):
            fig.add_trace(go.Scatter(x=df["abrev"], y=df[t_col], mode="lines+markers+text", name="To-Be",
                                     texto=[f"{v:,.1f}" para v en df[t_col]], posición del texto="centro superior",
                                     línea=dict(color=VERDE, ancho=3), marcador=dict(tamaño=10)))
        fig.add_hline(y=m["estándar"], line_dash="dot", line_color=NAVY, line_width=2,
                      annotation_text=f"Estándar: {m['estandar']:,.1f}{u}", annotation_position="top right")
        fig.update_layout(title=f"📈 Evolución mensual: {esc} · {m['ind']}", yaxis_title=m["unidad"], xaxis_title="",
                          plot_bgcolor="white", paper_bgcolor="white", height=380,
                          leyenda=dict(orientación="h", y=1.12))
        st.plotly_chart(fig)

    # ---------- Termómetro ----------
    con g2:
        val_g = val_asis si esc == "Tal como está" de lo contrario val_tobe
        etiqueta = "Tal cual" if esc == "Tal cual" else "Por venir"
        max_g = 100 si m["unidad"] == "%" sino max(m["as_is"], m["estandar"], max(df[a_col])) * 1.25
        si m["mejor"] == "mayor":
            pasos = [dict(rango=[0, m["estandar"]], color="#FFD1D8"), dict(rango=[m["estandar"], max_g], color="#C9F7E4")]
        demás:
            pasos = [dict(rango=[0, m["estandar"]], color="#C9F7E4"), dict(rango=[m["estandar"], max_g], color="#FFD1D8")]
        ok_g = cumple(val_g, m["estandar"], m["mejor"])
        medidor = ir.Figura(ir.Indicador(
            modo="calibre+número", valor=redondeo(val_g, 1), número=dict(sufijo="" si m["unidad"] != "%" sino "%"),
            title=dict(text=f"🌡️ Termómetro vs estándar · {etiqueta}"),
            gauge=dict(axis=dict(range=[0, max_g]), bar=dict(color=VERDE if ok_g else ROJO), steps=pasos,
                       umbral=dict(línea=dict(color=NAVY, ancho=5), grosor=0.85, valor=m["estándar"]))))
        gauge.update_layout(height=380, paper_bgcolor="white", margin=dict(t=70, b=10))
        st.plotly_chart(gauge)

    h1, h2 = st.columns([1.6, 1])
    # ---------- Gráfico inferior ----------
    con h1:
        fig3 = ir.Figura()
        if m["col"] == "capacitacion":
            idx = [ABREV.index(a) para a en df["abrev"]]
            Si esc en ("Ambos", "Tal cual"):
                fig3.add_trace(go.Bar(x=df["abrev"], y=[CAP_ASIST_ASIS[i] for i in idx], name="Asistieron As-Is",
                                      color_marcador=ROJO, texto=[CAP_ASIST_ASIS[i] para i en idx], posición_texto="fuera"))
            Si esc en ("Ambos", "To-Be"):
                fig3.add_trace(go.Bar(x=df["abrev"], y=[CAP_ASIST_TOBE[i] for i in idx], name="Asistieron To-Be",
                                      color_marcador=VERDE, texto=[CAP_ASIST_TOBE[i] para i en idx], posición_texto="fuera"))
            fig3.add_hline(y=TOTAL_COLAB, line_dash="dot", line_color=NAVY,
                           annotation_text=f"Total colaboradores: {TOTAL_COLAB}", annotation_position="top right")
            fig3.update_layout(title="👥 Colaboradores que asistieron a la capacitación por mes", barmode="group")
        demás:
            sig = 1 si m["mejor"] == "mayor" else -1
            Si esc en ("Ambos", "Tal cual"):
                brecha = [(v - m["estandar"]) * sig for v in df[a_col]]
                fig3.add_trace(go.Bar(x=df["abrev"], y=brecha, name="Brecha tal como está", marcador_color=ROJO,
                                      texto=[f"{b:+,.1f}" para b en brecha], posición del texto="fuera"))
            Si esc en ("Ambos", "To-Be"):
                brecha = [(v - m["estandar"]) * sig for v in df[t_col]]
                fig3.add_trace(go.Bar(x=df["abrev"], y=brecha, name="Brecha Futura", marcador_color=VERDE,
                                      texto=[f"{b:+,.1f}" para b en brecha], posición del texto="fuera"))
            fig3.add_hline(y=0, line_color=NAVY)
            fig3.update_layout(title="📊 Brecha vs estándar por mes (positivo = cumple)", barmode="group")
        fig3.update_layout(plot_bgcolor="white", paper_bgcolor="white", height=340, xaxis_title="",
                           leyenda=dict(orientación="h", y=1.15))
        st.plotly_chart(fig3)

    # ---------- Detalle mensual ----------
    con h2:
        st.markdown(f"**📋 Detalle mensual ({m['unidad']})**")
        det = pd.DataFrame({"Mes": df["abrev"], "Tal como está": df[a_col].round(1), "Para ser": df[t_col].round(1),
                            "Estandar": m["estandar"]})
        Si esc == "Tal como está":
            det = det.drop(columnas=["Futura"])
        elif esc == "To-Be":
            det = det.drop(columnas=["Tal como está"])
        st.dataframe(det, hide_index=True, height=300)