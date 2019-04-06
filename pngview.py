from PyQt5.QtCore import QFile
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QGraphicsView, QWidget, QGraphicsScene, QLabel, QGraphicsPixmapItem, QGraphicsItem


class PngView(QGraphicsView):
    def __init__(self, parent=None):
        super(PngView, self).__init__(parent)
        self.file_name = None
        self.setViewport(QWidget())
        self.setScene(QGraphicsScene(self))
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)

    def open_file(self, filename):
        png_file = QFile(filename)

        if not png_file.exists():
            return

        self.file_name = png_file
        self.resetTransform()
        self.scale(2.0, 2.0)

        pixmap = QPixmap(png_file.fileName())
        png_item = QGraphicsPixmapItem(pixmap)
        png_item.setFlags(QGraphicsItem.ItemClipsToShape)
        png_item.setCacheMode(QGraphicsItem.NoCache)
        png_item.setZValue(0)

        s = self.scene()
        s.clear()
        s.addItem(png_item)

    def wheelEvent(self, event) -> None:
        factor = pow(1.2, event.angleDelta().y() / 240.0)
        self.scale(factor, factor)
        event.accept()


if __name__ == '__main__':
    from PyQt5.QtWidgets import QMainWindow, QSizePolicy, QApplication
    import sys

    class MainWindow(QMainWindow):
        def __init__(self):
            super(MainWindow, self).__init__()
            self.rootView = PngView()
            self.rootView.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
            self.setCentralWidget(self.rootView)

        def open_file(self, path=None):
            self.rootView.open_file(path)

    app = QApplication(sys.argv)
    window = MainWindow()
    window.open_file('./test.png')
    window.show()
    sys.exit(app.exec_())
