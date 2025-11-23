# src/app/ui/styles/theme.py

class DarkTheme:
    
    # Colores
    BACKGROUND_DARK = "#1E1E1E"
    BACKGROUND_MEDIUM = "#2D2D2D"
    BORDER_COLOR = "#444444"
    ACCENT_COLOR = "#336699" # Azul de acento
    ACCENT_HOVER = "#4477AA"
    TEXT_LIGHT = "#CCCCCC"
    ERROR_RED = "#AA0000"

    GLOBAL_STYLES = f"""
        QMainWindow {{ background-color: {BACKGROUND_DARK}; color: {TEXT_LIGHT}; }}
        QPushButton {{ 
            background-color: {ACCENT_COLOR}; 
            color: white; 
            border: 1px solid {BORDER_COLOR}; 
            padding: 5px 10px; 
            border-radius: 4px; 
        }}
        QPushButton:hover {{ background-color: {ACCENT_HOVER}; }}
        QPushButton:checked {{ background-color: {ERROR_RED}; }}
        QSlider::groove:horizontal {{ border: 1px solid {BORDER_COLOR}; background: {BACKGROUND_MEDIUM}; height: 8px; border-radius: 4px; }}
        QSlider::handle:horizontal {{ background: {ACCENT_COLOR}; border: 1px solid {BORDER_COLOR}; width: 15px; margin: -4px 0; border-radius: 4px; }}
        QLabel {{ color: {TEXT_LIGHT}; }}
        QComboBox {{ background-color: {BACKGROUND_MEDIUM}; border: 1px solid {BORDER_COLOR}; color: {TEXT_LIGHT}; padding: 3px; }}
    """
    
    SIDEBAR_CONTAINER = f"background-color: {BACKGROUND_MEDIUM}; border-left: 1px solid {BORDER_COLOR};"
    TOOLBAR_STYLES = f"background-color: {BACKGROUND_MEDIUM}; border-bottom: 1px solid {BORDER_COLOR};"
    SIDEBAR_ACTION_BUTTON = f"background-color: {ACCENT_COLOR}; color: white;"
    SIDEBAR_ACTION_BUTTON_SMALL = f"background-color: {ACCENT_COLOR}; color: white; padding: 3px 5px;"
    CLOSE_BUTTON = f"background-color: {ERROR_RED}; color: white; border-radius: 10px;"