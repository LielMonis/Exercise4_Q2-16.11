from PySide6.QtWidgets import QApplication, QWidget, QLabel
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt

class About_window (QWidget):

    def __init__(self):
        super().__init__()
        self.setWindowTitle('About Me')
        self.setGeometry(200,200,400,500)
        self.setStyleSheet('background-color : lightblue')

        self.name = QLabel("Liel Monis", self)
        self.name.setGeometry(135,10,200,30)
        self.name.setStyleSheet('font-size : 30px ; color : darkblue ; font-weight : bold')

        self.my_picture = QLabel(self)
        self.my_picture.setGeometry(50,60,300,300)

        image = QPixmap('liel_picture.jpg').scaled(300,300, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.my_picture.setPixmap(image)

        self.email = QLabel('My Email address is: lielmonis9@gmail.com', self)
        self.email.setGeometry(10,400,400,30)
        self.email.setStyleSheet('font-size : 20px ; color : darkblue')

        self.linkedin = QLabel('<a href="https://www.linkedin.com/in/liel-monis-4784043a6/?lipi=urn%3Ali%3Apage%3Ad_flagship3_profile_view_base_contact_details%3BaesurkA9QfaJFyu3eOxL7A%3D%3D">To my LinkedIn profile</a>', self)
        self.linkedin.setOpenExternalLinks(True)
        self.linkedin.setGeometry(10,430,400,30)
        self.linkedin.setStyleSheet('font-size : 20px ; color : darkblue')

        self.github = QLabel('<a href="https://github.com/LielMonis/Exercise4_Q2-16.11.git">To the project page</a>', self)
        self.github.setOpenExternalLinks(True)
        self.github.setGeometry(10,460,400,30)
        self.github.setStyleSheet('font-size : 20px ; color : darkblue')

if __name__ == '__main__':
    app = QApplication()
    window = About_window()
    window.show()
    app.exec()