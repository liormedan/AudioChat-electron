from PyQt6.QtWidgets import QWidget, QStackedLayout, QLabel

class ContentArea(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QStackedLayout(self)

        self.pages = {
            "Home": QLabel("Welcome to Audio Chat!"),
            "Audio Editor": QLabel("Audio Editor Page"),
            "Audio AI": QLabel("Audio AI Page"),
        }

        for page in self.pages.values():
            self.layout.addWidget(page)

        self.show_page("Home")

    def show_page(self, name):
        widget = self.pages.get(name)
        if widget:
            self.layout.setCurrentWidget(widget)
