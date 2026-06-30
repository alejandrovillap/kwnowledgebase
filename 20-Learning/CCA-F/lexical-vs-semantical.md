---
title: Lexical Vs Semantical
date: 2026-03-26
type: resume
technology: "gen-ai"
status: active
tags: ["lexical-search", "semantic-search", bm25, embeddings, "hybrid-search", rag, "vector-database"]
keywords: [lexical search, semantic search, BM25, inverted index, embeddings, cosine similarity, HNSW, hybrid search, RRF, RAG, vector database, ANN, vocabulary mismatch]
source: "notion-migration"
project: ""
certification: CCA
confidence: high
---

# Lexical Vs Semantical

## Búsqueda Lexical — definición formal

**Definición:** La búsqueda lexical es un modelo de recuperación de información basado en la coincidencia exacta o parcial de términos entre la query del usuario y los documentos indexados. Opera sobre la forma superficial del texto — las palabras como cadenas de caracteres — sin inferir significado ni contexto.

**Mecanismo interno:**

El sistema construye un **índice invertido** — una estructura de datos que mapea cada término único a la lista de documentos que lo contienen, con su frecuencia de aparición.

```
Índice invertido:
"cancelar"    →  [doc_3, doc_7, doc_12]
"contrato"    →  [doc_1, doc_3, doc_8, doc_12]
"terminacion" →  [doc_2, doc_5, doc_9]
"rescision"   →  [doc_5, doc_11]
```

Cuando el usuario busca *"cancelar contrato"* el sistema intersecta las listas — encuentra doc_3 y doc_12. Los documentos con *"terminacion"* o *"rescision"* no aparecen aunque signifiquen lo mismo.

**El algoritmo estándar — BM25:**

BM25 (Best Match 25) es el algoritmo de ranking lexical más usado en producción. Calcula la relevancia de un documento para una query considerando:

```
TF  — Term Frequency: cuántas veces aparece el término en el documento
IDF — Inverse Document Frequency: qué tan raro es el término en toda la colección
L   — normalización por longitud del documento
```

Un término que aparece frecuentemente en un documento corto y es raro en la colección general recibe el score más alto. Es el algoritmo detrás de Elasticsearch, Apache Solr, y la búsqueda de Google antes de los embeddings.

**Propiedades formales:**

- Determinista — la misma query sobre el mismo índice produce siempre el mismo resultado ordenado.
- Exacta — no tolera variaciones morfológicas sin preprocesamiento explícito. *"cancelar"* y *"cancelación"* son términos diferentes a menos que apliques stemming o lematización.
- Transparente — puedes explicar exactamente por qué un documento fue recuperado.

**Limitaciones formales:**

- Vocabulary mismatch problem — cuando el vocabulario del usuario no coincide con el vocabulario del documento. Es la limitación fundamental e irresoluble del modelo lexical puro.
- Ausencia de comprensión semántica — no distingue entre *"banco financiero"* y *"banco de madera"* a menos que el contexto esté explícito en el texto.

## Búsqueda Semántica — definición formal

**Definición:** La búsqueda semántica es un modelo de recuperación de información basado en la similitud de representaciones vectoriales densas del significado. Opera sobre el espacio latente del lenguaje — capturando relaciones semánticas, sintácticas, y contextuales que trascienden la forma superficial del texto.

**Mecanismo interno:**

Un modelo de embeddings — típicamente un transformer preentrenado como text-embedding-ada-002 de OpenAI o los modelos de Anthropic — transforma cada fragmento de texto en un vector denso de alta dimensión.

```
Dimensiones típicas:
text-embedding-ada-002  →  1,536 dimensiones
sentence-transformers   →  768 dimensiones
modelos grandes         →  3,072+ dimensiones
```

Cada dimensión captura una característica semántica latente del texto. El vector resultante es una coordenada en un espacio de significado donde textos similares ocupan regiones cercanas.

**La medida de similitud — Cosine Similarity:**

Mide el coseno del ángulo entre dos vectores en el espacio n-dimensional:

```
similarity(A, B) = (A · B) / (||A|| × ||B||)

Donde:
A · B  = suma de productos elemento a elemento
||A||  = raíz de la suma de cuadrados de A
||B||  = raíz de la suma de cuadrados de B

Rango: [-1, 1]
  1.0  = vectores idénticos en dirección
  0.0  = vectores ortogonales, sin relación
 -1.0  = vectores opuestos en dirección
```

La ventaja sobre la distancia euclidiana es que cosine similarity es invariante a la magnitud — solo importa la dirección del vector, no su longitud.

**La Vector Database:**

Almacena los vectores y ejecuta búsquedas de similitud eficientemente. El problema computacional es encontrar los K vectores más similares entre millones — llamado **Approximate Nearest Neighbor (ANN)**.

Los algoritmos más usados:

```
HNSW  — Hierarchical Navigable Small World
        Construye un grafo jerárquico de vectores
        Búsqueda O(log n) — el más rápido en producción

IVF   — Inverted File Index
        Agrupa vectores en clusters
        Busca solo en los clusters más prometedores

PQ    — Product Quantization
        Comprime vectores para reducir memoria
        Sacrifica precisión por velocidad y escala
```

Bases de datos vectoriales populares: Pinecone, Weaviate, Chroma, pgvector (extensión de PostgreSQL).

**Propiedades formales:**

- Probabilístico — el resultado puede variar con el mismo query si el modelo de embeddings se actualiza.
- Aproximado — los algoritmos ANN no garantizan encontrar el vecino más cercano exacto.
- Opaco — no puedes explicar exactamente por qué un documento fue recuperado en términos de reglas explícitas.

## Hybrid Search — definición formal

**Definición:** Hybrid Search es la combinación de recuperación lexical y semántica cuyos resultados se fusionan mediante un algoritmo de re-ranking para producir un ranking final que maximiza tanto la precisión como la cobertura.

**El mecanismo de fusión — Reciprocal Rank Fusion (RRF):**

Cada sistema produce su propio ranking. RRF combina los rankings sin requerir que los scores sean comparables entre sistemas:

```
RRF_score(d) = Σ 1 / (k + rank_i(d))

Donde:
d       = documento
k       = constante de suavizado (típicamente 60)
rank_i  = posición del documento en el ranking del sistema i
```

Un documento que aparece en posición 1 en lexical y posición 3 en semántica recibe un score combinado alto.

**Las tres fases del Hybrid Search:**

```
Fase 1 — Recuperación paralela
  Lexical   →  BM25 sobre índice invertido  →  Top-K documentos con score BM25
  Semántica →  ANN sobre Vector DB          →  Top-K documentos con cosine similarity

Fase 2 — Fusión
  RRF combina ambos rankings en un ranking unificado

Fase 3 — Re-ranking opcional
  Un cross-encoder evalúa cada par (query, documento) en profundidad
  Reordena el Top-N final con mayor precisión
  Más lento pero más preciso — se aplica solo al Top-N, no a toda la colección
```

## La tabla comparativa formal completa

| Dimensión | Lexical | Semántica | Hybrid |
|---|---|---|---|
| Modelo | Índice invertido + BM25 | Embeddings + Vector DB | BM25 + ANN + RRF |
| Representación | Sparse vector (TF-IDF) | Dense vector (1536 dims) | Ambas |
| Algoritmo de similitud | BM25 | Cosine Similarity | RRF |
| Complejidad computacional | O(log n) | O(log n) con ANN | O(log n) × 2 |
| Vocabulario mismatch | No resuelve | Resuelve | Resuelve |
| Términos exactos | Alta precisión | Puede fallar | Alta precisión |
| Lenguaje natural | Falla | Alta cobertura | Alta cobertura |
| Determinismo | Determinista | Probabilístico | Probabilístico |
| Explicabilidad | Alta | Baja | Media |
| Costo | Bajo | Alto | Alto |
| Caso de uso óptimo | IDs, códigos, términos técnicos | Preguntas en lenguaje natural | Producción enterprise |

## La tabla de diferencias formales

| Dimensión | Lexical | Semántica |
|---|---|---|
| Qué busca | Palabras exactas | Significado e intención |
| Cómo funciona | Índice invertido — mapea palabra a documento | Vectores — compara cosine similarity |
| Velocidad | Muy rápida | Más lenta — requiere cómputo vectorial |
| Resultado | Determinista — siempre igual | Probabilístico — puede variar |
| Falla cuando | El usuario usa sinónimos o paráfrasis | Términos muy específicos como IDs o códigos |
| Tecnología | SQL LIKE, Elasticsearch, grep, BM25 | Vector DB, embeddings, cosine similarity |
| Costo | Bajo | Alto — requiere modelo de embeddings |

## La jerarquía de decisión arquitectónica

```
¿El sistema recibe queries en lenguaje natural?
    NO  →  Lexical es suficiente
    SÍ  →  ¿El dominio tiene vocabulario técnico específico?
               NO  →  Semántica pura
               SÍ  →  Hybrid Search
                       Lexical para términos técnicos exactos
                       Semántica para lenguaje natural
                       RRF para fusión de resultados
```

## Cuándo usar cuál — la decisión arquitectónica

**Lexical es mejor cuando:**
- Buscas términos técnicos exactos — número de contrato, código de producto, ID de orden
- El vocabulario es controlado y predecible
- La velocidad es crítica
- Necesitas resultados 100% reproducibles

**Semántica es mejor cuando:**
- Los usuarios escriben en lenguaje natural
- Hay múltiples formas de decir lo mismo
- Buscas por concepto, no por término exacto
- El dominio tiene sinónimos frecuentes

**Hybrid Search es mejor cuando:**
- Tienes ambos tipos de queries
- Necesitas alta precisión Y alta cobertura
- Es un sistema de producción enterprise

## La conexión con RAG y el examen

En arquitectura RAG el sistema de búsqueda es el componente que determina qué información recibe Claude. Una decisión incorrecta aquí propaga el error a todo lo demás:

```
Búsqueda incorrecta  →  chunks irrelevantes recuperados
                     →  Context Injection con información incorrecta
                     →  Claude responde con base en datos incorrectos
                     →  Output incorrecto aunque Claude funcione perfectamente
```

El examen te presenta este escenario y pregunta dónde está el fallo. La respuesta siempre apunta al sistema de recuperación — no a Claude, no al prompt, no al schema.

En un sistema RAG de producción el examen te preguntaría: *"Un agente de soporte busca en la base de conocimiento pero no encuentra artículos relevantes cuando el usuario usa lenguaje informal. ¿Qué falta?"* La respuesta es que el sistema usa búsqueda lexical. La solución es agregar búsqueda semántica con embeddings.

## La manzanita

Tienes una biblioteca con 10,000 libros. Alguien te pregunta: *"¿tienes algo sobre autos que no consumen gasolina?"*

**El bibliotecario lexical** busca exactamente esas palabras — "autos", "gasolina" — en el índice. Si un libro dice *"vehículos eléctricos"* no aparece en los resultados porque no contiene las palabras exactas de la búsqueda.

**El bibliotecario semántico** entiende lo que quieres decir — *"autos que no consumen gasolina"* significa vehículos eléctricos, híbridos, de hidrógeno. Encuentra todos esos libros aunque ninguno use exactamente tus palabras.
