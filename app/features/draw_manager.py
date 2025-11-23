# features/draw_manager.py

import json
from PySide6.QtCore import QPoint

class DrawManager:
    """
    Gestiona el almacenamiento, carga y recuperación de datos de dibujo
    en función del tiempo del video.
    """
    def __init__(self):
        # Almacena los datos de dibujo. 
        # Formato: {start_time_msec: {'duration': duration_msec, 'paths': paths_data}}
        # paths_data es un dict: {'size': (w, h), 'paths': [[{'x': X, 'y': Y}, ...], ...]}
        self.drawing_data = {} 

    # --- Gestión de Datos ---

    def add_drawing_entry(self, start_time_msec: int, duration_msec: int, paths_data: dict):
        """
        Añade una nueva entrada de dibujo persistente. 
        
        Nota: paths_data ya está serializada (usa dicts en lugar de QPoint)
        gracias a DrawingVideoLabel.
        """
        
        entry = {
            'duration': duration_msec,
            'paths': paths_data  # Guardamos el diccionario completo: {'size': ..., 'paths': ...}
        }
        
        # El tiempo de inicio se usa como clave, convertido a string para consistencia de JSON
        self.drawing_data[str(start_time_msec)] = entry
        print(f"Drawing saved at {start_time_msec} ms for {duration_msec} ms.")


    def get_active_drawing_paths(self, current_time_msec: int) -> list:
        """
        Retorna una lista de todas las entradas de dibujo que deben estar visibles 
        en el tiempo actual del video (current_time_msec).

        Retorna: 
            list: Lista de diccionarios, donde cada dict contiene 'paths'.
        """
        active_paths = []
        
        # Iterar sobre las claves (tiempos de inicio)
        for start_time_str, data in self.drawing_data.items():
            try:
                # Convertir la clave (que puede ser string si viene de JSON) a int
                start_time = int(start_time_str)
                duration = data['duration']
                
                end_time = start_time + duration
                
                # Comprobar si el tiempo actual está dentro del rango del dibujo
                if start_time <= current_time_msec < end_time:
                    active_paths.append(data)
                    
            except (ValueError, KeyError) as e:
                print(f"Skipping invalid drawing entry: {e}")
                continue

        return active_paths

    # --- Persistencia (JSON) ---

    def save_data_to_file(self, filename: str):
        """Guarda todos los datos de dibujo en un archivo JSON."""
        try:
            with open(filename, 'w') as f:
                # Utilizamos self.drawing_data directamente, ya que las claves son str y los valores dicts
                json.dump(self.drawing_data, f, indent=4)
            print(f"Drawing data saved successfully to {filename}")
        except Exception as e:
            print(f"Error saving drawing data: {e}")

    def load_data_from_file(self, filename: str):
        """Carga los datos de dibujo desde un archivo JSON, reemplazando los datos actuales."""
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            
            # Las claves de JSON son strings, lo cual está bien para la carga.
            self.drawing_data = data
            print(f"Drawing data loaded successfully from {filename}. Total entries: {len(self.drawing_data)}")
        except FileNotFoundError:
            print(f"Error: File not found at {filename}")
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON format in {filename}")
        except Exception as e:
            print(f"Error loading drawing data: {e}")