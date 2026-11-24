"""Prototipo Kaufmann — Slotting inteligente con IA (alternativa 1A), bodega 1151 Padre Las Casas.
Prototipo académico del Proyecto Integrado (INACAP). Ejecutar con:  streamlit run app.py
"""
import io
import os
from html import escape as hx

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from motor import calcular, ZONAS, NOMBRES_ESC, META_KPI2, MEJORA_INFORME

st.set_page_config(page_title='Prototipo Kaufmann · Slotting con IA', page_icon='📦', layout='wide')

CSS = """
<style>
.block-container {max-width: 1180px; padding-top: 1.6rem;}
#MainMenu, footer, header [data-testid="stToolbar"] {visibility: hidden;}
.hero {background: linear-gradient(120deg, #0b1f3a 0%, #12386b 60%, #1f6feb 100%); color: #fff;
       border-radius: 18px; padding: 26px 30px; margin-bottom: 14px;}
.hero h1 {color: #fff; font-size: 30px; margin: 0 0 6px 0; padding: 0; letter-spacing: -0.3px;}
.hero p {color: #d6e2f5; margin: 0; font-size: 15px;}
.hero .tag {display: inline-block; background: rgba(255,255,255,.14); border: 1px solid rgba(255,255,255,.25);
            border-radius: 999px; padding: 3px 12px; font-size: 12px; margin-bottom: 12px; color: #fff;}
.steps {display: flex; gap: 10px; margin-top: 16px; flex-wrap: wrap;}
.step {background: rgba(255,255,255,.10); border-radius: 10px; padding: 8px 12px; font-size: 13px; color: #fff;}
.step b {background: #fff; color: #12386b; border-radius: 999px; padding: 0 7px; margin-right: 6px;}
.res-head {font-size: 14px; color: #475467; margin: 14px 2px 10px;}
.kpi-grid {display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px;}
@media (max-width: 900px) {.kpi-grid {grid-template-columns: repeat(2, 1fr);}}
.kpi {background: #fff; border: 1px solid #e4e7ec; border-radius: 14px; padding: 14px 16px;
      box-shadow: 0 1px 2px rgba(16,24,40,.05);}
.kpi-t {font-size: 12px; color: #667085; text-transform: uppercase; letter-spacing: .4px;}
.kpi-v {margin-top: 6px; display: flex; align-items: baseline; gap: 8px;}
.kpi-hoy {font-size: 16px; color: #98a2b3; text-decoration: line-through;}
.kpi-arrow {color: #98a2b3;}
.kpi-new {font-size: 28px; font-weight: 700; color: #12386b;}
.kpi-n {font-size: 12px; color: #039855; margin-top: 2px; font-weight: 600;}
.chips {display: flex; gap: 10px; flex-wrap: wrap; margin-top: 12px;}
.chip {background: #eef2f7; border-radius: 999px; padding: 7px 14px; font-size: 13px; color: #344054;}
.dot {display: inline-block; width: 8px; height: 8px; border-radius: 50%; margin: 0 4px 0 10px;}
.dot.r {background: #d92d20;} .dot.y {background: #f79009;} .dot.g {background: #12b76a;}
.tw {background: #fff; border: 1px solid #e4e7ec; border-radius: 14px; overflow-x: auto;
      box-shadow: 0 1px 2px rgba(16,24,40,.05); margin: 6px 0 14px;}
.tb {width: 100%; border-collapse: collapse; font-size: 13.5px; color: #344054;}
.tb th {background: #f8fafc; color: #667085; font-size: 11.5px; font-weight: 600; text-transform: uppercase;
        letter-spacing: .4px; text-align: left; padding: 10px 14px; border-bottom: 1px solid #e4e7ec; vertical-align: bottom;}
.tb td {padding: 10px 14px; border-bottom: 1px solid #f0f2f5; vertical-align: middle;}
.tb tr:last-child td {border-bottom: none;}
.tb tbody tr:hover {background: #f8fbff;}
.tb td.b {font-weight: 600; color: #1d2939; min-width: 190px;}
.tb.rec th {white-space: nowrap;}
.tb tr.hl td {background: #eef5ff; color: #12386b; font-weight: 600;}
.pill {display: inline-block; border-radius: 999px; padding: 3px 11px; font-size: 12px; font-weight: 600; white-space: nowrap;}
.pill.alta {background: #fee4e2; color: #b42318;} .pill.media {background: #fef0c7; color: #b54708;}
.pill.baja {background: #d1fadf; color: #027a48;}
.rep {font-weight: 600; color: #1d2939;} .cod {font-size: 12px; color: #98a2b3; margin-top: 1px;}
.mov {display: flex; align-items: center; gap: 10px;}
.ub {display: flex; flex-direction: column; line-height: 1.25;}
.ub span {font-size: 11.5px;}
.ub.old b {color: #98a2b3; text-decoration: line-through; font-weight: 500;} .ub.old span {color: #98a2b3;}
.ub.new b {color: #12386b; font-size: 15px;} .ub.new span {color: #1f6feb;}
.flecha {color: #98a2b3; font-size: 16px;}
.mot {font-size: 13px; color: #475467;}
.aviso {display: flex; width: fit-content; align-items: center; gap: 5px; background: #fffaeb; color: #b54708;
  border: 1px solid #fedf89; border-radius: 6px; padding: 2px 8px; font-size: 11.5px; font-weight: 700; margin-bottom: 4px;}
.aviso svg {width: 13px; height: 13px;}
.t {white-space: nowrap;} .t0 {color: #98a2b3;} .t1 {font-weight: 700; color: #344054;} .t1.ok {color: #039855;}
.tb.rec th:last-child {text-align: right;}
.n {text-align: right; font-variant-numeric: tabular-nums;}
.pag {text-align: center; color: #667085; font-size: 13px; padding-top: 6px;}
/* Pestañas tipo botón */
.stTabs [role="tablist"] {gap: 6px; background: #eef2f7; padding: 6px; border-radius: 14px; border: none;}
.stTabs [role="tab"] {background: transparent; border-radius: 10px; padding: 8px 16px; margin: 0;}
.stTabs [role="tab"] p {font-size: 14px; font-weight: 600; color: #475467;}
.stTabs [role="tab"][aria-selected="true"] {background: #fff; box-shadow: 0 1px 3px rgba(16,24,40,.12);}
.stTabs [role="tab"][aria-selected="true"] p {color: #12386b;}
.stTabs .react-aria-SelectionIndicator {display: none;}
.stTabs [role="tabpanel"] {padding-top: 18px;}
/* Cajas con borde (st.container con key "caja_...") como tarjetas blancas */
[class*="st-key-caja"] {background: #fff; border-radius: 14px !important; border: 1px solid #e4e7ec !important;
  box-shadow: 0 1px 2px rgba(16,24,40,.05);}
/* Títulos de sección */
.sec {display: flex; gap: 12px; align-items: center; margin: 6px 0 12px;}
.sec-ic {width: 40px; height: 40px; border-radius: 12px; background: #e8f1ff; display: flex; align-items: center;
         justify-content: center; font-size: 20px; flex-shrink: 0;}
.sec h3 {margin: 0; padding: 0; font-size: 19px; color: #1d2939;}
.sec p {margin: 1px 0 0; color: #667085; font-size: 13.5px;}
/* Tarjetas de carga de archivos */
.up-t {font-weight: 700; color: #1d2939; font-size: 15px;}
.up-s {color: #667085; font-size: 12.5px; margin: 2px 0 4px;}
.up-ok {color: #039855; font-size: 12.5px; font-weight: 600;}
.vacio {text-align: center; padding: 34px 20px; color: #667085; background: #fff; border: 1px dashed #d0d5dd;
        border-radius: 14px; margin-top: 8px;}
.vacio b {display: block; color: #344054; font-size: 16px; margin: 6px 0 2px;}
.vacio .ic {font-size: 30px;}
/* Resumen por prioridad */
.prio-grid {display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 14px;}
.pc {background: #fff; border: 1px solid #e4e7ec; border-radius: 14px; padding: 14px 16px; border-left-width: 5px;}
.pc.alta {border-left-color: #d92d20;} .pc.media {border-left-color: #f79009;} .pc.baja {border-left-color: #12b76a;}
.pc-n {font-size: 26px; font-weight: 700; color: #1d2939;} .pc-t {font-size: 13px; font-weight: 700; color: #344054;}
.pc-s {font-size: 12.5px; color: #667085; margin-top: 2px;}
.guia {display: flex; gap: 10px; flex-wrap: wrap; background: #f0f6ff; border: 1px solid #d6e6ff; border-radius: 12px;
       padding: 10px 14px; margin-bottom: 14px; font-size: 13.5px; color: #12386b; align-items: center;}
.guia b {background: #12386b; color: #fff; border-radius: 999px; padding: 0 7px; margin-right: 4px; font-size: 12px;}
.guia .sep {color: #98a2b3;}
.pie {text-align: center; color: #98a2b3; font-size: 12px; margin-top: 30px;}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


def cl(x, dec=1):
    """Número en formato chileno: 8.082 y 75,6"""
    return f"{x:,.{dec}f}".replace(',', '_').replace('.', ',').replace('_', '.')


def _card(titulo, hoy, prop, nota=''):
    return (f'<div class="kpi"><div class="kpi-t">{titulo}</div>'
            f'<div class="kpi-v"><span class="kpi-hoy">{hoy}</span><span class="kpi-arrow">→</span>'
            f'<span class="kpi-new">{prop}</span></div><div class="kpi-n">{nota}</div></div>')


def tarjetas(res):
    e, real = res['escenarios'], res['real']
    hoy, prop = e['Actual'], e['v2']
    lista = res['lista']
    n = lista.prioridad.value_counts()
    pa = real['pesados_alto']
    cards = ''.join([
        _card('Cumplimiento KPI2 (4 min/línea)', f"{cl(real['kpi2'])} %", f"{cl(prop['kpi2'])} %",
              f"+{cl(prop['kpi2'] - real['kpi2'])} p.p. · meta {META_KPI2} %"),
        _card('Segundos por línea (mediana)', f"{cl(hoy['seg_linea_mediana'], 0)} s", f"{cl(prop['seg_linea_mediana'], 0)} s",
              f"−{cl((1 - prop['seg_linea_mediana'] / hoy['seg_linea_mediana']) * 100, 0)} %"),
        _card('Horas de picking al mes', f"{cl(hoy['horas_mes'], 0)} h", f"{cl(prop['horas_mes'], 0)} h",
              f"−{cl(hoy['horas_mes'] - prop['horas_mes'], 0)} h al mes"),
        _card('SKU A y B en su zona ideal', f"{cl(hoy['bien_ubicados'], 0)} %", f"{cl(prop['bien_ubicados'], 0)} %",
              'repuestos más vendidos bien ubicados'),
    ])
    return f"""
<div class="res-head">Resultado con <b>{cl(real['ordenes'], 0)}</b> órdenes reales de SAP (ago–oct 2026) · Hoy → Con slotting</div>
<div class="kpi-grid">{cards}</div>
<div class="chips">
  <div class="chip"><b>{cl(len(lista), 0)}</b> reubicaciones:
    <span class="dot r"></span>Alta {cl(n.get('Alta', 0), 0)}
    <span class="dot y"></span>Media {cl(n.get('Media', 0), 0)}
    <span class="dot g"></span>Baja {cl(n.get('Baja', 0), 0)}</div>
  <div class="chip">🦺 Pesados en rack alto: <b>{cl(pa['hoy'], 0)} → {cl(pa['v2'], 0)}</b></div>
  <div class="chip">📦 <b>{cl(real['articulos_dia'], 0)}</b> artículos pickeados por día hábil</div>
</div>
"""


NOMBRE_ZONA = {
    'EST-MB-1': 'Estantería Mercedes · piso 1', 'EST-MB-2': 'Estantería Mercedes · piso 2',
    'EST-MB-3': 'Estantería Mercedes · piso 3', 'EST-OM-1': 'Estantería otras marcas · piso 1',
    'EST-OM-2': 'Estantería otras marcas · piso 2', 'EST-OM-3': 'Estantería otras marcas · piso 3',
    'RACK-BAJO': 'Rack bajo (nivel 1–2)', 'RACK-ALTO': 'Rack alto (nivel 3 o más)', 'OTRA': 'Otra (patio, búnker, jaula)',
}
CLASE_TXT = {'A': 'Muy vendido', 'B': 'Venta media', 'C': 'Poca venta'}
PRIO_TXT = {'Alta': '🔴 Alta', 'Media': '🟡 Media', 'Baja': '🟢 Baja'}


def zona_txt(z):
    return NOMBRE_ZONA.get(z, z)


def ubicaciones_recomendadas(d):
    """Ubicación exacta recomendada para cada repuesto (misma regla del motor): dentro de cada zona,
    los repuestos que se mueven toman las ubicaciones libres y el más vendido se queda con la más cercana."""
    ubic = d.ubic.copy()
    for z, grupo in d.groupby('zona_v2'):
        if z == 'OTRA':
            continue
        fijos = grupo[~grupo.movible]
        pool = d[d.zona_actual == z].drop(fijos.index, errors='ignore').sort_values('seg_ubic')
        movs = grupo[grupo.movible].sort_values('pickings_12m', ascending=False)
        k = min(len(pool), len(movs))
        ubic.loc[movs.index[:k]] = pool.ubic.values[:k]
        ubic.loc[movs.index[k:]] = 'Espacio por definir'
    return ubic


def recomendaciones(res):
    """Tabla 'antes → después' lista para leer en bodega."""
    if 'reco' in res:
        return res['reco']
    d = res['d']
    d['ubic_v2'] = ubicaciones_recomendadas(d)
    l = d.loc[res['lista'].index]
    l = l.assign(prioridad=res['lista'].prioridad, seguridad=res['lista'].motivo.str.startswith('Seguridad'))
    acerca = l.seg_v2 < l.seg_ubic
    motivo = [('Pesado en rack alto: bajarlo por seguridad' if s else
               f"{CLASE_TXT[c]} ({c}): {'acercarlo a la entrega' if a else 'liberar espacio cercano para los más vendidos'}")
              for s, c, a in zip(l.seguridad, l.clase, acerca)]
    reco = pd.DataFrame({
        'prioridad': l.prioridad, 'codigo': l.material, 'repuesto': l.texto.fillna('').str.strip().str.title(),
        'ubic_hoy': l.ubic.fillna('—'), 'zona_hoy': l.zona_actual.map(zona_txt),
        'ubic_new': l.ubic_v2, 'zona_new': l.zona_v2.map(zona_txt), 'motivo': motivo, 'seguridad': l.seguridad,
        'seg_hoy': l.seg_ubic, 'seg_new': l.seg_v2, 'pedidos': l.pickings_12m.astype(int),
    })
    res['reco'] = reco
    return reco


def html_tabla(df, resaltar=None, primera_negrita=True):
    """Tabla simple con el mismo estilo de las tarjetas. `resaltar`: índice de fila a destacar."""
    th = ''.join(f'<th>{hx(str(c))}</th>' for c in df.columns)
    filas = []
    for i, (_, r) in enumerate(df.iterrows()):
        celdas = ''.join(f'<td{" class=b" if (j == 0 and primera_negrita) else ""}>{hx(str(v))}</td>'
                         for j, v in enumerate(r.values))
        filas.append(f'<tr{" class=hl" if i == resaltar else ""}>{celdas}</tr>')
    return f'<div class="tw"><table class="tb"><thead><tr>{th}</tr></thead><tbody>{"".join(filas)}</tbody></table></div>'


AVISO = ('<div class="aviso"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" '
         'stroke-linecap="round" stroke-linejoin="round"><path d="M10.3 3.9 1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0z"/>'
         '<line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>Advertencia de seguridad</div>')


def html_recomendaciones(v):
    """Tabla de recomendaciones: antes (tachado) → después (destacado), como las tarjetas de KPI."""
    filas = []
    for r in v.itertuples():
        p = r.prioridad.lower()
        mejor = r.seg_new < r.seg_hoy
        filas.append(
            f'<tr><td><span class="pill {p}">{r.prioridad}</span></td>'
            f'<td><div class="rep">{hx(r.repuesto)}</div><div class="cod">{hx(r.codigo)}</div></td>'
            f'<td><div class="mov"><div class="ub old"><b>{hx(r.ubic_hoy)}</b><span>{hx(r.zona_hoy)}</span></div>'
            f'<div class="flecha">→</div>'
            f'<div class="ub new"><b>{hx(r.ubic_new)}</b><span>{hx(r.zona_new)}</span></div></div></td>'
            f'<td class="mot">{AVISO if r.seguridad else ""}{hx(r.motivo)}</td>'
            f'<td class="t"><span class="t0">{r.seg_hoy:.0f} s</span> → '
            f'<span class="{"t1 ok" if mejor else "t1"}">{r.seg_new:.0f} s</span></td>'
            f'<td class="n">{cl(r.pedidos, 0)}</td></tr>')
    return ('<div class="tw"><table class="tb rec"><thead><tr><th>Prioridad</th><th>Repuesto</th>'
            '<th>Hoy está en → Moverlo a</th><th>Motivo</th><th>Tiempo por picking</th><th>Pedidos/año</th>'
            f'</tr></thead><tbody>{"".join(filas)}</tbody></table></div>')


def excel_recomendaciones(res):
    """Excel para la bodega: lo mismo que se ve en la página, con las ubicaciones en código Kaufmann (PPEE-MMNN)."""
    if 'excel_ui' in res:
        return res['excel_ui']
    from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
    from openpyxl.utils import get_column_letter
    reco, d = recomendaciones(res), res['d']
    hoja1 = pd.DataFrame({
        'Prioridad': reco.prioridad, 'Código': reco.codigo, 'Repuesto': reco.repuesto,
        'Ubicación actual': reco.ubic_hoy, 'Zona actual': reco.zona_hoy,
        'Ubicación recomendada': reco.ubic_new, 'Zona recomendada': reco.zona_new,
        'Motivo': reco.motivo,
        'Tiempo hoy (s)': reco.seg_hoy.round(0).astype(int), 'Tiempo recomendado (s)': reco.seg_new.round(0).astype(int),
        'Ahorro por picking (s)': (reco.seg_hoy - reco.seg_new).round(0).astype(int), 'Pedidos al año': reco.pedidos,
    })
    mueve = d.movible & (d.zona_v2 != d.zona_actual)
    hoja2 = pd.DataFrame({
        'Código': d.material, 'Repuesto': d.texto.fillna('').str.strip().str.title(),
        'Clase IA': d.clase.map(lambda c: f'{c} · {CLASE_TXT[c]}'), 'Pedidos al año': d.pickings_12m.astype(int),
        'Ubicación actual': d.ubic.fillna('—'), 'Zona actual': d.zona_actual.map(zona_txt),
        'Acción': mueve.map({True: 'Mover', False: 'Se queda'}),
        'Ubicación recomendada': d.ubic_v2.where(mueve, d.ubic).fillna('—'),
        'Zona recomendada': d.zona_v2.where(mueve, d.zona_actual).map(zona_txt),
    }).sort_values('Pedidos al año', ascending=False)
    hoja3 = tabla_escenarios_txt(res)
    ocup = res['ocupacion'].T.reset_index().rename(columns={'index': 'Zona'})
    ocup['Zona'] = ocup.Zona.map(zona_txt)
    for c in ocup.columns[1:]:
        ocup[c] = ocup[c].map(lambda v: cl(v) + ' %')
    hojas = [('Recomendaciones', hoja1, 'Recomendaciones de ubicación · ordenadas por prioridad'),
             ('Todos los repuestos', hoja2, 'Clasificación IA y ubicación recomendada de cada repuesto'),
             ('Resumen escenarios', hoja3, 'Comparación de escenarios (simulación con órdenes reales)'),
             ('Ocupación por zona', ocup, 'Ocupación de cada zona respecto de su capacidad actual')]
    azul, gris = '12386B', 'F2F4F7'
    fill_prio = {'Alta': 'FEE4E2', 'Media': 'FEF0C7', 'Baja': 'D1FADF'}
    font_prio = {'Alta': 'B42318', 'Media': 'B54708', 'Baja': '027A48'}
    linea = Side(style='thin', color='E4E7EC')
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine='openpyxl') as w:
        for nombre, df, sub in hojas:
            df.to_excel(w, sheet_name=nombre, index=False, startrow=3)
            ws = w.sheets[nombre]
            ws['A1'] = 'Slotting inteligente con IA · Kaufmann bodega 1151 Padre Las Casas'
            ws['A1'].font = Font(bold=True, size=14, color=azul)
            ws['A2'] = sub
            ws['A2'].font = Font(size=10, color='667085')
            n = len(df.columns)
            for j in range(1, n + 1):
                c = ws.cell(row=4, column=j)
                c.font = Font(bold=True, color='FFFFFF')
                c.fill = PatternFill('solid', fgColor=azul)
                c.alignment = Alignment(vertical='center', wrap_text=True)
                largo = max([len(str(df.columns[j - 1]))] + [len(str(x)) for x in df.iloc[:300, j - 1]])
                ws.column_dimensions[get_column_letter(j)].width = min(max(largo + 2, 10), 62)
            ws.row_dimensions[4].height = 30
            ws.page_setup.orientation = 'landscape'           # listo para imprimir y llevar a bodega
            ws.sheet_properties.pageSetUpPr.fitToPage = True
            ws.page_setup.fitToWidth, ws.page_setup.fitToHeight = 1, 0
            ws.print_title_rows = '4:4'
            ws.freeze_panes = 'C5' if nombre in ('Recomendaciones', 'Todos los repuestos') else 'B5'
            ws.auto_filter.ref = f'A4:{get_column_letter(n)}{len(df) + 4}'
            cols = list(df.columns)
            for i in range(len(df)):
                fila = i + 5
                if nombre != 'Todos los repuestos':   # hoja grande: sin bordes para que se genere rápido
                    for j in range(1, n + 1):
                        ws.cell(row=fila, column=j).border = Border(bottom=linea)
                if nombre == 'Recomendaciones':
                    p = df.iat[i, 0]
                    c = ws.cell(row=fila, column=1)
                    c.fill = PatternFill('solid', fgColor=fill_prio[p])
                    c.font = Font(bold=True, color=font_prio[p])
                    ws.cell(row=fila, column=cols.index('Ubicación actual') + 1).font = Font(color='98A2B3')
                    ws.cell(row=fila, column=cols.index('Ubicación recomendada') + 1).font = Font(bold=True, color=azul)
                elif nombre == 'Todos los repuestos':
                    if df.iat[i, cols.index('Acción')] == 'Mover':
                        ws.cell(row=fila, column=cols.index('Acción') + 1).font = Font(bold=True, color='1F6FEB')
                        ws.cell(row=fila, column=cols.index('Ubicación recomendada') + 1).font = Font(bold=True, color=azul)
                elif i % 2:
                    for j in range(1, n + 1):
                        ws.cell(row=fila, column=j).fill = PatternFill('solid', fgColor=gris)
    res['excel_ui'] = buf.getvalue()
    return res['excel_ui']


def tabla_escenarios_txt(res):
    """Tabla de escenarios con números en formato chileno."""
    t = res['tabla'].copy()
    for c in t.columns[1:]:
        dec = 0 if ('Segundos' in c or 'Horas' in c) else 1
        t[c] = t[c].map(lambda v: cl(v, dec) + (' %' if '(%)' in c else ''))
    t.columns = [c.replace(' (%)', '') for c in t.columns]
    return t


def tabla_tiempos(res):
    d = res['d']
    filas = []
    for z in ZONAS:
        g = d[d.zona_actual == z]
        if g.empty:
            continue
        filas.append({'Zona': zona_txt(z), 'Repuestos': cl(len(g), 0),
                      'Tiempo promedio': f'{g.seg_ubic.mean():.0f} s',
                      'Ubicación más cercana': f'{g.seg_ubic.min():.0f} s',
                      'Ubicación más lejana': f'{g.seg_ubic.max():.0f} s'})
    return pd.DataFrame(filas)


def grafico_kpi(res):
    e = res['escenarios']
    nombres = ['Hoy (real)'] + [NOMBRES_ESC[k] for k in ('v1', 'v2')]
    valores = [res['real']['kpi2'], e['v1']['kpi2'], e['v2']['kpi2']]
    fig, ax = plt.subplots(figsize=(8, 3.6))
    barras = ax.bar(nombres, valores, color=['#9aa5b1', '#8fb8f5', '#1f6feb'], width=0.55)
    ax.bar_label(barras, labels=[cl(v) + ' %' for v in valores], fontsize=9, padding=3)
    ax.axhline(META_KPI2, color='#d1242f', ls='--', lw=1.2)
    ax.text(2.45, META_KPI2 + 0.6, f'Meta {META_KPI2} %', color='#d1242f', ha='right', fontsize=8)
    proy = min(res['real']['kpi2'] + MEJORA_INFORME, 100)
    ax.axhline(proy, color='#bf8700', ls=':', lw=1.2)
    ax.text(2.45, proy - 2.2, f'Proyección del informe (hoy + 9,2 p.p.): {cl(proy)} %', color='#bf8700', ha='right', fontsize=8)
    ax.set_ylim(max(0, min(valores) - 15), 100)
    ax.set_ylabel('% de órdenes dentro de 4 min por línea')
    ax.set_title('KPI2: ¿cuánto mejora el cumplimiento con el slotting?')
    ax.tick_params(axis='x', labelsize=8)
    ax.spines[['top', 'right']].set_visible(False)
    fig.tight_layout()
    return fig


def grafico_zonas(res):
    d = res['d']; pk = d[d.pickings_12m > 0]
    tot = pk.pickings_12m.sum()
    hoy = pk.groupby('zona_actual').pickings_12m.sum() / tot * 100
    prop = pk.groupby('zona_v2').pickings_12m.sum() / tot * 100
    o = pd.DataFrame({'Hoy': hoy, 'Con slotting': prop}).reindex(ZONAS).fillna(0)
    fig, ax = plt.subplots(figsize=(8, 3.6))
    o.plot.bar(ax=ax, color=['#9aa5b1', '#1f6feb'], width=0.75)
    for c in ax.containers:
        ax.bar_label(c, labels=[f'{v:.0f}%' for v in c.datavalues], fontsize=7, padding=2)
    ax.set_ylabel('% de los pickings del año'); ax.set_xlabel('')
    ax.set_title('¿De qué zona salen los pickings? (piso 1 y rack bajo son los más rápidos)')
    ax.tick_params(axis='x', rotation=0, labelsize=8)
    ax.spines[['top', 'right']].set_visible(False)
    fig.tight_layout()
    return fig


def seccion(icono, titulo, sub=''):
    st.markdown(f'<div class="sec"><div class="sec-ic">{icono}</div><div><h3>{titulo}</h3>'
                f'{f"<p>{sub}</p>" if sub else ""}</div></div>', unsafe_allow_html=True)


def vacio(icono, titulo, texto):
    st.markdown(f'<div class="vacio"><div class="ic">{icono}</div><b>{titulo}</b>{texto}</div>', unsafe_allow_html=True)


def subir(col, titulo, ayuda, key):
    with col.container(border=True, key=f'caja_{key}'):
        st.markdown(f'<div class="up-t">{titulo}</div><div class="up-s">{ayuda}</div>', unsafe_allow_html=True)
        f = st.file_uploader(titulo, type='xlsx', key=key, label_visibility='collapsed')
        if f:
            st.markdown('<div class="up-ok">✓ Archivo cargado</div>', unsafe_allow_html=True)
    return f


# ---------------- Página ----------------
st.markdown("""<div class="hero"><span class="tag">Prototipo · Alternativa 1A · Bodega 1151 Padre Las Casas</span>
  <h1>📦 Slotting inteligente con IA</h1>
  <p>Clasificación ABC con machine learning (K-means) y propuesta de reubicación de repuestos,
  calculada con datos reales de SAP y el layout de la bodega.</p>
  <div class="steps"><div class="step"><b>1</b>Suba los 3 Excel</div><div class="step"><b>2</b>Presione Calcular</div>
  <div class="step"><b>3</b>Revise los escenarios y las recomendaciones de ubicación</div></div></div>""",
            unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs(['📥 Cargar y calcular', '📊 Escenarios', '📍 Recomendaciones de ubicación',
                                  '🔎 Buscar repuesto'])

with tab1:
    demo = os.environ.get('SLOTTING_DEMO')   # solo para pruebas locales
    seccion('📥', 'Cargue los datos de SAP', 'Los 3 Excel originales de Kaufmann. Se procesan en esta sesión y no se guardan.')
    c1, c2, c3 = st.columns(3)
    f1 = subir(c1, '1 · Stock con ubicación', 'Repuestos con su ubicación PPEE-MMNN', 'f1')
    f2 = subir(c2, '2 · FORM MIX', 'Consumo y pickings de 12 meses', 'f2')
    f3 = subir(c3, '3 · Tiempos de picking', 'Órdenes reales con su tiempo y cumplimiento', 'f3')
    with st.expander('⚙️ Parámetros del cálculo (opcional)'):
        st.markdown('El tiempo de cada ubicación se **calcula con el layout medido en terreno**: distancia ida y '
                    'vuelta por los pasillos hasta las mesas de picking ÷ velocidad de caminata, + escalera si está '
                    'en piso 2 o 3, + escalera tipo avión si es rack nivel 3 o más.')
        p1, p2, p3 = st.columns(3)
        vel = p1.slider('Velocidad de caminata (m/s)', 0.6, 1.4, 1.0, 0.1)
        esc = p2.slider('Escalera: segundos por piso (subir y bajar)', 5, 60, 20, 5)
        ralto = p3.slider('Rack nivel 3+: segundos con escalera tipo avión', 0, 120, 60, 5)
        p4, p5 = st.columns(2)
        vol = p4.slider('Voluminoso: más de (dm³) va al rack', 10, 100, 40, 5)
        vol_alto = p5.slider('Seguridad: rack alto solo hasta (dm³), aprox. livianos', 5, 60, 20, 5)

    if st.button('Calcular propuesta', type='primary', width='stretch'):
        if demo:
            files = [os.path.join(demo, n) for n in ('stock con ubicacion.xlsx',
                     'Copia de FORM MIX ZONA SUR Y EXT SUR NOV 2026.xlsx', 'tiempos de picking.xlsx')]
        elif not (f1 and f2 and f3):
            st.error('Faltan archivos: suba los 3 Excel de Kaufmann.')
            files = None
        else:
            files = [io.BytesIO(f.getvalue()) for f in (f1, f2, f3)]
        if files:
            barra = st.progress(0.0, text='Iniciando…')
            try:
                res = calcular(*files, vel, esc, ralto, vol, vol_alto, carpeta='/tmp/resultados',
                               avance=lambda x, desc=None: barra.progress(min(float(x), 1.0), text=desc or ''))
                barra.progress(1.0, text='Preparando recomendaciones y Excel…')
                recomendaciones(res)
                excel_recomendaciones(res)
                st.session_state['res'] = res
            except Exception as ex:
                st.error(f'No se pudo leer o procesar algún archivo. Revise que sean los Excel originales. Detalle: {ex}')
            barra.empty()

    if 'res' in st.session_state:
        st.markdown(tarjetas(st.session_state['res']), unsafe_allow_html=True)
    else:
        vacio('📊', 'Todavía no hay resultados', 'Suba los 3 Excel y presione <i>Calcular propuesta</i>.')

res = st.session_state.get('res')


def sin_resultados():
    vacio('⏳', 'Primero calcule la propuesta', 'Vaya a la pestaña 📥 Cargar y calcular.')


with tab2:
    if not res:
        sin_resultados()
    else:
        seccion('📊', 'Comparación de escenarios',
                'Simulación con las órdenes reales: hoy, slotting sin límite de capacidad (v1) y con capacidad (v2, la propuesta).')
        st.markdown(html_tabla(tabla_escenarios_txt(res), resaltar=2), unsafe_allow_html=True)
        g1, g2 = st.columns(2)
        with g1.container(border=True, key='caja_g1'):
            st.pyplot(grafico_kpi(res))
        with g2.container(border=True, key='caja_g2'):
            st.pyplot(grafico_zonas(res))
        seccion('⏱️', 'Tiempo de ida y vuelta por zona', 'Calculado con el layout de la bodega, según dónde están hoy los repuestos.')
        st.markdown(html_tabla(tabla_tiempos(res)), unsafe_allow_html=True)

with tab3:
    if not res:
        sin_resultados()
    else:
        reco = recomendaciones(res)
        n = reco.prioridad.value_counts()
        cab, bot = st.columns([4, 1.3])
        with cab:
            seccion('📍', 'Recomendaciones de ubicación', 'Qué repuesto mover, desde dónde y hacia dónde.')
        bot.download_button('⬇️ Descargar Excel', excel_recomendaciones(res), type='primary', width='stretch',
                            file_name='recomendaciones_slotting_kaufmann_1151.xlsx')
        st.markdown(f"""<div class="prio-grid">
  <div class="pc alta"><div class="pc-t">🔴 Prioridad alta</div><div class="pc-n">{cl(n.get('Alta', 0), 0)}</div>
    <div class="pc-s">Los más vendidos (A) y los pesados en rack alto</div></div>
  <div class="pc media"><div class="pc-t">🟡 Prioridad media</div><div class="pc-n">{cl(n.get('Media', 0), 0)}</div>
    <div class="pc-s">Venta media (B)</div></div>
  <div class="pc baja"><div class="pc-t">🟢 Prioridad baja</div><div class="pc-n">{cl(n.get('Baja', 0), 0)}</div>
    <div class="pc-s">Poca venta (C): liberan espacio cercano</div></div></div>
<div class="guia"><span><b>1</b>Busque el repuesto en <i>Hoy está en</i></span><span class="sep">›</span>
  <span><b>2</b>Llévelo a la ubicación en azul</span><span class="sep">›</span>
  <span><b>3</b>Parta por las de prioridad alta</span></div>""", unsafe_allow_html=True)
        with st.container(border=True, key='caja_filtro'):
            cA, cB = st.columns([3, 2])
            q3 = cA.text_input('🔎 Buscar', placeholder='Código o nombre del repuesto…', key='q3')
            prio = cB.segmented_control('Prioridad', list(PRIO_TXT.values()), selection_mode='multi',
                                        default=list(PRIO_TXT.values()), key='prio3')
        elegidas = [k for k, t in PRIO_TXT.items() if t in (prio or [])]
        v = reco[reco.prioridad.isin(elegidas)]
        if q3.strip():
            v = v[v.codigo.str.contains(q3, case=False, na=False, regex=False) |
                  v.repuesto.str.contains(q3, case=False, na=False, regex=False)]
        # Paginación: 25 filas por página; vuelve a la 1 si cambian los filtros
        POR_PAG = 25
        paginas = max(1, -(-len(v) // POR_PAG))
        filtro = (q3, tuple(elegidas))
        if st.session_state.get('filtro3') != filtro:
            st.session_state.filtro3, st.session_state.pag3 = filtro, 0
        pag = min(st.session_state.get('pag3', 0), paginas - 1)
        if v.empty:
            vacio('🔍', 'Sin resultados', 'No hay recomendaciones con ese filtro.')
        else:
            st.markdown(html_recomendaciones(v.iloc[pag * POR_PAG:(pag + 1) * POR_PAG]), unsafe_allow_html=True)
            p1, p2, p3 = st.columns([1, 3, 1])
            if p1.button('← Anterior', disabled=pag == 0, width='stretch'):
                st.session_state.pag3 = pag - 1
                st.rerun()
            p2.markdown(f'<div class="pag">Página {pag + 1} de {cl(paginas, 0)} · {cl(len(v), 0)} de '
                        f'{cl(len(reco), 0)} recomendaciones</div>', unsafe_allow_html=True)
            if p3.button('Siguiente →', disabled=pag >= paginas - 1, width='stretch'):
                st.session_state.pag3 = pag + 1
                st.rerun()
        with st.expander('¿Cómo leer el código de ubicación (PPEE-MMNN)?'):
            st.markdown('- **PP = piso**: 10, 20 y 30 son los pisos 1 a 3 de la estantería; 40 o más son racks.\n'
                        '- **EE = estantería**: la 01 está junto al mostrador; de la 04 a la 08 son Mercedes-Benz.\n'
                        '- **MM = módulo**: el 01 está en la pared izquierda.\n'
                        '- **NN = nivel**: en estantería el 01 es el de arriba; en rack el 01 es el de abajo.')

with tab4:
    if not res:
        sin_resultados()
    else:
        recomendaciones(res)   # calcula la ubicación recomendada de cada repuesto
        seccion('🔎', 'Buscar repuesto', 'Vea dónde está hoy cualquier repuesto y si conviene moverlo.')
        with st.container(border=True, key='caja_buscar'):
            q = st.text_input('Código de material o descripción', placeholder='Ej: filtro, A0004771302…')
        if not q.strip():
            vacio('🔎', 'Escriba un código o nombre', 'Se muestran hasta 30 resultados.')
        else:
            d = res['d']
            m = d[d.material.str.contains(q, case=False, na=False, regex=False) |
                  d.texto.str.contains(q, case=False, na=False, regex=False)].head(30)
            if m.empty:
                vacio('🔍', 'Sin resultados', f'No encontré repuestos con «{hx(q)}».')
            else:
                mueve = m.movible & (m.zona_v2 != m.zona_actual)
                st.markdown(html_tabla(pd.DataFrame({
                    'Código': m.material,
                    'Repuesto': m.texto.str.strip().str.title(),
                    'Venta': m.clase.map(lambda c: f'{CLASE_TXT[c]} ({c})'),
                    'Hoy está en': m.ubic.fillna('—') + '  ·  ' + m.zona_actual.map(zona_txt),
                    'Recomendación': [f'Moverlo a {u}  ·  {zona_txt(z)}' if mv else '✅ Se queda donde está'
                                      for u, z, mv in zip(m.ubic_v2, m.zona_v2, mueve)],
                })), unsafe_allow_html=True)

st.markdown('<div class="pie">Prototipo académico · Proyecto Integrado, Técnico en Logística INACAP · '
            'Los datos se procesan en la sesión y no se guardan.</div>', unsafe_allow_html=True)
