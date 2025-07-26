import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QComboBox, QDateEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox, QFrame
)
from PySide6.QtSql import QSqlDatabase, QSqlQuery
from PySide6.QtCore import QDate, Qt, QRegularExpression
from PySide6.QtGui import QRegularExpressionValidator, QColor


class ExpenseApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_database()
        self.init_ui()
        self.load_table()
        self.update_total()

    def setup_database(self):
        """Initialize database connection and create tables if needed"""
        self.db = QSqlDatabase.addDatabase("QSQLITE")
        self.db.setDatabaseName("expense.db")
        
        if not self.db.open():
            QMessageBox.critical(None, "Database Error", "Could not open database.")
            sys.exit(1)

        query = QSqlQuery()
        query.exec("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                category TEXT NOT NULL,
                amount REAL NOT NULL CHECK(amount > 0),
                description TEXT NOT NULL
            )
        """)

    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Expense Tracker 2.0")
        self.resize(800, 600)
        self.setup_styles()
        self.create_widgets()
        self.setup_layouts()
        self.setup_connections()

    def setup_styles(self):
        """Configure application styles"""
        self.setStyleSheet("""
            QWidget {
                font-family: 'Segoe UI';
                font-size: 14px;
            }
            QPushButton {
                padding: 8px;
                border-radius: 6px;
                min-width: 80px;
            }
            QPushButton#addButton {
                background-color: #4CAF50;
                color: white;
            }
            QPushButton#addButton:hover {
                background-color: #45a049;
            }
            QPushButton#clearButton {
                background-color: #f44336;
                color: white;
            }
            QPushButton#clearButton:hover {
                background-color: #d32f2f;
            }
            QPushButton#deleteButton {
                background-color: #607d8b;
                color: white;
            }
            QPushButton#deleteButton:hover {
                background-color: #455a64;
            }
            QLineEdit, QComboBox, QDateEdit {
                padding: 5px;
                border: 1px solid #ccc;
                border-radius: 4px;
            }
            QTableWidget {
                border: 1px solid #ccc;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QTableWidget::item:selected {
                background-color: #2196F3;
                color: white;
            }
            QHeaderView::section {
                background-color: #f0f0f0;
                padding: 5px;
                border: none;
            }
            QLabel#totalLabel {
                font-weight: bold;
                font-size: 16px;
                color: #333;
                padding: 5px;
                background-color: #e8f5e9;
                border-radius: 4px;
            }
        """)

    def create_widgets(self):
        """Create all UI widgets"""
        # Date input
        self.date_box = QDateEdit()
        self.date_box.setDate(QDate.currentDate())
        self.date_box.setCalendarPopup(True)
        self.date_box.setMaximumDate(QDate.currentDate())

        # Category dropdown
        self.category_dropdown = QComboBox()
        self.category_dropdown.addItems(["Food", "Transport", "Bills", "Shopping", "Entertainment", "Healthcare", "Others"])
        
        # Amount input with validation
        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("0.00")
        amount_validator = QRegularExpressionValidator(QRegularExpression(r'^\d+\.?\d{0,2}$'))
        self.amount_input.setValidator(amount_validator)

        # Description input
        self.description_input = QLineEdit()
        self.description_input.setPlaceholderText("Expense details")

        # Buttons
        self.add_button = QPushButton("Add Expense")
        self.add_button.setObjectName("addButton")
        
        self.clear_button = QPushButton("Clear")
        self.clear_button.setObjectName("clearButton")
        
        self.delete_button = QPushButton("Delete")
        self.delete_button.setObjectName("deleteButton")

        # Table widget with improved selection visibility
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setHorizontalHeaderLabels(["ID", "Date", "Category", "Amount", "Description"])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)

        # Total label
        self.total_label = QLabel("Total: ₹0.00")
        self.total_label.setObjectName("totalLabel")
        self.total_label.setAlignment(Qt.AlignRight)

    def setup_layouts(self):
        """Set up the application layout"""
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # Input rows
        input_layout = QVBoxLayout()
        input_layout.setSpacing(10)

        row1 = QHBoxLayout()
        row1.addWidget(QLabel("Date:"), stretch=1)
        row1.addWidget(self.date_box, stretch=3)
        row1.addWidget(QLabel("Category:"), stretch=1)
        row1.addWidget(self.category_dropdown, stretch=3)

        row2 = QHBoxLayout()
        row2.addWidget(QLabel("Amount (₹):"), stretch=1)
        row2.addWidget(self.amount_input, stretch=3)
        row2.addWidget(QLabel("Description:"), stretch=1)
        row2.addWidget(self.description_input, stretch=3)

        input_layout.addLayout(row1)
        input_layout.addLayout(row2)

        # Button row
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.clear_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addStretch()

        # Add to main layout
        main_layout.addLayout(input_layout)
        main_layout.addLayout(button_layout)

        # Separator line
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(line)

        # Table and total
        main_layout.addWidget(self.table)
        main_layout.addWidget(self.total_label)

        self.setLayout(main_layout)

    def setup_connections(self):
        """Connect signals to slots"""
        self.add_button.clicked.connect(self.add_expense)
        self.clear_button.clicked.connect(self.clear_inputs)
        self.delete_button.clicked.connect(self.delete_expense)
        self.amount_input.returnPressed.connect(self.add_expense)
        self.description_input.returnPressed.connect(self.add_expense)

    def clear_inputs(self):
        """Reset all input fields to default values"""
        self.amount_input.clear()
        self.description_input.clear()
        self.category_dropdown.setCurrentIndex(0)
        self.date_box.setDate(QDate.currentDate())
        self.amount_input.setFocus()

    def update_total(self):
        """Calculate and display the total of all expenses"""
        total = 0.0
        query = QSqlQuery("SELECT SUM(amount) FROM expenses")
        if query.next():
            total = query.value(0) or 0.0
        
        self.total_label.setText(f"Total: ₹{total:,.2f}")

    def load_table(self):
        """Load all expenses from database into the table"""
        self.table.setRowCount(0)
        
        query = QSqlQuery("""
            SELECT id, date, category, amount, description 
            FROM expenses 
            ORDER BY date DESC
        """)
        
        while query.next():
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            for col in range(5):
                value = query.value(col)
                item = QTableWidgetItem(str(value))
                
                if col == 3:
                    item.setText(f"₹{float(value):,.2f}")
                    item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                
                self.table.setItem(row, col, item)

        self.table.resizeColumnsToContents()
        self.table.setColumnWidth(3, 120)

    def add_expense(self):
        """Add a new expense to the database"""
        date = self.date_box.date().toString("yyyy-MM-dd")
        category = self.category_dropdown.currentText()
        amount_text = self.amount_input.text().strip()
        description = self.description_input.text().strip()

        if not amount_text:
            QMessageBox.warning(self, "Input Error", "Please enter an amount.")
            self.amount_input.setFocus()
            return
            
        if not description:
            QMessageBox.warning(self, "Input Error", "Please enter a description.")
            self.description_input.setFocus()
            return

        try:
            amount = float(amount_text)
            if amount <= 0:
                raise ValueError
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Amount must be a positive number.")
            self.amount_input.selectAll()
            self.amount_input.setFocus()
            return

        query = QSqlQuery()
        query.prepare("""
            INSERT INTO expenses (date, category, amount, description) 
            VALUES (?, ?, ?, ?)
        """)
        query.addBindValue(date)
        query.addBindValue(category)
        query.addBindValue(amount)
        query.addBindValue(description)

        if not query.exec():
            QMessageBox.critical(self, "Database Error", 
                               f"Failed to add expense:\n{query.lastError().text()}")
        else:
            self.clear_inputs()
            self.load_table()
            self.update_total()

    def delete_expense(self):
        """Delete the selected expense from the database"""
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Delete Error", "Please select an expense to delete.")
            return

        row = selected_rows[0].row()
        expense_id = self.table.item(row, 0).text()
        amount = self.table.item(row, 3).text()
        description = self.table.item(row, 4).text()

        confirm = QMessageBox.question(
            self, "Confirm Delete",
            f"Delete this expense?\n\n"
            f"Amount: {amount}\n"
            f"Description: {description}",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirm == QMessageBox.Yes:
            query = QSqlQuery()
            query.prepare("DELETE FROM expenses WHERE id = ?")
            query.addBindValue(expense_id)

            if not query.exec():
                QMessageBox.critical(self, "Database Error", 
                                   f"Failed to delete expense:\n{query.lastError().text()}")
            else:
                self.load_table()
                self.update_total()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = ExpenseApp()
    window.show()
    sys.exit(app.exec())