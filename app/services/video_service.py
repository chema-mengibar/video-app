from PySide6.QtCore import QObject, Signal, Slot
import os
import numpy as np
import cv2 

# Importación del adaptador (CORREGIDA a importación absoluta desde la raíz del paquete 'app')
from adapters.opencv_video_processor import OpenCVVideoProcessor 

class VideoService(QObject):
    """
    Servicio de Video (Video Service).
    
    Mediador entre la UI y el procesador de video.
    """
    
    # Señales emitidas a la UI o a otros módulos
    frame_ready_signal = Signal(object) # Emite el frame (numpy array)
    time_updated_signal = Signal(int)    # Emite el tiempo actual en msec
    video_loaded_signal = Signal(bool, int, str) # éxito, duración, path del video

    def __init__(self, processor: OpenCVVideoProcessor, parent=None): 
        super().__init__(parent)
        
        # Inyección de Dependencia: El procesador de bajo nivel (adaptador)
        self.processor = processor 
        self.current_time_msec = 0
        self.duration_msec = 0
        self.video_path = None
        self.is_playing = False
        self.is_slider_down = False 

        # Rutas base para guardar screenshots, se configuran al cargar el video
        self.video_directory = None
        self.video_filename_base = None

        self._connect_processor_signals()

    def _connect_processor_signals(self):
        """Conecta las señales del procesador de video a los slots del servicio."""
        self.processor.frame_ready_signal.connect(self.frame_ready_signal)
        self.processor.time_updated_signal.connect(self._handle_time_update)
        self.processor.video_loaded_signal.connect(self._handle_video_loaded)

    # --- Métodos de Ayuda ---
    
    @staticmethod
    def format_time(msec: int) -> str:
        """Formatea milisegundos a una cadena de tiempo (HH_MM_SS_mmm) para nombre de archivo."""
        msec = int(msec)
        milliseconds = msec % 1000
        total_seconds = msec // 1000
        seconds = total_seconds % 60
        minutes = (total_seconds // 60) % 60
        hours = total_seconds // 3600
        
        # Usamos guiones bajos (_) como separador para ser amigables con nombres de archivo
        if hours > 0:
            return f"{hours:02d}_{minutes:02d}_{seconds:02d}_{milliseconds:03d}"
        return f"{minutes:02d}_{seconds:02d}_{milliseconds:03d}"
        
    # --- Slots Internos y Handlers ---
            
    @Slot(int)
    def _handle_time_update(self, current_msec):
        """Actualiza el tiempo interno y notifica a la UI si el slider no está siendo arrastrado."""
        self.current_time_msec = current_msec
        if not self.is_slider_down:
            self.time_updated_signal.emit(current_msec)
            
    @Slot(bool, int, str)
    def _handle_video_loaded(self, success: bool, duration_msec: int, video_path: str):
        """
        Maneja la carga exitosa/fallida del video y establece las rutas de archivos para screenshots.
        """
        self.duration_msec = duration_msec
        self.video_path = video_path
        
        if success:
            # Parsear y guardar la información de la ruta para el screenshot
            self.video_directory = os.path.dirname(video_path)
            filename_with_ext = os.path.basename(video_path)
            self.video_filename_base = os.path.splitext(filename_with_ext)[0]
            
            self.toggle_play_pause(False) # Iniciar en pausa
            
        self.video_loaded_signal.emit(success, duration_msec, video_path)

    # --- Métodos de Control (API del Servicio usados por la UI) ---
    
    def is_video_loaded(self) -> bool:
        """
        Verifica si el procesador subyacente ha cargado un video exitosamente.
        (Función requerida por el módulo de bookmarks).
        """
        return self.processor.is_loaded 
    
    def get_current_time(self) -> int:
        """Retorna el tiempo actual de reproducción en milisegundos."""
        return self.current_time_msec

    def load_video_file(self, path: str):
        """Solicita al procesador que cargue un archivo de video."""
        self.video_path = path
        self.processor.load_video(path)

    def toggle_play_pause(self, play: bool):
        """Alterna el estado de reproducción."""
        if self.processor.is_loaded:
            self.is_playing = play
            self.processor.set_playing(play)

    def seek(self, msec: int):
        """Solicita al procesador que se mueva a un tiempo específico."""
        self.is_slider_down = False
        self.processor.seek(msec)
        self.time_updated_signal.emit(msec) 

    def slider_moved(self):
        """Marca que el slider está siendo arrastrado por el usuario."""
        self.is_slider_down = True
        
    def set_quality(self, factor: float):
        """Solicita al procesador que cambie la calidad de reproducción."""
        self.processor.set_quality(factor)
        
    def stop_service(self):
        """Detiene el hilo de procesamiento de video al cerrar la aplicación."""
        self.processor.stop_processing()
        
    @Slot() 
    def save_screenshot(self):
        """
        Captura el frame actual y lo guarda en una subcarpeta de "screenshots"
        dentro del directorio del video.
        """
        # 1. Obtener el frame y el tiempo del procesador (adaptador)
        frame = self.processor.get_last_frame()
        current_msec = self.processor.get_current_time_msec()

        if frame is None or not self.processor.is_loaded:
            print("VideoService: No hay frame disponible para guardar o video no cargado.")
            return

        if not (self.video_directory and self.video_filename_base):
            print("VideoService: ERROR. Información de ruta de video no configurada. Cargue un video primero.")
            return

        # 2. Generar nombre de archivo basado en tiempo
        time_str = self.format_time(current_msec)
        
        # 3. Construir la ruta de la carpeta: /directorio_video/nombre_video__screenshots/
        screenshot_dir = os.path.join(
            self.video_directory, 
            f"{self.video_filename_base}__screenshots"
        )
        
        try:
            # Asegurar que la carpeta exista
            os.makedirs(screenshot_dir, exist_ok=True)
        except OSError as e:
            print(f"VideoService: ERROR al crear el directorio {screenshot_dir}: {e}")
            return
            
        # 4. Definir la ruta final: /.../capture_MM_SS_mmm.jpeg
        filepath = os.path.join(screenshot_dir, f"capture_{time_str}.jpeg")
                
        try:
            # 5. Guardar la imagen usando OpenCV
            success = cv2.imwrite(
                filepath, 
                frame, 
                [cv2.IMWRITE_JPEG_QUALITY, 95] 
            )
            
            if success:
                print(f"VideoService: Captura guardada exitosamente en: {filepath}")
            else:
                print(f"VideoService: ERROR desconocido al guardar la captura en: {filepath}")

        except Exception as e:
            print(f"VideoService: EXCEPCIÓN al guardar la captura: {e}")