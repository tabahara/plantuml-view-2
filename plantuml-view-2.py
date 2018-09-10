import re
import subprocess
from typing import List

from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QTabWidget, QApplication, QMenu, QSizePolicy
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from svgview import SvgView

import os
import sys

# for ctrl-c
#import signal
#signal.signal(signal.SIGINT, signal.SIG_DFL)


class PlantUMLView2(QApplication):
    def usage(self):
        print("Usage: %s target_file" % self.arguments()[0])
        sys.exit(-1)

    def __init__(self,argv):
        super(PlantUMLView2,self).__init__(argv)
        if len(argv) == 1:
            self.usage()

        self.root_view = MainWindow()

        self.aboutToQuit.connect(self.quit_application)

        self.target_file = argv[1]
        plantuml_handler = PlantUMLHandler(self.target_file)
        self.update_data.connect(self.update_view)

        self.target_dir = os.path.dirname(self.target_file)
        if self.target_dir == '':
            self.target_dir = '.'
        self.observer = Observer()

        print(self.target_dir)

        self.observer.schedule(plantuml_handler, self.target_dir)

        self.root_view.resize(500,600)
        self.root_view.show()

    def quit_application(self):
        print("aboutToQuit")
        print("stop observer..")
        self.observer.stop()
        self.observer.join()
        print("observer stopped")

    def main_loop(self):
        self.plantuml()
        self.update_view()
        self.observer.start()
        sys.exit(self.exec_())

    update_data = pyqtSignal()

    def plantuml(self):
        # plantuml_path = os.path.join(os.path.dirname(self.arguments()[0]),'plantuml.jar')
        plantuml_path = os.path.join(os.path.dirname(os.path.abspath(sys.executable)), 'plantuml.jar')
        print("PlantUML path:%s"%plantuml_path)
        subprocess.call(['java', '-jar', plantuml_path, '-svg', self.target_file])
        self.update_data.emit()

    def update_view(self):
        for svg_file in self.svg_list():
            self.root_view.add(svg_file)

    def svg_list(self) -> List:
        result = []
        f = open(self.target_file)

        current_output_filename = None
        for line in f:
            match = re.search(r'@startuml[ \t]+([^\s]+)', line)
            if match:
                current_output_filename = match.group(1)
                continue

            match = re.search(r'@enduml', line)
            if match:
                if current_output_filename:
                    result.append(os.path.join(self.target_dir, current_output_filename))
                    current_output_filename = None
                continue

        f.close()
        return result


class PlantUMLHandler(FileSystemEventHandler):
    def __init__(self, target_file):
        print("target_file:%s" % target_file)
        self.target_file = target_file

    def on_modified(self, event):
        # print(event)
        p = os.path.abspath(event.src_path)
        q = os.path.abspath(self.target_file)
        if p == q:
            # print("target_file:%s"%p)
            QApplication.instance().plantuml()


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.tabs = QTabWidget()
        self.init_ui()

    def update_file(self):
        self.tabs.clear()
        for f in QApplication.instance().svg_list():
            self.add(f)

    def init_ui(self):
        file_menu = QMenu("&File", self)

        update_action = file_menu.addAction("update")
        update_action.triggered.connect(self.update_file)

        quit_action = file_menu.addAction("E&xit")
        quit_action.triggered.connect(QApplication.instance().quit)
        self.menuBar().addMenu(file_menu)
        self.setCentralWidget(self.tabs)

    def add(self, svg_file):
        tab_name = os.path.basename(svg_file)

        svg_view = None
        for i in range(self.tabs.count()):
            if self.tabs.tabText(i) == tab_name :
                svg_view = self.tabs.widget(i)
                break

        if svg_view is None:
            svg_view = SvgView()
            self.tabs.addTab(svg_view, tab_name)

        svg_view.open_file(svg_file)


if __name__ == '__main__':
    if len(sys.argv) == 1 :
        sys.argv.append('test.puml')
    app = PlantUMLView2(sys.argv)
    app.main_loop()


