"""
Dashboard TGM (Transvisa E.I.R.L.) - Baja eficacia del cumplimiento de mantenimiento preventivo
Versión 2: panel lateral de navegación + filtros dinámicos (meses y As-Is / To-Be) interconectados.
Ejecutar con:  streamlit run dashboard_tgm_v2.py
"""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="TGM | Mantenimiento preventivo", page_icon="🚛", layout="wide")

# ======================= DATOS (del Excel del equipo) =======================
SEMANAL = [['S01-02', 15, 10, 14747.8, 19894.03], ['S03-04', 8, 5, 3347.84, 8468.14], ['S04-05', 11, 6, 10635.51, 4471.74], ['S06-07', 11, 7, 18621.93, 1407.28], ['S08-09', 12, 8, 5261.22, 18017.83], ['S10-11', 14, 9, 11229.77, 29989.02], ['S12-13', 14, 10, 13467.64, 17211.7], ['S14-15', 8, 8, 18270.01, 3658.39], ['S16-17', 2, 2, 5066.83, 192.66], ['S18-19', 5, 4, 3133.43, 5416.55], ['S20-21', 7, 4, 8958.43, 2817.64], ['S22-23', 7, 4, 695.32, 134.08], ['S24-25', 4, 1, 1888.82, 560.2], ['S26-27', 18, 12, 12858.83, 7151.18], ['S28-29', 17, 12, 14418.1, 9635.9], ['S30-31', 15, 11, 7220.69, 8395.15], ['S32-33', 10, 8, 4846.09, 56401.09], ['S34-35', 7, 7, 4219.55, 2183.42], ['S36-37', 5, 3, 18895.25, 6572.13], ['S38-39', 14, 10, 21726.35, 4019.43], ['S40-41', 11, 11, 19618.58, 10931.71], ['S42-43', 7, 4, 20759.2, 1042.59], ['S44-45', 10, 8, 5648.05, 7963.19], ['S46-47', 10, 8, 11969.78, 2604.7], ['S48-49', 9, 9, 15490.3, 5380.88], ['S50-51', 11, 9, 0.0, 0.0]]
MESES = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
ABREV = [m[:3].upper() for m in MESES]
ASIS_MENSUAL = {
    'capacitacion': [66.7, 58.3, 75.0, 50.0, 41.7, 66.7, 75.0, 58.3, 58.3, 50.0, 75.0, 66.7],
    'tiempo_muerto': [11.67, 15.0, 10.83, 3.33, 5.83, 7.0, 2.0, 8.33, 3.67, 8.67, 2.08, 1.33],
    'disponibilidad': [88.9, 83.7, 92.3, 78.3, 87.0, 82.4, 78.4, 74.2, 89.4, 86.3, 85.1, 93.3],
    'reprocesos': [22.2, 33.3, 10.0, 14.3, 12.5, 22.2, 28.6, 40.0, 10.0, 25.0, 11.1, 9.1],
    'setup': [520.0, 580.0, 470.0, 180.0, 310.0, 390.0, 100.0, 450.0, 200.0, 470.0, 110.0, 80.0],
}
# Capacitación: To-Be mensual tomado de tu Power BI (simulación ADDIE) y asistentes por mes
CAP_TOBE = [92.8, 91.1, 94.6, 89.3, 87.5, 92.8, 94.6, 91.1, 91.1, 89.3, 94.6, 92.8]
CAP_ASIST_ASIS = [8, 7, 9, 6, 5, 8, 9, 7, 7, 6, 9, 8]
CAP_ASIST_TOBE = [11.1, 10.9, 11.4, 10.7, 10.5, 11.1, 11.4, 10.9, 10.9, 10.7, 11.4, 11.1]
TOTAL_COLAB = 12

META_OT = 90.0
FACTURACION_ANUAL = 2_585_000

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
         metodo="Intelligent Scheduling Optimization System",
         metodo_det="Intelligent Scheduling Optimization System (programación inteligente de recursos)",
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
    dict(id="C5", icono="⚙️", color=AMBAR, nombre="Setup", col="setup",
         ind="Tiempo de setup mensual", unidad="minutos", as_is=321.7, to_be=166.1, estandar=140.4, mejor="menor",
         metodo="SMED", metodo_det="SMED (Cambio rápido de herramientas / preparación)",
         formula="Setup mensual = Σ minutos de preparación previa al servicio de mantenimiento",
         causa="Ausencia de un procedimiento estandarizado para la preparación previa del servicio de mantenimiento."),
]

# ---------- DataFrames ----------
semanal = pd.DataFrame(SEMANAL, columns=["semana", "programados", "ejecutados", "costo_tracto", "costo_tolva"])
semanal["cumplimiento"] = semanal["ejecutados"] / semanal["programados"] * 100
semanal["costo_total"] = semanal["costo_tracto"] + semanal["costo_tolva"]


def serie_tobe(m):
    """To-Be mensual: C1 usa tus valores del Power BI; el resto es una simulación coherente
    (misma forma del As-Is, promedio igual al To-Be del Excel)."""
    if m["col"] == "capacitacion":
        return CAP_TOBE
    base = ASIS_MENSUAL[m["col"]]
    prom = sum(base) / len(base)
    if m["mejor"] == "mayor":
        return [round(min(100, m["to_be"] + (v - prom) * 0.35), 1) for v in base]
    return [round(v * m["to_be"] / prom, 2) for v in base]


mensual = pd.DataFrame({"mes": MESES, "abrev": ABREV})
for m in MOTIVOS:
    mensual[m["col"] + "_asis"] = ASIS_MENSUAL[m["col"]]
    mensual[m["col"] + "_tobe"] = serie_tobe(m)

resumen = pd.DataFrame(MOTIVOS)


def mejora(as_is, to_be, mejor):
    return (to_be - as_is) / as_is * 100 if mejor == "mayor" else (as_is - to_be) / as_is * 100


def cumple(valor, est, mejor):
    return valor >= est if mejor == "mayor" else valor <= est


# ======================= ESTILOS =======================
st.markdown(f"""
<style>
.stApp {{ background: linear-gradient(135deg,#F4F7FF 0%,#FFF4FA 50%,#F0FFF9 100%); }}
section[data-testid="stSidebar"] > div {{ background: linear-gradient(180deg,#0A2A7A 0%,#1456D6 55%,#2F9BFF 100%); }}
section[data-testid="stSidebar"] * {{ color: #FFFFFF; }}
section[data-testid="stSidebar"] .stButton > button {{
    width:100%; text-align:left; border-radius:12px; border:1px solid rgba(255,255,255,.25);
    background: rgba(255,255,255,.08); font-weight:700; padding:.55rem .8rem; transition:all .2s; }}
section[data-testid="stSidebar"] .stButton > button:hover {{ background: rgba(255,255,255,.25); transform: translateX(4px); }}
section[data-testid="stSidebar"] .stButton > button[kind="primary"] {{
    background: linear-gradient(90deg,#E5173F,#FF3D5A); color:#FFFFFF !important; border:none; }}
section[data-testid="stSidebar"] .stButton > button[kind="primary"] p {{ color:#FFFFFF !important; }}
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
             padding:7px 10px; margin:6px 0; font-size:.88rem; font-weight:600; }}
.seccion {{ font-size:.78rem; font-weight:800; letter-spacing:1.5px; margin:14px 0 4px 0; color:{AMBAR}; }}
</style>
""", unsafe_allow_html=True)


def kpi(titulo, valor, sub, color, color2=None):
    color2 = color2 or color
    st.markdown(f"""<div class="kpi" style="background:linear-gradient(135deg,{color},{color2});">
        <div class="t">{titulo}</div><div class="v">{valor}</div><div class="s">{sub}</div></div>""",
                unsafe_allow_html=True)


def banner(titulo, sub, color, color2, chips=()):
    ch = "".join(f'<span class="chip">{c}</span>' for c in chips)
    st.markdown(f"""<div class="banner" style="background:linear-gradient(110deg,{color},{color2});">
        <h1>{titulo}</h1><p>{sub}</p>{ch}</div>""", unsafe_allow_html=True)


# ======================= ESTADO (interconexión) =======================
if "pagina" not in st.session_state:
    st.session_state.pagina = "resumen"
if "meses_sel" not in st.session_state:
    st.session_state.meses_sel = []     # vacío = todos los meses
if "escenario" not in st.session_state:
    st.session_state.escenario = "Ambos"


def ir(p):
    st.session_state.pagina = p


# ======================= PANEL IZQUIERDO =======================
with st.sidebar:
    st.markdown("""<div class="empresa"><div style="font-size:2.6rem">🚛</div>
        <h2>TRANSVISA E.I.R.L.</h2><div style="font-size:.8rem;opacity:.85">TGM · Año 2025</div></div>""",
                unsafe_allow_html=True)
    st.markdown('<div class="seccion">SERVICIOS</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="servicio">🚚 Transporte de carga pesada</div>
    <div class="servicio" style="border-left-color:#00D68F">🛢️ Fabricación de cisternas</div>
    <div class="servicio" style="border-left-color:#FF2D87">🔧 Mantenimiento</div>""", unsafe_allow_html=True)

    st.markdown('<div class="seccion">PANEL</div>', unsafe_allow_html=True)
    st.button("📋  Resumen ejecutivo", on_click=ir, args=("resumen",), key="b_res",
              type="primary" if st.session_state.pagina == "resumen" else "secondary")
    st.button("🚨  Problema general", on_click=ir, args=("general",), key="b_gen",
              type="primary" if st.session_state.pagina == "general" else "secondary")

    st.markdown('<div class="seccion">LAS 5 CAUSAS</div>', unsafe_allow_html=True)
    puntos = {"C1": "🟣", "C2": "🟠", "C3": "🔵", "C4": "🌸", "C5": "🟡"}
    for m in MOTIVOS:
        st.button(f"{puntos[m['id']]} {m['icono']}  {m['id']} · {m['nombre']}", on_click=ir, args=(m["id"],),
                  key="b_" + m["id"], type="primary" if st.session_state.pagina == m["id"] else "secondary")
    st.caption("Fuente: Excel del equipo (hojas Ficha Técnica y Planteamiento)")

pagina = st.session_state.pagina

# ======================= PÁGINA: RESUMEN EJECUTIVO =======================
if pagina == "resumen":
    banner("📋 RESUMEN EJECUTIVO", "Baja eficacia del cumplimiento de mantenimiento preventivo · TGM / Transvisa E.I.R.L.",
           AZUL, MORADO, ["🎯 5 causas raíz", "📈 As-Is vs To-Be", "🧰 5 metodologías"])
    cumpl = semanal["cumplimiento"].mean()
    costo = semanal["costo_total"].sum()
    ok = sum(cumple(m["to_be"], m["estandar"], m["mejor"]) for m in MOTIVOS)

    c1, c2, c3, c4 = st.columns(4)
    with c1: kpi("✅ Cumplimiento OT (As-Is)", f"{cumpl:.1f}%", f"Meta {META_OT:.0f}% · {cumpl - META_OT:.1f} pp", ROJO, "#FF7A00")
    with c2: kpi("💰 Impacto económico", f"S/ {costo:,.0f}", "Costo tracto + tolva/cisterna", AZUL, CIAN)
    with c3: kpi("📉 % facturación anual", f"{costo / FACTURACION_ANUAL * 100:.1f}%", f"Facturación S/ {FACTURACION_ANUAL:,.0f}", MORADO, ROSA)
    with c4: kpi("🏆 To-Be cumple estándar", f"{ok} de {len(MOTIVOS)}", "Causas que alcanzan su estándar", "#00A878", VERDE)

    st.markdown("### 🎯 Las 5 causas de un vistazo")
    cols = st.columns(5)
    for col, m in zip(cols, MOTIVOS):
        u = "%" if m["unidad"] == "%" else f" {m['unidad'][:3]}."
        mj = mejora(m["as_is"], m["to_be"], m["mejor"])
        c = cumple(m["to_be"], m["estandar"], m["mejor"])
        with col:
            kpi(f"{m['icono']} {m['id']} · {m['nombre']}", f"{m['to_be']:,.1f}{u}",
                f"As-Is {m['as_is']:,.1f}{u} · ▲ {mj:.0f}% · {'✔ cumple' if c else '✖ no cumple'}", m["color"], NAVY)

    resumen["mejora_pct"] = resumen.apply(lambda r: mejora(r.as_is, r.to_be, r.mejor), axis=1)
    resumen["etiqueta"] = resumen["id"] + " · " + resumen["nombre"]
    fig = px.bar(resumen, x="etiqueta", y="mejora_pct", color="etiqueta",
                 color_discrete_sequence=[m["color"] for m in MOTIVOS],
                 text=resumen["mejora_pct"].round(1).astype(str) + "%",
                 title="📈 Mejora esperada por causa (To-Be vs As-Is)", labels={"mejora_pct": "% de mejora", "etiqueta": ""})
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
    with c1: kpi("✅ Cumplimiento OT", f"{cumpl:.1f}%", f"{cumpl - META_OT:.1f} pp vs meta {META_OT:.0f}%", ROJO, NARANJA)
    with c2: kpi("📝 OT ejecutadas / programadas", f"{ejec} / {prog}", "Total del año", AZUL, CIAN)
    with c3: kpi("💰 Impacto económico", f"S/ {costo:,.0f}", "Tracto + tolva/cisterna", MORADO, ROSA)
    with c4: kpi("📉 % facturación anual", f"{costo / FACTURACION_ANUAL * 100:.1f}%", "Sobre ingresos anuales", "#00A878", VERDE)

    fig = px.line(semanal, x="semana", y="cumplimiento", markers=True,
                  title="📈 % de cumplimiento de órdenes de trabajo por quincena")
    fig.update_traces(line_color=ROSA, line_width=3, marker=dict(size=9, color=AZUL))
    fig.add_hline(y=META_OT, line_dash="dash", line_color=ROJO, annotation_text=f"Meta {META_OT:.0f}%",
                  annotation_position="top left")
    fig.update_layout(yaxis_title="% cumplimiento", xaxis_title="", yaxis_range=[0, 110],
                      plot_bgcolor="white", paper_bgcolor="white")
    st.plotly_chart(fig)

    costos = semanal.melt(id_vars="semana", value_vars=["costo_tracto", "costo_tolva"], var_name="tipo", value_name="costo")
    costos["tipo"] = costos["tipo"].map({"costo_tracto": "🚛 Tracto", "costo_tolva": "🛢️ Tolva / cisterna"})
    fig2 = px.bar(costos, x="semana", y="costo", color="tipo", title="💸 Costo por periodo (S/)",
                  color_discrete_map={"🚛 Tracto": AZUL, "🛢️ Tolva / cisterna": NARANJA},
                  labels={"costo": "S/", "semana": "", "tipo": ""})
    fig2.update_layout(plot_bgcolor="white", paper_bgcolor="white")
    st.plotly_chart(fig2)

    with st.expander("📑 Ver datos del cumplimiento semanal"):
        st.dataframe(semanal, hide_index=True)

# ======================= PÁGINAS: CAUSAS C1..C5 =======================
else:
    m = next(x for x in MOTIVOS if x["id"] == pagina)
    color = m["color"]
    u = "%" if m["unidad"] == "%" else f" {m['unidad']}"

    banner(f"{m['icono']} CAUSA {m['id'][1]} · {m['nombre'].upper()}",
           f"Causa raíz: {m['causa']}", color, NAVY,
           [f"📐 Indicador: {m['ind']}", f"🧰 Metodología: {m['metodo']}",
            f"📏 Parámetro (estándar): {m['estandar']:,.1f}{u}"])
    with st.expander("🔎 Fórmula y herramienta / metodología aplicada", expanded=False):
        st.markdown(f"**📐 Indicador:** {m['formula']}")
        st.markdown(f"**🧰 Herramienta / metodología:** {m['metodo_det']}")
        st.markdown(f"**📏 Parámetro (estándar):** {m['estandar']:,.1f}{u} "
                    f"({'mayor es mejor' if m['mejor'] == 'mayor' else 'menor es mejor'})")

    # ---------- Filtros interconectados (botones de mes + As-Is / To-Be) ----------
    f1, f2 = st.columns([4, 1.4])
    with f1:
        st.markdown("**📅 Meses** (sin selección = todo el año)")
        if hasattr(st, "pills"):
            sel = st.pills("Meses", ABREV, selection_mode="multi", key="meses_sel", label_visibility="collapsed")
        else:
            sel = st.multiselect("Meses", ABREV, key="meses_sel", label_visibility="collapsed")
    with f2:
        st.markdown("**🔀 Escenario**")
        st.radio("Escenario", ["Ambos", "As-Is", "To-Be"], key="escenario", horizontal=True,
                 label_visibility="collapsed")
    sel = sel or ABREV
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
    with k[3]: kpi("🚀 Mejora esperada", f"{'▲' if mj >= 0 else '▼'} {abs(mj):.1f}%", "Frente al As-Is", AZUL, CIAN)
    with k[4]:
        kpi("🏁 Estado del To-Be", "CUMPLE ✔" if cumple_tobe else "NO CUMPLE ✖", "Comparado con el estándar",
            "#00A878" if cumple_tobe else ROJO, VERDE if cumple_tobe else NARANJA)

    g1, g2 = st.columns([1.6, 1])
    # ---------- Evolución mensual ----------
    with g1:
        fig = go.Figure()
        if esc in ("Ambos", "As-Is"):
            fig.add_trace(go.Scatter(x=df["abrev"], y=df[a_col], mode="lines+markers+text", name="As-Is",
                                     text=[f"{v:,.1f}" for v in df[a_col]], textposition="bottom center",
                                     line=dict(color=ROJO, width=3), marker=dict(size=10)))
        if esc in ("Ambos", "To-Be"):
            fig.add_trace(go.Scatter(x=df["abrev"], y=df[t_col], mode="lines+markers+text", name="To-Be",
                                     text=[f"{v:,.1f}" for v in df[t_col]], textposition="top center",
                                     line=dict(color=VERDE, width=3), marker=dict(size=10)))
        fig.add_hline(y=m["estandar"], line_dash="dot", line_color=NAVY, line_width=2,
                      annotation_text=f"Estándar: {m['estandar']:,.1f}{u}", annotation_position="top right")
        fig.update_layout(title=f"📈 Evolución mensual: {esc} · {m['ind']}", yaxis_title=m["unidad"], xaxis_title="",
                          plot_bgcolor="white", paper_bgcolor="white", height=380,
                          legend=dict(orientation="h", y=1.12))
        st.plotly_chart(fig)

    # ---------- Termómetro (gauge) ----------
    with g2:
        val_g = val_asis if esc == "As-Is" else val_tobe
        etiqueta = "As-Is" if esc == "As-Is" else "To-Be"
        max_g = 100 if m["unidad"] == "%" else max(m["as_is"], m["estandar"], max(df[a_col])) * 1.25
        if m["mejor"] == "mayor":
            pasos = [dict(range=[0, m["estandar"]], color="#FFD1D8"), dict(range=[m["estandar"], max_g], color="#C9F7E4")]
        else:
            pasos = [dict(range=[0, m["estandar"]], color="#C9F7E4"), dict(range=[m["estandar"], max_g], color="#FFD1D8")]
        ok_g = cumple(val_g, m["estandar"], m["mejor"])
        gauge = go.Figure(go.Indicator(
            mode="gauge+number", value=round(val_g, 1), number=dict(suffix="" if m["unidad"] != "%" else "%"),
            title=dict(text=f"🌡️ Termómetro vs estándar · {etiqueta}"),
            gauge=dict(axis=dict(range=[0, max_g]), bar=dict(color=VERDE if ok_g else ROJO), steps=pasos,
                       threshold=dict(line=dict(color=NAVY, width=5), thickness=0.85, value=m["estandar"]))))
        gauge.update_layout(height=380, paper_bgcolor="white", margin=dict(t=70, b=10))
        st.plotly_chart(gauge)

    h1, h2 = st.columns([1.6, 1])
    # ---------- Gráfico inferior ----------
    with h1:
        fig3 = go.Figure()
        if m["col"] == "capacitacion":
            idx = [ABREV.index(a) for a in df["abrev"]]
            if esc in ("Ambos", "As-Is"):
                fig3.add_trace(go.Bar(x=df["abrev"], y=[CAP_ASIST_ASIS[i] for i in idx], name="Asistieron As-Is",
                                      marker_color=ROJO, text=[CAP_ASIST_ASIS[i] for i in idx], textposition="outside"))
            if esc in ("Ambos", "To-Be"):
                fig3.add_trace(go.Bar(x=df["abrev"], y=[CAP_ASIST_TOBE[i] for i in idx], name="Asistieron To-Be",
                                      marker_color=VERDE, text=[CAP_ASIST_TOBE[i] for i in idx], textposition="outside"))
            fig3.add_hline(y=TOTAL_COLAB, line_dash="dot", line_color=NAVY,
                           annotation_text=f"Total colaboradores: {TOTAL_COLAB}", annotation_position="top right")
            fig3.update_layout(title="👥 Colaboradores que asistieron a la capacitación por mes", barmode="group")
        else:
            sig = 1 if m["mejor"] == "mayor" else -1
            if esc in ("Ambos", "As-Is"):
                brecha = [(v - m["estandar"]) * sig for v in df[a_col]]
                fig3.add_trace(go.Bar(x=df["abrev"], y=brecha, name="Brecha As-Is", marker_color=ROJO,
                                      text=[f"{b:+,.1f}" for b in brecha], textposition="outside"))
            if esc in ("Ambos", "To-Be"):
                brecha = [(v - m["estandar"]) * sig for v in df[t_col]]
                fig3.add_trace(go.Bar(x=df["abrev"], y=brecha, name="Brecha To-Be", marker_color=VERDE,
                                      text=[f"{b:+,.1f}" for b in brecha], textposition="outside"))
            fig3.add_hline(y=0, line_color=NAVY)
            fig3.update_layout(title="📊 Brecha vs estándar por mes (positivo = cumple)", barmode="group")
        fig3.update_layout(plot_bgcolor="white", paper_bgcolor="white", height=340, xaxis_title="",
                           legend=dict(orientation="h", y=1.15))
        st.plotly_chart(fig3)

    # ---------- Detalle mensual ----------
    with h2:
        st.markdown(f"**📋 Detalle mensual ({m['unidad']})**")
        det = pd.DataFrame({"Mes": df["abrev"], "As-Is": df[a_col].round(1), "To-Be": df[t_col].round(1),
                            "Estándar": m["estandar"]})
        if esc == "As-Is":
            det = det.drop(columns=["To-Be"])
        elif esc == "To-Be":
            det = det.drop(columns=["As-Is"])
        st.dataframe(det, hide_index=True, height=300)
