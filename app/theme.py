# theme.py

class DarkTheme:
    """
    Define un conjunto de constantes de estilo CSS para el tema oscuro de la aplicación PySide6.
    """
    
    # --- Colores Base ---
    PRIMARY_COLOR = "#0078D4"    # Azul de acento (Microsoft Blue)
    BACKGROUND_COLOR = "#1E1E1E" # Fondo principal
    SECONDARY_BACKGROUND = "#2D2D30" # Contenedores y áreas secundarias
    TEXT_COLOR = "white"
    HIGHLIGHT_COLOR = "#FFD700"  # Dorado/Amarillo para resaltar tiempo/videomarks
    
    # --- Estilos Globales ---
    GLOBAL_STYLES = f"""
        QMainWindow, QWidget {{
            background-color: {BACKGROUND_COLOR};
            color: {TEXT_COLOR};
            font-size: 10pt;
        }}
        QPushButton {{
            background-color: {SECONDARY_BACKGROUND};
            border: 1px solid #444444;
            color: {TEXT_COLOR};
            padding: 5px 10px;
            border-radius: 4px;
        }}
        QPushButton:hover {{
            background-color: #3C3C3C;
        }}
        QPushButton:pressed {{
            background-color: #005A9E; /* Tono más oscuro de azul */
        }}
        QToolBar {{
            background-color: {SECONDARY_BACKGROUND};
            border: none;
            padding: 5px;
        }}
        QSlider::groove:horizontal {{
            border: 1px solid #3C3C3C;
            height: 4px;
            background: #2D2D30;
            margin: 2px 0;
            border-radius: 2px;
        }}
        QSlider::handle:horizontal {{
            background: {PRIMARY_COLOR};
            border: 1px solid {PRIMARY_COLOR};
            width: 10px;
            height: 10px;
            margin: -3px 0;
            border-radius: 5px;
        }}
        QComboBox {{
            background-color: {SECONDARY_BACKGROUND};
            color: {TEXT_COLOR};
            border: 1px solid #444444;
            padding: 2px;
            border-radius: 4px;
        }}
    """
    
    # 🟢 AGREGADO CRÍTICO: Estilo para QToolBar
    TOOLBAR_STYLES = f"""
        QToolBar {{
            background-color: {SECONDARY_BACKGROUND};
            border: 1px solid #444444;
            padding: 5px;
            spacing: 5px; /* Espaciado entre widgets en la barra */
        
        }}
    """
    
    # --- Sidebar ---
    SIDEBAR_CONTAINER = f"""
        QWidget {{
            background-color: {SECONDARY_BACKGROUND};
        }}
    """
    
    SIDEBAR_ACTION_BUTTON = f"""
        QPushButton {{
            background-color: {PRIMARY_COLOR};
            border: none;
            padding: 6px 10px;
            color: white;
        }}
        QPushButton:hover {{
            background-color: #0066AA;
        }}
    """
    
    SIDEBAR_ACTION_BUTTON_SMALL = f"""
        QPushButton {{
            background-color: #444444;
            border: none;
            padding: 2px 5px;
            font-size: 8pt;
        }}
        QPushButton:hover {{
            background-color: #555555;
        }}
    """
    
    CLOSE_BUTTON = f"""
        QPushButton {{
            background-color: #444444;
            color: white;
            border: none;
            padding: 0;
        }}
        QPushButton:hover {{
            background-color: #FF5555;
        }}
    """
    
    # --- Videomarks ---
    
    LIST_STYLES = f"""
        QListWidget {{
            background-color: {SECONDARY_BACKGROUND}; 
            border: 1px solid #444444;
            padding: 5px;
            outline: 0; 
        }}
        QListWidget::item:selected {{
            background-color: transparent;
        }}
    """

    LIST_ITEM_STYLES = f"""
        QWidget {{
            background-color: #3C3C3C; 
            border-radius: 4px;
            margin-bottom: 2px;
        }}
    """
    
    LIST_ITEM_HIGHLIGHT = f"""
        QWidget {{
            background-color: #4A4A4A;
            border: 2px solid {HIGHLIGHT_COLOR};
            border-radius: 4px;
            margin-bottom: 2px;
        }}
    """