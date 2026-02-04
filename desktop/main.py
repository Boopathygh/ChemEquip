import sys
import requests
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                             QMessageBox, QFileDialog, QTabWidget, QTableWidget, 
                             QTableWidgetItem, QListWidget)
from PyQt5.QtCore import Qt

API_URL = "http://localhost:8000/api"

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ChemEquip - Login")
        self.setGeometry(300, 300, 300, 200)
        self.setStyleSheet("background-color: #f4f6f7;")
        
        layout = QVBoxLayout()
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        
        btn_login = QPushButton("Login")
        btn_login.setStyleSheet("background-color: #2ecc71; color: white; padding: 5px;")
        btn_login.clicked.connect(self.handle_login)
        
        layout.addWidget(QLabel("ChemEquip Desktop"))
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_input)
        layout.addWidget(btn_login)
        
        self.setLayout(layout)

    def handle_login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        
        # Verify creds with backend
        try:
            auth = requests.auth.HTTPBasicAuth(username, password)
            response = requests.get(f"{API_URL}/history/", auth=auth)
            
            if response.status_code == 200:
                self.main_window = MainWindow(auth)
                self.main_window.show()
                self.close()
            else:
                QMessageBox.warning(self, "Error", "Invalid Credentials")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Connection failed: {str(e)}")

class MainWindow(QMainWindow):
    def __init__(self, auth):
        super().__init__()
        self.auth = auth
        self.setWindowTitle("ChemEquip - Dashboard")
        self.setGeometry(100, 100, 1000, 600)
        
        # Main Layout
        central_widget = QWidget()
        main_layout = QHBoxLayout(central_widget)
        self.setCentralWidget(central_widget)
        
        # Sidebar
        sidebar_layout = QVBoxLayout()
        self.history_list = QListWidget()
        self.history_list.itemClicked.connect(self.load_history_item)
        sidebar_layout.addWidget(QLabel("History (Last 5)"))
        sidebar_layout.addWidget(self.history_list)
        
        btn_upload = QPushButton("Upload New CSV")
        btn_upload.setStyleSheet("background-color: #3498db; color: white; padding: 10px;")
        btn_upload.clicked.connect(self.upload_file)
        sidebar_layout.addWidget(btn_upload)
        
        main_layout.addLayout(sidebar_layout, 1)
        
        # Main Content Area
        self.tabs = QTabWidget()
        self.summary_tab = QWidget()
        self.data_tab = QWidget()
        
        self.tabs.addTab(self.summary_tab, "Summary & Charts")
        self.tabs.addTab(self.data_tab, "Raw Data")
        
        main_layout.addWidget(self.tabs, 3)
        
        # Init Summary Tab
        self.setup_summary_tab()
        
        # Init Data Tab
        self.setup_data_tab()
        
        self.refresh_history()

    def setup_summary_tab(self):
        layout = QVBoxLayout()
        self.lbl_stats = QLabel("Select a file to view stats")
        layout.addWidget(self.lbl_stats)
        
        # Matplotlib Figure
        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        
        self.summary_tab.setLayout(layout)

    def setup_data_tab(self):
        layout = QVBoxLayout()
        self.table = QTableWidget()
        layout.addWidget(self.table)
        self.data_tab.setLayout(layout)

    def refresh_history(self):
        try:
            response = requests.get(f"{API_URL}/history/", auth=self.auth)
            if response.status_code == 200:
                self.history_list.clear()
                self.history_data = response.json()
                for item in self.history_data:
                    self.history_list.addItem(f"{item['filename']} ({item['uploaded_at'][:10]})")
        except Exception as e:
            print(f"Error fetching history: {e}")

    def upload_file(self):
        fname, _ = QFileDialog.getOpenFileName(self, 'Open CSV', 'c:\\', "CSV Files (*.csv)")
        if fname:
            try:
                files = {'file': open(fname, 'rb')}
                response = requests.post(f"{API_URL}/upload/", files=files, auth=self.auth)
                if response.status_code == 201:
                    QMessageBox.information(self, "Success", "File uploaded successfully")
                    self.refresh_history()
                    # Automatically select the new item? Or just refresh
                    # Ideally we reload the analysis view with response data
                    data = response.json()
                    self.display_summary(data['summary_data'])
                    self.load_data_table(data['id'])
                else:
                    QMessageBox.warning(self, "Error", f"Upload failed: {response.text}")
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def load_history_item(self, item):
        index = self.history_list.row(item)
        data = self.history_data[index]
        self.display_summary(data['summary_data'])
        self.load_data_table(data['id'])

    def display_summary(self, summary):
        if not summary:
            return
            
        text = f"Total Count: {summary['total_count']}\n"
        text += f"Avg Flowrate: {summary['averages']['Flowrate']:.2f}\n"
        text += f"Avg Pressure: {summary['averages']['Pressure']:.2f}\n"
        text += f"Avg Tempoerature: {summary['averages']['Temperature']:.2f}"
        self.lbl_stats.setText(text)
        
        # Update Chart
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        types = list(summary['type_distribution'].keys())
        counts = list(summary['type_distribution'].values())
        
        ax.bar(types, counts, color=['#2ecc71', '#3498db', '#9b59b6', '#f1c40f'])
        ax.set_title("Equipment Type Distribution")
        
        self.canvas.draw()

    def load_data_table(self, file_id):
        try:
            response = requests.get(f"{API_URL}/data/{file_id}/", auth=self.auth)
            if response.status_code == 200:
                data = response.json()
                if not data: return
                
                rows = len(data)
                cols = len(data[0])
                keys = list(data[0].keys())
                
                self.table.setRowCount(rows)
                self.table.setColumnCount(cols)
                self.table.setHorizontalHeaderLabels(keys)
                
                for i, row in enumerate(data):
                    for j, key in enumerate(keys):
                        self.table.setItem(i, j, QTableWidgetItem(str(row[key])))
        except Exception as e:
            print(f"Error loading data: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Global Style
    app.setStyleSheet("""
        QMainWindow { background-color: white; }
        QLabel { font-size: 14px; }
    """)
    
    login = LoginWindow()
    login.show()
    sys.exit(app.exec_())
