# video_logic.py

import cv2
import time
import os
import sys

# 🛑 CORRECCIÓN: QObject, QThread, Signal, etc., DEBEN importarse desde QtCore.
from PySide6.QtCore import QObject, QThread, Signal, Slot, QMutex, QWaitCondition, QTimer
# QFileDialog DEBE importarse desde QtWidgets.
from PySide6.QtWidgets import QFileDialog 

# ----------------------------------------------------------------------
# WORKER: Lógica de Captura y Procesamiento de Frames en un Hilo Separado
# ----------------------------------------------------------------------

class VideoWorker(QObject):
    """
    Objeto Worker que vive en un QThread separado para manejar la captura
    y el procesamiento de video sin bloquear la interfaz de usuario.
    """
    frame_ready = Signal(object)
    video_loaded = Signal(bool, int) # Señal (éxito, duración_msec)
    time_updated = Signal(int)

    def __init__(self, mutex: QMutex, wait_condition: QWaitCondition):
        super().__init__()
        self.cap = None
        self.stop_requested = False
        self.is_paused = False
        self.target_msec = -1 
        self.is_seeking = False

        self._current_frame = None 
        self._current_msec = 0

        self.mutex = mutex
        self.wait_condition = wait_condition
        
        self.framerate = 30
        self.delay_msec = 33 # 1000 / 30 FPS inicial

    def set_capture(self, cap):
        """Inicializa el objeto de captura y calcula el framerate."""
        self.cap = cap
        if self.cap and self.cap.isOpened():
            self.framerate = self.cap.get(cv2.CAP_PROP_FPS)
            if self.framerate <= 0:
                self.framerate = 30
            self.delay_msec = 1000 / self.framerate
        else:
            self.cap = None
            self.framerate = 30
            self.delay_msec = 33

    # 🟢 CORRECCIÓN 1: Añadir método stop al Worker
    @Slot()
    def stop(self):
        """Método para detener el worker de forma segura."""
        self.stop_requested = True
        self.mutex.lock()
        # Despertar el hilo si está en pausa para que pueda salir del bucle
        self.wait_condition.wakeAll() 
        self.mutex.unlock()


    def run(self):
        """Loop principal del worker que lee frames."""
        print(f"Worker thread running. Delay: {self.delay_msec:.2f}ms")
        
        while not self.stop_requested:

            # Inicializar start_time al inicio del bucle para evitar UnboundLocalError
            start_time = time.time()
            
            self.mutex.lock()
            
            # Control de Pausa y Búsqueda
            if self.is_paused and not self.is_seeking:
                self.wait_condition.wait(self.mutex)
            
            if self.is_seeking:
                if self.cap and self.target_msec >= 0:
                    self.cap.set(cv2.CAP_PROP_POS_MSEC, self.target_msec)
                    self.target_msec = -1 
                    self.is_seeking = False
                else:
                    self.is_seeking = False
                    self.wait_condition.wait(self.mutex) # Esperar si no hay cap o target inválido

            # Lectura de Frame
            if self.cap and self.cap.isOpened():
                
                ret, frame = self.cap.read()
                
                if ret:
                    self._current_frame = frame
                    self._current_msec = int(self.cap.get(cv2.CAP_PROP_POS_MSEC))
                    
                    self.frame_ready.emit(frame)
                    self.time_updated.emit(self._current_msec)
                else:
                    # Final del video
                    fps = self.cap.get(cv2.CAP_PROP_FPS)
                    if fps > 0:
                        self._current_msec = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT) * 1000 / fps)
                    else:
                         self._current_msec = 0
                         
                    self.time_updated.emit(self._current_msec)
                    self.is_paused = True # Pausar al final
                    self.cap.set(cv2.CAP_PROP_POS_MSEC, 0) # Rewind para la siguiente reproducción
                    
            self.mutex.unlock()

            # Control de retardo para mantener el framerate
            elapsed_time = (time.time() - start_time) * 1000 # en msec
            sleep_time = max(0, self.delay_msec - elapsed_time) / 1000
            time.sleep(sleep_time)
            
        print("Worker thread finished.")
        if self.cap:
            self.cap.release()

# ----------------------------------------------------------------------
# CONTROLLER: Lógica de Control de Video
# ----------------------------------------------------------------------

class VideoPlayerController(QObject):
    """
    Controla el estado del video, la interacción con el Worker y la
    comunicación de señales hacia la UI.
    """
    # Señales que la UI conectará al Controller (duplicadas del worker para abstracción)
    frame_ready_signal = Signal(object)
    video_loaded_signal = Signal(bool, int)
    time_updated_signal = Signal(int)

    def __init__(self):
        super().__init__()
        
        self.is_video_loaded = False
        self.duration_msec = 0
        self.scale_factor = 1.0 

        self.video_path = None
        self.video_directory = None
        
        # Inicializar la variable del slider
        self.slider_released_value = 0 
        
        # Sincronización de hilos
        self.mutex = QMutex()
        self.wait_condition = QWaitCondition()
        
        # Hilo y Worker
        self.worker_thread = QThread()
        self.worker = VideoWorker(self.mutex, self.wait_condition)
        self.worker.moveToThread(self.worker_thread)
        
        # Conectar señales del worker a las señales públicas del controller
        self.worker.frame_ready.connect(self.frame_ready_signal)
        self.worker.video_loaded.connect(self._handle_video_loaded)
        self.worker.time_updated.connect(self.time_updated_signal)

    def _handle_video_loaded(self, success, duration_msec):
        """Maneja el resultado de la carga de video desde el worker."""
        self.is_video_loaded = success
        self.duration_msec = duration_msec
        self.video_loaded_signal.emit(success, duration_msec) # Propagar a la UI

    # --- Métodos de Interacción con el Hilo ---

    def load_video_file(self):
        """Abre diálogo y prepara el worker para cargar el video."""
        
        path, _ = QFileDialog.getOpenFileName(None, "Open Video", "", "Video Files (*.mp4 *.avi *.mov)")
        
        if path:
            cap = cv2.VideoCapture(path)
            if cap.isOpened():
                fps = cap.get(cv2.CAP_PROP_FPS)
                if fps > 0:
                    duration = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) * 1000 / fps)
                else:
                    duration = 0
                
                self.mutex.lock()
                self.worker.set_capture(cap)
                self.worker.is_paused = False # Asegurar reproducción
                self.wait_condition.wakeAll()
                self.mutex.unlock()
                
                self._handle_video_loaded(True, duration)
            else:
                self._handle_video_loaded(False, 0)
        else:
            self._handle_video_loaded(False, 0)


    @Slot(bool)
    def toggle_play_pause(self, play: bool):
        """Alterna el estado de reproducción del worker."""
        self.mutex.lock()
        self.worker.is_paused = not play
        if play:
            self.wait_condition.wakeAll()
        self.mutex.unlock()

    @Slot(int)
    def seek(self, msec):
        """Solicita al worker saltar a una posición específica."""
        if not self.is_video_loaded:
            return
            
        msec = max(0, min(msec, self.duration_msec)) # Asegurar que esté dentro del rango
            
        self.mutex.lock()
        self.worker.target_msec = msec
        self.worker.is_seeking = True
        self.wait_condition.wakeAll()
        self.mutex.unlock()


    # --- Métodos de Interacción UI (Slider/Quality) ---
    
    @Slot(int)
    def slider_moved(self, value):
        """Maneja el movimiento del slider (arrastre). Pausa el video."""
        self.toggle_play_pause(False) # Pausar

        # Guardar el valor actual del slider
        self.slider_released_value = value 

    def slider_released(self):
        """Maneja la liberación del slider. Realiza la búsqueda y mantiene la pausa."""
        self.seek(self.slider_released_value)
        self.toggle_play_pause(False) # Mantener en pausa hasta que el usuario presione Play

    def quality_changed(self, index):
        """Maneja el cambio de calidad de video (factor de escala)."""
        
        scale_map = {0: 1.0, 1: 0.5, 2: 0.25} 
        self.scale_factor = scale_map.get(index, 1.0)
        
        # Forzar un redibujo para aplicar el nuevo factor (buscando la posición actual)
        self.seek(self.get_current_time())


    # --- Métodos de Utilidad ---
    
    def get_current_time(self):
        """Retorna el tiempo actual del video."""
        self.mutex.lock()
        current_msec = self.worker._current_msec
        self.mutex.unlock()
        return current_msec

    def _format_time(self, msec):
        """Formatea el tiempo en milisegundos a HH:MM:SS.mmm."""
        total_seconds = msec // 1000
        milliseconds = msec % 1000
        seconds = total_seconds % 60
        minutes = (total_seconds // 60) % 60
        hours = total_seconds // 3600
        
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}.{milliseconds:03d}"
        
    # 🟢 CORRECCIÓN 3: Añadir método para detener el thread
    def stop_thread(self):
        """Detiene el worker de forma controlada."""
        self.worker.stop() # Llama al nuevo método stop() del Worker