import sys
import os
import numpy as np

from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QPushButton,QVBoxLayout, QHBoxLayout, QFileDialog,QCheckBox, QLabel, QLineEdit)
from PySide6.QtGui import QIcon

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg, NavigationToolbar2QT
from matplotlib.figure import Figure

from About import About_window

class MyToolbar(NavigationToolbar2QT):
    # Keep only the buttons we need (None = a separator line between groups)
    toolitems = [
        ('Home', 'Reset original view', 'home', 'home'),
        ('Back', 'Back to previous view', 'back', 'back'),
        ('Forward', 'Forward to next view', 'forward', 'forward'),
        (None, None, None, None),
        ('Pan', 'Left button pans, Right button zooms', 'move', 'pan'),
        ('Zoom', 'Zoom to rectangle', 'zoom_to_rect', 'zoom'),
        (None, None, None, None),
        ('Save', 'Save the figure', 'filesave', 'save_figure'),
    ]

class IceCreamWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle('Ice Cream Sales')
        self.setGeometry(100, 100, 900, 650)
        self.setWindowIcon(QIcon('icon.png'))           # The small picture in the title bar and taskbar

        # Buttons
        self.load_button = QPushButton('Load File')
        self.load_button.clicked.connect(self.load_file)

        self.clear_button = QPushButton('Clear')
        self.clear_button.clicked.connect(self.clear)

        self.about_button = QPushButton('About')
        self.about_button.clicked.connect(self.open_about)

        # Checkbox to show / hide the trend line
        self.trend_checkbox = QCheckBox('Show trend line')
        self.trend_checkbox.setChecked(True)                        # Shown by default
        self.trend_checkbox.stateChanged.connect(self.draw_graph)   # Redraw every time it is clicked

        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.load_button)
        buttons_layout.addWidget(self.clear_button)
        buttons_layout.addWidget(self.about_button)
        buttons_layout.addWidget(self.trend_checkbox)

        # Matplotlib graph + toolbar (zoom, pan, save as image)
        self.figure = Figure()
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.toolbar = MyToolbar(self.canvas, self)

        # Revenue predictor (under the graph)
        self.temp_label = QLabel('Temperature [°C]:')
        self.temp_input = QLineEdit()
        self.temp_input.setPlaceholderText('for example 25')
        self.temp_input.returnPressed.connect(self.predict)     # Pressing Enter also predicts

        self.predict_button = QPushButton('Predict')
        self.predict_button.clicked.connect(self.predict)

        self.result_label = QLabel('')

        predict_layout = QHBoxLayout()
        predict_layout.addWidget(self.temp_label)
        predict_layout.addWidget(self.temp_input)
        predict_layout.addWidget(self.predict_button)
        predict_layout.addWidget(self.result_label)
        predict_layout.addStretch()                     # Pushes everything to the left

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.addLayout(buttons_layout)
        main_layout.addWidget(self.toolbar)
        main_layout.addWidget(self.canvas)
        main_layout.addLayout(predict_layout)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # Status bar at the bottom of the window
        self.statusBar().showMessage('No file loaded')

        self.temps = []     #רשימת הטמפרטורות השונות
        self.revs = []      #רשימת הרווחים השונים

        self.m = None       # Slope of the trend line (None = no file loaded yet)
        self.b = None       # Intercept of the trend line

        self.draw_graph()


    def load_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, 'Open CSV File', '', 'CSV Files (*.csv)')
        if file_name == '':
            return  # the user pressed Cancel
        
        with open(file_name, 'r') as f:
            next(f)                 #מקדם אותנו שורה- קופץ מעל שורה אחת.
            self.temps = []         #שורות אלה יבטיחו כי הרשימות יתקרוקנו מהתוכן במצב של העלאת מספר קבצים אחד אחרי השני
            self.revs = []
            for line in f:
                parts = line.split(',')
                self.temps.append(float(parts[0]))         #הפיכה ממחרוזת של מספר *לא שלם* למספר לא שלם כערך
                self.revs.append(int(parts[1]))     #למרות שברכיב זה מופיעה פקודת ירידת השורה, ההגדרה כמספר שלם תמשוך רק את המספר

        short_name = os.path.basename(file_name)                    # Only the file name, without the folders before it
        self.setWindowTitle(f'Ice Cream Sales - {short_name}')
        self.statusBar().showMessage(f'{len(self.temps)} points loaded')

        self.result_label.setText('')       # Clear the old prediction - it belonged to the old file
        self.draw_graph()

    def draw_graph(self):
        self.figure.clear()
        ax = self.figure.add_subplot()
        ax.scatter(self.temps,self.revs,s=1)        #הנתונים נלקחים מרשימת הטמפ ורשימת הרווחים וכך נוצר תרשים עם נקודות בגודל 1 (כנדרש) 

        ax.spines['top'].set_visible(False)         #מוחק את המסגרת העליונה של הגרף
        ax.spines['right'].set_visible(False)       #מוחק את המסגרת הימנית של הגרף

        ax.set_title('Ice Cream Revenues per Temperature in USA')
        ax.set_xlabel('Temperature [°C]')
        ax.set_ylabel('Revenues [$]')

        if len(self.temps) > 0:                                     #כשהחלון נפתח והרשימות ריקות, לא יצוייר גרף לינארי
            m , b = np.polyfit(self.temps,self.revs,1)              #ערכי האיקס וה-וואי. 1 לצורך יצירת קו ישר. הפעלת הפונקציה מספקת שני ערכים- הראשון שיפוע והשני חיתוך עם ציר וואי
            self.m = m          # Saved so predict() can use them too
            self.b = b

            if self.trend_checkbox.isChecked():                     # Draw the line only if the checkbox is checked
                x_line = np.array([min(self.temps), max(self.temps)])   #הקו מוגדר ע"י שני ערכים- התחלתי וסופי. מתוך רשימת ערכי הציר האופקי יחולצו הערכים המינ' ומקס.
                y_line = m * x_line + b                                 #הפעולת הכפלה ומציאת התמונה מבוצעת על שתי הנקודות בעת אחת
                ax.plot(x_line, y_line, color='red', linewidth=2,
                        label=f'y = {m:.2f}x + {b:.2f}')
                ax.legend()

        self.canvas.draw()

    def predict(self):
        if self.m is None:
            self.result_label.setText('Load a file first')
            return

        try:
            temp = float(self.temp_input.text())
        except ValueError:
            self.result_label.setText('Please enter a number')
            return

        revenue = self.m * temp + self.b                # The trend line formula: y = m*x + b
        self.result_label.setText(f'Predicted revenue: ${revenue:.2f}')

    def clear(self):
        # Go back to how the window looked when the app started
        self.temps = []
        self.revs = []
        self.m = None
        self.b = None

        self.temp_input.setText('')
        self.result_label.setText('')
        self.setWindowTitle('Ice Cream Sales')
        self.statusBar().showMessage('No file loaded')

        self.draw_graph()       # Draws the empty graph

    def open_about(self):
        self.about_window = About_window()
        self.about_window.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Load the style file
    with open('style.qss', 'r') as file:
        app.setStyleSheet(file.read())

    window = IceCreamWindow()
    window.show()
    app.exec()