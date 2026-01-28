"""Best-Math: Enhanced math content editor with LaTeX, pages, and graphing tools."""

from __future__ import annotations

import math
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from PyQt6.QtCore import Qt, QSize, QLocale
from PyQt6.QtGui import (
    QAction,
    QFont,
    QImage,
    QKeySequence,
    QPixmap,
)
from PyQt6.QtPrintSupport import QPrintDialog, QPrinter
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFontComboBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QSplitter,
    QStackedWidget,
    QTextEdit,
    QToolBar,
    QVBoxLayout,
    QWidget,
)


@dataclass
class LanguageStrings:
    file: str
    new: str
    open: str
    save: str
    save_pdf: str
    insert_latex: str
    insert_diagram: str
    insert_image: str
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
    add_page: str
    delete_page: str
    pages: str
    latex_tutorial: str
    search: str
    insert: str
    image_settings: str


LANGUAGES = {
    "en": LanguageStrings(
        file="File",
        new="New",
        open="Open",
        save="Save",
        save_pdf="Export as PDF",
        insert_latex="Insert LaTeX",
        insert_diagram="Insert Graph",
        insert_image="Insert Image",
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
        diagram_title="Graphing Canvas",
        diagram_prompt="Add functions and points to build graphs like Desmos.",
        font="Font",
        font_size="Size",
        shortcut_hint="Shortcuts: Ctrl+L LaTeX, Ctrl+G Graph, Ctrl+Shift+S PDF",
        add_page="Add Page",
        delete_page="Delete Page",
        pages="Pages",
        latex_tutorial="LaTeX Tutorial",
        search="Search",
        insert="Insert",
        image_settings="Image Settings",
    ),
    "ko": LanguageStrings(
        file="파일",
        new="새로 만들기",
        open="열기",
        save="저장",
        save_pdf="PDF로 내보내기",
        insert_latex="LaTeX 삽입",
        insert_diagram="그래프 삽입",
        insert_image="이미지 삽입",
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
        diagram_title="그래프 캔버스",
        diagram_prompt="함수와 점을 추가해 그래프를 만드세요.",
        font="글꼴",
        font_size="크기",
        shortcut_hint="단축키: Ctrl+L LaTeX, Ctrl+G 그래프, Ctrl+Shift+S PDF",
        add_page="페이지 추가",
        delete_page="페이지 삭제",
        pages="페이지",
        latex_tutorial="LaTeX 튜토리얼",
        search="검색",
        insert="삽입",
        image_settings="이미지 설정",
    ),
    "zh": LanguageStrings(
        file="文件",
        new="新建",
        open="打开",
        save="保存",
        save_pdf="导出 PDF",
        insert_latex="插入 LaTeX",
        insert_diagram="插入图表",
        insert_image="插入图片",
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
        diagram_title="绘图画布",
        diagram_prompt="添加函数与点生成图像。",
        font="字体",
        font_size="大小",
        shortcut_hint="快捷键: Ctrl+L LaTeX, Ctrl+G 图表, Ctrl+Shift+S PDF",
        add_page="新增页面",
        delete_page="删除页面",
        pages="页面",
        latex_tutorial="LaTeX 教程",
        search="搜索",
        insert="插入",
        image_settings="图片设置",
    ),
    "es": LanguageStrings(
        file="Archivo",
        new="Nuevo",
        open="Abrir",
        save="Guardar",
        save_pdf="Exportar a PDF",
        insert_latex="Insertar LaTeX",
        insert_diagram="Insertar gráfico",
        insert_image="Insertar imagen",
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
        diagram_title="Lienzo de gráficos",
        diagram_prompt="Agrega funciones y puntos como en Desmos.",
        font="Fuente",
        font_size="Tamaño",
        shortcut_hint="Atajos: Ctrl+L LaTeX, Ctrl+G Gráfico, Ctrl+Shift+S PDF",
        add_page="Agregar página",
        delete_page="Eliminar página",
        pages="Páginas",
        latex_tutorial="Tutorial LaTeX",
        search="Buscar",
        insert="Insertar",
        image_settings="Ajustes de imagen",
    ),
}


LATEX_TUTORIAL = [
    ("Fractions", r"\\frac{a}{b}", "Use for any fraction"),
    ("Square root", r"\\sqrt{x}", "Radical with optional index"),
    ("Nth root", r"\\sqrt[n]{x}", "Root with degree n"),
    ("Summation", r"\\sum_{i=1}^{n} i", "Summations with bounds"),
    ("Integral", r"\\int_{a}^{b} f(x)\\,dx", "Definite integral"),
    ("Matrix", r"\\begin{bmatrix}a&b\\\\c&d\\end{bmatrix}", "Matrix block"),
    ("Limit", r"\\lim_{x\\to 0} \\frac{\\sin x}{x}", "Limit notation"),
    ("Piecewise", r"f(x)=\\begin{cases}x^2,&x>0\\\\-x,&x\\le 0\\end{cases}", "Piecewise"),
    ("Vector", r"\\vec{v} = \\langle x, y, z \\rangle", "Vector notation"),
    ("Greek letters", r"\\alpha \\beta \\gamma \\theta \\pi", "Greek symbols"),
]


class LatexDialog(QDialog):
    def __init__(self, language: LanguageStrings, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.language = language
        self.setWindowTitle(language.insert_latex)
        self.setMinimumSize(780, 520)

        self.input_field = QLineEdit(self)
        self.input_field.setPlaceholderText(language.latex_prompt)
        self.preview_label = QLabel(self)
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setMinimumHeight(140)

        self.search_field = QLineEdit(self)
        self.search_field.setPlaceholderText(f"{language.search} {language.latex_tutorial}...")
        self.tutorial_list = QListWidget(self)
        self._populate_tutorial("")

        self.quick_bar = QWidget(self)
        quick_layout = QHBoxLayout(self.quick_bar)
        quick_layout.setContentsMargins(0, 0, 0, 0)
        for label, snippet in [
            ("x^2", r"x^2"),
            ("Fraction", r"\\frac{a}{b}"),
            ("Root", r"\\sqrt{x}"),
            ("Sum", r"\\sum_{i=1}^{n}"),
            ("Integral", r"\\int_{a}^{b}"),
        ]:
            button = QPushButton(label, self)
            button.clicked.connect(lambda _checked=False, s=snippet: self._insert_snippet(s))
            quick_layout.addWidget(button)
        quick_layout.addStretch(1)

        self.insert_button = QPushButton(language.insert, self)
        self.cancel_button = QPushButton("Cancel", self)
        button_row = QHBoxLayout()
        button_row.addStretch(1)
        button_row.addWidget(self.insert_button)
        button_row.addWidget(self.cancel_button)

        tutorial_panel = QVBoxLayout()
        tutorial_panel.addWidget(QLabel(language.latex_tutorial, self))
        tutorial_panel.addWidget(self.search_field)
        tutorial_panel.addWidget(self.tutorial_list)

        input_panel = QVBoxLayout()
        input_panel.addWidget(self.input_field)
        input_panel.addWidget(self.quick_bar)
        input_panel.addWidget(self.preview_label)
        input_panel.addStretch(1)

        content = QHBoxLayout()
        content.addLayout(input_panel, 3)
        content.addLayout(tutorial_panel, 2)

        layout = QVBoxLayout(self)
        layout.addLayout(content)
        layout.addLayout(button_row)

        self.input_field.textChanged.connect(self._update_preview)
        self.search_field.textChanged.connect(self._populate_tutorial)
        self.tutorial_list.itemClicked.connect(self._apply_tutorial_item)
        self.insert_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

        self._update_preview()

    def _populate_tutorial(self, keyword: str) -> None:
        self.tutorial_list.clear()
        keyword_lower = keyword.strip().lower()
        for title, latex, description in LATEX_TUTORIAL:
            if keyword_lower and keyword_lower not in title.lower() and keyword_lower not in description.lower():
                continue
            item = QListWidgetItem(f"{title} — {description}\n{latex}")
            item.setData(Qt.ItemDataRole.UserRole, latex)
            self.tutorial_list.addItem(item)

    def _apply_tutorial_item(self, item: QListWidgetItem) -> None:
        latex = item.data(Qt.ItemDataRole.UserRole)
        self._insert_snippet(latex)

    def _insert_snippet(self, snippet: str) -> None:
        cursor = self.input_field.cursorPosition()
        text = self.input_field.text()
        new_text = f"{text[:cursor]}{snippet}{text[cursor:]}"
        self.input_field.setText(new_text)
        self.input_field.setCursorPosition(cursor + len(snippet))

    def _update_preview(self) -> None:
        text = self.input_field.text().strip()
        if not text:
            self.preview_label.setText("Preview")
            return
        try:
            image = MainWindow.render_latex_static(text)
        except Exception:
            self.preview_label.setText(self.language.latex_error)
            return
        pixmap = QPixmap.fromImage(image)
        self.preview_label.setPixmap(pixmap.scaled(
            self.preview_label.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        ))

    def get_latex(self) -> str:
        return self.input_field.text().strip()


class GraphDialog(QDialog):
    def __init__(self, language: LanguageStrings, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.language = language
        self.setWindowTitle(language.diagram_title)
        self.setMinimumSize(820, 600)

        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.axis = self.figure.add_subplot(111)
        self._configure_axes()

        self.function_input = QLineEdit(self)
        self.function_input.setPlaceholderText("f(x) = sin(x) + x^2")
        self.color_box = QComboBox(self)
        self.color_box.addItems(["blue", "red", "green", "purple", "orange", "black"])
        self.fill_check = QCheckBox("Fill under curve", self)
        self.add_function_button = QPushButton("Add Function", self)

        self.points_input = QLineEdit(self)
        self.points_input.setPlaceholderText("Points: (1,2), (2,3.5)")
        self.add_points_button = QPushButton("Add Points", self)
        self.clear_button = QPushButton("Clear", self)

        controls = QFormLayout()
        controls.addRow("Function", self.function_input)
        controls.addRow("Color", self.color_box)
        controls.addRow("", self.fill_check)
        controls.addRow("", self.add_function_button)
        controls.addRow("Points", self.points_input)
        controls.addRow("", self.add_points_button)
        controls.addRow("", self.clear_button)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
            self,
        )

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(language.diagram_prompt, self))
        splitter = QSplitter(self)
        left = QWidget(self)
        left_layout = QVBoxLayout(left)
        left_layout.addLayout(controls)
        left_layout.addStretch(1)
        splitter.addWidget(left)
        splitter.addWidget(self.canvas)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)
        layout.addWidget(splitter)
        layout.addWidget(buttons)

        self.add_function_button.clicked.connect(self.add_function)
        self.add_points_button.clicked.connect(self.add_points)
        self.clear_button.clicked.connect(self.clear_graph)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

    def _configure_axes(self) -> None:
        self.axis.clear()
        self.axis.grid(True, which="both", linestyle="--", linewidth=0.5)
        self.axis.axhline(0, color="black", linewidth=1)
        self.axis.axvline(0, color="black", linewidth=1)
        self.axis.set_xlabel("x")
        self.axis.set_ylabel("y")
        self.canvas.draw_idle()

    def add_function(self) -> None:
        expr = self.function_input.text().strip()
        if not expr:
            return
        x = np.linspace(-10, 10, 400)
        try:
            y = eval(expr, {"x": x, "np": np, "sin": np.sin, "cos": np.cos, "tan": np.tan,
                            "sqrt": np.sqrt, "log": np.log, "exp": np.exp, "abs": np.abs})
        except Exception:
            QMessageBox.warning(self, self.language.diagram_title, "Invalid function expression.")
            return
        color = self.color_box.currentText()
        self.axis.plot(x, y, color=color, linewidth=2)
        if self.fill_check.isChecked():
            self.axis.fill_between(x, y, color=color, alpha=0.2)
        self.canvas.draw_idle()

    def add_points(self) -> None:
        text = self.points_input.text().strip()
        if not text:
            return
        try:
            points = []
            pairs = [p.strip() for p in text.replace("(", "").replace(")", "").split(";") if p.strip()]
            if not pairs:
                pairs = [p.strip() for p in text.split(")") if p.strip()]
            for pair in pairs:
                cleaned = pair.replace("(", "").replace(")", "").strip()
                if not cleaned:
                    continue
                x_str, y_str = [v.strip() for v in cleaned.split(",", maxsplit=1)]
                points.append((float(x_str), float(y_str)))
        except Exception:
            QMessageBox.warning(self, self.language.diagram_title, "Invalid points format.")
            return
        if not points:
            return
        xs, ys = zip(*points)
        color = self.color_box.currentText()
        self.axis.scatter(xs, ys, color=color, s=40)
        self.canvas.draw_idle()

    def clear_graph(self) -> None:
        self._configure_axes()

    def render_to_image(self) -> QImage:
        self.figure.canvas.draw()
        width, height = self.figure.canvas.get_width_height()
        image = QImage(self.figure.canvas.buffer_rgba(), width, height, QImage.Format.Format_ARGB32)
        return image.copy()


class ImageInsertDialog(QDialog):
    def __init__(self, language: LanguageStrings, image_path: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.language = language
        self.image_path = image_path
        self.setWindowTitle(language.image_settings)
        self.setMinimumWidth(360)

        self.width_input = QLineEdit(self)
        self.height_input = QLineEdit(self)
        self.align_box = QComboBox(self)
        self.align_box.addItems(["Left", "Center", "Right"])

        form = QFormLayout()
        form.addRow("Width (px)", self.width_input)
        form.addRow("Height (px)", self.height_input)
        form.addRow("Alignment", self.align_box)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
            self,
        )

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(buttons)

        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

    def get_settings(self) -> tuple[int | None, int | None, Qt.AlignmentFlag]:
        def parse(text: str) -> int | None:
            try:
                return int(text)
            except ValueError:
                return None

        width = parse(self.width_input.text())
        height = parse(self.height_input.text())
        align_text = self.align_box.currentText()
        if align_text == "Center":
            align = Qt.AlignmentFlag.AlignCenter
        elif align_text == "Right":
            align = Qt.AlignmentFlag.AlignRight
        else:
            align = Qt.AlignmentFlag.AlignLeft
        return width, height, align


class PagesPanel(QWidget):
    def __init__(self, language: LanguageStrings, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.language = language
        self.page_list = QListWidget(self)
        self.page_stack = QStackedWidget(self)

        self.add_button = QPushButton(language.add_page, self)
        self.delete_button = QPushButton(language.delete_page, self)

        button_row = QHBoxLayout()
        button_row.addWidget(self.add_button)
        button_row.addWidget(self.delete_button)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(language.pages, self))
        layout.addWidget(self.page_list)
        layout.addLayout(button_row)

        self.page_list.currentRowChanged.connect(self.page_stack.setCurrentIndex)
        self.add_button.clicked.connect(self.add_page)
        self.delete_button.clicked.connect(self.delete_page)

    def add_page(self, title: str | None = None) -> QTextEdit:
        index = self.page_list.count() + 1
        name = title or f"Page {index}"
        self.page_list.addItem(name)
        editor = QTextEdit(self)
        editor.setAcceptRichText(True)
        editor.setFont(QFont("Times New Roman", 12))
        self.page_stack.addWidget(editor)
        self.page_list.setCurrentRow(self.page_list.count() - 1)
        return editor

    def delete_page(self) -> None:
        row = self.page_list.currentRow()
        if row < 0 or self.page_list.count() <= 1:
            return
        item = self.page_list.takeItem(row)
        widget = self.page_stack.widget(row)
        self.page_stack.removeWidget(widget)
        widget.deleteLater()
        del item
        if row > 0:
            self.page_list.setCurrentRow(row - 1)

    def current_editor(self) -> QTextEdit:
        widget = self.page_stack.currentWidget()
        if not isinstance(widget, QTextEdit):
            raise RuntimeError("No editor available")
        return widget


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.language_code = self._detect_language()
        self.language = LANGUAGES[self.language_code]
        self.setWindowTitle("Best-Math")
        self.resize(1320, 820)

        self.pages_panel = PagesPanel(self.language, self)
        self.pages_panel.add_page()
        self.pages_panel.page_stack.currentChanged.connect(self._update_preview)

        self.preview = QTextEdit(self)
        self.preview.setReadOnly(True)
        self.preview.setHtml("<h3>Live Preview</h3><p>Insert LaTeX, graphs, or images.</p>")

        main_splitter = QSplitter(self)
        main_splitter.addWidget(self.pages_panel)
        main_splitter.addWidget(self.pages_panel.page_stack)
        main_splitter.addWidget(self.preview)
        main_splitter.setStretchFactor(0, 1)
        main_splitter.setStretchFactor(1, 4)
        main_splitter.setStretchFactor(2, 2)
        self.setCentralWidget(main_splitter)

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

    def current_editor(self) -> QTextEdit:
        return self.pages_panel.current_editor()

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
        self.insert_diagram_action.setShortcut(QKeySequence("Ctrl+G"))
        self.insert_diagram_action.triggered.connect(self.insert_diagram)

        self.insert_image_action = QAction(self.language.insert_image, self)
        self.insert_image_action.setShortcut(QKeySequence("Ctrl+I"))
        self.insert_image_action.triggered.connect(self.insert_image)

        self.print_action = QAction(self.language.print_doc, self)
        self.print_action.setShortcut(QKeySequence.StandardKey.Print)
        self.print_action.triggered.connect(self.print_document)

        self.exit_action = QAction(self.language.exit, self)
        self.exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        self.exit_action.triggered.connect(self.close)

        self.undo_action = QAction(self.language.undo, self)
        self.undo_action.setShortcut(QKeySequence.StandardKey.Undo)
        self.undo_action.triggered.connect(lambda: self.current_editor().undo())

        self.redo_action = QAction(self.language.redo, self)
        self.redo_action.setShortcut(QKeySequence.StandardKey.Redo)
        self.redo_action.triggered.connect(lambda: self.current_editor().redo())

        self.cut_action = QAction(self.language.cut, self)
        self.cut_action.setShortcut(QKeySequence.StandardKey.Cut)
        self.cut_action.triggered.connect(lambda: self.current_editor().cut())

        self.copy_action = QAction(self.language.copy, self)
        self.copy_action.setShortcut(QKeySequence.StandardKey.Copy)
        self.copy_action.triggered.connect(lambda: self.current_editor().copy())

        self.paste_action = QAction(self.language.paste, self)
        self.paste_action.setShortcut(QKeySequence.StandardKey.Paste)
        self.paste_action.triggered.connect(lambda: self.current_editor().paste())

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

        self.insert_menu = menu_bar.addMenu("Insert")
        self.insert_menu.addAction(self.insert_latex_action)
        self.insert_menu.addAction(self.insert_diagram_action)
        self.insert_menu.addAction(self.insert_image_action)

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
        toolbar.addAction(self.insert_image_action)
        toolbar.addSeparator()
        toolbar.addAction(self.save_pdf_action)
        toolbar.addSeparator()

        self.font_combo = QFontComboBox(toolbar)
        self.font_combo.setCurrentFont(self.current_editor().font())
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
        self.insert_image_action.setText(self.language.insert_image)
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
        self.pages_panel.add_button.setText(self.language.add_page)
        self.pages_panel.delete_button.setText(self.language.delete_page)
        self.statusBar().showMessage(self.language.shortcut_hint)

    def set_language(self, code: str) -> None:
        self.language_code = code
        for action in self.language_group:
            action.setChecked(action.text() == code)
        self._apply_language()

    def _set_font(self, font: QFont) -> None:
        self.current_editor().setCurrentFont(font)

    def _set_font_size(self, size: str) -> None:
        try:
            value = int(size)
        except ValueError:
            return
        self.current_editor().setFontPointSize(value)

    def new_document(self) -> None:
        self.pages_panel.page_list.clear()
        while self.pages_panel.page_stack.count():
            widget = self.pages_panel.page_stack.widget(0)
            self.pages_panel.page_stack.removeWidget(widget)
            widget.deleteLater()
        self.pages_panel.add_page()
        self.preview.clear()

    def open_document(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, self.language.open, "", "HTML Files (*.html)")
        if not path:
            return
        content = Path(path).read_text(encoding="utf-8")
        self.current_editor().setHtml(content)
        self._update_preview()

    def save_document(self) -> None:
        path, _ = QFileDialog.getSaveFileName(self, self.language.save, "", "HTML Files (*.html)")
        if not path:
            return
        Path(path).write_text(self.current_editor().toHtml(), encoding="utf-8")

    def export_pdf(self) -> None:
        path, _ = QFileDialog.getSaveFileName(self, self.language.save_pdf, "", "PDF Files (*.pdf)")
        if not path:
            return
        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
        printer.setOutputFileName(path)
        self.current_editor().document().print(printer)

    def print_document(self) -> None:
        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        dialog = QPrintDialog(printer, self)
        if dialog.exec():
            self.current_editor().document().print(printer)

    def insert_latex(self) -> None:
        dialog = LatexDialog(self.language, self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        latex = dialog.get_latex()
        if not latex:
            return
        try:
            image = self._render_latex(latex)
        except Exception:
            QMessageBox.warning(self, self.language.insert_latex, self.language.latex_error)
            return

        cursor = self.current_editor().textCursor()
        cursor.insertImage(image)
        self._update_preview()

    def insert_diagram(self) -> None:
        dialog = GraphDialog(self.language, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            image = dialog.render_to_image()
            cursor = self.current_editor().textCursor()
            cursor.insertImage(image)
            self._update_preview()

    def insert_image(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, self.language.insert_image, "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if not path:
            return
        dialog = ImageInsertDialog(self.language, path, self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        width, height, alignment = dialog.get_settings()

        image = QImage(path)
        if image.isNull():
            QMessageBox.warning(self, self.language.insert_image, "Unable to load image.")
            return
        if width and height:
            image = image.scaled(width, height, Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.SmoothTransformation)
        elif width:
            image = image.scaledToWidth(width, Qt.TransformationMode.SmoothTransformation)
        elif height:
            image = image.scaledToHeight(height, Qt.TransformationMode.SmoothTransformation)

        cursor = self.current_editor().textCursor()
        block_format = cursor.blockFormat()
        block_format.setAlignment(alignment)
        cursor.setBlockFormat(block_format)

        cursor.insertImage(image)
        self._update_preview()

    def _update_preview(self) -> None:
        self.preview.setHtml(self.current_editor().toHtml())

    @staticmethod
    def render_latex_static(formula: str) -> QImage:
        fig = plt.figure(figsize=(0.01, 0.01), dpi=300)
        fig.text(0, 0, f"${formula}$", fontsize=16)
        fig.patch.set_facecolor("white")
        fig.canvas.draw()
        buf, (w, h) = fig.canvas.print_to_buffer()
        plt.close(fig)
        image = QImage(buf, w, h, QImage.Format.Format_ARGB32)
        return image

    def _render_latex(self, formula: str) -> QImage:
        return self.render_latex_static(formula)

    def show_about(self) -> None:
        QMessageBox.information(
            self,
            self.language.about,
            "Best-Math: An easy math editor for teachers.\n"
            "Insert LaTeX, graphs, and images with live preview and pages.",
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
