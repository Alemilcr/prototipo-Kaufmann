"""Motor de cálculo del prototipo de slotting con IA (alternativa 1A) — bodega Kaufmann 1151."""
# Misma lógica del Prototipo 1A, metida en una función para que la app la llame.
import os, warnings
import numpy as np, pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
warnings.filterwarnings('ignore')

SEMILLA = 1151
EST_MB = {'04', '05', '06', '07', '08'}   # estanterías asignadas a Mercedes-Benz
ZONAS = ['EST-MB-1', 'EST-MB-2', 'EST-MB-3', 'EST-OM-1', 'EST-OM-2', 'EST-OM-3', 'RACK-BAJO', 'RACK-ALTO']
NOMBRES_ESC = {'Actual': 'Hoy', 'v1': 'Slotting v1 (sin límite de capacidad)', 'v2': 'Slotting v2 (con capacidad)'}
# ---------- Layout (medidas tomadas en terreno, en metros) ----------
# Origen: esquina inferior izquierda del bloque de estanterías (pared de abajo, pared izquierda).
PUNTO_ENTREGA = (20.0, 0.0)        # mesas de picking / entrega, al final derecho de la estantería 01
LARGO_EST, MODULOS_EST, FONDO_EST = 19.3, 19, 11.8
# Estantería 01 pegada a la pared de abajo (mostrador); sube de a pares hacia los racks.
FILA_EST = {'01': 0, '02': 1, '03': 1, '04': 2, '05': 2, '06': 3, '07': 3,
            '08': 4, '09': 4, '10': 5, '11': 5, '12': 6, '00': 0}
# Racks 40: 01-02 fila 4, 03-04 fila 3, 05-06 fila 2, 07 rack grande (pasillo desde donde se pickea, en m)
Y_RACK = {'01': 11.9, '02': 15.2, '03': 15.2, '04': 20.1, '05': 20.1, '06': 25.1, '07': 25.1}
RACK_X0, RACK_MOD = 0.97, 2.1      # racks de 14,7 m con 7 módulos
GRANDE_X0, GRANDE_MOD = -0.9, 2.86 # rack grande de 20 m con 7 módulos
OTRAS_XY = (8.0, 20.0)             # ubicaciones 50-90 sin posición confirmada: centro de la zona de racks

MEJORA_INFORME = 9.2   # informe (Tabla 12): el slotting 1A sube el KPI2 en 9,2 p.p.
META_KPI2 = 95


def posicion(pp, est, mod):
    """Coordenadas (x, y) en metros de una ubicación, según el layout."""
    p, mo = int(pp), int(mod)
    if p in (10, 20, 30):
        x = (mo - 0.5) * LARGO_EST / MODULOS_EST
        y = FILA_EST.get(est, 3) * FONDO_EST / 6
        return x, y
    if p == 40:
        if est == '07':
            return GRANDE_X0 + (mo - 0.5) * GRANDE_MOD, Y_RACK['07']
        return RACK_X0 + (mo - 0.5) * RACK_MOD, Y_RACK.get(est, 20.0)
    return OTRAS_XY


def segundos_ubicacion(r, vel, seg_escalera, seg_rack_alto):
    """Tiempo extra de ir a buscar un repuesto a su ubicación y volver al punto de entrega.
    Caminata: recorrido en L por los pasillos (ida y vuelta) / velocidad.
    Piso 2 y 3: se suma la escalera por cada piso. Rack nivel 3 o más: escalera tipo avión."""
    if pd.isna(r.pp):
        return np.nan
    x, y = posicion(r.pp, r.est, r['mod'])
    dist = abs(PUNTO_ENTREGA[0] - x) + abs(y - PUNTO_ENTREGA[1])
    t = 2 * dist / vel
    p = int(r.pp)
    if p in (20, 30):
        t += seg_escalera * (p // 10 - 1)
    elif p >= 40 and int(r.niv) >= 3:
        t += seg_rack_alto
    return t


def _ruta(f):
    """Acepta una ruta, un archivo subido (Streamlit) o un objeto con .name (Gradio)."""
    if isinstance(f, str) or hasattr(f, 'read'):
        return f
    return getattr(f, 'name', f)


def calcular(f_stock, f_mix, f_tiempos, vel_caminata=1.0, seg_escalera=20, seg_rack_alto=60,
             vol_rack_dm3=40, vol_max_alto_dm3=20, carpeta='resultados', avance=None):
    paso = avance or (lambda x, desc=None: None)

    # ---------- 1. Carga y limpieza ----------
    paso(0.05, desc='Leyendo los 3 Excel…')
    st = pd.read_excel(_ruta(f_stock), sheet_name='Sheet1', dtype=str)
    st.columns = ['centro', 'almacen', 'material', 'texto', 'stock', 'ubic', 'grupo', 'grupo_desc']
    st = st.drop_duplicates('material')
    mx = pd.read_excel(_ruta(f_mix), sheet_name='Propuesta mix ZS y ZES', dtype={'Ce.': str, 'Material': str})
    mx = mx[mx['Ce.'] == '1151'].drop_duplicates('Material')
    mx = mx.rename(columns={'Material': 'material', '¿Está hoy en Mix suc?': 'en_mix',
                            'Frecuencia 12 meses': 'pickings_12m', 'Hitos 12 meses': 'meses_con_venta',
                            'Consumo total 12 meses': 'unidades_12m', 'Volumen unitario en m3': 'vol_m3'})
    t = pd.read_excel(_ruta(f_tiempos), header=2, dtype={'mblnr': str})
    t = t[t.cumplimiento.isin(['Cumple', 'No cumple'])].copy()

    d = st.merge(mx[['material', 'en_mix', 'pickings_12m', 'meses_con_venta', 'unidades_12m', 'vol_m3']],
                 on='material', how='left')
    d['en_mix'] = d.en_mix.fillna('SIN REGISTRO')
    for c in ['pickings_12m', 'meses_con_venta', 'unidades_12m']:
        d[c] = pd.to_numeric(d[c], errors='coerce').fillna(0).clip(lower=0)
    d['vol_dm3'] = pd.to_numeric(d.vol_m3, errors='coerce') * 1000

    u = d.ubic.str.extract(r'^(\d{2})(\d{2})-(\d{2})(\d{2})')
    u.columns = ['pp', 'est', 'mod', 'niv']
    d = pd.concat([d, u], axis=1)

    def zona(r):
        if pd.isna(r.pp): return 'OTRA'
        p = int(r.pp)
        if p in (10, 20, 30): return f"EST-{'MB' if r.est in EST_MB else 'OM'}-{p // 10}"
        return 'RACK-BAJO' if int(r.niv) <= 2 else 'RACK-ALTO'
    d['zona_actual'] = d.apply(zona, axis=1)
    d['tipo_zona'] = d.zona_actual.str.split('-').str[0]
    d['familia'] = d.grupo.str.extract(r'^\d?([A-Z]{2})')[0].fillna('OTROS')
    d['mb'] = (d.familia == 'MB') | d.grupo_desc.fillna('').str.contains('MERCEDES', case=False)

    # Tiempo de cada ubicación actual, calculado con el layout (no con supuestos por piso)
    d['seg_ubic'] = d.apply(segundos_ubicacion, axis=1, args=(vel_caminata, seg_escalera, seg_rack_alto))
    d['seg_ubic'] = d.seg_ubic.fillna(d.seg_ubic.max())   # patio, búnker, jaula: lo más lejano

    # ---------- 2. Clasificación K-means y asignación ----------
    paso(0.2, desc='Clasificando repuestos con K-means…')
    act = d[d.pickings_12m > 0].copy()
    act['u_linea'] = act.unidades_12m / act.pickings_12m
    X = np.log1p(act[['pickings_12m', 'meses_con_venta', 'u_linea']])
    km = KMeans(n_clusters=3, n_init=20, random_state=SEMILLA).fit(StandardScaler().fit_transform(X))
    act['g'] = km.labels_
    orden = act.groupby('g').pickings_12m.mean().sort_values(ascending=False).index
    mapa = {orden[0]: 'A', orden[1]: 'B', orden[2]: 'C'}
    d['clase'] = 'C'
    d.loc[act.index, 'clase'] = act.g.map(mapa)

    d['voluminoso'] = d.vol_dm3 > vol_rack_dm3
    # Regla de seguridad: en rack alto (nivel 3+) solo repuestos livianos. Sin peso en los datos,
    # se usa el volumen como aproximación (si SAP entrega el peso bruto, se reemplaza aquí).
    d['pesado'] = d.vol_dm3 > vol_max_alto_dm3
    # Se reubican los del mix y sin registro. Los fuera de mix (pedidos de cliente) se quedan,
    # salvo que sean pesados en rack alto: por seguridad se bajan igual.
    d['seguridad'] = d.pesado & (d.zona_actual == 'RACK-ALTO')
    d['movible'] = ((d.en_mix != 'NO') | d.seguridad) & (d.zona_actual != 'OTRA')

    def destino_ideal(r):
        if r.tipo_zona == 'RACK' or r.voluminoso:
            return 'RACK-BAJO' if (r.clase in ('A', 'B') or r.pesado) else 'RACK-ALTO'
        g = 'MB' if r.mb else 'OM'
        return f"EST-{g}-{ {'A': 1, 'B': 2, 'C': 3}[r.clase]}"
    d['zona_ideal'] = d.apply(destino_ideal, axis=1)
    cap = d[d.zona_actual != 'OTRA'].zona_actual.value_counts().to_dict()

    def asignar(df, controlar_capacidad=True):
        ocup = df[~df.movible].zona_actual.value_counts().to_dict()
        nueva = df.zona_actual.copy()
        pisos = {'1': '123', '2': '213', '3': '321'}
        def orden_est(z, pesado=False):
            if z.startswith('RACK'):
                if pesado: return ['RACK-BAJO']          # nunca a rack alto
                return [z, 'RACK-ALTO' if z == 'RACK-BAJO' else 'RACK-BAJO']
            g, p = z.split('-')[1], z[-1]; o = 'OM' if g == 'MB' else 'MB'
            return [f'EST-{g}-{x}' for x in pisos[p]] + [f'EST-{o}-{x}' for x in pisos[p]]
        for i, r in df[df.movible].sort_values('pickings_12m', ascending=False).iterrows():
            if not controlar_capacidad:
                z = r.zona_ideal
            else:
                z = next((x for x in orden_est(r.zona_ideal, r.pesado) if ocup.get(x, 0) < cap.get(x, 0)), r.zona_actual)
            ocup[z] = ocup.get(z, 0) + 1
            nueva.at[i] = z
        return nueva
    d['zona_v1'] = asignar(d, controlar_capacidad=False)
    d['zona_v2'] = asignar(d, controlar_capacidad=True)

    # ---------- 3. Indicadores y simulación ----------
    def ocupacion(col):
        o = d[d[col] != 'OTRA'][col].value_counts()
        return {z: round(o.get(z, 0) / cap[z] * 100, 1) if cap.get(z) else 0 for z in ZONAS}
    eval_ = d[d.movible & d.clase.isin(['A', 'B']) & (d.pickings_12m > 0)]
    def bien(col): return round((eval_[col] == eval_.zona_ideal).mean() * 100, 1)
    pk = d[d.pickings_12m > 0]
    def pick_piso1(col):
        w = pk.pickings_12m
        return round(w[pk[col].str.endswith('-1') | (pk[col] == 'RACK-BAJO')].sum() / w.sum() * 100, 1)

    def segundos_escenario(col):
        """Segundos de cada SKU en el escenario. En cada zona, los repuestos que se mueven toman las
        ubicaciones libres de esa zona: los de más pickings, las más cercanas a la entrega."""
        if col == 'zona_actual':
            return d.seg_ubic.copy()
        out = d.seg_ubic.copy()
        for z, grupo in d.groupby(col):
            if z == 'OTRA':
                continue
            fijos = grupo[~grupo.movible]
            pool = d[(d.zona_actual == z)].seg_ubic.drop(fijos.index, errors='ignore').sort_values().values
            movs = grupo[grupo.movible].sort_values('pickings_12m', ascending=False)
            relleno = pool.mean() if len(pool) else d.seg_ubic.mean()
            vals = list(pool[:len(movs)]) + [relleno] * max(0, len(movs) - len(pool))
            out.loc[movs.index] = vals
        return out

    p = (pk.pickings_12m / pk.pickings_12m.sum()).values
    seg0 = d.loc[pk.index, 'seg_ubic'].values
    def simular(col):
        # Cada orden real conserva su tiempo; solo cambia la diferencia de segundos de ubicación de cada línea.
        seg1 = segundos_escenario(col).loc[pk.index].values
        r = np.random.default_rng(SEMILLA)
        tiempos = []
        for n, tp in zip(t.lineas.values, t.time_prom_lineas.values):
            idx = r.choice(len(p), size=int(n), p=p)
            delta = (seg0[idx] - seg1[idx]).mean()
            tiempos.append(max(tp - delta, 10))
        tiempos = np.array(tiempos); lin = t.lineas.values
        return {'kpi2': round((tiempos <= 240).mean() * 100, 1),
                'seg_linea_mediana': round(float(np.median(tiempos)), 0),
                'min_linea_promedio': round(float((tiempos * lin).sum() / lin.sum() / 60), 2),
                'horas_mes': round(float((tiempos * lin).sum() / 3 / 3600), 1)}

    escenarios = {}
    lista_esc = [('Actual', 'zona_actual'), ('v1', 'zona_v1'), ('v2', 'zona_v2')]
    for k, (nom, col) in enumerate(lista_esc):
        paso(0.35 + 0.55 * k / len(lista_esc), desc=f'Simulando las órdenes reales: {NOMBRES_ESC[nom]}…')
        e = {'bien_ubicados': bien(col), 'pickings_piso1': pick_piso1(col), 'ocupacion': ocupacion(col)}
        e.update(simular(col))
        escenarios[nom] = e

    pesados_alto = {'hoy': int((d.pesado & (d.zona_actual == 'RACK-ALTO')).sum()),
                    'v2': int((d.pesado & (d.zona_v2 == 'RACK-ALTO')).sum())}
    real = {'ordenes': int(len(t)), 'kpi2': round((t.cumplimiento == 'Cumple').mean() * 100, 1),
            'pesados_alto': pesados_alto,
            # artículos (líneas) pickeados por día hábil: 3 meses x 22 días; el informe asumió 120
            'articulos_dia': round(float(t.lineas.sum()) / (3 * 22), 0)}

    # ---------- 4. Salidas ----------
    paso(0.92, desc='Armando el Excel de reubicaciones…')
    os.makedirs(carpeta, exist_ok=True)
    lista = d[d.movible & (d.zona_v2 != d.zona_actual)].copy()
    lista['prioridad'] = lista.clase.map({'A': 'Alta', 'B': 'Media', 'C': 'Baja'})
    lista.loc[lista.seguridad, 'prioridad'] = 'Alta'
    lista['motivo'] = np.where(lista.seguridad, 'Seguridad: pesado en altura', 'Rotación (clase ' + lista.clase + ')')
    lista['_o'] = lista.prioridad.map({'Alta': 0, 'Media': 1, 'Baja': 2})
    lista = lista.sort_values(['_o', 'pickings_12m'], ascending=[True, False])
    cols = ['material', 'texto', 'clase', 'prioridad', 'motivo', 'pickings_12m', 'meses_con_venta', 'en_mix', 'ubic',
            'zona_actual', 'zona_v2']
    lista = lista[cols].rename(columns={'ubic': 'ubicacion_actual', 'zona_v2': 'zona_nueva'})

    tabla = tabla_escenarios(escenarios)
    ocup = pd.DataFrame({NOMBRES_ESC[k]: v['ocupacion'] for k, v in escenarios.items()}).T
    xlsx = f'{carpeta}/lista_reubicaciones_slotting_datos_reales.xlsx'
    with pd.ExcelWriter(xlsx, engine='openpyxl') as w:
        lista.to_excel(w, sheet_name='Reubicaciones', index=False)
        tabla.to_excel(w, sheet_name='Indicadores', index=False)
        ocup.to_excel(w, sheet_name='Ocupacion')
        d[['material', 'texto', 'en_mix', 'pickings_12m', 'meses_con_venta', 'unidades_12m', 'clase', 'ubic',
           'zona_actual', 'zona_v2']].to_excel(w, sheet_name='Clasificacion_IA', index=False)
    paso(1.0, desc='Listo')
    d['seg_v2'] = segundos_escenario('zona_v2')
    return {'d': d, 'escenarios': escenarios, 'real': real, 'lista': lista, 'tabla': tabla,
            'ocupacion': ocup, 'excel': xlsx}


def tabla_escenarios(escenarios):
    """Tabla con nombres que se entienden en una presentación."""
    filas = []
    for k, v in escenarios.items():
        filas.append({'Escenario': NOMBRES_ESC[k],
                      'Órdenes que cumplen 4 min/línea (%)': v['kpi2'],
                      'Pickings en piso 1 o rack bajo (%)': v['pickings_piso1'],
                      'SKU A y B bien ubicados (%)': v['bien_ubicados'],
                      'Segundos por línea (mediana)': v['seg_linea_mediana'],
                      'Horas de picking al mes': v['horas_mes']})
    return pd.DataFrame(filas)
