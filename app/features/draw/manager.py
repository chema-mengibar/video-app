# src/app/features/draw/manager.py

import json
import os

class DrawManager:
    """
    Gestiona la persistencia y recuperación de los trazos de dibujo 
    asociados a un rango de tiempo específico en el video.
    
    Estructura interna:
    self.drawing_entries = [
        {'time_msec': X, 'duration_msec': Y, 'paths': [PathData]}, 
        ...
    ]
    Donde PathData es el diccionario generado por DrawingVideoLabel.
    """
    
    def __init__(self):
        self.drawing_entries = []
        
    def add_drawing_entry(self, start_msec: int, duration_msec: int, paths_data: list):
        """
        Añade una nueva entrada de dibujo persistente.

        :param start_msec: Tiempo en milisegundos donde el dibujo empieza a mostrarse.
        :param duration_msec: Duración en milisegundos que el dibujo es visible.
        :param paths_data: Lista de diccionarios que describen los trazos dibujados.
        """
        if not paths_data:
            return
            
        new_entry = {
            "time_msec": start_msec,
            "duration_msec": duration_msec,
            "paths": paths_data
        }
        self.drawing_entries.append(new_entry)
        
    def get_active_drawing_paths(self, current_msec: int) -> list:
        """
        Retorna la lista de 'paths' (trazos) que deben estar activos en el 
        tiempo actual del video.
        
        :param current_msec: El tiempo actual de reproducción del video.
        :return: Lista de PathsData activos en ese momento.
        """
        active_paths = []
        
        for entry in self.drawing_entries:
            start = entry['time_msec']
            end = entry['time_msec'] + entry['duration_msec']
            
            # El dibujo está activo si el tiempo actual está dentro del rango [start, end)
            if start <= current_msec < end:
                active_paths.extend(entry['paths'])
                
        return active_paths

    # ------------------------------------------------------------------
    # PERSISTENCIA (Manejo de Errores)
    # ------------------------------------------------------------------
    
    def save_data_to_file(self, path: str):
        """Guarda la lista de entradas de dibujo en un archivo JSON."""
        try:
            with open(path, 'w') as f:
                json.dump(self.drawing_entries, f, indent=4)
            print(f"Dibujos guardados en: {path}")
        except Exception as e:
            print(f"Error al guardar dibujos en {path}: {e}")

    def load_data_from_file(self, path: str):
        """
        Carga la lista de entradas de dibujo desde un archivo JSON con validación robusta.
        Si falla, la lista de dibujos queda vacía.
        """
        
        if not os.path.exists(path):
            print(f"Archivo de dibujo no encontrado ({path}). Inicializando lista vacía.")
            self.drawing_entries = []
            return

        try:
            with open(path, 'r') as f:
                data = json.load(f)

            if not isinstance(data, list):
                print(f"Error de formato: El archivo JSON en {path} no contiene una lista de entradas (esperado: [...]).")
                self.drawing_entries = []
                return

            loaded_entries = []
            required_keys = ['time_msec', 'duration_msec', 'paths']
            
            for item in data:
                if all(k in item for k in required_keys) and isinstance(item['paths'], list):
                    loaded_entries.append(item)
                else:
                    print(f"Advertencia: Entrada de dibujo con formato inválido ignorada: {item}")

            self.drawing_entries = loaded_entries
            print(f"Dibujos cargados ({len(loaded_entries)} entradas) desde: {path}")

        except json.JSONDecodeError:
            print(f"Error al decodificar el archivo JSON en {path}. El archivo está corrupto o tiene formato inválido.")
            self.drawing_entries = []
        except Exception as e:
            print(f"Error desconocido al cargar dibujos desde {path}: {e}")
            self.drawing_entries = []