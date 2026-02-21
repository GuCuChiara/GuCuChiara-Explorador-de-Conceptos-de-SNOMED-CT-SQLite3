## Explorador SNOMED-CT Argentina – Streamlit + SQLite3
### La solución implementa un pipeline ETL local optimizado, motor de consultas SQL y una interfaz en Streamlit.

---

## Descripción:
## 📌 Aplicación interactiva para implementar un explorador semántico de SNOMED-CT Edition Snapshot Argentina utilizando:
* 🐍 Python
* 🗄 SQLite3 (base optimizada local)
* 📊 Pandas
* 🌐 Streamlit (interfaz interactiva)
* ⚙️ Archivos RF2 de Descripciones y Relaciones (Snapshot_ArgentinaEdition_20251120).

---

## El sistema permite buscar conceptos por FSN en español y visualizar:
* Relaciones jerárquicas (Is-A / Ancestros)
* Relaciones de atributos
* Descendientes inferidos
* Exportación dinámica de subconjuntos (Refsets) a Excel

---

## La solución está pensada como herramienta de exploración semántica local sin servidor Snowstorm, para el apoyo de:
* Exploración y aprendizaje sobre la Ontología
* Navegación jerárquica offline
* Construcción de Refsets
* Soporte a interoperabilidad clínica (FHIR / ValueSets).

---
## 🖥️ Arquitectura de Despliegue (Local / Portable):
* 100% local
* No requiere:
   * Snowstorm
   * Elasticsearch
   * Servidor externo
* **Portable** (puede ejecutarse en cualquier entorno Python compatible)

---

## ⚙️ Componentes Técnicos:

| Capa         | Tecnología         | Función                        |
| ------------ | ------------------ | ------------------------------ |
| ETL          | Pandas             | Procesamiento inicial Snapshot |
| DB           | SQLite             | Persistencia optimizada        |
| Query Engine | SQL parametrizado  | Exploración semántica          |
| Resolver     | Bulk SQL query     | Traducción eficiente SCTID→FSN |
| UI           | Streamlit          | Interfaz interactiva           |
| Export       | OpenPyXL + BytesIO | Generación Excel en memoria    |

---
## Estructura del Proyecto:

```
├── Buscador_SNOMED-CT_5_Sqlite3.py
├── snomed_argentina.db (auto-generado)
├── README.md
└── Snapshot/
    ├── sct2_Description_Snapshot_ArgentinaEdition_20251120.txt
    └── sct2_Relationship_Snapshot_ArgentinaEdition_20251120.txt

```

---

## 🧩 Funcionalidades:

## 🔎 Búsqueda por FSN (Español):

* Filtro activo (active = 1)
* Limitación a 50 resultados
---

<img width="1516" height="543" alt="image" src="https://github.com/user-attachments/assets/1202ffcc-3262-427f-8909-fddcd1f214e7" />

---

## ⬆️ Exploración de Jerarquías:
* Ancestros (Is-A)
---
<img width="1068" height="602" alt="image" src="https://github.com/user-attachments/assets/cf8a4f6b-3e79-4193-9e21-5ae68f4a2101" />

---

* Descendientes (inversa de Is-A)
---
<img width="1589" height="508" alt="image" src="https://github.com/user-attachments/assets/b84d3c1c-68a2-4bcf-b0ce-1fa7a8c9452b" />

---
## 🧩 Atributos
---
<img width="989" height="458" alt="image" src="https://github.com/user-attachments/assets/97bd3649-97de-4086-9e87-0d350aa397dc" />

---


## 🌳 Construcción de Refset
* Selección de descendientes con checkbox
* Exportación Excel multi-hoja:
    * Concepto raíz
    * Descendientes seleccionados
    * Atributos detallados
---
<img width="1597" height="855" alt="image" src="https://github.com/user-attachments/assets/74d29a00-751f-49d3-bd53-f601218c6e36" />

---


## 🧠 Casos de Uso en Health Informatics
* Construcción de ValueSets para FHIR
* Curación de subconjuntos clínicos
* Auditoría basada en jerarquía SNOMED-CT
* Soporte a decisiones terminológicas
* Exploración offline en entornos regulados

---
## 🚀 Instalación

### 1️⃣ Clonar repositorio:
```
git clone https://github.com/tu_usuario/snomed-explorer.git
cd snomed-explorer
```
### 2️⃣ Crear entorno
```
python -m venv venv
venv\Scripts\activate
```
### 3️⃣ Instalar dependencias
```
pip install streamlit pandas openpyxl
```
### 4️⃣ Ejecutar
```
streamlit run Buscador_SNOMED-CT_5_Sqlite3.py
```

---






