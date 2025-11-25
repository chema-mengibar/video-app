# src/app/ui/styles/theme.py

class DarkTheme:
    
    # Colores
    BACKGROUND_DARK = "#1E1E1E"
    BACKGROUND_MEDIUM = "#2D2D2D"
    BACKGROUND_LIGHT = "#2D2D2D"

    # Colores Primarios
    ACCENT_HOVER = "#e8cc51" 
    ACCENT_COLOR = "#bda437"
    BASE = "#000000"
    BASE_LIGHT = "#ffffff"

    TEXT_LIGHT = "#CCCCCC"

    WOW_COLOR = "#eb3474"

    BORDER_COLOR = "#99999988"
    DIVISION = '1px solid #99999988'
    
    # Colores Secundarios
    SECONDARY_COLOR = '#222222'
    SECONDARY_HOVER = '#000000'

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
        QPushButton:checked {{ background-color: {BASE_LIGHT}; }}

        QPushButton[is-active="true"] {{
            background-color:{BASE_LIGHT}
       
        }}

        QPushButton[button_type="secondary"] {{
            background-color: {SECONDARY_COLOR}; 
            color: {TEXT_LIGHT};
            padding: 6px 10px; 
            border-radius: 1px; 
            border: {DIVISION};
        }}
        QPushButton[button_type="secondary"]:hover {{
            background-color: {SECONDARY_HOVER};
            color: {TEXT_LIGHT}; 
            padding: 6px 10px;
            border-radius: 1px;
            border: none;
        }}

        QListWidget::item[is-now="true"] {{
            background-color: {WOW_COLOR}; 
            color: {TEXT_LIGHT};         
        }}

        QSlider::groove:horizontal {{ border: 1px solid {BORDER_COLOR}; background: {BACKGROUND_MEDIUM}; height: 8px; border-radius: 4px; }}
        QSlider::handle:horizontal {{ background: {ACCENT_COLOR}; border: 1px solid {BORDER_COLOR}; width: 15px; margin: -4px 0; border-radius: 4px; }}
        QLabel {{ color: {TEXT_LIGHT}; }}
        QComboBox {{ background-color: {BACKGROUND_MEDIUM}; border: 1px solid {BORDER_COLOR}; color: {TEXT_LIGHT}; padding: 3px; }}
        QListWidget {{ background-color: {BACKGROUND_DARK}; color: {TEXT_LIGHT}; border: 1px solid #555555; }}
    """
    
    SIDEBAR_HEADER = f"padding: 5px; font-weight: bold"
    SIDEBAR_CONTAINER = f"background-color: {BACKGROUND_DARK}; border-left: {DIVISION};"

    TIMELINE_RULER = f"""
            TimelineRuler {{
                background-color: {BACKGROUND_DARK}
               
            }}
    """

    TOOLBAR_STYLES = f"""
        #topbar_widget {{ 
            background-color: {BACKGROUND_DARK}; 
            border-bottom: {DIVISION};
            padding: 5px;
            height: 24px; 
        }}
    """
