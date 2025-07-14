import sys
import time
import threading
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                             QWidget, QPushButton, QLineEdit, QLabel, 
                             QSpinBox, QDoubleSpinBox, QComboBox, QGroupBox, QRadioButton, 
                             QButtonGroup, QCheckBox, QTableWidget, QTableWidgetItem,
                             QHeaderView, QSplitter)
from PyQt6.QtCore import QTimer, pyqtSignal, QObject, Qt
from PyQt6.QtGui import QFont, QPixmap, QIcon
import pynput
from pynput.keyboard import Key, Listener
import os


class KeyboardController(QObject):
    """Handles keyboard automation functionality"""
    
    combination_recorded = pyqtSignal(str)  # Signal to emit when combination is recorded
    
    def __init__(self):
        super().__init__()
        self.keyboard_controller = pynput.keyboard.Controller()
        self.is_running = False
        self.is_recording = False
        self.recorded_keys = list()
        self.listener = None
        self.stop_key = Key.esc  # Default stop key is ESC
        
    def set_stop_key(self, key_name):
        """Set the key that stops recording"""
        if hasattr(Key, key_name.lower()):
            self.stop_key = getattr(Key, key_name.lower())
        else:
            self.stop_key = key_name
            
    def start_recording(self):
        """Start recording key combination"""
        self.is_recording = True
        self.recorded_keys.clear()
        
        def on_press(key):
            if not self.is_recording:
                return False
            

            # Check if stop key is pressed
            if key == self.stop_key:
                self.stop_recording()
                return False
                
            # Add key to recorded set
            try:
                if hasattr(key, 'char') and key.char:
                    self.recorded_keys.append(key.char)
                else:
                    self.recorded_keys.append(key.name)
            except AttributeError:
                self.recorded_keys.append(str(key).replace('Key.', ''))
        
        def on_release(key):
            if not self.is_recording:
                return False
                
        self.listener = Listener(on_press=on_press, on_release=on_release)
        self.listener.start()
    
    def stop_recording(self):
        """Stop recording and emit the combination"""
        if not self.is_recording:
            return
            
        self.is_recording = False
        if self.listener:
            self.listener.stop()
            self.listener = None
            
        # Convert recorded keys to string
        if self.recorded_keys:
            combination = '+'.join(self.recorded_keys)
            self.combination_recorded.emit(combination)
        
    def send_key_combination(self, keys, timing_intervals=None, include_final_delay=True):
        """Send keys sequentially with timing delays from the table"""
        try:
            import time  # Make sure time is available
            key_objects = []
            for key_name in keys:
                if hasattr(Key, key_name.lower()):
                    key_objects.append(getattr(Key, key_name.lower()))
                else:
                    key_objects.append(key_name)
            
            # Always send keys sequentially with timing
            for i, key in enumerate(key_objects):
                self.keyboard_controller.press(key)
                self.keyboard_controller.release(key)
                
                # Apply delay after each key
                if timing_intervals and i < len(timing_intervals):
                    # For automation (include_final_delay=False), skip the last delay
                    # as it will be handled by the timer cycle
                    if not include_final_delay and i == len(timing_intervals) - 1:
                        continue
                    delay = timing_intervals[i] / 1000.0  # Convert ms to seconds
                    time.sleep(delay)
                elif include_final_delay:
                    # Default delay if no timing specified (only for test mode)
                    time.sleep(0.1)  # 100ms default
            
            return True
        except Exception as e:
            print(f"Error sending key combination: {e}")
            return False


class AutoKeyApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.keyboard_controller = KeyboardController()
        self.keyboard_controller.combination_recorded.connect(self.on_combination_recorded)
        self.is_running = False
        self.is_recording = False
        self.init_ui()
        self.setup_timers()
        
    def init_ui(self):
        self.setWindowTitle("ASSP - Auto Stereotaxic Surgery Program")
        self.setGeometry(100, 100, 1200, 700)
        
        # Set window icon if available
        self.setup_images()
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Add a subtle background gradient
        central_widget.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #f8f9fa, stop: 1 #e9ecef);
            }
            QGroupBox {
                background-color: white;
                border: 2px solid #dee2e6;
                border-radius: 8px;
                margin: 5px;
                padding-top: 10px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #495057;
            }
            QComboBox {
                background-color: white;
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 5px;
                color: black;
                selection-background-color: #3498db;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left-width: 1px;
                border-left-color: #ccc;
                border-left-style: solid;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #666;
                width: 0px;
                height: 0px;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                color: black;
                border: 1px solid #ccc;
                selection-background-color: #3498db;
            }
            QRadioButton {
                color: black;
                background-color: transparent;
                spacing: 5px;
            }
            QRadioButton::indicator {
                width: 13px;
                height: 13px;
                border-radius: 7px;
                border: 2px solid #666;
                background-color: white;
            }
            QRadioButton::indicator:checked {
                background-color: #3498db;
                border: 2px solid #2980b9;
            }
            QLabel {
                color: black;
                background-color: transparent;
            }
            QLineEdit {
                background-color: white;
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 5px;
                color: black;
            }
            QSpinBox {
                background-color: white;
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 2px;
                color: black;
            }
            QDoubleSpinBox {
                background-color: white;
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 2px;
                color: black;
            }
        """)
        
        # Create splitter for better layout
        splitter = QSplitter(Qt.Orientation.Horizontal)
        central_widget_layout = QHBoxLayout(central_widget)
        central_widget_layout.addWidget(splitter)
        
        # Left panel
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Title
        title = QLabel(f"Auto Stereotaxic Surgery Program")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("QLabel { color: #2E86AB; margin: 10px; }")
        left_layout.addWidget(title)
        
        # Key combination selection
        self.create_key_selection_group(left_layout)
        
        # DV Calculation section
        self.create_dv_calculation_group(left_layout)
        
        # Timing options
        self.create_timing_group(left_layout)
        
        # Control buttons
        self.create_control_buttons(left_layout)
        
        # Status display
        self.status_label = QLabel("Ready to start...")
        self.status_label.setStyleSheet("QLabel { color: #666; font-style: italic; }")
        left_layout.addWidget(self.status_label)
        
        # Add footer with logo and credits
        self.create_footer(left_layout)
        
        # Right panel - Timing Table
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        self.create_timing_table_group(right_layout)
        
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([400, 500])
        
    def setup_images(self):
        """Setup images and icons for the application"""
        try:
            # Set window icon from asset/img/logo.png
            logo_path = "asset/img/logo.png"
            if os.path.exists(logo_path):
                self.setWindowIcon(QIcon(logo_path))
                print(f"Window icon loaded from: {logo_path}")
            else:
                print(f"Logo file not found at: {logo_path}")
            
            # Store image paths for later use
            self.images = {
                'record_icon': '🔴',  # Using emoji as fallback
                'play_icon': '▶️',
                'stop_icon': '⏹️',
                'test_icon': '🧪',
                'keyboard_icon': '⌨️'
            }
            
        except Exception as e:
            print(f"Could not load images: {e}")
            # Fallback to text-only interface
            self.images = {
                'record_icon': 'Record',
                'play_icon': 'Start',
                'stop_icon': 'Stop', 
                'test_icon': 'Test',
                'keyboard_icon': 'AutoKey'
            }
    
    def create_key_selection_group(self, parent_layout):
        """Create key combination selection controls"""
        key_group = QGroupBox("Key Combination")
        layout = QVBoxLayout(key_group)
        
        # Predefined combinations
        predefined_layout = QHBoxLayout()
        
        # Common combinations dropdown
        combo_layout = QHBoxLayout()
        combo_layout.addWidget(QLabel("Preset combinations:"))
        self.preset_combo = QComboBox()
        self.preset_combo.addItems([
            "Custom",
            "Page Down",
            "Page Up", 
            "Arrow Down",
            "Arrow Up",
            "Arrow Left", 
            "Arrow Right",
            "Space",
            "Enter",
            "Tab",
            "Ctrl+C",
            "Ctrl+V",
            "Alt+Tab",
            "F5 (Refresh)"
        ])
        self.preset_combo.currentTextChanged.connect(self.on_preset_changed)
        combo_layout.addWidget(self.preset_combo)
        layout.addLayout(combo_layout)
        
        # Custom combination input
        custom_layout = QHBoxLayout()
        custom_layout.addWidget(QLabel("Custom combination:"))
        self.combo_input = QLineEdit()
        self.combo_input.setPlaceholderText("Enter keys separated by '+' (e.g., 'ctrl+shift+s')")
        self.combo_input.textChanged.connect(self.update_timing_table)  # Update table when text changes
        custom_layout.addWidget(self.combo_input)
        layout.addLayout(custom_layout)
        
        # Recording section
        record_layout = QVBoxLayout()
        
        # Stop key selection
        stop_key_layout = QHBoxLayout()
        stop_key_layout.addWidget(QLabel("Stop recording key:"))
        self.stop_key_combo = QComboBox()
        self.stop_key_combo.addItems(["ESC", "F1", "F2", "F3", "F4", "Space", "Enter"])
        self.stop_key_combo.currentTextChanged.connect(self.on_stop_key_changed)
        stop_key_layout.addWidget(self.stop_key_combo)
        stop_key_layout.addStretch()
        record_layout.addLayout(stop_key_layout)
        
        # Record button and status
        record_button_layout = QHBoxLayout()
        self.record_btn = QPushButton(f"{self.images.get('record_icon', '🔴')} Record Key Combination")
        self.record_btn.setStyleSheet("QPushButton { background-color: #ff4444; color: white; font-weight: bold; padding: 8px; border-radius: 5px; }")
        self.record_btn.clicked.connect(self.start_recording)
        record_button_layout.addWidget(self.record_btn)
        
        self.recording_status = QLabel("")
        self.recording_status.setStyleSheet("QLabel { color: #ff4444; font-weight: bold; }")
        record_button_layout.addWidget(self.recording_status)
        record_layout.addLayout(record_button_layout)
        
        layout.addLayout(record_layout)
        
        # Test button
        test_btn = QPushButton(f"{self.images.get('test_icon', '🧪')} Test Key Combination")
        test_btn.setStyleSheet("QPushButton { background-color: #6C5CE7; color: white; font-weight: bold; padding: 8px; border-radius: 5px; }")
        test_btn.clicked.connect(self.test_combination)
        layout.addWidget(test_btn)
        
        parent_layout.addWidget(key_group)
    
    def create_timing_group(self, parent_layout):
        """Create timing control group"""
        timing_group = QGroupBox("Timing Settings")
        layout = QVBoxLayout(timing_group)
        
        # Mode selection
        mode_layout = QVBoxLayout()
        self.mode_group = QButtonGroup()
        
        self.continuous_radio = QRadioButton("Continuous (until stopped)")
        self.continuous_radio.setChecked(True)
        self.mode_group.addButton(self.continuous_radio, 0)
        mode_layout.addWidget(self.continuous_radio)
        
        self.timed_radio = QRadioButton("For specific number of repeats")
        self.mode_group.addButton(self.timed_radio, 1)
        mode_layout.addWidget(self.timed_radio)
        
        layout.addLayout(mode_layout)
        
        # Repeat count setting (for repeat mode)
        repeat_layout = QHBoxLayout()
        repeat_layout.addWidget(QLabel("Number of repeats:"))
        self.repeat_count_spin = QSpinBox()
        self.repeat_count_spin.setRange(1, 10000)
        self.repeat_count_spin.setValue(10)
        self.repeat_count_spin.setSuffix(" times")
        self.repeat_count_spin.setEnabled(False)
        repeat_layout.addWidget(self.repeat_count_spin)
        repeat_layout.addStretch()
        layout.addLayout(repeat_layout)
        
        # Enable/disable repeat count based on mode
        self.timed_radio.toggled.connect(self.repeat_count_spin.setEnabled)
        
        parent_layout.addWidget(timing_group)
    
    def create_dv_calculation_group(self, parent_layout):
        """Create DV calculation controls"""
        dv_group = QGroupBox("DV Calculation")
        layout = QVBoxLayout(dv_group)
        
        # Current DV input
        current_dv_layout = QHBoxLayout()
        current_dv_layout.addWidget(QLabel("Current DV (mm):"))
        self.current_dv_spin = QDoubleSpinBox()
        self.current_dv_spin.setDecimals(3)  # Allow 3 decimal places
        self.current_dv_spin.setRange(-999.999, 999.999)
        self.current_dv_spin.setValue(0.000)
        self.current_dv_spin.setSingleStep(0.001)
        self.current_dv_spin.setSuffix(" mm")
        current_dv_layout.addWidget(self.current_dv_spin)
        current_dv_layout.addStretch()
        layout.addLayout(current_dv_layout)
        
        # Final DV input
        final_dv_layout = QHBoxLayout()
        final_dv_layout.addWidget(QLabel("Final DV (mm):"))
        self.final_dv_spin = QDoubleSpinBox()
        self.final_dv_spin.setDecimals(3)  # Allow 3 decimal places
        self.final_dv_spin.setRange(-999.999, 999.999)
        self.final_dv_spin.setValue(1.000)
        self.final_dv_spin.setSingleStep(0.001)
        self.final_dv_spin.setSuffix(" mm")
        final_dv_layout.addWidget(self.final_dv_spin)
        final_dv_layout.addStretch()
        layout.addLayout(final_dv_layout)
        
        # Step size input
        step_size_layout = QHBoxLayout()
        step_size_layout.addWidget(QLabel("Step size (presses per 0.001mm):"))
        self.step_size_spin = QSpinBox()
        self.step_size_spin.setRange(1, 1000)
        self.step_size_spin.setValue(1)  # Default value: 1 press per 0.001mm
        self.step_size_spin.setSuffix(" presses/0.001mm")
        step_size_layout.addWidget(self.step_size_spin)
        step_size_layout.addStretch()
        layout.addLayout(step_size_layout)
        
        # Calculate button and result
        calc_layout = QHBoxLayout()
        calc_btn = QPushButton("🧮 Calculate Repetitions")
        calc_btn.setStyleSheet("QPushButton { background-color: #2E86AB; color: white; font-weight: bold; padding: 8px; border-radius: 5px; }")
        calc_btn.clicked.connect(self.calculate_dv_repetitions)
        calc_layout.addWidget(calc_btn)
        
        # Result display
        self.dv_result_label = QLabel("Click Calculate to see result")
        self.dv_result_label.setStyleSheet("QLabel { color: #666; font-style: italic; margin: 5px; }")
        calc_layout.addWidget(self.dv_result_label)
        calc_layout.addStretch()
        layout.addLayout(calc_layout)
        
        parent_layout.addWidget(dv_group)
    
    def create_timing_table_group(self, parent_layout):
        """Create timing table for individual key intervals"""
        timing_table_group = QGroupBox("Key Sequence Timing")
        layout = QVBoxLayout(timing_table_group)
        
        # Instructions
        instructions = QLabel("Define timing intervals between each key in the sequence.\nThe sum of all intervals determines how often the combination repeats.")
        instructions.setWordWrap(True)
        instructions.setStyleSheet("QLabel { color: #666; font-style: italic; margin: 5px; }")
        layout.addWidget(instructions)
        
        # Auto-fill controls
        auto_fill_layout = QHBoxLayout()
        auto_fill_layout.addWidget(QLabel("Auto-fill all intervals:"))
        
        self.auto_fill_spin = QSpinBox()
        self.auto_fill_spin.setRange(1, 5000)
        self.auto_fill_spin.setValue(100)
        self.auto_fill_spin.setSuffix(" ms")
        auto_fill_layout.addWidget(self.auto_fill_spin)
        
        auto_fill_btn = QPushButton("⚡ Apply to All")
        auto_fill_btn.setStyleSheet("QPushButton { background-color: #FF9500; color: white; font-weight: bold; padding: 5px; border-radius: 3px; }")
        auto_fill_btn.clicked.connect(self.auto_fill_timing)
        auto_fill_layout.addWidget(auto_fill_btn)
        auto_fill_layout.addStretch()
        layout.addLayout(auto_fill_layout)
        
        # Timing table
        self.timing_table = QTableWidget()
        self.timing_table.setColumnCount(3)
        self.timing_table.setHorizontalHeaderLabels(["From Key", "To Key", "Delay (ms)"])
        
        # Make table columns resize properly
        header = self.timing_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        self.timing_table.setColumnWidth(2, 100)
        
        layout.addWidget(self.timing_table)
        
        parent_layout.addWidget(timing_table_group)
    
    def create_control_buttons(self, parent_layout):
        """Create control buttons"""
        button_layout = QHBoxLayout()
        
        self.start_btn = QPushButton(f"{self.images.get('play_icon', '▶️')} Start Pressing")
        self.start_btn.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; font-weight: bold; padding: 10px; border-radius: 5px; }")
        self.start_btn.clicked.connect(self.start_countdown)
        button_layout.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton(f"{self.images.get('stop_icon', '⏹️')} Stop")
        self.stop_btn.setStyleSheet("QPushButton { background-color: #f44336; color: white; font-weight: bold; padding: 10px; border-radius: 5px; }")
        self.stop_btn.clicked.connect(self.stop_pressing)
        self.stop_btn.setEnabled(False)
        button_layout.addWidget(self.stop_btn)
        
        parent_layout.addLayout(button_layout)
    
    def create_footer(self, parent_layout):
        """Create footer with logo and credits"""
        # Add some spacing before footer
        parent_layout.addStretch()
        
        # Footer container
        footer_layout = QVBoxLayout()
        
        # Logo at bottom
        logo_layout = QHBoxLayout()
        logo_layout.addStretch()  # Center the logo
        
        footer_logo_label = QLabel()
        logo_path = "asset/img/logo.png"
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            # Scale the footer logo to a smaller size (32x32 pixels)
            scaled_pixmap = pixmap.scaled(32, 32, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            footer_logo_label.setPixmap(scaled_pixmap)
            print(f"Footer logo loaded from: {logo_path}")
        else:
            # Fallback to emoji if no image file
            footer_logo_label.setText("🏥")
            footer_logo_label.setFont(QFont("Arial", 16))
            print(f"Footer logo file not found at: {logo_path}, using emoji fallback")
        
        footer_logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_layout.addWidget(footer_logo_label)
        logo_layout.addStretch()  # Center the logo
        
        # Credits text
        credits_label = QLabel("Made by Yeonseo Choo")
        credits_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        credits_label.setStyleSheet("QLabel { color: #888; font-size: 12px; font-style: italic; margin: 5px; }")
        
        footer_layout.addLayout(logo_layout)
        footer_layout.addWidget(credits_label)
        
        parent_layout.addLayout(footer_layout)
    
    def setup_timers(self):
        """Setup timers for automation"""
        self.press_timer = QTimer()
        self.press_timer.timeout.connect(self.execute_key_press)
        
        self.duration_timer = QTimer()
        self.duration_timer.timeout.connect(self.stop_pressing)
        self.duration_timer.setSingleShot(True)
        
        # Recording countdown timer
        self.countdown_timer = QTimer()
        self.countdown_timer.timeout.connect(self.countdown_tick)
        
        # Start countdown timer
        self.start_countdown_timer = QTimer()
        self.start_countdown_timer.timeout.connect(self.start_countdown_tick)
        
        self.press_count = 0
        self.target_repeats = 0
        self.start_time = 0
        self.countdown_value = 0
        self.start_countdown_value = 0
    
    def on_preset_changed(self, preset_text):
        """Handle preset combination selection"""
        preset_mappings = {
            "Page Down": "page_down",
            "Page Up": "page_up",
            "Arrow Down": "down",
            "Arrow Up": "up",
            "Arrow Left": "left",
            "Arrow Right": "right",
            "Space": "space",
            "Enter": "enter",
            "Tab": "tab",
            "Ctrl+C": "ctrl+c",
            "Ctrl+V": "ctrl+v",
            "Alt+Tab": "alt+tab",
            "F5 (Refresh)": "f5"
        }
        
        if preset_text in preset_mappings:
            self.combo_input.setText(preset_mappings[preset_text])
        elif preset_text == "Custom":
            self.combo_input.clear()
    
    def on_stop_key_changed(self, stop_key_text):
        """Handle stop key selection change"""
        key_mappings = {
            "ESC": "esc",
            "F1": "f1",
            "F2": "f2", 
            "F3": "f3",
            "F4": "f4",
            "Space": "space",
            "Enter": "enter"
        }
        
        if stop_key_text in key_mappings:
            self.keyboard_controller.set_stop_key(key_mappings[stop_key_text])
    
    def start_recording(self):
        """Start the recording process with countdown"""
        if self.is_recording:
            return
            
        self.is_recording = True
        self.record_btn.setEnabled(False)
        self.countdown_value = 3
        
        # Start countdown
        self.recording_status.setText(f"Recording in {self.countdown_value}...")
        self.countdown_timer.start(1000)  # 1 second intervals
    
    def countdown_tick(self):
        """Handle countdown timer tick"""
        self.countdown_value -= 1
        
        if self.countdown_value > 0:
            self.recording_status.setText(f"Recording in {self.countdown_value}...")
        else:
            self.countdown_timer.stop()
            self.recording_status.setText(f"🔴 RECORDING! Press keys, then {self.stop_key_combo.currentText()} to stop")
            self.keyboard_controller.start_recording()
    
    def on_combination_recorded(self, combination):
        """Handle when a combination is recorded"""
        self.is_recording = False
        self.record_btn.setEnabled(True)
        self.recording_status.setText(f"✅ Recorded: {combination}")
        self.combo_input.setText(combination)
        self.status_label.setText(f"Key combination recorded: {combination}")
        
        # Auto-select "Custom" in preset dropdown
        self.preset_combo.setCurrentText("Custom")
        
        # Update timing table
        self.update_timing_table()
    
    def update_timing_table(self):
        """Update the timing table based on current key combination"""
        keys = self.get_current_keys()
        if not keys:
            self.timing_table.setRowCount(0)
            return
        
        # Create rows for each transition
        transitions = []
        if len(keys) == 1:
            # For single key, create transition from key to itself (for repeat delay)
            key = keys[0]
            transitions.append((key, key))
        else:
            # For multiple keys, create transitions between each key
            for i in range(len(keys)):
                from_key = keys[i]
                to_key = keys[(i + 1) % len(keys)]  # Wrap around to first key
                transitions.append((from_key, to_key))
        
        self.timing_table.setRowCount(len(transitions))
        
        for row, (from_key, to_key) in enumerate(transitions):
            # From key (read-only)
            from_item = QTableWidgetItem(from_key)
            from_item.setFlags(from_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.timing_table.setItem(row, 0, from_item)
            
            # To key (read-only)
            to_item = QTableWidgetItem(to_key)
            to_item.setFlags(to_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.timing_table.setItem(row, 1, to_item)
            
            # Delay (editable)
            delay_item = QTableWidgetItem("100")  # Default 100ms
            self.timing_table.setItem(row, 2, delay_item)
    
    def auto_fill_timing(self):
        """Auto-fill all timing intervals with the same value"""
        fill_value = str(self.auto_fill_spin.value())
        for row in range(self.timing_table.rowCount()):
            delay_item = QTableWidgetItem(fill_value)
            self.timing_table.setItem(row, 2, delay_item)
    
    def get_timing_intervals(self):
        """Get timing intervals from the table"""
        intervals = []
        for row in range(self.timing_table.rowCount()):
            delay_item = self.timing_table.item(row, 2)
            if delay_item:
                try:
                    delay = int(delay_item.text())
                    intervals.append(delay)
                except ValueError:
                    intervals.append(100)  # Default fallback
            else:
                intervals.append(100)
        return intervals
    
    def get_current_keys(self):
        """Get the current key combination"""
        combo_text = self.combo_input.text().strip()
        if not combo_text:
            return None
        print(f"Current key combination: {combo_text}")
        return [key.strip() for key in combo_text.split('+')]
    
    def test_combination(self):
        """Test the current key combination"""
        keys = self.get_current_keys()
        if keys:
            self.status_label.setText("Testing key combination...")
            timing_intervals = self.get_timing_intervals()
            # For testing, include the final delay to show the complete sequence
            success = self.keyboard_controller.send_key_combination(keys, timing_intervals, include_final_delay=True)
            if success:
                self.status_label.setText(f"Test successful! Sequential keys: {' → '.join(keys)}")
            else:
                self.status_label.setText("Test failed! Check your key combination.")
        else:
            self.status_label.setText("Please enter a key combination first.")
    
    def start_pressing(self):
        """Start the key pressing automation"""
        keys = self.get_current_keys()
        if not keys:
            self.status_label.setText("Please enter a key combination first.")
            return
        
        self.is_running = True
        self.press_count = 0
        self.start_time = time.time()
        
        # Set target repeats if in repeat mode
        if self.timed_radio.isChecked():
            self.target_repeats = self.repeat_count_spin.value()
        else:
            self.target_repeats = 0  # Continuous mode
        
        # Update UI
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        
        # Calculate total cycle time from timing table for the timer
        timing_intervals = self.get_timing_intervals()
        if timing_intervals and len(timing_intervals) > 0:
            # Use sum of all timing intervals as the cycle time
            cycle_time = sum(timing_intervals)
        else:
            # Default fallback if no timing table
            cycle_time = 1000  # 1 second default
        
        # Start pressing with calculated cycle time
        self.press_timer.start(cycle_time)
        
        # Set status message
        if self.timed_radio.isChecked():
            self.status_label.setText(f"Started! Will repeat {self.target_repeats} times...")
        else:
            self.status_label.setText("Started! Press 'Stop' to end.")
    
    def execute_key_press(self):
        """Execute a single key press"""
        if not self.is_running:
            return
        
        # Check if we've reached the target number of repeats
        if self.target_repeats > 0 and self.press_count >= self.target_repeats:
            self.stop_pressing()
            return
            
        keys = self.get_current_keys()
        if keys:
            # Always use sequential timing with timing table
            timing_intervals = self.get_timing_intervals()
            print(f"Using sequential timing: {timing_intervals}")
            # For automation, don't include the final delay - let the timer handle it
            success = self.keyboard_controller.send_key_combination(keys, timing_intervals, include_final_delay=False)
                
            if success:
                self.press_count += 1
                elapsed = time.time() - self.start_time
                
                if self.target_repeats > 0:
                    remaining = self.target_repeats - self.press_count
                    # Calculate estimated time remaining
                    if remaining > 0:
                        cycle_time = sum(timing_intervals) / 1000.0 if timing_intervals else 1.0  # Convert ms to seconds
                        estimated_time_remaining = remaining * cycle_time
                        time_remaining_str = self.format_time_remaining(estimated_time_remaining)
                        self.status_label.setText(f"Running... Completed: {self.press_count}/{self.target_repeats}, Remaining: {remaining} ({time_remaining_str})")
                    else:
                        self.status_label.setText(f"Running... Completed: {self.press_count}/{self.target_repeats}, Finishing...")
                else:
                    self.status_label.setText(f"Running... Presses: {self.press_count}, Elapsed: {elapsed:.1f}s")
    
    def stop_pressing(self):
        """Stop the key pressing automation"""
        self.is_running = False
        self.press_timer.stop()
        self.duration_timer.stop()
        self.start_countdown_timer.stop()  # Also stop countdown timer if running
        
        # Update UI
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        
        elapsed = time.time() - self.start_time if self.start_time > 0 else 0
        
        if self.target_repeats > 0:
            if self.press_count >= self.target_repeats:
                self.status_label.setText(f"✅ Completed! {self.press_count} repeats in {elapsed:.1f}s")
            else:
                self.status_label.setText(f"⏹️ Stopped. {self.press_count}/{self.target_repeats} repeats in {elapsed:.1f}s")
        else:
            self.status_label.setText(f"⏹️ Stopped. Total presses: {self.press_count}, Duration: {elapsed:.1f}s")

    def start_countdown(self):
        """Start the 3-second countdown before automation begins"""
        keys = self.get_current_keys()
        if not keys:
            self.status_label.setText("Please enter a key combination first.")
            return
            
        # Disable start button during countdown
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        
        # Initialize countdown
        self.start_countdown_value = 3
        self.status_label.setText(f"Starting in {self.start_countdown_value}...")
        
        # Start countdown timer (1 second intervals)
        self.start_countdown_timer.start(1000)
    
    def start_countdown_tick(self):
        """Handle countdown timer tick"""
        self.start_countdown_value -= 1
        
        if self.start_countdown_value > 0:
            self.status_label.setText(f"Starting in {self.start_countdown_value}...")
        else:
            # Countdown finished, stop timer and start automation
            self.start_countdown_timer.stop()
            self.status_label.setText("Starting automation...")
            self.start_pressing()
    
    def calculate_dv_repetitions(self):
        """Calculate the number of repetitions based on DV values and step size"""
        import math
        
        current_dv = self.current_dv_spin.value()
        final_dv = self.final_dv_spin.value()
        step_size = self.step_size_spin.value()  # presses per 0.001mm
        
        # Validate inputs
        if step_size <= 0:
            self.dv_result_label.setText("❌ Step size must be greater than 0")
            self.dv_result_label.setStyleSheet("QLabel { color: #ff4444; font-weight: bold; }")
            return
        
        if abs(final_dv - current_dv) < 0.0001:  # Check if values are essentially the same
            self.dv_result_label.setText("❌ Current and Final DV must be different")
            self.dv_result_label.setStyleSheet("QLabel { color: #ff4444; font-weight: bold; }")
            return
        
        # Calculate the difference and number of steps
        dv_difference = final_dv - current_dv  # in mm
        distance_in_0001mm = abs(dv_difference) * 1000  # Convert to 0.001mm units
        
        # Calculate total repetitions: distance * presses_per_unit
        exact_repetitions = distance_in_0001mm * step_size
        
        # Round up to get the smallest integer >= exact_repetitions
        repetitions = math.ceil(exact_repetitions)
        
        # Update the result label
        direction = "increase" if dv_difference > 0 else "decrease"
        self.dv_result_label.setText(f"✅ {repetitions} presses ({direction} by {abs(dv_difference):.3f} mm)")
        self.dv_result_label.setStyleSheet("QLabel { color: #2E86AB; font-weight: bold; }")
        
        # Automatically set the repeat count and switch to repeat mode
        self.repeat_count_spin.setValue(repetitions)
        self.timed_radio.setChecked(True)  # Switch to "For specific number of repeats"
        
        # Update status
        self.status_label.setText(f"DV calculation complete: {repetitions} repetitions calculated")
        
        print(f"DV Calculation: {current_dv:.3f} → {final_dv:.3f} mm, step: {step_size} presses/0.001mm, repetitions: {repetitions}")
    
    def format_time_remaining(self, seconds):
        """Format time remaining as either seconds or min:sec"""
        if seconds < 60:
            return f"{seconds:.0f}s"
        else:
            minutes = int(seconds // 60)
            secs = int(seconds % 60)
            return f"{minutes}:{secs:02d}"


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("AutoKey")
    
    # Set application style
    app.setStyle('Fusion')
    
    window = AutoKeyApp()
    window.show()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
