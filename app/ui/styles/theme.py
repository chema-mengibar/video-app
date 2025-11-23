# src/app/ui/styles/theme.py

class DarkTheme:
    
    # Colores
    BACKGROUND_DARK = "#1E1E1E"
    BACKGROUND_MEDIUM = "#2D2D2D"

    
    ACCENT_HOVER = "#e8cc51" 
    ACCENT_COLOR = "#bda437"
    BASE = "#000000"

    TEXT_LIGHT = "#CCCCCC"
    ERROR_RED = "#AA0000"

    BORDER_COLOR = "#99999988"
    DIVISION = '1px solid #99999988'

    GLOBAL_STYLES = f"""
        QMainWindow {{ background-color: {BACKGROUND_DARK}; color: {TEXT_LIGHT}; }}
        QPushButton {{ 
            background-color: {ACCENT_COLOR}; 
            color: {BACKGROUND_MEDIUM}; 
            padding: 5px 10px; 
            border-radius: 1px; 
            border: none;
        }}
        QPushButton:hover {{ background-color: {ACCENT_HOVER}; }}
        QPushButton:checked {{ background-color: {BASE}; }}
        QSlider::groove:horizontal {{ border: 1px solid {BORDER_COLOR}; background: {BACKGROUND_MEDIUM}; height: 8px; border-radius: 4px; }}
        QSlider::handle:horizontal {{ background: {ACCENT_COLOR}; border: 1px solid {BORDER_COLOR}; width: 15px; margin: -4px 0; border-radius: 4px; }}
        QLabel {{ color: {TEXT_LIGHT}; }}
        QComboBox {{ background-color: {BACKGROUND_MEDIUM}; border: 1px solid {BORDER_COLOR}; color: {TEXT_LIGHT}; padding: 3px; }}
    """
    
    SIDEBAR_CONTAINER = f"background-color: {BACKGROUND_DARK}; border-left: {DIVISION};"

    TOOLBAR_STYLES = f"""
        #topbar_widget {{ 
            background-color: {BACKGROUND_DARK}; 
            border-bottom: {DIVISION};
            padding: 5px;
            height: 24px; 
        }}
    """
    SIDEBAR_ACTION_BUTTON = f"background-color: {ACCENT_COLOR}; color: white;"
    SIDEBAR_ACTION_BUTTON_SMALL = f"background-color: {ACCENT_COLOR}; color: white; padding: 3px 5px;"
    CLOSE_BUTTON = f"background-color: {ERROR_RED}; color: white; border-radius: 10px;"