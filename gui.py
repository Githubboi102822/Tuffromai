"""
Tuff Bot GUI
Clean tabbed interface for the Lock-On System
Optimized for Python 3.12+
"""

import sys
import threading
import config
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QTabWidget, QSlider, QLabel, QCheckBox, QPushButton, QSpinBox,
    QGroupBox, QComboBox, QStatusBar
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QObject
from PyQt5.QtGui import QFont, QColor, QIcon
import main as lock_on_main
import time


class StatusSignals(QObject):
    """Signals for updating GUI status"""
    fps_updated = pyqtSignal(float)
    persons_updated = pyqtSignal(int)
    locked_updated = pyqtSignal(bool)
    status_updated = pyqtSignal(str)


class TuffBotGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.is_running = False
        self.bot_thread = None
        self.signals = StatusSignals()
        
        # Connect signals
        self.signals.fps_updated.connect(self.update_fps)
        self.signals.persons_updated.connect(self.update_persons)
        self.signals.locked_updated.connect(self.update_locked)
        self.signals.status_updated.connect(self.update_status)
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize the UI"""
        self.setWindowTitle("🎯 Tuff Bot - Lock-On System")
        self.setGeometry(100, 100, 600, 700)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
                color: #ffffff;
            }
            QTabWidget::pane {
                border: 1px solid #444;
            }
            QTabBar::tab {
                background-color: #2d2d2d;
                color: #ffffff;
                padding: 8px 20px;
                border: 1px solid #444;
            }
            QTabBar::tab:selected {
                background-color: #0066cc;
            }
            QLabel {
                color: #ffffff;
            }
            QSlider {
                background-color: #2d2d2d;
            }
            QSlider::groove:horizontal {
                background: #444;
                height: 8px;
            }
            QSlider::handle:horizontal {
                background: #0066cc;
                width: 18px;
                margin: -5px 0;
                border-radius: 9px;
            }
            QPushButton {
                background-color: #0066cc;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #0080ff;
            }
            QPushButton:pressed {
                background-color: #0052a3;
            }
            QPushButton:disabled {
                background-color: #444;
            }
            QCheckBox {
                color: #ffffff;
            }
            QGroupBox {
                color: #ffffff;
                border: 1px solid #444;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px 0 3px;
            }
            QSpinBox, QComboBox {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #444;
                padding: 5px;
            }
        """)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Tab widget
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)
        
        # Create tabs
        self.create_lockout_tab()
        self.create_detection_tab()
        self.create_advanced_tab()
        self.create_stats_tab()
        
        # Run button
        run_button_layout = QHBoxLayout()
        self.run_button = QPushButton("🚀 Run Tuff Bot")
        self.run_button.setFixedHeight(50)
        self.run_button.setFont(QFont("Arial", 14, QFont.Bold))
        self.run_button.clicked.connect(self.toggle_bot)
        run_button_layout.addWidget(self.run_button)
        main_layout.addLayout(run_button_layout)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready to start")
        
    def create_lockout_tab(self):
        """Lock-On Settings Tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Mouse Smoothing
        smoothing_group = QGroupBox("Mouse Smoothing")
        smoothing_layout = QVBoxLayout()
        
        smoothing_layout.addWidget(QLabel("Smoothing Level:"))
        self.smoothing_slider = QSlider(Qt.Horizontal)
        self.smoothing_slider.setMinimum(0)
        self.smoothing_slider.setMaximum(100)
        self.smoothing_slider.setValue(int(config.MOUSE_SMOOTHING * 100))
        self.smoothing_slider.setTickPosition(QSlider.TicksBelow)
        self.smoothing_slider.setTickInterval(10)
        self.smoothing_label = QLabel(f"{config.MOUSE_SMOOTHING:.2f}")
        self.smoothing_slider.sliderMoved.connect(lambda: self.smoothing_label.setText(f"{self.smoothing_slider.value() / 100:.2f}"))
        smoothing_layout.addWidget(self.smoothing_slider)
        smoothing_layout.addWidget(self.smoothing_label)
        
        smoothing_group.setLayout(smoothing_layout)
        layout.addWidget(smoothing_group)
        
        # Enable/Disable
        enable_group = QGroupBox("Lock-On Controls")
        enable_layout = QVBoxLayout()
        
        self.enable_debug = QCheckBox("Show Debug Window")
        self.enable_debug.setChecked(config.SHOW_DEBUG_WINDOW)
        enable_layout.addWidget(self.enable_debug)
        
        enable_group.setLayout(enable_layout)
        layout.addWidget(enable_group)
        
        layout.addStretch()
        self.tabs.addTab(widget, "🎯 Lock-On")
        
    def create_detection_tab(self):
        """Detection Settings Tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Model Selection
        model_group = QGroupBox("YOLO Model")
        model_layout = QVBoxLayout()
        
        model_layout.addWidget(QLabel("Model Size:"))
        self.model_combo = QComboBox()
        self.model_combo.addItems(["yolov8n.pt (Fastest)", "yolov8s.pt (Balanced)", "yolov8m.pt (Accurate)"])
        self.model_combo.setCurrentIndex(0)
        model_layout.addWidget(self.model_combo)
        
        model_group.setLayout(model_layout)
        layout.addWidget(model_group)
        
        # Detection Confidence
        confidence_group = QGroupBox("Detection Confidence")
        confidence_layout = QVBoxLayout()
        
        confidence_layout.addWidget(QLabel("Confidence Threshold:"))
        self.confidence_slider = QSlider(Qt.Horizontal)
        self.confidence_slider.setMinimum(10)
        self.confidence_slider.setMaximum(100)
        self.confidence_slider.setValue(int(config.YOLO_CONFIDENCE * 100))
        self.confidence_slider.setTickPosition(QSlider.TicksBelow)
        self.confidence_slider.setTickInterval(10)
        self.confidence_label = QLabel(f"{config.YOLO_CONFIDENCE:.2f}")
        self.confidence_slider.sliderMoved.connect(lambda: self.confidence_label.setText(f"{self.confidence_slider.value() / 100:.2f}"))
        confidence_layout.addWidget(self.confidence_slider)
        confidence_layout.addWidget(self.confidence_label)
        
        confidence_group.setLayout(confidence_layout)
        layout.addWidget(confidence_group)
        
        # Person Size Filter
        size_group = QGroupBox("Person Size Filter")
        size_layout = QVBoxLayout()
        
        # Min width
        min_width_layout = QHBoxLayout()
        min_width_layout.addWidget(QLabel("Minimum Width:"))
        self.min_width_spin = QSpinBox()
        self.min_width_spin.setMinimum(5)
        self.min_width_spin.setMaximum(500)
        self.min_width_spin.setValue(config.MIN_PERSON_WIDTH)
        min_width_layout.addWidget(self.min_width_spin)
        min_width_layout.addStretch()
        size_layout.addLayout(min_width_layout)
        
        # Min height
        min_height_layout = QHBoxLayout()
        min_height_layout.addWidget(QLabel("Minimum Height:"))
        self.min_height_spin = QSpinBox()
        self.min_height_spin.setMinimum(10)
        self.min_height_spin.setMaximum(1000)
        self.min_height_spin.setValue(config.MIN_PERSON_HEIGHT)
        min_height_layout.addWidget(self.min_height_spin)
        min_height_layout.addStretch()
        size_layout.addLayout(min_height_layout)
        
        size_group.setLayout(size_layout)
        layout.addWidget(size_group)
        
        layout.addStretch()
        self.tabs.addTab(widget, "🔍 Detection")
        
    def create_advanced_tab(self):
        """Advanced Settings Tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Performance
        perf_group = QGroupBox("Performance")
        perf_layout = QVBoxLayout()
        
        # Debug window scale
        scale_layout = QHBoxLayout()
        scale_layout.addWidget(QLabel("Debug Window Scale:"))
        self.scale_spin = QSpinBox()
        self.scale_spin.setMinimum(10)
        self.scale_spin.setMaximum(100)
        self.scale_spin.setValue(int(config.DEBUG_WINDOW_SCALE * 100))
        self.scale_spin.setSuffix(" %")
        scale_layout.addWidget(self.scale_spin)
        scale_layout.addStretch()
        perf_layout.addLayout(scale_layout)
        
        # IOU Threshold
        iou_layout = QHBoxLayout()
        iou_layout.addWidget(QLabel("IOU Threshold:"))
        self.iou_spin = QSpinBox()
        self.iou_spin.setMinimum(1)
        self.iou_spin.setMaximum(100)
        self.iou_spin.setValue(int(config.YOLO_IOU * 100))
        self.iou_spin.setSuffix(" %")
        iou_layout.addWidget(self.iou_spin)
        iou_layout.addStretch()
        perf_layout.addLayout(iou_layout)
        
        perf_group.setLayout(perf_layout)
        layout.addWidget(perf_group)
        
        # Info
        info_group = QGroupBox("Information")
        info_layout = QVBoxLayout()
        
        info_text = QLabel(
            "🎮 Hold 'E' to activate lock-on\n"
            "🖥️ Press 'Q' to exit the bot\n"
            "⌚ Real-time FPS and stats shown in debug window\n"
            "🔒 Automatically tracks closest person"
        )
        info_text.setStyleSheet("color: #aaa; line-height: 1.8;")
        info_layout.addWidget(info_text)
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        layout.addStretch()
        self.tabs.addTab(widget, "⚙️ Advanced")
        
    def create_stats_tab(self):
        """Live Stats Tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Stats display
        stats_group = QGroupBox("Live Statistics")
        stats_layout = QVBoxLayout()
        
        # FPS
        fps_layout = QHBoxLayout()
        fps_layout.addWidget(QLabel("Current FPS:"))
        self.fps_display = QLabel("0.0")
        self.fps_display.setStyleSheet("color: #00ff00; font-weight: bold; font-size: 14px;")
        fps_layout.addWidget(self.fps_display)
        fps_layout.addStretch()
        stats_layout.addLayout(fps_layout)
        
        # Persons detected
        persons_layout = QHBoxLayout()
        persons_layout.addWidget(QLabel("Persons Detected:"))
        self.persons_display = QLabel("0")
        self.persons_display.setStyleSheet("color: #00ff00; font-weight: bold; font-size: 14px;")
        persons_layout.addWidget(self.persons_display)
        persons_layout.addStretch()
        stats_layout.addLayout(persons_layout)
        
        # Lock-on status
        locked_layout = QHBoxLayout()
        locked_layout.addWidget(QLabel("Lock-On Status:"))
        self.locked_display = QLabel("Inactive")
        self.locked_display.setStyleSheet("color: #ff6600; font-weight: bold; font-size: 14px;")
        locked_layout.addWidget(self.locked_display)
        locked_layout.addStretch()
        stats_layout.addLayout(locked_layout)
        
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)
        
        # Status messages
        status_group = QGroupBox("Status")
        status_layout = QVBoxLayout()
        
        self.status_display = QLabel("Bot is stopped. Click 'Run Tuff Bot' to start.")
        self.status_display.setStyleSheet("color: #aaa;")
        self.status_display.setWordWrap(True)
        status_layout.addWidget(self.status_display)
        
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)
        
        layout.addStretch()
        self.tabs.addTab(widget, "📊 Stats")
        
    def apply_settings(self):
        """Apply GUI settings to config"""
        config.MOUSE_SMOOTHING = self.smoothing_slider.value() / 100
        config.SHOW_DEBUG_WINDOW = self.enable_debug.isChecked()
        config.YOLO_CONFIDENCE = self.confidence_slider.value() / 100
        config.MIN_PERSON_WIDTH = self.min_width_spin.value()
        config.MIN_PERSON_HEIGHT = self.min_height_spin.value()
        config.DEBUG_WINDOW_SCALE = self.scale_spin.value() / 100
        config.YOLO_IOU = self.iou_spin.value() / 100
        
        # Model selection
        model_map = {
            0: "yolov8n.pt",
            1: "yolov8s.pt",
            2: "yolov8m.pt"
        }
        config.YOLO_MODEL = model_map[self.model_combo.currentIndex()]
        
    def toggle_bot(self):
        """Start/Stop the bot"""
        if not self.is_running:
            self.start_bot()
        else:
            self.stop_bot()
            
    def start_bot(self):
        """Start the bot"""
        self.apply_settings()
        self.is_running = True
        self.run_button.setText("⏹️ Stop Tuff Bot")
        self.run_button.setStyleSheet("""
            QPushButton {
                background-color: #ff4444;
            }
            QPushButton:hover {
                background-color: #ff6666;
            }
        """)
        
        # Disable settings while running
        self.tabs.setEnabled(False)
        
        self.status_display.setText("🚀 Bot is running... Press Q in the window to stop.")
        self.status_bar.showMessage("Bot running")
        
        # Start bot in thread
        self.bot_thread = threading.Thread(target=self.run_bot_thread, daemon=True)
        self.bot_thread.start()
        
    def run_bot_thread(self):
        """Run bot in background thread"""
        try:
            lock_on_main.main()
        except Exception as e:
            self.signals.status_updated.emit(f"Error: {str(e)}")
        finally:
            self.is_running = False
            self.run_button.setText("🚀 Run Tuff Bot")
            self.run_button.setStyleSheet("""
                QPushButton {
                    background-color: #0066cc;
                }
                QPushButton:hover {
                    background-color: #0080ff;
                }
            """)
            self.tabs.setEnabled(True)
            self.status_display.setText("Bot stopped.")
            self.status_bar.showMessage("Bot stopped")
            
    def stop_bot(self):
        """Stop the bot"""
        # This will be triggered when the user presses Q in the debug window
        pass
        
    def update_fps(self, fps):
        """Update FPS display"""
        self.fps_display.setText(f"{fps:.1f}")
        
    def update_persons(self, count):
        """Update persons count"""
        self.persons_display.setText(str(count))
        
    def update_locked(self, locked):
        """Update lock-on status"""
        if locked:
            self.locked_display.setText("🔒 LOCKED")
            self.locked_display.setStyleSheet("color: #00ff00; font-weight: bold; font-size: 14px;")
        else:
            self.locked_display.setText("Inactive")
            self.locked_display.setStyleSheet("color: #ff6600; font-weight: bold; font-size: 14px;")
            
    def update_status(self, message):
        """Update status message"""
        self.status_display.setText(message)


def run_gui():
    """Run the GUI"""
    # Check Python version
    if sys.version_info.major != 3 or sys.version_info.minor < 12:
        print(f"⚠️  WARNING: This bot is optimized for Python 3.12+")
        print(f"You are using Python {sys.version_info.major}.{sys.version_info.minor}")
        print("Some features may not work correctly.")
        print("Download Python 3.12: https://www.python.org/downloads/release/python-31212/")
    
    app = QApplication(sys.argv)
    gui = TuffBotGUI()
    gui.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    run_gui()
