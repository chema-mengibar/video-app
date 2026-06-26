

# Configuration & Setup

## IA
- ollama
- ollama run qwen2.5-coder:7b
- file Modelfile
- En la terminal, en la misma carpeta del archivo, ejecuta:
  ollama create model-dev -f Modelfile
- En la Terminal: En lugar de ollama run qwen2.5-coder, ahora puedes poner ollama run model-dev.
- En IntelliJ: En la configuración del plugin (como Continue), donde dice model, debes poner "model-dev".
- %USERPROFILE%\.continue


## Backend
- pip install pywebview

## Frontend

- cd frontend
- npm create vite@latest . -- --template vue
- npm install
- npm install axios sass

# Development

Terminal 1 (Frontend): 
`cd frontend && npm run dev`

Terminal 2 (Python): 
`python main.py`