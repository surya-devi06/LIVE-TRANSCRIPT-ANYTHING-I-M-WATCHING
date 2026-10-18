"""Application UI styles and Qt Style Sheets (QSS)."""

from live_transcript.constants import ThemeMode

DARK_THEME_QSS = """
/* Global Window & Fonts */
QWidget {
    background-color: #121316;
    color: #E2E8F0;
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, 'Roboto', sans-serif;
    font-size: 13px;
    selection-background-color: #2563EB;
    selection-color: #FFFFFF;
}

/* Header Bar */
#HeaderBar {
    background-color: #1A1C23;
    border-bottom: 1px solid #2D3139;
    min-height: 54px;
    max-height: 54px;
    padding: 0 16px;
}

#HeaderTitle {
    font-size: 16px;
    font-weight: 700;
    color: #F8FAFC;
    letter-spacing: 0.5px;
}

#HeaderSubtitle {
    font-size: 12px;
    color: #94A3B8;
}

/* Sidebar Navigation */
#SidebarWidget {
    background-color: #16181F;
    border-right: 1px solid #252830;
    min-width: 210px;
    max-width: 210px;
}

QPushButton.nav-btn {
    text-align: left;
    padding: 10px 16px;
    margin: 2px 10px;
    border-radius: 6px;
    border: none;
    font-size: 13px;
    font-weight: 500;
    color: #94A3B8;
    background-color: transparent;
}

QPushButton.nav-btn:hover {
    background-color: #21252E;
    color: #F1F5F9;
}

QPushButton.nav-btn:checked {
    background-color: #1E293B;
    color: #38BDF8;
    font-weight: 600;
    border-left: 3px solid #38BDF8;
}

/* Central Content Stack */
#CentralStack {
    background-color: #121316;
    padding: 16px;
}

/* Cards & Panels */
QFrame.card {
    background-color: #1A1C23;
    border: 1px solid #282C35;
    border-radius: 8px;
    padding: 16px;
}

QFrame.card:hover {
    border-color: #363B47;
}

/* Headings */
QLabel.view-title {
    font-size: 20px;
    font-weight: 700;
    color: #F8FAFC;
    margin-bottom: 4px;
}

QLabel.view-desc {
    font-size: 13px;
    color: #94A3B8;
    margin-bottom: 16px;
}

QLabel.section-header {
    font-size: 14px;
    font-weight: 600;
    color: #CBD5E1;
    margin-top: 8px;
    margin-bottom: 4px;
}

/* Buttons */
QPushButton {
    padding: 8px 16px;
    border-radius: 6px;
    font-weight: 500;
    font-size: 13px;
    border: 1px solid #334155;
    background-color: #1E293B;
    color: #F1F5F9;
}

QPushButton:hover {
    background-color: #334155;
    border-color: #475569;
}

QPushButton:pressed {
    background-color: #0F172A;
}

QPushButton:disabled {
    background-color: #1E222A;
    color: #475569;
    border-color: #282C35;
}

QPushButton.primary-btn {
    background-color: #2563EB;
    border: 1px solid #3B82F6;
    color: #FFFFFF;
    font-weight: 600;
}

QPushButton.primary-btn:hover {
    background-color: #1D4ED8;
    border-color: #60A5FA;
}

QPushButton.primary-btn:pressed {
    background-color: #1E40AF;
}

QPushButton.danger-btn {
    background-color: #DC2626;
    border: 1px solid #EF4444;
    color: #FFFFFF;
}

QPushButton.danger-btn:hover {
    background-color: #B91C1C;
}

QPushButton.success-btn {
    background-color: #16A34A;
    border: 1px solid #22C55E;
    color: #FFFFFF;
}

/* Inputs & Form Controls */
QLineEdit, QComboBox, QSpinBox {
    background-color: #1A1C23;
    border: 1px solid #334155;
    border-radius: 6px;
    padding: 7px 10px;
    color: #F8FAFC;
    selection-background-color: #2563EB;
}

QLineEdit:focus, QComboBox:focus, QSpinBox:focus {
    border: 1px solid #38BDF8;
}

QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 24px;
    border-left: 1px solid #334155;
}

QComboBox QAbstractItemView {
    background-color: #1A1C23;
    border: 1px solid #334155;
    selection-background-color: #2563EB;
    color: #F8FAFC;
    padding: 4px;
}

/* Tables */
QTableWidget {
    background-color: #16181F;
    border: 1px solid #282C35;
    border-radius: 6px;
    gridline-color: #242832;
    selection-background-color: #1E293B;
    selection-color: #38BDF8;
}

QTableWidget::item {
    padding: 8px 10px;
}

QHeaderView::section {
    background-color: #1E2129;
    color: #94A3B8;
    font-weight: 600;
    padding: 6px 10px;
    border: none;
    border-bottom: 1px solid #282C35;
}

/* Scroll Areas & Bars */
QScrollArea {
    border: none;
    background: transparent;
}

QScrollBar:vertical {
    background: #121316;
    width: 10px;
    margin: 0;
}

QScrollBar::handle:vertical {
    background: #2D3139;
    min-height: 20px;
    border-radius: 5px;
}

QScrollBar::handle:vertical:hover {
    background: #475569;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

/* Tab Widget */
QTabWidget::pane {
    border: 1px solid #282C35;
    border-radius: 6px;
    background-color: #16181F;
    padding: 16px;
}

QTabBar::tab {
    background-color: #121316;
    color: #94A3B8;
    padding: 8px 16px;
    margin-right: 4px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    border: 1px solid #282C35;
    border-bottom: none;
}

QTabBar::tab:selected {
    background-color: #16181F;
    color: #38BDF8;
    font-weight: 600;
}

/* Status Badges */
QLabel.status-badge {
    padding: 4px 10px;
    border-radius: 12px;
    font-weight: 600;
    font-size: 11px;
    text-transform: uppercase;
}
"""

LIGHT_THEME_QSS = """
/* Global Window & Fonts */
QWidget {
    background-color: #F8FAFC;
    color: #1E293B;
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, 'Roboto', sans-serif;
    font-size: 13px;
    selection-background-color: #2563EB;
    selection-color: #FFFFFF;
}

/* Header Bar */
#HeaderBar {
    background-color: #FFFFFF;
    border-bottom: 1px solid #E2E8F0;
    min-height: 54px;
    max-height: 54px;
    padding: 0 16px;
}

#HeaderTitle {
    font-size: 16px;
    font-weight: 700;
    color: #0F172A;
    letter-spacing: 0.5px;
}

#HeaderSubtitle {
    font-size: 12px;
    color: #64748B;
}

/* Sidebar Navigation */
#SidebarWidget {
    background-color: #F1F5F9;
    border-right: 1px solid #E2E8F0;
    min-width: 210px;
    max-width: 210px;
}

QPushButton.nav-btn {
    text-align: left;
    padding: 10px 16px;
    margin: 2px 10px;
    border-radius: 6px;
    border: none;
    font-size: 13px;
    font-weight: 500;
    color: #475569;
    background-color: transparent;
}

QPushButton.nav-btn:hover {
    background-color: #E2E8F0;
    color: #0F172A;
}

QPushButton.nav-btn:checked {
    background-color: #E0E7FF;
    color: #2563EB;
    font-weight: 600;
    border-left: 3px solid #2563EB;
}

/* Central Content Stack */
#CentralStack {
    background-color: #F8FAFC;
    padding: 16px;
}

/* Cards & Panels */
QFrame.card {
    background-color: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 8px;
    padding: 16px;
}

QFrame.card:hover {
    border-color: #CBD5E1;
}

/* Headings */
QLabel.view-title {
    font-size: 20px;
    font-weight: 700;
    color: #0F172A;
    margin-bottom: 4px;
}

QLabel.view-desc {
    font-size: 13px;
    color: #64748B;
    margin-bottom: 16px;
}

QLabel.section-header {
    font-size: 14px;
    font-weight: 600;
    color: #334155;
    margin-top: 8px;
    margin-bottom: 4px;
}

/* Buttons */
QPushButton {
    padding: 8px 16px;
    border-radius: 6px;
    font-weight: 500;
    font-size: 13px;
    border: 1px solid #CBD5E1;
    background-color: #FFFFFF;
    color: #1E293B;
}

QPushButton:hover {
    background-color: #F1F5F9;
    border-color: #94A3B8;
}

QPushButton:pressed {
    background-color: #E2E8F0;
}

QPushButton.primary-btn {
    background-color: #2563EB;
    border: 1px solid #1D4ED8;
    color: #FFFFFF;
    font-weight: 600;
}

QPushButton.primary-btn:hover {
    background-color: #1D4ED8;
}

QPushButton.danger-btn {
    background-color: #DC2626;
    border: 1px solid #B91C1C;
    color: #FFFFFF;
}

/* Inputs & Form Controls */
QLineEdit, QComboBox, QSpinBox {
    background-color: #FFFFFF;
    border: 1px solid #CBD5E1;
    border-radius: 6px;
    padding: 7px 10px;
    color: #0F172A;
    selection-background-color: #2563EB;
}

QLineEdit:focus, QComboBox:focus, QSpinBox:focus {
    border: 1px solid #2563EB;
}

QTableWidget {
    background-color: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 6px;
    gridline-color: #F1F5F9;
    selection-background-color: #EFF6FF;
    selection-color: #2563EB;
}

QHeaderView::section {
    background-color: #F8FAFC;
    color: #64748B;
    font-weight: 600;
    padding: 6px 10px;
    border: none;
    border-bottom: 1px solid #E2E8F0;
}
"""


def get_theme_stylesheet(theme: ThemeMode = ThemeMode.DARK) -> str:
    """Return the Qt Style Sheet string corresponding to the theme mode."""
    if theme == ThemeMode.LIGHT:
        return LIGHT_THEME_QSS
    return DARK_THEME_QSS
