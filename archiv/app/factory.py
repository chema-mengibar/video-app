import sys
from PySide6.QtWidgets import QApplication

# 1. Adaptadores e Implementaciones
from adapters.opencv_video_processor import OpenCVVideoProcessor
from features.draw.manager import DrawManager
# 🟢 Importar GridsManager para inicialización
from features.grid.grids_manager import GridsManager 

# 2. Servicios
from services.video_service import VideoService
from services.draw_service import DrawService

# 3. Core
from core.service_manager import ServiceManager

# 4. Presentación (UI)
from ui.main_window import MainWindow

# 5. Otros Features
# Deberías tener un Manager para la funcionalidad de dibujo
# from features.draw.draw_manager import DrawManager # Asumo que existe

def create_app():
    """
    Función Factory: Crea la aplicación, instancia las dependencias 
    y las cablea (Dependency Injection).
    """
    # 1. Inicializar PySide6
    app = QApplication(sys.argv)
    
    # 2. Crear Adaptadores y Managers de Features
    video_processor = OpenCVVideoProcessor()
    # Asumo que DrawManager ya está definido e importado
    # Si no, crea un mock simple:
    # class DrawManager:
    #     def __init__(self): pass
    #     def load_data(self, path): print(f"DrawManager: Loading {path}")
    #     def save_data(self, data, path): print(f"DrawManager: Saving {path}")
    draw_manager = DrawManager()
    grids_manager = GridsManager() # 🟢 Inicializar GridsManager
    
    # 3. Crear Servicios (Inyectando Adaptadores)
    video_service = VideoService(processor=video_processor)
    draw_service = DrawService(manager=draw_manager) 
    
    # 4. Crear el Gestor de Servicios (Coordina los servicios entre sí)
    # 🟢 INYECTAR todos los managers y servicios que serán accedidos globalmente
    service_manager = ServiceManager(
        video_service=video_service, 
        draw_service=draw_service,
        grids_manager=grids_manager # 🟢 Añadir GridsManager al ServiceManager
    )
    
    # 5. Crear la Ventana Principal (Inyectando ServiceManager)
    # 🛑 CORRECCIÓN CRÍTICA: La MainWindow ahora solo recibe el ServiceManager.
    # El ServiceManager debe exponer los servicios internamente o a través de helpers.
    # Si MainWindow NECESITA una referencia directa a VideoService, debe usar el helper:
    # Asumiendo que MainWindow espera una instancia de VideoService como primer argumento.
    # Si MainWindow recibe solo el ServiceManager, entonces el constructor de MainWindow debe cambiar.
    # Si el código fallaba en este punto, debe ser por el acceso:
    
    # Uso el helper 'video()' para acceder a VideoService si es necesario en MainWindow constructor:
    main_window = MainWindow(
        service_manager=service_manager, 
      
    )
    
    # 6. Mostrar UI
    main_window.show()
    return app