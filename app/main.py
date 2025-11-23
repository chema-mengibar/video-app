# src/app/main.py

import sys
# Asumiendo que factory.py está en el mismo nivel o es un módulo accesible.
from factory import create_app 

def run_app():
    """Arranque de la aplicación a través del factory."""
    try:
        app, main_window = create_app()
        main_window.show()
        sys.exit(app.exec())
    except Exception as e:
        print(f"FATAL ERROR during application startup: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_app()