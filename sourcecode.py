"""Best-Math: Simple math content editor with LaTeX and geometry diagrams.

This module provides a PyQt6-based editor aimed at making math teachers'
workflows easy: insert LaTeX, draw geometry diagrams, and export to PDF.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from PyQt6.QtCore import Qt, QSize, QLocale
from PyQt6.QtGui import (
    QAction,
    QFont,
    QFontDatabase,
    QIcon,
    QImage,
    QKeySequence,
    QPainter,
    QPixmap,
)
from PyQt6.QtPrintSupport import QPrintDialog, QPrinter
from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFontComboBox,
    QFormLayout,
    QGraphicsEllipseItem,
    QGraphicsLineItem,
    QGraphicsRectItem,
    QGraphicsScene,
    QGraphicsTextItem,
    QGraphicsView,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSplitter,
    QTextEdit,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

import matplotlib
from matplotlib import pyplot as plt
from matplotlib import mathtext


@dataclass
class LanguageStrings:
    file: str
    new: str
    open: str
    save: str
    save_pdf: str
    insert_latex: str
    insert_shape: str
    insert_text_shape: str
    insert_line: str
    insert_rectangle: str
    insert_ellipse: str
    insert_diagram: str
    print_doc: str
    exit: str
    edit: str
    undo: str
    redo: str
    cut: str
    copy: str
    paste: str
    view: str
    language: str
    help: str
    about: str
    latex_prompt: str
    latex_error: str
    diagram_title: str
    diagram_prompt: str
    font: str
    font_size: str
    shortcut_hint: str


LANGUAGES = {
    "en": LanguageStrings(
        file="File",
        new="New",
        open="Open",
        save="Save",
        save_pdf="Export as PDF",
        insert_latex="Insert LaTeX",
        insert_shape="Insert Shape",
        insert_text_shape="Text",
        insert_line="Line",
        insert_rectangle="Rectangle",
        insert_ellipse="Ellipse",
        insert_diagram="Insert Diagram",
        print_doc="Print",
        exit="Exit",
        edit="Edit",
        undo="Undo",
        redo="Redo",
        cut="Cut",
        copy="Copy",
        paste="Paste",
        view="View",
        language="Language",
        help="Help",
        about="About",
        latex_prompt="Enter LaTeX formula",
        latex_error="Unable to render LaTeX formula.",
        diagram_title="Geometry Diagram",
        diagram_prompt="Use the diagram canvas to draw shapes then insert.",
        font="Font",
        font_size="Size",
        shortcut_hint="Shortcuts: Ctrl+L LaTeX, Ctrl+D Diagram, Ctrl+Shift+S PDF",
    ),
    "ko": LanguageStrings(
        file="파일",
        new="새로 만들기",
        open="열기",
        save="저장",
        save_pdf="PDF로 내보내기",
        insert_latex="LaTeX 삽입",
        insert_shape="도형 삽입",
        insert_text_shape="텍스트",
        insert_line="선",
        insert_rectangle="사각형",
        insert_ellipse="타원",
        insert_diagram="도형/그림 삽입",
        print_doc="인쇄",
        exit="종료",
        edit="편집",
        undo="실행 취소",
        redo="다시 실행",
        cut="잘라내기",
        copy="복사",
        paste="붙여넣기",
        view="보기",
        language="언어",
        help="도움말",
        about="정보",
        latex_prompt="LaTeX 수식 입력",
        latex_error="LaTeX 수식을 렌더링할 수 없습니다.",
        diagram_title="기하 도형",
        diagram_prompt="도형 캔버스에서 그림을 그린 후 삽입하세요.",
        font="글꼴",
        font_size="크기",
        shortcut_hint="단축키: Ctrl+L LaTeX, Ctrl+D 도형, Ctrl+Shift+S PDF",
    ),
    "zh": LanguageStrings(
        file="文件",
        new="新建",
        open="打开",
        save="保存",
        save_pdf="导出 PDF",
        insert_latex="插入 LaTeX",
        insert_shape="插入形状",
        insert_text_shape="文本",
        insert_line="直线",
        insert_rectangle="矩形",
        insert_ellipse="椭圆",
        insert_diagram="插入图形",
        print_doc="打印",
        exit="退出",
        edit="编辑",
        undo="撤销",
        redo="重做",
        cut="剪切",
        copy="复制",
        paste="粘贴",
        view="视图",
        language="语言",
        help="帮助",
        about="关于",
        latex_prompt="输入 LaTeX 公式",
        latex_error="无法渲染 LaTeX 公式。",
        diagram_title="几何图形",
        diagram_prompt="在画布中绘制图形后插入。",
        font="字体",
        font_size="大小",
        shortcut_hint="快捷键: Ctrl+L LaTeX, Ctrl+D 图形, Ctrl+Shift+S PDF",
    ),
    "es": LanguageStrings(
        file="Archivo",
        new="Nuevo",
        open="Abrir",
        save="Guardar",
        save_pdf="Exportar a PDF",
        insert_latex="Insertar LaTeX",
        insert_shape="Insertar forma",
        insert_text_shape="Texto",
        insert_line="Línea",
        insert_rectangle="Rectángulo",
        insert_ellipse="Elipse",
        insert_diagram="Insertar diagrama",
        print_doc="Imprimir",
        exit="Salir",
        edit="Editar",
        undo="Deshacer",
        redo="Rehacer",
        cut="Cortar",
        copy="Copiar",
        paste="Pegar",
        view="Ver",
        language="Idioma",
        help="Ayuda",
        about="Acerca de",
        latex_prompt="Ingresa la fórmula LaTeX",
        latex_error="No se pudo renderizar la fórmula LaTeX.",
        diagram_title="Diagrama de geometría",
        diagram_prompt="Dibuja en el lienzo y luego inserta.",
        font="Fuente",
        font_size="Tamaño",
        shortcut_hint="Atajos: Ctrl+L LaTeX, Ctrl+D Diagrama, Ctrl+Shift+S PDF",
    ),
}


class DiagramDialog(QDialog):
    def __init__(self, language: LanguageStrings, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.language = language
        self.setWindowTitle(language.diagram_title)
        self.scene = QGraphicsScene(self)
        self.view = QGraphicsView(self.scene, self)
        self.view.setMinimumSize(QSize(480, 320))

        self.text_button = QPushButton(language.insert_text_shape, self)
        self.line_button = QPushButton(language.insert_line, self)
        self.rect_button = QPushButton(language.insert_rectangle, self)
        self.ellipse_button = QPushButton(language.insert_ellipse, self)
        self.clear_button = QPushButton("Clear", self)

        self.text_button.clicked.connect(self.add_text)
        self.line_button.clicked.connect(self.add_line)
        self.rect_button.clicked.connect(self.add_rect)
        self.ellipse_button.clicked.connect(self.add_ellipse)
        self.clear_button.clicked.connect(self.scene.clear)

        button_row = QHBoxLayout()
        button_row.addWidget(self.text_button)
        button_row.addWidget(self.line_button)
        button_row.addWidget(self.rect_button)
        button_row.addWidget(self.ellipse_button)
        button_row.addWidget(self.clear_button)

        self.message_label = QLabel(language.diagram_prompt, self)
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel,
            self,
        )
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addWidget(self.message_label)
        layout.addWidget(self.view)
        layout.addLayout(button_row)
        layout.addWidget(self.buttons)

    def add_text(self) -> None:
        text, ok = QInputDialogCompat.get_text(self, self.language.insert_text_shape)
        if ok and text:
            item = QGraphicsTextItem(text)
            item.setFlag(QGraphicsTextItem.GraphicsItemFlag.ItemIsMovable, True)
            item.setFlag(QGraphicsTextItem.GraphicsItemFlag.ItemIsSelectable, True)
            self.scene.addItem(item)

    def add_line(self) -> None:
        line = QGraphicsLineItem(10, 10, 200, 10)
        line.setFlag(QGraphicsLineItem.GraphicsItemFlag.ItemIsMovable, True)
        line.setFlag(QGraphicsLineItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.scene.addItem(line)

    def add_rect(self) -> None:
        rect = QGraphicsRectItem(10, 10, 180, 100)
        rect.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsMovable, True)
        rect.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.scene.addItem(rect)

    def add_ellipse(self) -> None:
        ellipse = QGraphicsEllipseItem(10, 10, 180, 100)
        ellipse.setFlag(QGraphicsEllipseItem.GraphicsItemFlag.ItemIsMovable, True)
        ellipse.setFlag(QGraphicsEllipseItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.scene.addItem(ellipse)

    def render_to_image(self) -> QImage:
        rect = self.scene.itemsBoundingRect().adjusted(-10, -10, 10, 10)
        image = QImage(rect.size().toSize(), QImage.Format.Format_ARGB32)
        image.fill(Qt.GlobalColor.white)
        painter = QPainter(image)
        self.scene.render(painter, target=rect, source=rect)
        painter.end()
        return image


class QInputDialogCompat:
    @staticmethod
    def get_text(parent: QWidget, title: str) -> tuple[str, bool]:
        dialog = QDialog(parent)
        dialog.setWindowTitle(title)
        layout = QVBoxLayout(dialog)
        input_field = QLineEdit(dialog)
        layout.addWidget(input_field)
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel,
            dialog,
        )
        layout.addWidget(buttons)

        def accept() -> None:
            dialog.accept()

        def reject() -> None:
            dialog.reject()

        buttons.accepted.connect(accept)
        buttons.rejected.connect(reject)

        result = dialog.exec()
        return input_field.text(), result == QDialog.DialogCode.Accepted


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.language_code = self._detect_language()
        self.language = LANGUAGES[self.language_code]
        self.setWindowTitle("Best-Math")
        self.resize(1200, 720)

        self.editor = QTextEdit(self)
        self.editor.setFont(QFont("Times New Roman", 12))
        self.editor.setAcceptRichText(True)

        self.preview = QTextEdit(self)
        self.preview.setReadOnly(True)
        self.preview.setHtml("<h3>Live Notes</h3><p>Insert LaTeX or diagrams to see them here.</p>")

        splitter = QSplitter(self)
        splitter.addWidget(self.editor)
        splitter.addWidget(self.preview)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 1)
        self.setCentralWidget(splitter)

        self._build_actions()
        self._build_menus()
        self._build_toolbar()
        self.statusBar().showMessage(self.language.shortcut_hint)
        self._apply_language()

    def _detect_language(self) -> str:
        locale = QLocale.system().name().lower()
        for lang in LANGUAGES:
            if locale.startswith(lang):
                return lang
        return "en"

    def _build_actions(self) -> None:
        self.new_action = QAction(self.language.new, self)
        self.new_action.setShortcut(QKeySequence.StandardKey.New)
        self.new_action.triggered.connect(self.new_document)

        self.open_action = QAction(self.language.open, self)
        self.open_action.setShortcut(QKeySequence.StandardKey.Open)
        self.open_action.triggered.connect(self.open_document)

        self.save_action = QAction(self.language.save, self)
        self.save_action.setShortcut(QKeySequence.StandardKey.Save)
        self.save_action.triggered.connect(self.save_document)

        self.save_pdf_action = QAction(self.language.save_pdf, self)
        self.save_pdf_action.setShortcut(QKeySequence("Ctrl+Shift+S"))
        self.save_pdf_action.triggered.connect(self.export_pdf)

        self.insert_latex_action = QAction(self.language.insert_latex, self)
        self.insert_latex_action.setShortcut(QKeySequence("Ctrl+L"))
        self.insert_latex_action.triggered.connect(self.insert_latex)

        self.insert_diagram_action = QAction(self.language.insert_diagram, self)
        self.insert_diagram_action.setShortcut(QKeySequence("Ctrl+D"))
        self.insert_diagram_action.triggered.connect(self.insert_diagram)

        self.print_action = QAction(self.language.print_doc, self)
        self.print_action.setShortcut(QKeySequence.StandardKey.Print)
        self.print_action.triggered.connect(self.print_document)

        self.exit_action = QAction(self.language.exit, self)
        self.exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        self.exit_action.triggered.connect(self.close)

        self.undo_action = QAction(self.language.undo, self)
        self.undo_action.setShortcut(QKeySequence.StandardKey.Undo)
        self.undo_action.triggered.connect(self.editor.undo)

        self.redo_action = QAction(self.language.redo, self)
        self.redo_action.setShortcut(QKeySequence.StandardKey.Redo)
        self.redo_action.triggered.connect(self.editor.redo)

        self.cut_action = QAction(self.language.cut, self)
        self.cut_action.setShortcut(QKeySequence.StandardKey.Cut)
        self.cut_action.triggered.connect(self.editor.cut)

        self.copy_action = QAction(self.language.copy, self)
        self.copy_action.setShortcut(QKeySequence.StandardKey.Copy)
        self.copy_action.triggered.connect(self.editor.copy)

        self.paste_action = QAction(self.language.paste, self)
        self.paste_action.setShortcut(QKeySequence.StandardKey.Paste)
        self.paste_action.triggered.connect(self.editor.paste)

        self.about_action = QAction(self.language.about, self)
        self.about_action.triggered.connect(self.show_about)

    def _build_menus(self) -> None:
        menu_bar = self.menuBar()
        self.file_menu = menu_bar.addMenu(self.language.file)
        self.file_menu.addAction(self.new_action)
        self.file_menu.addAction(self.open_action)
        self.file_menu.addAction(self.save_action)
        self.file_menu.addAction(self.save_pdf_action)
        self.file_menu.addAction(self.print_action)
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.exit_action)

        self.edit_menu = menu_bar.addMenu(self.language.edit)
        self.edit_menu.addAction(self.undo_action)
        self.edit_menu.addAction(self.redo_action)
        self.edit_menu.addSeparator()
        self.edit_menu.addAction(self.cut_action)
        self.edit_menu.addAction(self.copy_action)
        self.edit_menu.addAction(self.paste_action)

        self.view_menu = menu_bar.addMenu(self.language.view)
        self.language_menu = self.view_menu.addMenu(self.language.language)
        self.language_group = []
        for code, language in LANGUAGES.items():
            action = QAction(code, self)
            action.setCheckable(True)
            action.setChecked(code == self.language_code)
            action.triggered.connect(lambda checked, c=code: self.set_language(c))
            self.language_menu.addAction(action)
            self.language_group.append(action)

        self.help_menu = menu_bar.addMenu(self.language.help)
        self.help_menu.addAction(self.about_action)

    def _build_toolbar(self) -> None:
        toolbar = QToolBar("Main", self)
        toolbar.setMovable(False)
        toolbar.addAction(self.new_action)
        toolbar.addAction(self.open_action)
        toolbar.addAction(self.save_action)
        toolbar.addSeparator()
        toolbar.addAction(self.insert_latex_action)
        toolbar.addAction(self.insert_diagram_action)
        toolbar.addSeparator()
        toolbar.addAction(self.save_pdf_action)
        toolbar.addSeparator()

        self.font_combo = QFontComboBox(toolbar)
        self.font_combo.setCurrentFont(self.editor.font())
        self.font_combo.currentFontChanged.connect(self._set_font)

        self.font_size_combo = QComboBox(toolbar)
        self.font_size_combo.setEditable(True)
        self.font_size_combo.setFixedWidth(60)
        for size in [8, 9, 10, 11, 12, 14, 16, 18, 20, 24, 28, 32, 36, 48, 64]:
            self.font_size_combo.addItem(str(size))
        self.font_size_combo.setCurrentText("12")
        self.font_size_combo.currentTextChanged.connect(self._set_font_size)

        toolbar.addWidget(QLabel(f"{self.language.font}: "))
        toolbar.addWidget(self.font_combo)
        toolbar.addWidget(QLabel(f"{self.language.font_size}: "))
        toolbar.addWidget(self.font_size_combo)

        self.addToolBar(toolbar)

    def _apply_language(self) -> None:
        self.language = LANGUAGES[self.language_code]
        self.new_action.setText(self.language.new)
        self.open_action.setText(self.language.open)
        self.save_action.setText(self.language.save)
        self.save_pdf_action.setText(self.language.save_pdf)
        self.insert_latex_action.setText(self.language.insert_latex)
        self.insert_diagram_action.setText(self.language.insert_diagram)
        self.print_action.setText(self.language.print_doc)
        self.exit_action.setText(self.language.exit)
        self.undo_action.setText(self.language.undo)
        self.redo_action.setText(self.language.redo)
        self.cut_action.setText(self.language.cut)
        self.copy_action.setText(self.language.copy)
        self.paste_action.setText(self.language.paste)
        self.about_action.setText(self.language.about)

        self.file_menu.setTitle(self.language.file)
        self.edit_menu.setTitle(self.language.edit)
        self.view_menu.setTitle(self.language.view)
        self.language_menu.setTitle(self.language.language)
        self.help_menu.setTitle(self.language.help)
        self.statusBar().showMessage(self.language.shortcut_hint)

    def set_language(self, code: str) -> None:
        self.language_code = code
        for action in self.language_group:
            action.setChecked(action.text() == code)
        self._apply_language()

    def _set_font(self, font: QFont) -> None:
        self.editor.setCurrentFont(font)

    def _set_font_size(self, size: str) -> None:
        try:
            value = int(size)
        except ValueError:
            return
        self.editor.setFontPointSize(value)

    def new_document(self) -> None:
        self.editor.clear()
        self.preview.clear()

    def open_document(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, self.language.open, "", "HTML Files (*.html);;Text Files (*.txt)")
        if not path:
            return
        content = Path(path).read_text(encoding="utf-8")
        if path.endswith(".html"):
            self.editor.setHtml(content)
        else:
            self.editor.setPlainText(content)

    def save_document(self) -> None:
        path, _ = QFileDialog.getSaveFileName(self, self.language.save, "", "HTML Files (*.html);;Text Files (*.txt)")
        if not path:
            return
        if path.endswith(".html"):
            Path(path).write_text(self.editor.toHtml(), encoding="utf-8")
        else:
            Path(path).write_text(self.editor.toPlainText(), encoding="utf-8")

    def export_pdf(self) -> None:
        path, _ = QFileDialog.getSaveFileName(self, self.language.save_pdf, "", "PDF Files (*.pdf)")
        if not path:
            return
        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
        printer.setOutputFileName(path)
        self.editor.document().print(printer)

    def print_document(self) -> None:
        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        dialog = QPrintDialog(printer, self)
        if dialog.exec():
            self.editor.document().print(printer)

    def insert_latex(self) -> None:
        latex, ok = QInputDialogCompat.get_text(self, self.language.latex_prompt)
        if not ok or not latex.strip():
            return
        try:
            image = self._render_latex(latex.strip())
        except Exception:
            QMessageBox.warning(self, self.language.insert_latex, self.language.latex_error)
            return

        cursor = self.editor.textCursor()
        cursor.insertImage(image)
        self._update_preview()

    def insert_diagram(self) -> None:
        dialog = DiagramDialog(self.language, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            image = dialog.render_to_image()
            cursor = self.editor.textCursor()
            cursor.insertImage(image)
            self._update_preview()

    def _update_preview(self) -> None:
        self.preview.setHtml(self.editor.toHtml())

    def _render_latex(self, formula: str) -> QImage:
        fig = plt.figure(figsize=(0.01, 0.01), dpi=300)
        fig.text(0, 0, f"${formula}$", fontsize=14)
        fig.patch.set_facecolor("white")
        fig.canvas.draw()
        buf, (w, h) = fig.canvas.print_to_buffer()
        plt.close(fig)
        image = QImage(buf, w, h, QImage.Format.Format_ARGB32)
        return image

    def show_about(self) -> None:
        QMessageBox.information(
            self,
            self.language.about,
            "Best-Math: An easy math editor for teachers.\n"
            "Insert LaTeX, draw diagrams, and export to PDF.",
        )


def main() -> None:
    app = QApplication(sys.argv)
    app.setOrganizationName("Best-Math")
    app.setApplicationName("Best-Math")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
