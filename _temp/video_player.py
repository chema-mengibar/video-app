import sys
# 1. Componentes de la Interfaz (UI)
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QFileDialog, 
    QGridLayout, QLabel, QPushButton, QVBoxLayout, QSizePolicy, QSlider, QComboBox
)
# 🟢 CORRECCIÓN: Ahora importamos 'Signal'
from PySide6.QtCore import Qt, QTimer, Signal 
# Importar componentes de Dibujo para la Regla
from PySide6.QtGui import QPixmap, QImage, QPainter, QPen, QColor 

# 2. Procesamiento de Video
import cv2 


# --- CLASE: TimelineRuler (Regla de Tiempo) ---
class TimelineRuler(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(50) 
        self.total_duration_msec = 0

    def _format_time(self, msec):
        """Convierte milisegundos a formato MM:SS (sin ms para mantener el espacio de la regla)."""
        seconds = int(msec / 1000)
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02d}:{seconds:02d}"

    def set_duration(self, msec):
        self.total_duration_msec = msec
        self.update() 

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        if self.total_duration_msec == 0:
            return

        pen = QPen(QColor(150, 150, 150))
        pen.setWidth(1)
        painter.setPen(pen)
        painter.setBrush(QColor(0, 0, 0))
        
        width = self.width()
        
        margin = 10 
        draw_width = width - (margin * 2) 
        
        for i in range(0, 11): 
            
            percentage = i / 10.0 
            x_pos = int(draw_width * percentage) + margin

            if i == 10:
                x_pos = width - margin

            painter.drawLine(x_pos, 0, x_pos, 10) 
            
            time_msec = int(self.total_duration_msec * percentage)
            time_str = self._format_time(time_msec)
            
            text_rect = painter.fontMetrics().boundingRect(time_str)
            text_x = x_pos - text_rect.width() // 2
            text_y = 10 + 5 + text_rect.height()

            if i == 0: 
                text_x = margin
            elif i == 10:
                text_x = width - margin - text_rect.width()
            
            painter.drawText(text_x, text_y, time_str)
            
        painter.end()


# --- CLASE PRINCIPAL: VideoPlayerApp ---
class VideoPlayerApp(QMainWindow):
    # 1. Definir la señal personalizada para la búsqueda de tiempo
    seek_video_signal = Signal(int) 

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Reproductor de Video con Bookmarks y Dibujo")
        self.setGeometry(100, 100, 1200, 800) 

        self.video_cap = None
        self.frame_timer = QTimer(self)
        self.is_playing = False
        
        self.video_width = 0
        self.video_height = 0
        self.total_duration_msec = 0 
        
        # --- Lógica de Throttling ---
        self.seek_timer = QTimer(self)
        self.seek_timer.setSingleShot(True)
        self.seek_timer.timeout.connect(self._perform_seek)
        self.pending_seek_position = 0 
        
        self.setup_ui()
        
        # 2. Conectar la señal al manejador
        self.seek_video_signal.connect(self._handle_seek_request)


    # --- UI SETUP ---
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_grid = QGridLayout(central_widget)

        self.video_label = QLabel("Cargar Video Aquí")
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setStyleSheet("background-color: black; color: white; border: 1px solid gray;")
        self.video_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        main_grid.addWidget(self.video_label, 0, 0, 1, 3) 

        timeline_widget = QWidget()
        timeline_layout = QGridLayout(timeline_widget)
        
        timeline_layout.setContentsMargins(0, 0, 0, 0)
        timeline_layout.setHorizontalSpacing(0)
        timeline_layout.setVerticalSpacing(0)
        
        self.timeline_slider = QSlider(Qt.Horizontal)
        self.timeline_slider.setRange(0, 0)
        self.timeline_slider.sliderMoved.connect(self.slider_moved)
        self.timeline_slider.sliderReleased.connect(self.slider_released)
        self.timeline_slider.setEnabled(False)
        
        self.time_label = QLabel("00:00.000 / 00:00.000") 
        self.time_label.setFixedWidth(130) 
        self.time_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter) 
        
        self.ruler_widget = TimelineRuler()
        self.ruler_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        timeline_layout.addWidget(self.timeline_slider, 0, 0) 
        timeline_layout.addWidget(self.time_label, 0, 1)      

        timeline_layout.addWidget(self.ruler_widget, 1, 0) 
        
        empty_spacer = QWidget()
        empty_spacer.setFixedWidth(self.time_label.width())
        empty_spacer.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        timeline_layout.addWidget(empty_spacer, 1, 1)

        timeline_layout.setColumnStretch(0, 1)
        timeline_layout.setColumnStretch(1, 0) 


        main_grid.addWidget(timeline_widget, 1, 0, 1, 3) 

        self.btn_load = QPushButton("📂 Cargar Video")
        self.btn_load.clicked.connect(self.load_video_file)
        
        self.btn_play = QPushButton("▶️ Reproducir")
        self.btn_play.clicked.connect(self.toggle_play_pause)
        self.btn_play.setEnabled(False) 
        
        self.btn_screenshot = QPushButton("📸 Screenshot")
        self.btn_screenshot.clicked.connect(self.take_screenshot)
        self.btn_screenshot.setEnabled(False) 
        
        main_grid.addWidget(self.btn_load, 2, 0)
        main_grid.addWidget(self.btn_play, 2, 1)
        main_grid.addWidget(self.btn_screenshot, 2, 2)
        
        bookmarks_container = QWidget()
        bookmarks_layout = QVBoxLayout(bookmarks_container)
        
        quality_label = QLabel("Calidad de Repro.:")
        self.quality_combo = QComboBox()
        self.quality_combo.addItem("Alta (Nativa)", 1.0) 
        self.quality_combo.addItem("Media (50%)", 0.5)  
        self.quality_combo.addItem("Baja (25%)", 0.25)  
        self.quality_combo.currentIndexChanged.connect(self.quality_changed)
        
        quality_box = QWidget()
        q_layout = QVBoxLayout(quality_box)
        q_layout.setContentsMargins(0, 0, 0, 0)
        q_layout.addWidget(quality_label)
        q_layout.addWidget(self.quality_combo)

        bookmarks_layout.addWidget(QLabel("### Bookmarks de Tiempo"))
        bookmarks_layout.addWidget(quality_box)
        bookmarks_layout.addStretch(1) 
        
        main_grid.addWidget(bookmarks_container, 0, 3, 3, 1) 

        self.frame_timer.timeout.connect(self.update_frame)

    # 3. Manejador de Solicitud de Búsqueda
    def _handle_seek_request(self, position_msec):
      """Maneja la solicitud de búsqueda de tiempo de forma asíncrona (el listener)."""
      if not self.video_cap or not self.video_cap.isOpened():
          return
          
      was_playing = self.is_playing
      if was_playing:
          self.frame_timer.stop() 

      # 1. Realizar la búsqueda de OpenCV
      self.video_cap.set(cv2.CAP_PROP_POS_MSEC, position_msec)
      
      # 2. Forzar la actualización del frame
      self.update_frame(only_read_once=True, low_res=False) 
      
      # 🟢 PASO 2.5: Forzar el valor del deslizador a la posición deseada
      # Esto sobrescribe cualquier valor de 0 que el update_frame pudiera haber leído incorrectamente.
      self.timeline_slider.setValue(int(position_msec)) 
      
      # También actualizamos la etiqueta de tiempo solo para asegurar (aunque update_frame ya lo hizo)
      self.time_label.setText(self._format_time(position_msec) + " / " + self._format_time(self.total_duration_msec))

      # 3. Reiniciar la reproducción
      if was_playing:
          self.toggle_play_pause()


    # --- HELPERS Y EVENTOS ---
    def _format_time(self, msec):
        """Convierte milisegundos a formato MM:SS.mmm."""
        total_seconds = msec / 1000.0
        seconds = int(total_seconds)
        minutes = seconds // 60
        seconds_only = seconds % 60
        milliseconds = int(msec % 1000) 
        return f"{minutes:02d}:{seconds_only:02d}.{milliseconds:03d}"

    def quality_changed(self):
        self.update_frame(only_read_once=True)

    def _perform_seek(self):
        """Ejecuta la búsqueda de frame real después del retraso del throttling."""
        position = self.pending_seek_position
        
        if self.video_cap and self.video_cap.isOpened():
            
            was_playing = self.is_playing
            if was_playing:
                self.frame_timer.stop() 

            self.video_cap.set(cv2.CAP_PROP_POS_MSEC, position)
            
            self.update_frame(only_read_once=True, low_res=True) 
            
            if was_playing:
                self.frame_timer.start()

    def slider_moved(self, position):
        """
        [onDrag] Limita la frecuencia de búsqueda de frame (Debounce/Throttling) 
        y actualiza la etiqueta de tiempo inmediatamente.
        """
        self.time_label.setText(self._format_time(position) + " / " + self._format_time(self.total_duration_msec))
        self.pending_seek_position = position 
        
        if self.seek_timer.isActive():
            self.seek_timer.stop()
            
        self.seek_timer.start(50) 

    def slider_released(self):
        """
        [onRelease] Emite la señal de búsqueda final para fijar la posición y reanudar.
        """
        # Detenemos el timer de debounce si está activo
        if self.seek_timer.isActive():
            self.seek_timer.stop()
        
        position_msec = self.timeline_slider.value()
        
        # 4. EMITIMOS LA SEÑAL: Se realiza la búsqueda en _handle_seek_request de forma asíncrona
        self.seek_video_signal.emit(position_msec)
        
        # Aseguramos que la etiqueta de tiempo muestre el valor final inmediatamente
        self.time_label.setText(self._format_time(position_msec) + " / " + self._format_time(self.total_duration_msec))


    # --- MÉTODOS DE VIDEO ---
    def load_video_file(self):
        video_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Seleccionar Archivo de Video", 
            "", 
            "Archivos de Video (*.mp4 *.avi *.mkv);;Todos los Archivos (*)"
        )
        
        if not video_path:
            return 
        
        if self.video_cap and self.video_cap.isOpened():
            self.video_cap.release()
            self.frame_timer.stop()

        self.video_cap = cv2.VideoCapture(video_path)
        
        if self.video_cap.isOpened():
            self.video_width = int(self.video_cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            self.video_height = int(self.video_cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            fps = self.video_cap.get(cv2.CAP_PROP_FPS)
            frame_count = self.video_cap.get(cv2.CAP_PROP_FRAME_COUNT)
            self.total_duration_msec = (frame_count * 1000) / fps if fps > 0 else 0

            self.btn_play.setEnabled(True)
            self.btn_screenshot.setEnabled(True)
            self.is_playing = False
            self.btn_play.setText("▶️ Reproducir")
            
            self.timeline_slider.setRange(0, int(self.total_duration_msec))
            self.timeline_slider.setEnabled(True)
            
            self.ruler_widget.set_duration(self.total_duration_msec) 
            
            self.time_label.setText(self._format_time(0) + " / " + self._format_time(self.total_duration_msec))

            if fps > 0:
                self.frame_timer.setInterval(int(1000 / fps)) 
            
            print(f"Video cargado con éxito. FPS: {fps}")
            self.update_frame(only_read_once=True)
        else:
            print(f"Error al cargar el video: {video_path}")
            self.video_cap = None
            self.btn_play.setEnabled(False)
            self.btn_screenshot.setEnabled(False)
            
    def toggle_play_pause(self):
        if self.is_playing:
            self.frame_timer.stop()
            self.is_playing = False
            self.btn_play.setText("▶️ Reproducir")
        else:
            if self.video_cap and self.video_cap.isOpened():
                self.frame_timer.start()
                self.is_playing = True
                self.btn_play.setText("⏸ Pausar")

    def update_frame(self, only_read_once=False, low_res=False):
        if not self.video_cap or not self.video_cap.isOpened():
            return

        ret = True
        
        # Lógica para forzar la lectura del frame actual cuando se pausa o se hace un seek
        if only_read_once or not self.is_playing:
            current_pos = self.video_cap.get(cv2.CAP_PROP_POS_FRAMES)
            self.video_cap.set(cv2.CAP_PROP_POS_FRAMES, max(0, current_pos - 1))
            ret, frame = self.video_cap.read()
            if ret and current_pos > 0:
                self.video_cap.set(cv2.CAP_PROP_POS_FRAMES, current_pos) 
        else:
             ret, frame = self.video_cap.read()


        if ret:
            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            
            qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qt_image)
            
            if self.video_width > 0:
                aspect_ratio = self.video_height / self.video_width
                
                if low_res:
                    target_width_RENDER = 300 
                    scaling_mode = Qt.FastTransformation
                
                else: 
                    scale_factor = self.quality_combo.currentData()
                    target_width_RENDER = int(self.video_width * scale_factor) 
                    scaling_mode = Qt.SmoothTransformation
            
            else:
                scaling_mode = Qt.SmoothTransformation
                target_width_RENDER = self.video_width

            target_height_RENDER = int(target_width_RENDER * aspect_ratio)

            # --- PASO 1: Reducción de Calidad (Renderizado Interno) ---
            rendered_pixmap = pixmap.scaled(
                target_width_RENDER, 
                target_height_RENDER, 
                Qt.IgnoreAspectRatio, 
                scaling_mode
            )

            # --- PASO 2: Visualización (Estiramiento al 100% del contenedor) ---
            final_target_width = self.video_label.width()
            final_target_height = int(final_target_width * aspect_ratio)

            self.video_label.setPixmap(rendered_pixmap.scaled(
                final_target_width,
                final_target_height,
                Qt.KeepAspectRatio, 
                scaling_mode
            ))
            
            # --- ACTUALIZACIÓN DE TIMELINE ---
            current_msec = self.video_cap.get(cv2.CAP_PROP_POS_MSEC)
            
            # Actualización del Slider: Solo si NO está siendo arrastrado (comportamiento normal)
            if not self.timeline_slider.isSliderDown():
                self.timeline_slider.setValue(int(current_msec))
            
            self.time_label.setText(self._format_time(current_msec) + " / " + self._format_time(self.total_duration_msec))
        else:
            if self.is_playing:
                self.toggle_play_pause()

    # --- EVENTOS DE VENTANA ---
    def take_screenshot(self):
        current_pixmap = self.video_label.pixmap()
        
        if current_pixmap is None:
            print("No hay video cargado para tomar screenshot.")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "Guardar Screenshot", 
            "screenshot.png", 
            "PNG (*.png);;JPEG (*.jpg)"
        )

        if file_path:
            current_pixmap.save(file_path)
            print(f"Screenshot guardado en: {file_path}")

    def wheelEvent(self, event):
        if not self.video_cap or not self.video_cap.isOpened():
            super().wheelEvent(event)
            return

        JUMP_MSEC = 5000 
        delta = event.angleDelta().y()
        current_msec = self.video_cap.get(cv2.CAP_PROP_POS_MSEC)
        
        if delta > 0:
            new_msec = current_msec + JUMP_MSEC
        elif delta < 0:
            new_msec = max(0, current_msec - JUMP_MSEC)
        else:
            super().wheelEvent(event)
            return

        print(f"Saltando a: {new_msec / 1000:.1f}s")
        
        self.video_cap.set(cv2.CAP_PROP_POS_MSEC, new_msec)
        self.update_frame(only_read_once=True)

    def resizeEvent(self, event):
        self.update_frame(only_read_once=True)
        self.ruler_widget.update() 
        super().resizeEvent(event)

    def closeEvent(self, event):
        if self.video_cap:
            self.video_cap.release()
        event.accept()

# --- Bloque principal para ejecutar la aplicación ---
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VideoPlayerApp()
    window.show()
    sys.exit(app.exec())