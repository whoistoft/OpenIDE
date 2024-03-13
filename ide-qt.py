import sys
import os
import time
os.system('pip install PyQt5')
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QTextCursor, QTextCharFormat, QColor, QKeySequence, QFont
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPlainTextEdit, QAction, QVBoxLayout, QWidget, QPushButton, QLabel,
    QFileDialog, QMenu, QActionGroup, QMenuBar, QTextBrowser, QMessageBox, QSplitter, QTextEdit
)
os.system('clear')
print("""   ___                           ___   ____    _____ 
  / _ \   _ __     ___   _ __   |_ _| |  _ \  | ____|
 | | | | | '_ \   / _ \ | '_ \   | |  | | | | |  _|  
 | |_| | | |_) | |  __/ | | | |  | |  | |_| | | |___ 
  \___/  | .__/   \___| |_| |_| |___| |____/  |_____|
         |_|                                         """)
time.sleep(0.8)
print('This is the console. If you close this, it will also close the main window!')
time.sleep(1)
class CodeWorker(QThread):
    signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()

    def run(self):
        code = code_editor.toPlainText()
        sys.stdout = self
        try:
            exec(code)
        except Exception as e:
            sys.stdout = sys.__stdout__
            self.signal.emit(str(e))
        else:
            sys.stdout = sys.__stdout__

    def write(self, text):
        self.signal.emit(text)


class CodeEditor(QPlainTextEdit):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        font = QFont()
        font.setFamily("Courier New")
        font.setPointSize(10)
        self.setFont(font)
        self.setStyleSheet("background-color: #212121; color: white;")
        self.setTabStopWidth(40)
        self.textChanged.connect(self.clearOutput)
        self.worker = CodeWorker()
        self.worker.signal.connect(self.handleCodeExecutionResult)

    def clearOutput(self):
        output_widget.clear()

    def handleCodeExecutionResult(self, text):
        output_widget.append(text)


class OutputWidget(QTextBrowser):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        font = QFont()
        font.setFamily("Courier New")
        font.setPointSize(10)
        self.setFont(font)
        self.setStyleSheet("background-color: #212121; color: white;")


class HistoryWindow(QWidget):
    def __init__(self, history_text):
        super().__init__()
        self.initUI(history_text)

    def initUI(self, history_text):
        self.setGeometry(200, 200, 400, 400)
        self.setWindowTitle("History")

        layout = QVBoxLayout()

        self.history_text = QTextEdit()
        self.history_text.setReadOnly(True)

        layout.addWidget(self.history_text)

        self.setLayout(layout)

        # Load and display history
        self.history_text.setPlainText(history_text)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setGeometry(100, 100, 600, 800)
        self.setWindowTitle("Python IDE")

        menubar = self.menuBar()
        menubar.setStyleSheet("background-color: #2c2d2e; color: white;")

        file_menu = menubar.addMenu("File")
        run_menu = menubar.addMenu("Run")
        history_menu = menubar.addMenu("History")

        # File menu actions
        open_action = QAction("Open", self)
        open_action.setShortcut(QKeySequence.Open)
        open_action.triggered.connect(self.openFile)
        file_menu.addAction(open_action)

        save_action = QAction("Save", self)
        save_action.setShortcut(QKeySequence.Save)
        save_action.triggered.connect(self.saveFile)
        file_menu.addAction(save_action)

        exit_action = QAction("Exit", self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Run menu actions
        run_action = QAction("Run", self)
        run_action.setShortcut(QKeySequence("Ctrl+R"))
        run_action.triggered.connect(self.runCode)
        run_menu.addAction(run_action)

        # History menu action to open history window
        history_action = QAction("Show History", self)
        history_action.triggered.connect(self.showHistory)
        history_menu.addAction(history_action)

        # Create a splitter widget for code editor and output
        splitter = QSplitter(Qt.Horizontal)

        global code_editor
        code_editor = CodeEditor()

        global output_widget
        output_widget = OutputWidget()

        splitter.addWidget(code_editor)
        splitter.addWidget(output_widget)

        self.setCentralWidget(splitter)

        # Set the filename label in the middle of the menu bar
        self.filename_label = QLabel()
        menubar.setCornerWidget(self.filename_label, Qt.TopRightCorner)

        self.show()

        # Create or clear the "temp.py" file and open it
        self.createOrClearTempFile()
        self.openTempFile()

    def createOrClearTempFile(self):
        data_dir = "data"
        temp_file_path = os.path.join(data_dir, "temp.py")

        if not os.path.exists(data_dir):
            os.makedirs(data_dir)

        with open(temp_file_path, "w") as temp_file:
            temp_file.write("")  # Clear the file content

    def openTempFile(self):
        data_dir = "data"
        temp_file_path = os.path.join(data_dir, "temp.py")

        if os.path.exists(temp_file_path):
            with open(temp_file_path, "r") as file:
                code_editor.setPlainText(file.read())
                code_editor.document().setModified(False)
                self.setWindowTitle("OpenIDE - Temporary File")
                self.filename_label.setText("Temporary File")

    def openFile(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_name, _ = QFileDialog.getOpenFileName(self, "Open File", "", "Python Files (*.py);;All Files (*)", options=options)
        if file_name:
            with open(file_name, "r") as file:
                code_editor.setPlainText(file.read())
                code_editor.document().setModified(False)
                self.setWindowTitle(f"OpenIDE - {file_name}")

            # Update the history file
            self.updateHistory(file_name)

            # Update the filename label
            if file_name == os.path.join("data", "temp.py"):
                self.filename_label.setText("Temporary File")
            else:
                self.filename_label.setText(os.path.basename(file_name))

    def updateHistory(self, file_name):
        data_dir = "data"
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)

        history_file = os.path.join(data_dir, "history.txt")

        with open(history_file, "a") as history:
            history.write(file_name + "\n")

    def saveFile(self):
        pass

    def runCode(self):
        code_editor.worker.start()

    def showHistory(self):
        data_dir = "data"
        history_file = os.path.join(data_dir, "history.txt")

        history_text = ""
        if os.path.exists(history_file):
            with open(history_file, "r") as history:
                history_text = history.read()

        history_window = HistoryWindow(history_text)
        history_window.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    sys.exit(app.exec_())
