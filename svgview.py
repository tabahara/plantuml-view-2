from PyQt5.QtCore import Qt, QFile
from PyQt5.QtGui import QBrush, QPixmap, QPainter, QColor
from PyQt5.QtSvg import QGraphicsSvgItem
from PyQt5.QtWidgets import QMainWindow, QGraphicsView, QGraphicsScene, QGraphicsItem, QWidget, QApplication, QMenu, \
    QSizePolicy


class SvgView(QGraphicsView):
    def __init__(self, parent=None):
        super(SvgView, self).__init__(parent)
        self.file_name = None
        self.setViewport(QWidget())
        self.setScene(QGraphicsScene(self))
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)

        # tile_pixmap = QPixmap(64,64)
        # tile_pixmap.fill(Qt.white)
        # tile_painter = QPainter(tile_pixmap)
        # color = QColor(220, 220, 220)
        # tile_painter.fillRect( 0, 0,32,32, color)
        # tile_painter.fillRect(32,32,32,32, color)
        # tile_painter.end()
        # self.setBackgroundBrush(QBrush(tile_pixmap))

    def open_file(self, filename):
        svg_file = QFile(filename)

        if not svg_file.exists():
            return

        self.file_name = svg_file
        self.resetTransform()
        self.scale(2.0, 2.0)
        svg_item = QGraphicsSvgItem(svg_file.fileName())
        svg_item.setFlags(QGraphicsItem.ItemClipsToShape)
        svg_item.setCacheMode(QGraphicsItem.NoCache)
        svg_item.setZValue(0)

        s = self.scene()
        s.clear()
        s.addItem(svg_item)

    def wheelEvent(self, event):
        factor = pow(1.2, event.angleDelta().y() / 240.0)
        self.scale(factor, factor)
        event.accept()


if __name__ == '__main__':
    import sys
    import svgviewer_rc

    class MainWindow(QMainWindow):
        def __init__(self):
            super(MainWindow, self).__init__()
            self.rootView = SvgView()
            self.rootView.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
            self.setCentralWidget(self.rootView)

        def open_file(self, path=None):
            self.rootView.open_file(path)

    app = QApplication(sys.argv)
    window = MainWindow()
    window.open_file(':/files/bubbles.svg')
    # window.open_file('./test1.svg')
    window.show()
    sys.exit(app.exec_())
