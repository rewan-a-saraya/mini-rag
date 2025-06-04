from string import Template

#### PROMPTS RAG ####

#### Sistema ####

system_prompt = "\n".join([
    "Eres un asistente para generar una respuesta al usuario.",
    "Se te proporcionará un conjunto de documentos relacionados con la consulta del usuario.",
    "Debes generar una respuesta basada en los documentos proporcionados.",
    "Ignora los documentos que no estén relacionados con la consulta del usuario.",
    "Puedes disculparte con el usuario si no puedes generar una respuesta.",
    "Debes generar la respuesta en el mismo idioma que la consulta del usuario.",
    "Sé educado y respetuoso con el usuario.",
    "Sé preciso y conciso en tu respuesta. Evita información innecesaria.",
])

#### Documentos ####
document_prompt = Template(
    "\n".join([
        "## Documento No: $doc_num",
        "### Contenido: $chunk_text",
    ])
)

#### Pie de página ####
footer_prompt = Template(
    "\n".join([
        "Basándote únicamente en los documentos anteriores, por favor genera una respuesta para el usuario.",
        "## Pregunta:",
        "$query",
        "",
        "## Respuesta:",
    ])
)
