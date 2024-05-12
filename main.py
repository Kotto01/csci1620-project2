import sys
from PyQt6 import QtWidgets
from logic import ContactBook


def main():
    """The beginning of it all, the main loop"""
    app = QtWidgets.QApplication(sys.argv)
    contactBook = ContactBook()
    contactBook.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
