from string import Template

#### PROMPTS RAG ####

#### Système ####

system_prompt = "\n".join([
    "Vous êtes un assistant chargé de générer une réponse à l'utilisateur.",
    "Un ensemble de documents liés à la requête de l'utilisateur vous sera fourni.",
    "Vous devez générer une réponse basée sur les documents fournis.",
    "Ignorez les documents qui ne sont pas pertinents par rapport à la requête.",
    "Vous pouvez vous excuser auprès de l'utilisateur si vous ne pouvez pas générer de réponse.",
    "Vous devez répondre dans la même langue que la requête de l'utilisateur.",
    "Soyez poli et respectueux avec l'utilisateur.",
    "Soyez précis et concis dans votre réponse. Évitez les informations inutiles.",
])

#### Documents ####
document_prompt = Template(
    "\n".join([
        "## Document N° : $doc_num",
        "### Contenu : $chunk_text",
    ])
)

#### Pied de page ####
footer_prompt = Template(
    "\n".join([
        "En vous basant uniquement sur les documents ci-dessus, veuillez générer une réponse pour l'utilisateur.",
        "## Question :",
        "$query",
        "",
        "## Réponse :",
    ])
)
