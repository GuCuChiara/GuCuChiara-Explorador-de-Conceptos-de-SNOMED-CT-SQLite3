# =============================================================
# Explorador de Conceptos de SNOMED-CT (Enterprise-ready UI)
# - Botón flotante SaaS: fijo + sombra + hover + tooltip
# - Limpieza segura de estado (búsqueda + selección)
# =============================================================

import streamlit as st
import pandas as pd
import sqlite3
import os
from pathlib import Path
from io import BytesIO

# ==========================================
# 1. CONFIGURACIÓN Y CONSTANTES
# ==========================================
st.set_page_config(page_title="Explorador de Conceptos de SNOMED-CT", layout="wide", page_icon="🧬")

# ⚠️ AJUSTAR ESTA RUTA A LA CARPETA LOCAL CON SNOMED-CT
BASE_PATH = Path(
    r"C:\Users\gcuello\Downloads\SnomedCT_Argentina-EditionRelease_PRODUCTION_20251120T120000Z"
    r"\SnomedCT_Argentina-EditionRelease_PRODUCTION_20251120T120000Z"
    r"\Snapshot\Terminology"
)

DESC_FILE = BASE_PATH / "sct2_Description_Snapshot_ArgentinaEdition_20251120.txt"
REL_FILE  = BASE_PATH / "sct2_Relationship_Snapshot_ArgentinaEdition_20251120.txt"
DB_FILE = "snomed_argentina.db"

# SNOMED CONSTANTS
IS_A = "116680003"
FSN_TYPE = "900000000000003001"

# ==========================================
# 2. UTILIDADES ENTERPRISE (ESTADO + UI)
# ==========================================

def init_state():
    """Inicializa session_state con claves usadas por la app."""
    defaults = {
        "query": "",
        "selected_option": None,
        "last_query": "",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

def clear_search_state():
    """Limpia la búsqueda y la selección para reiniciar la vista."""
    st.session_state.query = ""
    st.session_state.selected_option = None
    st.session_state.last_query = ""

def inject_enterprise_css():
    """CSS estilo SaaS médico: tipografías, espaciado, y botón flotante."""
    st.markdown(
        """
<style>
/* ====== SaaS-ish spacing ====== */
.block-container { padding-top: 1.2rem; padding-bottom: 2rem; }
h1, h2, h3 { letter-spacing: -0.2px; }

/* ====== Floating action button (FAB) ====== */
.fab-wrap{
    position: fixed;
    right: 28px;
    bottom: 28px;
    z-index: 9999;
    display: flex;
    align-items: center;
    gap: 10px;
}

/* Tooltip bubble (visible on hover) */
.fab-tooltip{
    opacity: 0;
    transform: translateY(4px);
    transition: all 160ms ease;
    background: rgba(15, 23, 42, 0.92);
    color: #fff;
    padding: 8px 10px;
    border-radius: 10px;
    font-size: 12.5px;
    box-shadow: 0 12px 28px rgba(2, 6, 23, 0.28);
    pointer-events: none;
    white-space: nowrap;
}

/* Button itself */
.fab-btn{
    width: 54px;
    height: 54px;
    border-radius: 16px;
    border: 1px solid rgba(255,255,255,0.16);
    background: linear-gradient(135deg, rgba(239,68,68,0.95), rgba(220,38,38,0.95));
    color: #fff;
    font-size: 22px;
    cursor: pointer;
    box-shadow:
        0 10px 20px rgba(220, 38, 38, 0.20),
        0 6px 12px rgba(2, 6, 23, 0.14);
    transition: transform 160ms ease, box-shadow 160ms ease, filter 160ms ease;
}

/* Hover & active animation */
.fab-btn:hover{
    transform: translateY(-2px) scale(1.02);
    filter: brightness(1.03);
    box-shadow:
        0 16px 30px rgba(220, 38, 38, 0.26),
        0 8px 16px rgba(2, 6, 23, 0.18);
}
.fab-btn:active{
    transform: translateY(0px) scale(0.99);
}

/* Show tooltip on hover */
.fab-wrap:hover .fab-tooltip{
    opacity: 1;
    transform: translateY(0px);
}

/* Small hint text under title */
.subtle-hint{
    color: rgba(71,85,105,0.9);
    font-size: 0.92rem;
    margin-top: -8px;
}

/* Code blocks: slightly nicer */
pre { border-radius: 14px !important; }

/* Data editor container spacing */
[data-testid="stDataEditor"] { border-radius: 14px; }

</style>
        """,
        unsafe_allow_html=True,
    )

def render_floating_clear_button():
    """
    Renderiza un botón flotante (HTML) con tooltip.
    La acción real se hace con un st.button oculto + query param.
    """
    # 1) HTML del FAB que dispara un rerun con query param ?fab=1
    st.markdown(
        """
<div class="fab-wrap">
  <div class="fab-tooltip">Limpiar búsqueda</div>
  <a href="?fab=1" title="Limpiar búsqueda">
    <button class="fab-btn" aria-label="Limpiar búsqueda">🧹</button>
  </a>
</div>
        """,
        unsafe_allow_html=True,
    )

    # 2) Si viene el query param fab=1, limpiamos y volvemos a URL limpia
    params = st.query_params
    if params.get("fab") == "1":
        clear_search_state()
        st.query_params.clear()
        st.rerun()

# ==========================================
# 3. GESTIÓN DE BASE DE DATOS (ETL)
# ==========================================
def check_db_exists():
    return os.path.exists(DB_FILE)

def inicializar_db():
    """Lee TXT, filtra activos/español y crea SQLite indexada."""
    if not DESC_FILE.exists() or not REL_FILE.exists():
        st.error(f"❌ No se encontraron los archivos TXT en: {BASE_PATH}")
        return False

    placeholder = st.empty()
    with placeholder.container():
        st.info("⏳ Generando base de datos optimizada... (Esto ocurre solo una vez)")
        bar = st.progress(0)

        conn = sqlite3.connect(DB_FILE)

        # 1. Descripciones (Solo Activas y Español)
        st.write("Procesando Descripciones...")
        desc = pd.read_csv(
            DESC_FILE,
            sep="\t",
            dtype=str,
            usecols=["active", "conceptId", "languageCode", "typeId", "term"],
        )
        desc = desc[(desc["active"] == "1") & (desc["languageCode"] == "es")]
        desc.to_sql("descriptions", conn, index=False, if_exists="replace")
        bar.progress(40)

        # 2. Relaciones (Solo Activas)
        st.write("Procesando Relaciones...")
        rel = pd.read_csv(
            REL_FILE,
            sep="\t",
            dtype=str,
            usecols=["active", "sourceId", "destinationId", "relationshipGroup", "typeId"],
        )
        rel = rel[rel["active"] == "1"]
        rel.to_sql("relationships", conn, index=False, if_exists="replace")
        bar.progress(80)

        # 3. Índices (Clave para velocidad)
        st.write("Creando índices...")
        cur = conn.cursor()
        cur.execute("CREATE INDEX IF NOT EXISTS idx_desc_term ON descriptions(term)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_desc_cid ON descriptions(conceptId)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_rel_source ON relationships(sourceId)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_rel_dest ON relationships(destinationId)")
        conn.commit()
        conn.close()
        bar.progress(100)

    placeholder.success("✅ Base de datos lista.")
    return True

# ==========================================
# 4. FUNCIONES DE CONSULTA (LOGICA)
# ==========================================
def get_conn():
    return sqlite3.connect(DB_FILE, check_same_thread=False)

def resolver_nombres_bulk(lista_ids):
    """Traduce una lista de IDs a sus FSNs en una sola consulta."""
    if not lista_ids:
        return {}
    conn = get_conn()
    ids_str = ",".join([f"'{x}'" for x in set(lista_ids)])

    query = f"""
        SELECT conceptId, term
        FROM descriptions
        WHERE conceptId IN ({ids_str})
        AND typeId = '{FSN_TYPE}'
        AND active = '1'
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df.drop_duplicates("conceptId").set_index("conceptId")["term"].to_dict()

def buscar_concepto(texto):
    conn = get_conn()
    query = f"""
        SELECT conceptId, term
        FROM descriptions
        WHERE term LIKE ?
        AND typeId = '{FSN_TYPE}'
        AND active = '1'
        LIMIT 50
    """
    df = pd.read_sql_query(query, conn, params=(f"%{texto}%",))
    conn.close()
    return df

def obtener_info_completa(concept_id):
    conn = get_conn()

    # 1. Ancestros (Is A)
    q_isa = f"SELECT destinationId FROM relationships WHERE sourceId = ? AND typeId = '{IS_A}'"
    df_isa = pd.read_sql_query(q_isa, conn, params=(concept_id,))

    # 2. Atributos (No Is A)
    q_attr = f"""
        SELECT relationshipGroup, typeId, destinationId
        FROM relationships
        WHERE sourceId = ?
        AND typeId != '{IS_A}'
        ORDER BY relationshipGroup
    """
    df_attr = pd.read_sql_query(q_attr, conn, params=(concept_id,))

    # 3. Descendientes
    q_desc = f"SELECT sourceId FROM relationships WHERE destinationId = ? AND typeId = '{IS_A}'"
    df_desc = pd.read_sql_query(q_desc, conn, params=(concept_id,))

    conn.close()
    return df_isa, df_attr, df_desc

# ==========================================
# 5. INTERFAZ STREAMLIT
# ==========================================
init_state()
inject_enterprise_css()
render_floating_clear_button()

# --- Sidebar de Control ---
with st.sidebar:
    st.title("⚙️ Configuración")
    if check_db_exists():
        st.success("Base de datos conectada")
        if st.button("Reconstruir Base de Datos"):
            os.remove(DB_FILE)
            clear_search_state()
            st.rerun()
    else:
        st.warning("Base de datos no encontrada")
        if st.button("Inicializar DB"):
            inicializar_db()
            st.rerun()
    st.divider()
    st.info("Esta herramienta emula la lógica del Notebook usando SQLite3 local.")

# --- Cuerpo Principal ---
st.title("🧬 Explorador de Conceptos de SNOMED-CT")
st.markdown('<div class="subtle-hint">Búsqueda rápida por FSN (Fully Specified Name en español) + exploración de ancestros, atributos y descendientes.</div>',
            unsafe_allow_html=True)

# Input de búsqueda (con estado)
query = st.text_input(
    "Buscar concepto (FSN):",
    placeholder="Ej: corea (trastorno)",
    key="query",
)

# Si cambia la búsqueda, reseteamos selección para evitar inconsistencias
if st.session_state.query != st.session_state.last_query:
    st.session_state.selected_option = None
    st.session_state.last_query = st.session_state.query

if query and check_db_exists():
    resultados = buscar_concepto(query)

    if resultados.empty:
        st.warning("No se encontraron resultados.")
    else:
        # Selector para desambiguar
        opciones = resultados.apply(lambda x: f"{x['term']} | {x['conceptId']}", axis=1).tolist()

        seleccion_str = st.selectbox(
            "Seleccione el concepto exacto:",
            opciones,
            key="selected_option",
            index=0 if st.session_state.selected_option is None else opciones.index(st.session_state.selected_option),
        )

        if seleccion_str:
            # Extraer ID y Término
            fsn_sel = seleccion_str.split(" | ")[0]
            cid_sel = seleccion_str.split(" | ")[1]

            # --- OBTENER DATOS ---
            df_isa, df_attr, df_desc = obtener_info_completa(cid_sel)

            # Resolver nombres (Bulk resolution para velocidad)
            ids_a_resolver = set()
            if not df_isa.empty:
                ids_a_resolver.update(df_isa["destinationId"].tolist())
            if not df_attr.empty:
                ids_a_resolver.update(df_attr["typeId"].tolist())
                ids_a_resolver.update(df_attr["destinationId"].tolist())
            if not df_desc.empty:
                ids_a_resolver.update(df_desc["sourceId"].tolist())

            mapa_nombres = resolver_nombres_bulk(list(ids_a_resolver))

            # Enriquecer DataFrames
            if not df_isa.empty:
                df_isa["fsn"] = df_isa["destinationId"].map(mapa_nombres).fillna("Desconocido")
            if not df_attr.empty:
                df_attr["fsn_type"] = df_attr["typeId"].map(mapa_nombres).fillna("Desconocido")
                df_attr["fsn_dest"] = df_attr["destinationId"].map(mapa_nombres).fillna("Desconocido")
            if not df_desc.empty:
                df_desc["fsn"] = df_desc["sourceId"].map(mapa_nombres).fillna("Desconocido")

            st.divider()

            # 1. SECCIÓN CONCEPTO BUSCADO
            st.subheader("📌 Concepto Buscado")
            st.code(f"{cid_sel} |{fsn_sel}|", language="text")

            # 2. SECCIÓN ES UN[A] (ANCESTROS)
            st.subheader("⬆️ es un[a] (Ancestros)")
            if not df_isa.empty:
                for _, row in df_isa.iterrows():
                    st.text(f"{row['destinationId']} |{row['fsn']}|")
            else:
                st.caption("Concepto raíz o sin padres activos.")

            # 3. SECCIÓN ATRIBUTOS
            st.subheader("🧩 Atributos")
            if not df_attr.empty:
                texto_display = ""
                # Agrupamos por grupo de relación para replicar el estilo visual
                for grupo, df_grupo in df_attr.groupby("relationshipGroup"):
                    bloque = []
                    for _, row in df_grupo.iterrows():
                        bloque.append(
                            f"{row['typeId']} |{row['fsn_type']}| = {row['destinationId']} |{row['fsn_dest']}|"
                        )

                    # Formateo visual tipo JSON/Struct
                    texto_display += "{\n  " + ",\n  ".join(bloque) + "\n}\n"

                st.code(texto_display, language="text")
            else:
                st.caption("Sin atributos definidos.")

            # 4. SECCIÓN DESCENDIENTES Y REFSET
            st.subheader("🌳 Descendientes (Selección para Refset)")

            if not df_desc.empty:
                # Preparamos dataframe para el editor
                df_editor = df_desc[["sourceId", "fsn"]].copy()
                df_editor.columns = ["conceptId", "FSN"]
                df_editor.insert(0, "Incluir", False)  # Checkbox por defecto desactivado

                st.write(f"Descendientes detectados: {len(df_editor)}")

                # Tabla interactiva
                edited_df = st.data_editor(
                    df_editor,
                    column_config={
                        "Incluir": st.column_config.CheckboxColumn("Exportar", help="Seleccionar para Excel", default=False),
                        "conceptId": st.column_config.TextColumn("SCTID", width="medium"),
                        "FSN": st.column_config.TextColumn("Término", width="large"),
                    },
                    hide_index=True,
                    use_container_width=True,
                    height=400,
                )

                # Lógica de Exportación
                seleccionados = edited_df[edited_df["Incluir"] == True]

                if not seleccionados.empty:
                    # Crear Excel en memoria
                    buffer = BytesIO()
                    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                        # Hoja 1: Info
                        pd.DataFrame([{"Concepto Raíz": fsn_sel, "ID": cid_sel}]).to_excel(
                            writer, sheet_name="Info", index=False
                        )
                        # Hoja 2: Descendientes (Formato solicitado)
                        seleccionados[["conceptId", "FSN"]].to_excel(
                            writer, sheet_name="Descendientes_Refset", index=False
                        )
                        # Hoja 3: Atributos (Extra)
                        if not df_attr.empty:
                            df_attr.to_excel(writer, sheet_name="Detalle_Atributos", index=False)

                    buffer.seek(0)

                    st.download_button(
                        label=f"📥 Descargar Refset ({len(seleccionados)} conceptos)",
                        data=buffer,
                        file_name=f"Refset_{fsn_sel[:15]}_{cid_sel}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        type="primary",
                    )
            else:
                st.info("Este concepto no tiene descendientes.")

elif not query:
    st.info("👆 Ingrese un término en la barra de búsqueda para comenzar.")
