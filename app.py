"""Prototipo Kaufmann — Slotting inteligente con IA (alternativa 1A), bodega 1151 Padre Las Casas.
Prototipo académico del Proyecto Integrado (INACAP). Ejecutar con:  streamlit run app.py
"""
import io
import os

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
    motivo = [('🦺 Pesado en rack alto: bajarlo por seguridad' if s else
               f"{CLASE_TXT[c]} ({c}): {'acercarlo a la entrega' if a else 'liberar espacio cercano para los más vendidos'}")
              for s, c, a in zip(l.seguridad, l.clase, acerca)]
    reco = pd.DataFrame({
        'Prioridad': l.prioridad.map(PRIO_TXT),
        'Código': l.material,
        'Repuesto': l.texto.str.strip().str.title(),
        'Hoy está en': l.ubic.fillna('—') + '  ·  ' + l.zona_actual.map(zona_txt),
        'Moverlo a': l.ubic_v2 + '  ·  ' + l.zona_v2.map(zona_txt),
        'Motivo': motivo,
        'Tiempo por picking': [f'{a:.0f} s → {b:.0f} s' for a, b in zip(l.seg_ubic, l.seg_v2)],
        'Pedidos al año': l.pickings_12m.astype(int),
    })
    res['reco'] = reco
    return reco


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


# ---------------- Página ----------------
st.markdown("""<div class="hero"><span class="tag">Prototipo · Alternativa 1A · Bodega 1151 Padre Las Casas</span>
  <h1>📦 Slotting inteligente con IA</h1>
  <p>Clasificación ABC con machine learning (K-means) y propuesta de reubicación de repuestos,
  calculada con datos reales de SAP y el layout de la bodega.</p>
  <div class="steps"><div class="step"><b>1</b>Suba los 3 Excel</div><div class="step"><b>2</b>Presione Calcular</div>
  <div class="step"><b>3</b>Revise los escenarios y las recomendaciones de ubicación</div></div></div>""",
            unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs(['① Cargar y calcular', '② Escenarios', '③ Recomendaciones de ubicación',
                                  '④ Buscar repuesto'])

with tab1:
    demo = os.environ.get('SLOTTING_DEMO')   # solo para pruebas locales
    c1, c2, c3 = st.columns(3)
    f1 = c1.file_uploader('Stock con ubicación', type='xlsx')
    f2 = c2.file_uploader('FORM MIX (consumo 12 meses)', type='xlsx')
    f3 = c3.file_uploader('Tiempos de picking', type='xlsx')
    with st.expander('Cómo se calcula el tiempo (parámetros)'):
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
                with open(res['excel'], 'rb') as fh:
                    res['excel_bytes'] = fh.read()
                st.session_state['res'] = res
            except Exception as ex:
                st.error(f'No se pudo leer o procesar algún archivo. Revise que sean los Excel originales. Detalle: {ex}')
            barra.empty()

    if 'res' in st.session_state:
        st.markdown(tarjetas(st.session_state['res']), unsafe_allow_html=True)

res = st.session_state.get('res')
aviso = 'Primero calcule la propuesta en la pestaña ① Cargar y calcular.'

with tab2:
    if not res:
        st.info(aviso)
    else:
        st.subheader('Comparación de escenarios')
        st.dataframe(tabla_escenarios_txt(res), hide_index=True, width='stretch')
        g1, g2 = st.columns(2)
        g1.pyplot(grafico_kpi(res))
        g2.pyplot(grafico_zonas(res))
        st.subheader('Tiempo de ida y vuelta por zona (hoy)')
        st.dataframe(tabla_tiempos(res), hide_index=True, width='stretch')

with tab3:
    if not res:
        st.info(aviso)
    else:
        reco = recomendaciones(res)
        st.markdown('Cada fila es una recomendación: **saque el repuesto de "Hoy está en" y llévelo a "Moverlo a"**. '
                    'Parta por las de prioridad 🔴 Alta (los más vendidos y los pesados en altura).')
        cA, cB, cC = st.columns([2, 2, 1])
        q3 = cA.text_input('Buscar', placeholder='Código o nombre del repuesto…', key='q3')
        prio = cB.segmented_control('Prioridad', list(PRIO_TXT.values()), selection_mode='multi',
                                    default=list(PRIO_TXT.values()), key='prio3')
        cC.download_button('⬇️ Excel completo', res['excel_bytes'], file_name='lista_reubicaciones_slotting.xlsx',
                           width='stretch')
        v = reco[reco.Prioridad.isin(prio or [])]
        if q3.strip():
            v = v[v['Código'].str.contains(q3, case=False, na=False, regex=False) |
                  v.Repuesto.str.contains(q3, case=False, na=False, regex=False)]
        st.caption(f'Mostrando {cl(len(v), 0)} de {cl(len(reco), 0)} recomendaciones')
        st.dataframe(v, hide_index=True, width='stretch', height=520, column_config={
            'Prioridad': st.column_config.TextColumn(width='small'),
            'Código': st.column_config.TextColumn(width='small'),
            'Hoy está en': st.column_config.TextColumn(help='Ubicación actual (código PPEE-MMNN · zona)'),
            'Moverlo a': st.column_config.TextColumn(help='Ubicación recomendada (código PPEE-MMNN · zona)'),
            'Tiempo por picking': st.column_config.TextColumn(width='small',
                                                              help='Ida y vuelta a la entrega: hoy → recomendada'),
            'Pedidos al año': st.column_config.NumberColumn(width='small', help='Pickings de los últimos 12 meses'),
        })
        with st.expander('¿Cómo leer el código de ubicación (PPEE-MMNN)?'):
            st.markdown('- **PP = piso**: 10, 20 y 30 son los pisos 1 a 3 de la estantería; 40 o más son racks.\n'
                        '- **EE = estantería**: la 01 está junto al mostrador; de la 04 a la 08 son Mercedes-Benz.\n'
                        '- **MM = módulo**: el 01 está en la pared izquierda.\n'
                        '- **NN = nivel**: en estantería el 01 es el de arriba; en rack el 01 es el de abajo.')

with tab4:
    if not res:
        st.info(aviso)
    else:
        recomendaciones(res)   # calcula la ubicación recomendada de cada repuesto
        q = st.text_input('Código de material o descripción', placeholder='Ej: filtro, A0004771302…')
        if q.strip():
            d = res['d']
            m = d[d.material.str.contains(q, case=False, na=False, regex=False) |
                  d.texto.str.contains(q, case=False, na=False, regex=False)].head(30)
            if m.empty:
                st.warning(f'No encontré repuestos con «{q}».')
            else:
                mueve = m.movible & (m.zona_v2 != m.zona_actual)
                st.dataframe(pd.DataFrame({
                    'Código': m.material,
                    'Repuesto': m.texto.str.strip().str.title(),
                    'Venta': m.clase.map(lambda c: f'{CLASE_TXT[c]} ({c})'),
                    'Hoy está en': m.ubic.fillna('—') + '  ·  ' + m.zona_actual.map(zona_txt),
                    'Recomendación': [f'Moverlo a {u}  ·  {zona_txt(z)}' if mv else '✅ Se queda donde está'
                                      for u, z, mv in zip(m.ubic_v2, m.zona_v2, mueve)],
                }), hide_index=True, width='stretch')

st.markdown('<div class="pie">Prototipo académico · Proyecto Integrado, Técnico en Logística INACAP · '
            'Los datos se procesan en la sesión y no se guardan.</div>', unsafe_allow_html=True)
