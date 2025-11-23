# src/app/factory.py

import sys
from PySide6.QtWidgets import QApplication

# 1. Adaptadores e Implementaciones (Lógica de bajo nivel)
from adapters.opencv_video_processor import OpenCVVideoProcessor
from features.draw.manager import DrawManager

# 2. Servicios (La lógica de aplicación - Los Ports)
from services.video_service import VideoService
from services.draw_service import DrawService

# 3. Presentación (La Vista)
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
    # 🟢 CORRECCIÓN: Aseguramos que el argumento clave sea 'manager'
    draw_service = DrawService(manager=draw_manager) 
    
    # 4. Crear la Ventana Principal (Inyectando Servicios)
    main_window = MainWindow(
        video_service=video_service,
        draw_service=draw_service
    )
    
    return app, main_window