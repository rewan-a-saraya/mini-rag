# mini-rag

This is a minimal implementation of the RAG model for question answering

## Requirements

- Python 3.8 or later

### Install Python usinig Miniconda

1) Install Miniconda from : ([https://www.anaconda.com/docs/getting-started/miniconda/main](https://www.anaconda.com/download/success))
2) Create a new environment using :
   ```bash
   $  conda create -n mini-rag python=3.8
   ```
3) Activate the environment :
   ```bash
   $  conda activate mini-rag
   ```

### (Optional) Run Ollama Local LLM Server using Colab + Ngrok
- Check the https://colab.research.google.com/drive/1MvOXu4vEWZ6XJq0C2xkBy4eLhzvpnJx2#scrollTo=BrhlgM9KbCiE

## Installation

### Install the required packages

```bash
   $  pip install -r requirements.txt
   ```

### Setup the environment variables

```bash 
   $  cp .env.example .env
```

Set your environment variables in the .env file. Like OPENAI_API_KEY value.

### Run Docker Compose Services

```bash
   $ cd docker
   $ cp .env.example .env
```
update .env with your credentials

```bash
   $ cd docker
   $ sudo docker compose up -d
```

### Run the FastAPI Server


```bash 
   $  uvicorn main:app --reload --host 0.0.0.0
```
