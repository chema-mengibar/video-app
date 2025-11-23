
# src/app/factory.py

import sys
from PySide6.QtWidgets import QApplication

# 1. Adaptadores e Implementaciones
from adapters.opencv_video_processor import OpenCVVideoProcessor
from features.draw.manager import DrawManager

# 2. Servicios
from services.video_service import VideoService
from services.draw_service import DrawService

# 3. Core
from core.service_manager import ServiceManager

# 4. Presentación (UI)
from ui.main_window import MainWindow

def create_app():
    """
    Función Factory: Crea la aplicación, instancia las dependencias 
    y las cablea (Dependency Injection).
    """
    # 1. Inicializar PySide6
    app = QApplication(sys.argv)
    
    # 2. Crear Adaptadores y Managers de Features
    video_processor = OpenCVVideoProcessor()
    draw_manager = DrawManager()
    
    # 3. Crear Servicios (Inyectando Adaptadores)
    video_service = VideoService(processor=video_processor)
    draw_service = DrawService(manager=draw_manager) 
    
    # 4. Crear el Gestor de Servicios (Coordina los servicios entre sí)
    service_manager = ServiceManager(video_service=video_service, draw_service=draw_service)
    
    # 5. Crear la Ventana Principal (Inyectando Servicios y Manager)
    # La MainWindow solo conoce el ServiceManager y VideoService (para el seek directo)
    main_window = MainWindow(
        video_service=video_service, # Necesario para acciones directas (load, play)
        service_manager=service_manager # Coordinación y estado
    )
    
    return app, main_window