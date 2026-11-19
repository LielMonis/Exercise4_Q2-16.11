import sys
import os
import numpy as np

from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QPushButton,
                               QVBoxLayout, QHBoxLayout, QFileDialog)

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

        # Buttons
        self.load_button = QPushButton('Load File')
        self.load_button.clicked.connect(self.load_file)

        self.about_button = QPushButton('About')
        self.about_button.clicked.connect(self.open_about)

        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.load_button)
        buttons_layout.addWidget(self.about_button)

        # Matplotlib graph + toolbar (zoom, pan, save as image)
        self.figure = Figure()
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.toolbar = MyToolbar(self.canvas, self)

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.addLayout(buttons_layout)
        main_layout.addWidget(self.toolbar)
        main_layout.addWidget(self.canvas)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        self.temps = []     #רשימת הטמפרטורות השונות
        self.revs = []      #רשימת הרווחים השונים

        self.draw_graph()


    def load_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, 'Open CSV File', '', 'CSV Files (*.csv)')
        if file_name == '':
            return  # the user pressed Cancel
        
        with open(file_name, 'r') as f:
            next(f)             #מקדם אותנו שורה- קופץ מעל שורה אחת.
            self.temps = []         #שורות אלה יבטיחו כי הרשימות יתקרוקנו מהתוכן במצב של העלאת מספר קבצים אחד אחרי השני
            self.revs = []
            for line in f:
                parts = line.split(',')
                self.temps.append(float(parts[0]))         #הפיכה ממחרוזת של מספר *לא שלם* למספר לא שלם כערך
                self.revs.append(int(parts[1]))     #למרות שברכיב זה מופיעה פקודת ירידת השורה, ההגדרה כמספר שלם תמשוך רק את המספר

        short_name = os.path.basename(file_name)                    # Only the file name, without the folders before it
        self.setWindowTitle(f'Ice Cream Sales - {short_name}')

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
            x_line = np.array([min(self.temps), max(self.temps)])   #הקו מוגדר ע"י שני ערכים- התחלתי וסופי. מתוך רשימת ערכי הציר האופקי יחולצו הערכים המינ' ומקס.     
            y_line = m * x_line + b                                 #הפעולת הכפלה ומציאת התמונה מבוצעת על שתי הנקודות בעת אחת
            ax.plot(x_line, y_line, color='red', linewidth=2,
                    label=f'y = {m:.2f}x + {b:.2f}')
            ax.legend()

        self.canvas.draw()

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