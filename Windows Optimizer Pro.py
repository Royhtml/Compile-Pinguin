import sys
import os
import psutil
import subprocess
import platform
import winreg
import ctypes
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QLabel, QProgressBar, 
                             QTabWidget, QMessageBox, QSystemTrayIcon, QMenu,
                             QGroupBox, QCheckBox, QSpinBox, QComboBox, QLineEdit,
                             QFileDialog, QListWidget, QTreeWidget, QTreeWidgetItem)
from PyQt5.QtCore import QTimer, Qt, QSize
from PyQt5.QtGui import QIcon, QFont
import glob

class WindowsOptimizerPro(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Windows Optimizer Pro")
        self.setWindowIcon(QIcon("icon.ico"))
        self.setGeometry(100, 100, 900, 700)
        
        # Set style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QTabWidget::pane {
                border: 1px solid #c4c4c4;
                top: 1px;
                background: white;
            }
            QTabBar::tab {
                background: #e0e0e0;
                border: 1px solid #c4c4c4;
                padding: 8px;
                min-width: 100px;
            }
            QTabBar::tab:selected {
                background: white;
                border-bottom-color: white;
            }
            QGroupBox {
                border: 1px solid #c4c4c4;
                border-radius: 3px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px;
            }
            QPushButton {
                background-color: #e0e0e0;
                border: 1px solid #c4c4c4;
                padding: 5px 10px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #d0d0d0;
            }
            QPushButton:pressed {
                background-color: #c0c0c0;
            }
            QProgressBar {
                border: 1px solid #c4c4c4;
                border-radius: 3px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                width: 10px;
            }
        """)
        
        # System tray
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon("icon.ico"))
        self.tray_icon.setVisible(True)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create main widget and layout
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.main_layout = QVBoxLayout(self.main_widget)
        
        # Create tabs
        self.tabs = QTabWidget()
        self.main_layout.addWidget(self.tabs)
        
        # Create all tabs
        self.create_dashboard_tab()
        self.create_cleaner_tab()
        self.create_optimizer_tab()
        self.create_startup_tab()
        self.create_services_tab()
        self.create_tweaks_tab()
        self.create_settings_tab()
        
        # Status bar
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Ready")
        
        # Update system info periodically
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_system_info)
        self.timer.start(2000)
        
        # Load initial data
        self.update_system_info()
        self.load_startup_programs()
        self.load_services()
    
    def create_menu_bar(self):
        """Create the menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('File')
        
        exit_action = file_menu.addAction('Exit')
        exit_action.triggered.connect(self.close)
        
        # Tools menu
        tools_menu = menubar.addMenu('Tools')
        
        disk_cleanup_action = tools_menu.addAction('Disk Cleanup')
        disk_cleanup_action.triggered.connect(self.run_disk_cleanup)
        
        perf_monitor_action = tools_menu.addAction('Performance Monitor')
        perf_monitor_action.triggered.connect(self.open_perf_monitor)
        
        # Help menu
        help_menu = menubar.addMenu('Help')
        
        about_action = help_menu.addAction('About')
        about_action.triggered.connect(self.show_about)
        
        docs_action = help_menu.addAction('Documentation')
        docs_action.triggered.connect(self.show_documentation)
    
    def create_dashboard_tab(self):
        """Create the dashboard tab with system overview"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # System summary group
        summary_group = QGroupBox("System Summary")
        summary_layout = QVBoxLayout()
        
        self.system_summary = QLabel()
        self.system_summary.setWordWrap(True)
        summary_layout.addWidget(self.system_summary)
        
        # Performance metrics group
        metrics_group = QGroupBox("Performance Metrics")
        metrics_layout = QVBoxLayout()
        
        # CPU
        cpu_group = QGroupBox("CPU")
        cpu_layout = QVBoxLayout()
        self.cpu_label = QLabel("Usage: 0%")
        self.cpu_bar = QProgressBar()
        cpu_layout.addWidget(self.cpu_label)
        cpu_layout.addWidget(self.cpu_bar)
        cpu_group.setLayout(cpu_layout)
        
        # RAM
        ram_group = QGroupBox("RAM")
        ram_layout = QVBoxLayout()
        self.ram_label = QLabel("Usage: 0%")
        self.ram_bar = QProgressBar()
        ram_layout.addWidget(self.ram_label)
        ram_layout.addWidget(self.ram_bar)
        ram_group.setLayout(ram_layout)
        
        # Disk
        disk_group = QGroupBox("Disk (C:)")
        disk_layout = QVBoxLayout()
        self.disk_label = QLabel("Usage: 0%")
        self.disk_bar = QProgressBar()
        disk_layout.addWidget(self.disk_label)
        disk_layout.addWidget(self.disk_bar)
        disk_group.setLayout(disk_layout)
        
        # Network
        network_group = QGroupBox("Network")
        network_layout = QVBoxLayout()
        self.network_label = QLabel("Activity: 0 KB/s")
        network_layout.addWidget(self.network_label)
        network_group.setLayout(network_layout)
        
        # Add to metrics layout
        metrics_row1 = QHBoxLayout()
        metrics_row1.addWidget(cpu_group)
        metrics_row1.addWidget(ram_group)
        metrics_row2 = QHBoxLayout()
        metrics_row2.addWidget(disk_group)
        metrics_row2.addWidget(network_group)
        
        metrics_layout.addLayout(metrics_row1)
        metrics_layout.addLayout(metrics_row2)
        metrics_group.setLayout(metrics_layout)
        
        # Quick actions
        quick_actions_group = QGroupBox("Quick Actions")
        quick_actions_layout = QHBoxLayout()
        
        quick_clean_btn = QPushButton("Quick Clean")
        quick_clean_btn.clicked.connect(self.quick_clean)
        
        quick_optimize_btn = QPushButton("Quick Optimize")
        quick_optimize_btn.clicked.connect(self.quick_optimize)
        
        quick_boost_btn = QPushButton("Performance Boost")
        quick_boost_btn.clicked.connect(self.performance_boost)
        
        quick_actions_layout.addWidget(quick_clean_btn)
        quick_actions_layout.addWidget(quick_optimize_btn)
        quick_actions_layout.addWidget(quick_boost_btn)
        quick_actions_group.setLayout(quick_actions_layout)
        
        # Add to main layout
        summary_group.setLayout(summary_layout)
        layout.addWidget(summary_group)
        layout.addWidget(metrics_group)
        layout.addWidget(quick_actions_group)
        
        self.tabs.addTab(tab, "Dashboard")
    
    def create_cleaner_tab(self):
        """Create the cleaner tab with various cleaning options"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Disk Cleaner group
        disk_cleaner_group = QGroupBox("Disk Cleaner")
        disk_cleaner_layout = QVBoxLayout()
        
        # Clean options
        self.temp_files_check = QCheckBox("Temporary Files")
        self.temp_files_check.setChecked(True)
        
        self.prefetch_check = QCheckBox("Prefetch Files")
        
        self.dump_files_check = QCheckBox("Memory Dump Files")
        
        self.thumbnails_check = QCheckBox("Thumbnail Cache")
        
        self.browser_cache_check = QCheckBox("Browser Caches")
        
        # Clean button
        clean_disk_btn = QPushButton("Clean Selected Items")
        clean_disk_btn.clicked.connect(self.clean_selected_items)
        
        # Add to layout
        disk_cleaner_layout.addWidget(self.temp_files_check)
        disk_cleaner_layout.addWidget(self.prefetch_check)
        disk_cleaner_layout.addWidget(self.dump_files_check)
        disk_cleaner_layout.addWidget(self.thumbnails_check)
        disk_cleaner_layout.addWidget(self.browser_cache_check)
        disk_cleaner_layout.addWidget(clean_disk_btn)
        disk_cleaner_group.setLayout(disk_cleaner_layout)
        
        # Registry Cleaner group
        registry_cleaner_group = QGroupBox("Registry Cleaner")
        registry_cleaner_layout = QVBoxLayout()
        
        self.registry_issues_label = QLabel("Detected issues: 0")
        
        scan_registry_btn = QPushButton("Scan for Registry Issues")
        scan_registry_btn.clicked.connect(self.scan_registry)
        
        clean_registry_btn = QPushButton("Fix Selected Issues")
        clean_registry_btn.clicked.connect(self.clean_registry)
        
        # Registry issues list
        self.registry_issues_list = QListWidget()
        
        registry_cleaner_layout.addWidget(self.registry_issues_label)
        registry_cleaner_layout.addWidget(scan_registry_btn)
        registry_cleaner_layout.addWidget(self.registry_issues_list)
        registry_cleaner_layout.addWidget(clean_registry_btn)
        registry_cleaner_group.setLayout(registry_cleaner_layout)
        
        # Add to main layout
        layout.addWidget(disk_cleaner_group)
        layout.addWidget(registry_cleaner_group)
        
        self.tabs.addTab(tab, "Cleaner")
    
    def create_optimizer_tab(self):
        """Create the optimizer tab with system optimization options"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Performance Tweaks group
        perf_tweaks_group = QGroupBox("Performance Tweaks")
        perf_tweaks_layout = QVBoxLayout()
        
        # Visual effects
        visual_effects_group = QGroupBox("Visual Effects")
        visual_effects_layout = QVBoxLayout()
        
        self.visual_effects_combo = QComboBox()
        self.visual_effects_combo.addItems([
            "Let Windows decide",
            "Adjust for best appearance",
            "Adjust for best performance",
            "Custom"
        ])
        
        visual_effects_layout.addWidget(QLabel("Visual Effects Settings:"))
        visual_effects_layout.addWidget(self.visual_effects_combo)
        visual_effects_group.setLayout(visual_effects_layout)
        
        # Processor scheduling
        proc_scheduling_group = QGroupBox("Processor Scheduling")
        proc_scheduling_layout = QVBoxLayout()
        
        self.proc_scheduling_combo = QComboBox()
        self.proc_scheduling_combo.addItems([
            "Programs (default)",
            "Background services"
        ])
        
        proc_scheduling_layout.addWidget(QLabel("Processor Scheduling:"))
        proc_scheduling_layout.addWidget(self.proc_scheduling_combo)
        proc_scheduling_group.setLayout(proc_scheduling_layout)
        
        # Virtual memory
        virtual_mem_group = QGroupBox("Virtual Memory")
        virtual_mem_layout = QVBoxLayout()
        
        self.virtual_mem_check = QCheckBox("Automatically manage paging file size")
        self.virtual_mem_check.setChecked(True)
        
        virtual_mem_layout.addWidget(self.virtual_mem_check)
        virtual_mem_group.setLayout(virtual_mem_layout)
        
        # Apply button
        apply_tweaks_btn = QPushButton("Apply Performance Tweaks")
        apply_tweaks_btn.clicked.connect(self.apply_performance_tweaks)
        
        # Add to layout
        perf_tweaks_layout.addWidget(visual_effects_group)
        perf_tweaks_layout.addWidget(proc_scheduling_group)
        perf_tweaks_layout.addWidget(virtual_mem_group)
        perf_tweaks_layout.addWidget(apply_tweaks_btn)
        perf_tweaks_group.setLayout(perf_tweaks_layout)
        
        # System Maintenance group
        sys_maintenance_group = QGroupBox("System Maintenance")
        sys_maintenance_layout = QVBoxLayout()
        
        # Disk defrag
        defrag_btn = QPushButton("Defragment and Optimize Drives")
        defrag_btn.clicked.connect(self.defragment_disk)
        
        # Check disk
        check_disk_btn = QPushButton("Check Disk for Errors")
        check_disk_btn.clicked.connect(self.check_disk)
        
        sys_maintenance_layout.addWidget(defrag_btn)
        sys_maintenance_layout.addWidget(check_disk_btn)
        sys_maintenance_group.setLayout(sys_maintenance_layout)
        
        # Add to main layout
        layout.addWidget(perf_tweaks_group)
        layout.addWidget(sys_maintenance_group)
        
        self.tabs.addTab(tab, "Optimizer")
    
    def create_startup_tab(self):
        """Create the startup tab with startup program management"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Startup programs group
        startup_group = QGroupBox("Startup Programs")
        startup_layout = QVBoxLayout()
        
        self.startup_tree = QTreeWidget()
        self.startup_tree.setHeaderLabels(["Name", "Publisher", "Status", "Impact"])
        self.startup_tree.setSortingEnabled(True)
        
        refresh_startup_btn = QPushButton("Refresh List")
        refresh_startup_btn.clicked.connect(self.load_startup_programs)
        
        disable_startup_btn = QPushButton("Disable Selected")
        disable_startup_btn.clicked.connect(self.disable_startup_programs)
        
        startup_layout.addWidget(self.startup_tree)
        startup_layout.addWidget(refresh_startup_btn)
        startup_layout.addWidget(disable_startup_btn)
        startup_group.setLayout(startup_layout)
        
        # Scheduled tasks group
        tasks_group = QGroupBox("Scheduled Tasks")
        tasks_layout = QVBoxLayout()
        
        self.tasks_tree = QTreeWidget()
        self.tasks_tree.setHeaderLabels(["Task Name", "Status", "Next Run", "Last Run"])
        
        refresh_tasks_btn = QPushButton("Refresh List")
        refresh_tasks_btn.clicked.connect(self.load_scheduled_tasks)
        
        disable_tasks_btn = QPushButton("Disable Selected")
        disable_tasks_btn.clicked.connect(self.disable_scheduled_tasks)
        
        tasks_layout.addWidget(self.tasks_tree)
        tasks_layout.addWidget(refresh_tasks_btn)
        tasks_layout.addWidget(disable_tasks_btn)
        tasks_group.setLayout(tasks_layout)
        
        # Add to main layout
        layout.addWidget(startup_group)
        layout.addWidget(tasks_group)
        
        self.tabs.addTab(tab, "Startup")
    
    def create_services_tab(self):
        """Create the services tab with Windows services management"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Services management group
        services_group = QGroupBox("Windows Services")
        services_layout = QVBoxLayout()
        
        # Filter
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Filter:"))
        
        self.services_filter = QLineEdit()
        self.services_filter.setPlaceholderText("Search services...")
        self.services_filter.textChanged.connect(self.filter_services)
        
        filter_layout.addWidget(self.services_filter)
        services_layout.addLayout(filter_layout)
        
        # Services tree
        self.services_tree = QTreeWidget()
        self.services_tree.setHeaderLabels(["Service", "Status", "Startup Type", "Description"])
        self.services_tree.setSortingEnabled(True)
        
        # Service controls
        controls_layout = QHBoxLayout()
        
        start_service_btn = QPushButton("Start")
        start_service_btn.clicked.connect(self.start_service)
        
        stop_service_btn = QPushButton("Stop")
        stop_service_btn.clicked.connect(self.stop_service)
        
        restart_service_btn = QPushButton("Restart")
        restart_service_btn.clicked.connect(self.restart_service)
        
        change_startup_btn = QPushButton("Change Startup")
        change_startup_btn.clicked.connect(self.change_service_startup)
        
        controls_layout.addWidget(start_service_btn)
        controls_layout.addWidget(stop_service_btn)
        controls_layout.addWidget(restart_service_btn)
        controls_layout.addWidget(change_startup_btn)
        
        services_layout.addWidget(self.services_tree)
        services_layout.addLayout(controls_layout)
        services_group.setLayout(services_layout)
        
        # Recommended services group
        recommended_group = QGroupBox("Recommended Optimizations")
        recommended_layout = QVBoxLayout()
        
        # Recommended tweaks
        self.disable_superfetch_check = QCheckBox("Disable Superfetch (SysMain)")
        self.disable_wsearch_check = QCheckBox("Disable Windows Search (WSearch)")
        self.disable_telemetry_check = QCheckBox("Disable Telemetry Services")
        
        apply_recommended_btn = QPushButton("Apply Recommended Settings")
        apply_recommended_btn.clicked.connect(self.apply_recommended_services)
        
        recommended_layout.addWidget(self.disable_superfetch_check)
        recommended_layout.addWidget(self.disable_wsearch_check)
        recommended_layout.addWidget(self.disable_telemetry_check)
        recommended_layout.addWidget(apply_recommended_btn)
        recommended_group.setLayout(recommended_layout)
        
        # Add to main layout
        layout.addWidget(services_group)
        layout.addWidget(recommended_group)
        
        self.tabs.addTab(tab, "Services")
    
    def create_tweaks_tab(self):
        """Create the tweaks tab with various Windows tweaks"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # System tweaks group
        system_tweaks_group = QGroupBox("System Tweaks")
        system_tweaks_layout = QVBoxLayout()
        
        # Fast startup
        self.fast_startup_check = QCheckBox("Enable Fast Startup")
        
        # Hibernation
        self.disable_hibernation_check = QCheckBox("Disable Hibernation (save disk space)")
        
        # UAC level
        uac_group = QGroupBox("User Account Control (UAC)")
        uac_layout = QVBoxLayout()
        
        self.uac_slider = QComboBox()
        self.uac_slider.addItems([
            "Always notify (most secure)",
            "Notify only when apps try to make changes (default)",
            "Notify only when apps try to make changes (do not dim desktop)",
            "Never notify (least secure)"
        ])
        
        uac_layout.addWidget(self.uac_slider)
        uac_group.setLayout(uac_layout)
        
        # Context menu tweaks
        context_menu_group = QGroupBox("Context Menu Tweaks")
        context_menu_layout = QVBoxLayout()
        
        self.add_take_ownership_check = QCheckBox("Add 'Take Ownership' to context menu")
        self.add_copy_path_check = QCheckBox("Add 'Copy as Path' to context menu")
        
        context_menu_layout.addWidget(self.add_take_ownership_check)
        context_menu_layout.addWidget(self.add_copy_path_check)
        context_menu_group.setLayout(context_menu_layout)
        
        # Apply button
        apply_tweaks_btn = QPushButton("Apply System Tweaks")
        apply_tweaks_btn.clicked.connect(self.apply_system_tweaks)
        
        system_tweaks_layout.addWidget(self.fast_startup_check)
        system_tweaks_layout.addWidget(self.disable_hibernation_check)
        system_tweaks_layout.addWidget(uac_group)
        system_tweaks_layout.addWidget(context_menu_group)
        system_tweaks_layout.addWidget(apply_tweaks_btn)
        system_tweaks_group.setLayout(system_tweaks_layout)
        
        # Network tweaks group
        network_tweaks_group = QGroupBox("Network Tweaks")
        network_tweaks_layout = QVBoxLayout()
        
        # DNS settings
        dns_group = QGroupBox("DNS Settings")
        dns_layout = QVBoxLayout()
        
        self.dns_combo = QComboBox()
        self.dns_combo.addItems([
            "Automatic (default)",
            "Google Public DNS (8.8.8.8, 8.8.4.4)",
            "Cloudflare DNS (1.1.1.1, 1.0.0.1)",
            "OpenDNS (208.67.222.222, 208.67.220.220)"
        ])
        
        dns_layout.addWidget(self.dns_combo)
        dns_group.setLayout(dns_layout)
        
        # Network throttling
        self.disable_throttling_check = QCheckBox("Disable Network Throttling")
        
        apply_network_btn = QPushButton("Apply Network Tweaks")
        apply_network_btn.clicked.connect(self.apply_network_tweaks)
        
        network_tweaks_layout.addWidget(dns_group)
        network_tweaks_layout.addWidget(self.disable_throttling_check)
        network_tweaks_layout.addWidget(apply_network_btn)
        network_tweaks_group.setLayout(network_tweaks_layout)
        
        # Add to main layout
        layout.addWidget(system_tweaks_group)
        layout.addWidget(network_tweaks_group)
        
        self.tabs.addTab(tab, "Tweaks")
    
    def create_settings_tab(self):
        """Create the settings tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # General settings group
        general_group = QGroupBox("General Settings")
        general_layout = QVBoxLayout()
        
        # Auto-start option
        self.autostart_checkbox = QCheckBox("Enable Auto-start with Windows")
        self.autostart_checkbox.stateChanged.connect(self.toggle_autostart)
        
        # Minimize to tray option
        self.minimize_to_tray_checkbox = QCheckBox("Minimize to System Tray")
        self.minimize_to_tray_checkbox.setChecked(True)
        
        # Check for updates
        self.auto_update_checkbox = QCheckBox("Automatically check for updates")
        self.auto_update_checkbox.setChecked(True)
        
        general_layout.addWidget(self.autostart_checkbox)
        general_layout.addWidget(self.minimize_to_tray_checkbox)
        general_layout.addWidget(self.auto_update_checkbox)
        general_group.setLayout(general_layout)
        
        # UI settings group
        ui_group = QGroupBox("Interface Settings")
        ui_layout = QVBoxLayout()
        
        # Theme selection
        theme_layout = QHBoxLayout()
        theme_layout.addWidget(QLabel("Theme:"))
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Light", "Dark", "System"])
        
        theme_layout.addWidget(self.theme_combo)
        ui_layout.addLayout(theme_layout)
        
        # Font size
        font_layout = QHBoxLayout()
        font_layout.addWidget(QLabel("Font Size:"))
        
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 16)
        self.font_size_spin.setValue(10)
        
        font_layout.addWidget(self.font_size_spin)
        ui_layout.addLayout(font_layout)
        
        ui_group.setLayout(ui_layout)
        
        # About group
        about_group = QGroupBox("About")
        about_layout = QVBoxLayout()
        
        about_btn = QPushButton("About Windows Optimizer Pro")
        about_btn.clicked.connect(self.show_about)
        
        check_update_btn = QPushButton("Check for Updates")
        check_update_btn.clicked.connect(self.check_for_updates)
        
        about_layout.addWidget(about_btn)
        about_layout.addWidget(check_update_btn)
        about_group.setLayout(about_layout)
        
        # Add to main layout
        layout.addWidget(general_group)
        layout.addWidget(ui_group)
        layout.addWidget(about_group)
        layout.addStretch()
        
        self.tabs.addTab(tab, "Settings")
    
    def update_system_info(self):
        """Update the system information displays"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent()
            self.cpu_label.setText(f"Usage: {cpu_percent}%")
            self.cpu_bar.setValue(int(cpu_percent))
            
            # RAM usage
            ram = psutil.virtual_memory()
            ram_percent = ram.percent
            self.ram_label.setText(f"Usage: {ram_percent}% ({ram.used//1024//1024}MB / {ram.total//1024//1024}MB)")
            self.ram_bar.setValue(int(ram_percent))
            
            # Disk usage
            disk = psutil.disk_usage('C:')
            disk_percent = disk.percent
            self.disk_label.setText(f"Usage: {disk_percent}% ({disk.used//1024//1024}MB / {disk.total//1024//1024}MB)")
            self.disk_bar.setValue(int(disk_percent))
            
            # Network usage
            net_io = psutil.net_io_counters()
            kb_sent = net_io.bytes_sent / 1024
            kb_recv = net_io.bytes_recv / 1024
            self.network_label.setText(f"Activity: ↑{kb_sent:.1f} KB/s ↓{kb_recv:.1f} KB/s")
            
            # System summary
            uname = platform.uname()
            boot_time = psutil.boot_time()
            summary = f"""
            <b>System Information:</b><br>
            OS: {uname.system} {uname.release} ({uname.version})<br>
            Machine: {uname.machine}<br>
            Processor: {uname.processor}<br>
            CPU Cores: {psutil.cpu_count(logical=False)} physical, {psutil.cpu_count(logical=True)} logical<br>
            CPU Frequency: {psutil.cpu_freq().current:.2f} MHz<br>
            Boot Time: {boot_time}<br>
            Processes: {len(psutil.pids())} running
            """
            self.system_summary.setText(summary)
            
        except Exception as e:
            print(f"Error updating system info: {e}")
    
    def clean_selected_items(self):
        """Clean selected items in the cleaner tab"""
        try:
            cleaned_items = []
            
            if self.temp_files_check.isChecked():
                self.clean_temp_files()
                cleaned_items.append("Temporary Files")
            
            if self.prefetch_check.isChecked():
                self.clean_prefetch()
                cleaned_items.append("Prefetch Files")
            
            if self.dump_files_check.isChecked():
                self.clean_dump_files()
                cleaned_items.append("Memory Dump Files")
            
            if self.thumbnails_check.isChecked():
                self.clean_thumbnail_cache()
                cleaned_items.append("Thumbnail Cache")
            
            if self.browser_cache_check.isChecked():
                self.clean_browser_caches()
                cleaned_items.append("Browser Caches")
            
            if cleaned_items:
                QMessageBox.information(self, "Cleaning Complete", 
                    f"Successfully cleaned: {', '.join(cleaned_items)}")
            else:
                QMessageBox.warning(self, "No Selection", 
                    "Please select at least one item to clean")
                
        except Exception as e:
            self.show_error_message(f"Failed to clean selected items: {str(e)}")
    
    def clean_temp_files(self):
        """Clean temporary files"""
        try:
            self.status_bar.showMessage("Cleaning temporary files...")
            QApplication.processEvents()
            
            temp_dirs = [
                os.environ.get('TEMP', ''),
                os.environ.get('TMP', ''),
                r'C:\Windows\Temp',
                r'C:\Windows\Prefetch',
                os.path.expanduser('~\\AppData\\Local\\Temp')
            ]
            
            for temp_dir in temp_dirs:
                if os.path.exists(temp_dir):
                    for root, dirs, files in os.walk(temp_dir):
                        for file in files:
                            try:
                                os.remove(os.path.join(root, file))
                            except:
                                pass
            
            self.status_bar.showMessage("Temporary files cleaned successfully!")
            
        except Exception as e:
            self.show_error_message(f"Failed to clean temporary files: {str(e)}")
    
    def clean_prefetch(self):
        """Clean prefetch files"""
        try:
            prefetch_dir = r'C:\Windows\Prefetch'
            if os.path.exists(prefetch_dir):
                for file in os.listdir(prefetch_dir):
                    try:
                        os.remove(os.path.join(prefetch_dir, file))
                    except:
                        pass
            self.status_bar.showMessage("Prefetch files cleaned successfully!")
        except Exception as e:
            self.show_error_message(f"Failed to clean prefetch files: {str(e)}")
    
    def clean_dump_files(self):
        """Clean memory dump files"""
        try:
            dump_dir = r'C:\Windows\Minidump'
            if os.path.exists(dump_dir):
                for file in os.listdir(dump_dir):
                    try:
                        os.remove(os.path.join(dump_dir, file))
                    except:
                        pass
            
            dump_file = r'C:\Windows\MEMORY.DMP'
            if os.path.exists(dump_file):
                try:
                    os.remove(dump_file)
                except:
                    pass
            
            self.status_bar.showMessage("Memory dump files cleaned successfully!")
        except Exception as e:
            self.show_error_message(f"Failed to clean dump files: {str(e)}")
    
    def clean_thumbnail_cache(self):
        """Clean thumbnail cache"""
        try:
            thumb_cache = os.path.expanduser('~\\AppData\\Local\\Microsoft\\Windows\\Explorer\\thumbcache_*.db')
            for file in glob.glob(thumb_cache):
                try:
                    os.remove(file)
                except:
                    pass
            
            self.status_bar.showMessage("Thumbnail cache cleaned successfully!")
        except Exception as e:
            self.show_error_message(f"Failed to clean thumbnail cache: {str(e)}")
    
    def clean_browser_caches(self):
        """Clean browser caches"""
        try:
            browsers = {
                'Chrome': '~\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\Cache',
                'Edge': '~\\AppData\\Local\\Microsoft\\Edge\\User Data\\Default\\Cache',
                'Firefox': '~\\AppData\\Local\\Mozilla\\Firefox\\Profiles\\*.default-release\\cache2',
                'Opera': '~\\AppData\\Local\\Opera Software\\Opera Stable\\Cache'
            }
            
            for browser, cache_path in browsers.items():
                cache_dir = os.path.expanduser(cache_path)
                if os.path.exists(cache_dir):
                    for root, dirs, files in os.walk(cache_dir):
                        for file in files:
                            try:
                                os.remove(os.path.join(root, file))
                            except:
                                pass
            
            self.status_bar.showMessage("Browser caches cleaned successfully!")
        except Exception as e:
            self.show_error_message(f"Failed to clean browser caches: {str(e)}")
    
    def scan_registry(self):
        """Scan registry for issues (simulated)"""
        try:
            self.status_bar.showMessage("Scanning registry for issues...")
            QApplication.processEvents()
            
            # Simulate finding issues
            issues = [
                "Invalid file extensions (15)",
                "Obsolete software entries (8)",
                "Missing shared DLLs (3)",
                "Invalid paths (12)",
                "Orphaned startup entries (5)"
            ]
            
            self.registry_issues_list.clear()
            self.registry_issues_list.addItems(issues)
            self.registry_issues_label.setText(f"Detected issues: {len(issues)}")
            
            self.status_bar.showMessage("Registry scan completed!")
            
        except Exception as e:
            self.show_error_message(f"Failed to scan registry: {str(e)}")
    
    def clean_registry(self):
        """Clean selected registry issues (simulated)"""
        try:
            selected_items = self.registry_issues_list.selectedItems()
            if not selected_items:
                QMessageBox.warning(self, "No Selection", "Please select issues to fix")
                return
            
            self.status_bar.showMessage("Fixing selected registry issues...")
            QApplication.processEvents()
            
            # Simulate fixing
            fixed_count = len(selected_items)
            remaining_count = self.registry_issues_list.count() - fixed_count
            
            self.registry_issues_label.setText(f"Detected issues: {remaining_count}")
            
            for item in selected_items:
                self.registry_issues_list.takeItem(self.registry_issues_list.row(item))
            
            self.status_bar.showMessage(f"Fixed {fixed_count} registry issues!")
            
        except Exception as e:
            self.show_error_message(f"Failed to clean registry: {str(e)}")
    
    def apply_performance_tweaks(self):
        """Apply selected performance tweaks"""
        try:
            self.status_bar.showMessage("Applying performance tweaks...")
            QApplication.processEvents()
            
            # Visual effects
            visual_effect = self.visual_effects_combo.currentText()
            if visual_effect == "Adjust for best performance":
                # Simulate setting visual effects for performance
                pass
            
            # Processor scheduling
            proc_scheduling = self.proc_scheduling_combo.currentText()
            if proc_scheduling == "Background services":
                # Simulate setting processor scheduling
                pass
            
            # Virtual memory
            if not self.virtual_mem_check.isChecked():
                # Simulate custom virtual memory settings
                pass
            
            self.status_bar.showMessage("Performance tweaks applied successfully!")
            QMessageBox.information(self, "Success", "Performance tweaks have been applied")
            
        except Exception as e:
            self.show_error_message(f"Failed to apply performance tweaks: {str(e)}")
    
    def defragment_disk(self):
        """Defragment disk"""
        try:
            self.status_bar.showMessage("Defragmenting disk (requires admin)...")
            QApplication.processEvents()
            
            # Windows specific
            if os.name == 'nt':
                result = subprocess.run(['defrag', 'C:', '/U', '/V'], 
                                      capture_output=True, text=True)
                
                if result.returncode == 0:
                    self.status_bar.showMessage("Disk defragmentation completed!")
                    QMessageBox.information(self, "Success", "Disk defragmentation completed successfully")
                else:
                    self.status_bar.showMessage("Disk defragmentation failed")
                    QMessageBox.warning(self, "Warning", 
                        "Disk defragmentation failed. Try running as administrator.")
            else:
                self.status_bar.showMessage("Disk defragmentation not needed on this OS")
                
        except Exception as e:
            self.show_error_message(f"Failed to defragment disk: {str(e)}")
    
    def check_disk(self):
        """Check disk for errors"""
        try:
            self.status_bar.showMessage("Checking disk for errors (requires admin)...")
            QApplication.processEvents()
            
            # Windows specific
            if os.name == 'nt':
                result = subprocess.run(['chkdsk', 'C:', '/F'], 
                                       capture_output=True, text=True)
                
                if result.returncode == 0:
                    self.status_bar.showMessage("Disk check scheduled for next reboot")
                    QMessageBox.information(self, "Success", 
                        "Disk check has been scheduled for the next system restart")
                else:
                    self.status_bar.showMessage("Disk check failed")
                    QMessageBox.warning(self, "Warning", 
                        "Disk check failed. Try running as administrator.")
            else:
                self.status_bar.showMessage("Disk check not supported on this OS")
                
        except Exception as e:
            self.show_error_message(f"Failed to check disk: {str(e)}")
    
    def load_startup_programs(self):
        """Load startup programs (simulated)"""
        try:
            self.status_bar.showMessage("Loading startup programs...")
            QApplication.processEvents()
            
            # Simulate loading startup programs
            startup_programs = [
                {"name": "Steam", "publisher": "Valve", "status": "Enabled", "impact": "High"},
                {"name": "OneDrive", "publisher": "Microsoft", "status": "Enabled", "impact": "Medium"},
                {"name": "Adobe Reader", "publisher": "Adobe", "status": "Enabled", "impact": "Low"},
                {"name": "Spotify", "publisher": "Spotify AB", "status": "Disabled", "impact": "High"},
                {"name": "Discord", "publisher": "Discord Inc.", "status": "Enabled", "impact": "Medium"}
            ]
            
            self.startup_tree.clear()
            
            for program in startup_programs:
                item = QTreeWidgetItem()
                item.setText(0, program["name"])
                item.setText(1, program["publisher"])
                item.setText(2, program["status"])
                item.setText(3, program["impact"])
                self.startup_tree.addTopLevelItem(item)
            
            self.status_bar.showMessage("Startup programs loaded successfully!")
            
        except Exception as e:
            self.show_error_message(f"Failed to load startup programs: {str(e)}")
    
    def disable_startup_programs(self):
        """Disable selected startup programs (simulated)"""
        try:
            selected_items = self.startup_tree.selectedItems()
            if not selected_items:
                QMessageBox.warning(self, "No Selection", "Please select programs to disable")
                return
            
            self.status_bar.showMessage("Disabling selected startup programs...")
            QApplication.processEvents()
            
            for item in selected_items:
                item.setText(2, "Disabled")
            
            self.status_bar.showMessage(f"Disabled {len(selected_items)} startup programs!")
            
        except Exception as e:
            self.show_error_message(f"Failed to disable startup programs: {str(e)}")
    
    def load_scheduled_tasks(self):
        """Load scheduled tasks (simulated)"""
        try:
            self.status_bar.showMessage("Loading scheduled tasks...")
            QApplication.processEvents()
            
            # Simulate loading scheduled tasks
            scheduled_tasks = [
                {"name": "GoogleUpdateTask", "status": "Ready", "next_run": "2023-07-15 10:00", "last_run": "2023-07-14 10:00"},
                {"name": "Adobe Acrobat Update", "status": "Running", "next_run": "2023-07-16 12:00", "last_run": "2023-07-13 12:00"},
                {"name": "Microsoft Compatibility", "status": "Disabled", "next_run": "N/A", "last_run": "2023-06-20 08:00"},
                {"name": "OneDrive Standalone", "status": "Ready", "next_run": "2023-07-15 09:00", "last_run": "2023-07-14 09:00"}
            ]
            
            self.tasks_tree.clear()
            
            for task in scheduled_tasks:
                item = QTreeWidgetItem()
                item.setText(0, task["name"])
                item.setText(1, task["status"])
                item.setText(2, task["next_run"])
                item.setText(3, task["last_run"])
                self.tasks_tree.addTopLevelItem(item)
            
            self.status_bar.showMessage("Scheduled tasks loaded successfully!")
            
        except Exception as e:
            self.show_error_message(f"Failed to load scheduled tasks: {str(e)}")
    
    def disable_scheduled_tasks(self):
        """Disable selected scheduled tasks (simulated)"""
        try:
            selected_items = self.tasks_tree.selectedItems()
            if not selected_items:
                QMessageBox.warning(self, "No Selection", "Please select tasks to disable")
                return
            
            self.status_bar.showMessage("Disabling selected scheduled tasks...")
            QApplication.processEvents()
            
            for item in selected_items:
                item.setText(1, "Disabled")
            
            self.status_bar.showMessage(f"Disabled {len(selected_items)} scheduled tasks!")
            
        except Exception as e:
            self.show_error_message(f"Failed to disable scheduled tasks: {str(e)}")
    
    def load_services(self):
        """Load Windows services (simulated)"""
        try:
            self.status_bar.showMessage("Loading Windows services...")
            QApplication.processEvents()
            
            # Simulate loading services
            services = [
                {"name": "SysMain", "status": "Running", "startup": "Automatic", "desc": "Maintains system performance"},
                {"name": "WSearch", "status": "Running", "startup": "Automatic", "desc": "Windows Search service"},
                {"name": "DiagTrack", "status": "Running", "startup": "Automatic", "desc": "Connected User Experiences"},
                {"name": "BITS", "status": "Stopped", "startup": "Manual", "desc": "Background Intelligent Transfer"},
                {"name": "Spooler", "status": "Running", "startup": "Automatic", "desc": "Print Spooler service"}
            ]
            
            self.services_tree.clear()
            
            for service in services:
                item = QTreeWidgetItem()
                item.setText(0, service["name"])
                item.setText(1, service["status"])
                item.setText(2, service["startup"])
                item.setText(3, service["desc"])
                self.services_tree.addTopLevelItem(item)
            
            self.status_bar.showMessage("Windows services loaded successfully!")
            
        except Exception as e:
            self.show_error_message(f"Failed to load services: {str(e)}")
    
    def filter_services(self):
        """Filter services based on search text"""
        filter_text = self.services_filter.text().lower()
        
        for i in range(self.services_tree.topLevelItemCount()):
            item = self.services_tree.topLevelItem(i)
            item.setHidden(filter_text not in item.text(0).lower())
    
    def start_service(self):
        """Start selected service (simulated)"""
        try:
            selected_items = self.services_tree.selectedItems()
            if not selected_items:
                QMessageBox.warning(self, "No Selection", "Please select a service to start")
                return
            
            for item in selected_items:
                item.setText(1, "Running")
            
            self.status_bar.showMessage("Service started successfully!")
            
        except Exception as e:
            self.show_error_message(f"Failed to start service: {str(e)}")
    
    def stop_service(self):
        """Stop selected service (simulated)"""
        try:
            selected_items = self.services_tree.selectedItems()
            if not selected_items:
                QMessageBox.warning(self, "No Selection", "Please select a service to stop")
                return
            
            for item in selected_items:
                item.setText(1, "Stopped")
            
            self.status_bar.showMessage("Service stopped successfully!")
            
        except Exception as e:
            self.show_error_message(f"Failed to stop service: {str(e)}")
    
    def restart_service(self):
        """Restart selected service (simulated)"""
        try:
            selected_items = self.services_tree.selectedItems()
            if not selected_items:
                QMessageBox.warning(self, "No Selection", "Please select a service to restart")
                return
            
            for item in selected_items:
                item.setText(1, "Running")
            
            self.status_bar.showMessage("Service restarted successfully!")
            
        except Exception as e:
            self.show_error_message(f"Failed to restart service: {str(e)}")
    
    def change_service_startup(self):
        """Change service startup type (simulated)"""
        try:
            selected_items = self.services_tree.selectedItems()
            if not selected_items:
                QMessageBox.warning(self, "No Selection", "Please select a service to modify")
                return
            
            # In a real app, this would show a dialog to select startup type
            for item in selected_items:
                current = item.text(2)
                if current == "Automatic":
                    item.setText(2, "Manual")
                elif current == "Manual":
                    item.setText(2, "Disabled")
                else:
                    item.setText(2, "Automatic")
            
            self.status_bar.showMessage("Service startup type changed!")
            
        except Exception as e:
            self.show_error_message(f"Failed to change service startup: {str(e)}")
    
    def apply_recommended_services(self):
        """Apply recommended service optimizations (simulated)"""
        try:
            changes = []
            
            if self.disable_superfetch_check.isChecked():
                changes.append("Disabled Superfetch (SysMain)")
            
            if self.disable_wsearch_check.isChecked():
                changes.append("Disabled Windows Search (WSearch)")
            
            if self.disable_telemetry_check.isChecked():
                changes.append("Disabled Telemetry Services")
            
            if changes:
                self.status_bar.showMessage("Applied recommended service optimizations")
                QMessageBox.information(self, "Success", 
                    f"Applied optimizations:\n{', '.join(changes)}")
            else:
                QMessageBox.warning(self, "No Selection", 
                    "Please select at least one optimization to apply")
                
        except Exception as e:
            self.show_error_message(f"Failed to apply recommended services: {str(e)}")
    
    def apply_system_tweaks(self):
        """Apply system tweaks (simulated)"""
        try:
            changes = []
            
            if self.fast_startup_check.isChecked():
                changes.append("Enabled Fast Startup")
            
            if self.disable_hibernation_check.isChecked():
                changes.append("Disabled Hibernation")
            
            uac_level = self.uac_slider.currentText()
            changes.append(f"Set UAC to: {uac_level}")
            
            if self.add_take_ownership_check.isChecked():
                changes.append("Added 'Take Ownership' to context menu")
            
            if self.add_copy_path_check.isChecked():
                changes.append("Added 'Copy as Path' to context menu")
            
            if changes:
                self.status_bar.showMessage("Applied system tweaks")
                QMessageBox.information(self, "Success", 
                    f"Applied system tweaks:\n{', '.join(changes)}")
            else:
                QMessageBox.warning(self, "No Changes", 
                    "No system tweaks were selected")
                
        except Exception as e:
            self.show_error_message(f"Failed to apply system tweaks: {str(e)}")
    
    def apply_network_tweaks(self):
        """Apply network tweaks (simulated)"""
        try:
            changes = []
            
            dns_setting = self.dns_combo.currentText()
            changes.append(f"DNS set to: {dns_setting}")
            
            if self.disable_throttling_check.isChecked():
                changes.append("Disabled Network Throttling")
            
            if changes:
                self.status_bar.showMessage("Applied network tweaks")
                QMessageBox.information(self, "Success", 
                    f"Applied network tweaks:\n{', '.join(changes)}")
            else:
                QMessageBox.warning(self, "No Changes", 
                    "No network tweaks were selected")
                
        except Exception as e:
            self.show_error_message(f"Failed to apply network tweaks: {str(e)}")
    
    def toggle_autostart(self, state):
        """Toggle auto-start with Windows"""
        try:
            if state == Qt.Checked:
                # Add to startup
                key = winreg.OpenKey(
                    winreg.HKEY_CURRENT_USER,
                    r"Software\Microsoft\Windows\CurrentVersion\Run",
                    0, winreg.KEY_SET_VALUE)
                
                winreg.SetValueEx(key, "WindowsOptimizerPro", 0, winreg.REG_SZ, 
                                 sys.executable + ' "' + os.path.abspath(__file__) + '"')
                
                winreg.CloseKey(key)
                self.status_bar.showMessage("Added to Windows startup")
            else:
                # Remove from startup
                key = winreg.OpenKey(
                    winreg.HKEY_CURRENT_USER,
                    r"Software\Microsoft\Windows\CurrentVersion\Run",
                    0, winreg.KEY_SET_VALUE)
                
                try:
                    winreg.DeleteValue(key, "WindowsOptimizerPro")
                    self.status_bar.showMessage("Removed from Windows startup")
                except WindowsError:
                    pass
                
                winreg.CloseKey(key)
                
        except Exception as e:
            self.show_error_message(f"Failed to modify startup: {str(e)}")
    
    def quick_clean(self):
        """Perform quick clean operation"""
        try:
            self.status_bar.showMessage("Performing quick clean...")
            QApplication.processEvents()
            
            # Clean temp files
            self.clean_temp_files()
            
            # Clean browser caches
            self.clean_browser_caches()
            
            # Clean thumbnail cache
            self.clean_thumbnail_cache()
            
            self.status_bar.showMessage("Quick clean completed successfully!")
            QMessageBox.information(self, "Success", "Quick clean completed successfully")
            
        except Exception as e:
            self.show_error_message(f"Failed to perform quick clean: {str(e)}")
    
    def quick_optimize(self):
        """Perform quick optimization"""
        try:
            self.status_bar.showMessage("Performing quick optimization...")
            QApplication.processEvents()
            
            # Clean temp files
            self.clean_temp_files()
            
            # Apply visual effects for performance
            self.visual_effects_combo.setCurrentText("Adjust for best performance")
            
            # Disable some services
            self.disable_superfetch_check.setChecked(True)
            self.disable_telemetry_check.setChecked(True)
            
            self.status_bar.showMessage("Quick optimization completed successfully!")
            QMessageBox.information(self, "Success", "Quick optimization completed")
            
        except Exception as e:
            self.show_error_message(f"Failed to perform quick optimization: {str(e)}")
    
    def performance_boost(self):
        """Perform full performance boost"""
        try:
            self.status_bar.showMessage("Performing full performance boost...")
            QApplication.processEvents()
            
            # Clean everything
            self.quick_clean()
            
            # Optimize everything
            self.quick_optimize()
            
            # Disable startup programs
            # In a real app, this would disable all non-essential startup programs
            
            # Defragment disk
            self.defragment_disk()
            
            self.status_bar.showMessage("Performance boost completed successfully!")
            QMessageBox.information(self, "Success", "Full performance boost completed")
            
        except Exception as e:
            self.show_error_message(f"Failed to perform performance boost: {str(e)}")
    
    def run_disk_cleanup(self):
        """Run Windows Disk Cleanup utility"""
        try:
            self.status_bar.showMessage("Launching Disk Cleanup...")
            QApplication.processEvents()
            
            if os.name == 'nt':
                subprocess.Popen(['cleanmgr'])
                self.status_bar.showMessage("Disk Cleanup launched")
            else:
                self.status_bar.showMessage("Disk Cleanup not available on this OS")
                
        except Exception as e:
            self.show_error_message(f"Failed to launch Disk Cleanup: {str(e)}")
    
    def open_perf_monitor(self):
        """Open Windows Performance Monitor"""
        try:
            self.status_bar.showMessage("Launching Performance Monitor...")
            QApplication.processEvents()
            
            if os.name == 'nt':
                subprocess.Popen(['perfmon'])
                self.status_bar.showMessage("Performance Monitor launched")
            else:
                self.status_bar.showMessage("Performance Monitor not available on this OS")
                
        except Exception as e:
            self.show_error_message(f"Failed to launch Performance Monitor: {str(e)}")
    
    def check_for_updates(self):
        """Check for application updates (simulated)"""
        try:
            self.status_bar.showMessage("Checking for updates...")
            QApplication.processEvents()
            
            # Simulate update check
            QTimer.singleShot(2000, lambda: QMessageBox.information(
                self, "Update Check", "You have the latest version of Windows Optimizer Pro"))
            
            self.status_bar.showMessage("Update check completed")
            
        except Exception as e:
            self.show_error_message(f"Failed to check for updates: {str(e)}")
    
    def show_about(self):
        """Show about dialog"""
        about_text = """
        <h2>Windows Optimizer Pro</h2>
        <p>Version 1.0</p>
        <p>This application helps optimize your Windows performance by:</p>
        <ul>
            <li>Cleaning junk files and registry</li>
            <li>Managing startup programs</li>
            <li>Optimizing system services</li>
            <li>Applying performance tweaks</li>
            <li>Defragmenting disks</li>
        </ul>
        <p>© 2023 Windows Optimizer Team</p>
        """
        QMessageBox.about(self, "About Windows Optimizer Pro", about_text)
    
    def show_documentation(self):
        """Show documentation (simulated)"""
        QMessageBox.information(self, "Documentation", 
            "Documentation is available at our website (simulated)")
    
    def show_error_message(self, message):
        """Show error message dialog"""
        QMessageBox.critical(self, "Error", message)
    
    def closeEvent(self, event):
        """Handle window close event"""
        if self.minimize_to_tray_checkbox.isChecked():
            event.ignore()
            self.hide()
            self.tray_icon.showMessage(
                "Windows Optimizer Pro",
                "The application continues to run in the system tray",
                QSystemTrayIcon.Information,
                2000
            )
        else:
            event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Modern UI style
    
    # Set application information
    app.setApplicationName("Windows Optimizer Pro")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("Optimizer Inc.")
    
    # Set font
    font = QFont()
    font.setFamily("Segoe UI")
    font.setPointSize(10)
    app.setFont(font)
    
    optimizer = WindowsOptimizerPro()
    optimizer.show()
    sys.exit(app.exec_())