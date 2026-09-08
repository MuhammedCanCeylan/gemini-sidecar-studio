# -*- coding: utf-8 -*-
import os
import sys
import json
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QPlainTextEdit, QTabWidget,
    QFileDialog, QMessageBox, QFrame, QSplitter, QTreeView,
    QListWidget, QListWidgetItem, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView, QStatusBar, QComboBox, QSizePolicy
)
from PyQt6.QtGui import QFileSystemModel, QColor, QFont
from PyQt6.QtCore import Qt, QUrl, QDateTime, QStandardPaths

from extractor_engine import JS_DOM_DEEP_INSPECTOR, CodeIntelligenceExtractor

try:
    from PyQt6.QtWebEngineWidgets import QWebEngineView
    from PyQt6.QtWebEngineCore import QWebEngineProfile, QWebEnginePage
    HAS_WEBENGINE = True
except ImportError:
    HAS_WEBENGINE = False


STYLESHEET = """
QMainWindow { background-color: #0B0F19; }
QWidget { color: #CBD5E1; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 12px; }

#DashboardContainer, #TopBar { background: transparent; }

QFrame.MetricCard {
    background-color: #111827;
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 6px;
    padding: 6px 10px;
}
QLabel.MetricTitle { color: #64748B; font-size: 10px; font-weight: 700; letter-spacing: 0.5px; }
QLabel.MetricValue { color: #38BDF8; font-size: 14px; font-weight: bold; font-family: 'Cascadia Code', Consolas, monospace; }

QFrame.GlassPanel { background-color: #0F172A; border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 6px; }

QLineEdit, QPlainTextEdit, QComboBox {
    background-color: #0B0F19; border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 4px;
    padding: 4px 8px; color: #F8FAFC; font-family: "Cascadia Code", Consolas, monospace;
}
QLineEdit:focus, QPlainTextEdit:focus, QComboBox:focus { border: 1px solid #38BDF8; }

QPushButton { border-radius: 4px; padding: 5px 12px; font-weight: 600; }
QPushButton.GlassBtn { background-color: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); color: #E2E8F0; }
QPushButton.GlassBtn:hover { background-color: rgba(255, 255, 255, 0.1); border-color: rgba(255, 255, 255, 0.2); }
QPushButton.ActionRunBtn { background: #0284C7; border: 1px solid #0369A1; color: #FFFFFF; }
QPushButton.ActionRunBtn:hover { background: #0369A1; }
QPushButton.ActionSuccessBtn { background: #059669; border: 1px solid #047857; color: #FFFFFF; }
QPushButton.ActionSuccessBtn:hover { background: #047857; }

QTabWidget::pane { border: 1px solid rgba(255, 255, 255, 0.08); background: #0F172A; border-radius: 4px; }
QTabBar::tab { background: #0B0F19; color: #94A3B8; padding: 6px 12px; border-top-left-radius: 4px; border-top-right-radius: 4px; margin-right: 2px; }
QTabBar::tab:selected { background: #1E293B; color: #38BDF8; border-bottom: 2px solid #38BDF8; }

QTreeView, QListWidget, QTableWidget { background-color: #0B0F19; border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 4px; }
QHeaderView::section { background-color: #1E293B; color: #94A3B8; padding: 4px 6px; border: none; font-weight: bold; }
QStatusBar { background-color: #0B0F19; border-top: 1px solid rgba(255, 255, 255, 0.05); color: #64748B; }
"""

class ProjectArchitectStudioPro(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Project Architect Studio — Modular Sidecar Engine")
        self.resize(1640, 940)
        self.setStyleSheet(STYLESHEET)

        self.project_path = os.getcwd()
        self.history_stack = []
        self.staged_blocks = []

        self.init_ui()
        self.refresh_explorer()
        self.add_log("Studio Engine devrede. Ayrıştırma motoru: extractor_engine.py", "SUCCESS")

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        root_layout = QVBoxLayout(main_widget)
        root_layout.setContentsMargins(6, 6, 6, 4)
        root_layout.setSpacing(6)

        dash_widget = QWidget()
        dash_widget.setObjectName("DashboardContainer")
        dash_widget.setFixedHeight(55)
        dash_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        dash_row = QHBoxLayout(dash_widget)
        dash_row.setContentsMargins(0, 0, 0, 0)
        dash_row.setSpacing(6)

        self.card_files = self._create_card("PROJE DOSYALARI", "0")
        self.card_staged = self._create_card("YAKALANAN KOD BLOKLARI", "0")
        self.card_last_write = self._create_card("SON YAZILAN DOSYA", "—")
        self.card_undo_depth = self._create_card("UNDO GEÇMİŞİ", "0")

        dash_row.addWidget(self.card_files)
        dash_row.addWidget(self.card_staged)
        dash_row.addWidget(self.card_last_write)
        dash_row.addWidget(self.card_undo_depth)
        root_layout.addWidget(dash_widget)

        top_bar = QFrame()
        top_bar.setObjectName("TopBar")
        top_bar.setFixedHeight(45)
        top_bar.setProperty("class", "GlassPanel")
        top_bar.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(6, 4, 6, 4)
        top_layout.setSpacing(8)

        lbl_dir = QLabel("Proje Dizini:")
        lbl_dir.setStyleSheet("font-weight: bold;")
        top_layout.addWidget(lbl_dir)

        self.txt_path = QLineEdit(self.project_path)
        self.txt_path.textChanged.connect(self.on_path_manually_changed)
        top_layout.addWidget(self.txt_path, 1)

        btn_browse = QPushButton("📁 Gözat")
        btn_browse.setProperty("class", "GlassBtn")
        btn_browse.clicked.connect(self.browse_directory)
        top_layout.addWidget(btn_browse)

        self.btn_undo = QPushButton("⤺ Geri Al (0)")
        self.btn_undo.setProperty("class", "GlassBtn")
        self.btn_undo.setEnabled(False)
        self.btn_undo.clicked.connect(self.undo_action)
        top_layout.addWidget(self.btn_undo)

        top_layout.addSpacing(10)

        self.btn_parse = QPushButton("⚡ Kodları Ayrıştır")
        self.btn_parse.setProperty("class", "ActionRunBtn")
        self.btn_parse.clicked.connect(lambda: self.run_scraping_flow(auto_write=False))
        top_layout.addWidget(self.btn_parse)

        self.btn_write_direct = QPushButton("🚀 Ayrıştır ve Diske Yaz")
        self.btn_write_direct.setProperty("class", "ActionSuccessBtn")
        self.btn_write_direct.clicked.connect(lambda: self.run_scraping_flow(auto_write=True))
        top_layout.addWidget(self.btn_write_direct)

        self.btn_memory = QPushButton("🧠 Hafızayı Kopyala")
        self.btn_memory.setProperty("class", "ActionRunBtn")
        self.btn_memory.setStyleSheet("background: #8B5CF6; border: 1px solid #7C3AED; color: #FFFFFF;")
        self.btn_memory.clicked.connect(self.generate_project_memory)
        top_layout.addWidget(self.btn_memory)

        self.btn_tree_prompt = QPushButton("📁 Mimari Kodu İste")
        self.btn_tree_prompt.setProperty("class", "ActionRunBtn")
        self.btn_tree_prompt.setStyleSheet("background: #F59E0B; border: 1px solid #D97706; color: #FFFFFF;")
        self.btn_tree_prompt.clicked.connect(self.generate_tree_prompt)
        top_layout.addWidget(self.btn_tree_prompt)

        root_layout.addWidget(top_bar)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        left_panel = QFrame()
        left_panel.setProperty("class", "GlassPanel")
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(4, 4, 4, 4)
        left_layout.setSpacing(4)
        
        lbl_arch = QLabel("PROJE MİMARİSİ")
        lbl_arch.setStyleSheet("font-size: 10px; font-weight: 700; color: #64748B;")
        left_layout.addWidget(lbl_arch)

        self.fs_model = QFileSystemModel()
        self.fs_model.setRootPath(self.project_path)
        self.tree_view = QTreeView()
        self.tree_view.setModel(self.fs_model)
        self.tree_view.setRootIndex(self.fs_model.index(self.project_path))
        self.tree_view.setHeaderHidden(True)
        for c in range(1, 4):
            self.tree_view.hideColumn(c)
        self.tree_view.doubleClicked.connect(self.on_file_double_clicked)
        left_layout.addWidget(self.tree_view)
        splitter.addWidget(left_panel)

        mid_panel = QFrame()
        mid_panel.setProperty("class", "GlassPanel")
        mid_layout = QVBoxLayout(mid_panel)
        mid_layout.setContentsMargins(4, 4, 4, 4)
        self.mid_tabs = QTabWidget()

        if HAS_WEBENGINE:
            web_box = QWidget()
            web_layout = QVBoxLayout(web_box)
            web_layout.setContentsMargins(2, 2, 2, 2)
            
            top_web_ctrl = QHBoxLayout()
            lbl_ov = QLabel("Hedef Kuralı:")
            lbl_ov.setStyleSheet("font-weight: bold; color: #38BDF8;")
            top_web_ctrl.addWidget(lbl_ov)

            self.combo_target_override = QComboBox()
            self.combo_target_override.addItem("⚡ Otomatik Algıla (Derin Heuristic)")
            self.combo_target_override.setMinimumWidth(260)
            top_web_ctrl.addWidget(self.combo_target_override)

            btn_refresh_web = QPushButton("🔄 Sayfa Yenile")
            btn_refresh_web.setProperty("class", "GlassBtn")
            btn_refresh_web.clicked.connect(lambda: self.web_view.reload())
            top_web_ctrl.addWidget(btn_refresh_web)
            top_web_ctrl.addStretch()
            web_layout.addLayout(top_web_ctrl)

            storage_path = os.path.join(QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppDataLocation), "GeminiSidecarWebProfile")
            os.makedirs(storage_path, exist_ok=True)
            
            self.web_profile = QWebEngineProfile("GeminiSidecarWebProfile", self)
            self.web_profile.setPersistentStoragePath(storage_path)
            self.web_page = QWebEnginePage(self.web_profile, self)
            
            self.web_view = QWebEngineView(self)
            self.web_view.setPage(self.web_page)
            self.web_view.setUrl(QUrl("https://gemini.google.com/"))
            web_layout.addWidget(self.web_view)

            self.mid_tabs.addTab(web_box, "🌐 Gemini Web")
        else:
            self.mid_tabs.addTab(QLabel("PyQt6-WebEngine eksik. Kurulum: pip install PyQt6-WebEngine"), "🌐 Gemini Web")

        stg_box = QWidget()
        stg_layout = QVBoxLayout(stg_box)
        stg_layout.setContentsMargins(4, 4, 4, 4)
        stg_bar = QHBoxLayout()
        btn_save_staged = QPushButton("✔ Diske Bas")
        btn_save_staged.setProperty("class", "ActionSuccessBtn")
        btn_save_staged.clicked.connect(self.save_all_staged_to_disk)
        stg_bar.addWidget(btn_save_staged)
        btn_clear_staged = QPushButton("Temizle")
        btn_clear_staged.setProperty("class", "GlassBtn")
        btn_clear_staged.clicked.connect(self.clear_staged_table)
        stg_bar.addWidget(btn_clear_staged)
        stg_bar.addStretch()
        stg_layout.addLayout(stg_bar)

        self.table_staged = QTableWidget(0, 5)
        self.table_staged.setHorizontalHeaderLabels(["#", "Hedef Yol", "Güven", "Kaynak", "Boyut"])
        self.table_staged.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table_staged.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.table_staged.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table_staged.cellClicked.connect(self.on_table_row_clicked)
        stg_layout.addWidget(self.table_staged)
        self.mid_tabs.addTab(stg_box, "📋 Staging Alanı")

        edit_box = QWidget()
        edit_layout = QVBoxLayout(edit_box)
        edit_layout.setContentsMargins(4, 4, 4, 4)
        edit_bar = QHBoxLayout()
        self.lbl_editing_target = QLabel("Dosya: —")
        self.lbl_editing_target.setStyleSheet("font-weight: bold; color: #38BDF8;")
        edit_bar.addWidget(self.lbl_editing_target)
        edit_bar.addStretch()
        btn_save_editor = QPushButton("💾 Değişikliği Kaydet")
        btn_save_editor.setProperty("class", "GlassBtn")
        btn_save_editor.clicked.connect(self.save_editor_code_to_disk)
        edit_bar.addWidget(btn_save_editor)
        edit_layout.addLayout(edit_bar)

        self.txt_editor = QPlainTextEdit()
        font = QFont("Cascadia Code")
        font.setPointSize(11)
        self.txt_editor.setFont(font)
        edit_layout.addWidget(self.txt_editor)
        self.mid_tabs.addTab(edit_box, "💻 Kod Editörü")

        mid_layout.addWidget(self.mid_tabs)
        splitter.addWidget(mid_panel)

        right_panel = QFrame()
        right_panel.setProperty("class", "GlassPanel")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(4, 4, 4, 4)
        lbl_log = QLabel("SİSTEM GÜNLÜĞÜ")
        lbl_log.setStyleSheet("font-size: 10px; font-weight: 700; color: #64748B;")
        right_layout.addWidget(lbl_log)
        self.list_logs = QListWidget()
        right_layout.addWidget(self.list_logs)
        splitter.addWidget(right_panel)

        splitter.setSizes([220, 1080, 250])
        root_layout.addWidget(splitter)
        
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.lbl_status_msg = QLabel("Sistem Hazır")
        self.status_bar.addWidget(self.lbl_status_msg, 1)

    def _create_card(self, title: str, default_val: str) -> QFrame:
        frame = QFrame()
        frame.setProperty("class", "MetricCard")
        l = QVBoxLayout(frame)
        l.setContentsMargins(8, 4, 8, 4)
        l.setSpacing(0)
        lbl_t = QLabel(title)
        lbl_t.setProperty("class", "MetricTitle")
        l.addWidget(lbl_t)
        lbl_v = QLabel(default_val)
        lbl_v.setProperty("class", "MetricValue")
        l.addWidget(lbl_v)
        frame.val_label = lbl_v
        return frame

    def run_scraping_flow(self, auto_write: bool = False):
        if not HAS_WEBENGINE or not hasattr(self, "web_view"):
            self.add_log("PyQt6-WebEngine devrede değil.", "ERROR")
            return
        self.add_log("DOM katmanları taranıyor...", "INFO")
        self.web_view.page().runJavaScript(JS_DOM_DEEP_INSPECTOR, lambda raw_json: self.process_scraped_data(raw_json, auto_write))

    def process_scraped_data(self, raw_json: str, auto_write: bool):
        if not raw_json:
            self.add_log("Sayfa içeriğine erişilemedi.", "WARN")
            return
        try:
            payload = json.loads(raw_json)
        except Exception as e:
            self.add_log(f"DOM ayrıştırma hatası: {e}", "ERROR")
            return

        extracted = CodeIntelligenceExtractor.parse_payload(payload)
        extracted = [f for f in extracted if f.size > 20]

        if not extracted:
            self.add_log("Yazılacak geçerli kod tespit edilemedi.", "WARN")
            return

        self.staged_blocks = extracted
        self.card_staged.val_label.setText(str(len(self.staged_blocks)))
        self.render_staged_table()

        if auto_write:
            self.save_all_staged_to_disk()
        else:
            self.mid_tabs.setCurrentIndex(1)
            self.add_log(f"{len(extracted)} dosya ayrıştırıldı.", "SUCCESS")

    def render_staged_table(self):
        self.table_staged.setRowCount(0)
        for i, item in enumerate(self.staged_blocks):
            row = self.table_staged.rowCount()
            self.table_staged.insertRow(row)
            id_it = QTableWidgetItem(str(i + 1))
            target_it = QTableWidgetItem(item.target)
            conf_it = QTableWidgetItem(f"%{int(item.confidence * 100)}")
            reason_it = QTableWidgetItem(item.reason)
            size_it = QTableWidgetItem(f"{item.size} B")

            id_it.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            conf_it.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            size_it.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            if item.confidence >= 0.8:
                conf_it.setForeground(QColor("#34D399"))
            else:
                conf_it.setForeground(QColor("#FBBF24"))

            self.table_staged.setItem(row, 0, id_it)
            self.table_staged.setItem(row, 1, target_it)
            self.table_staged.setItem(row, 2, conf_it)
            self.table_staged.setItem(row, 3, reason_it)
            self.table_staged.setItem(row, 4, size_it)

    def on_table_row_clicked(self, row: int, col: int):
        if 0 <= row < len(self.staged_blocks):
            target = self.table_staged.item(row, 1).text()
            code = self.staged_blocks[row].code
            self.lbl_editing_target.setText(f"Dosya: {target}")
            self.txt_editor.setPlainText(code)

    def clear_staged_table(self):
        self.staged_blocks = []
        self.table_staged.setRowCount(0)
        self.card_staged.val_label.setText("0")
        self.add_log("Staging temizlendi.", "INFO")

    def save_all_staged_to_disk(self):
        override_rule = self.combo_target_override.currentText()
        use_override = not override_rule.startswith("⚡")
        written = 0
        for i, item in enumerate(self.staged_blocks):
            target = self.table_staged.item(i, 1).text() if self.table_staged.rowCount() > i else item.target
            if use_override: target = override_rule
            self.write_code_to_disk(target, item.code)
            written += 1
        self.add_log(f"{written} dosya diske yazıldı.", "SUCCESS")
        self.refresh_explorer()

    def save_editor_code_to_disk(self):
        target = self.lbl_editing_target.text().replace("Dosya: ", "").strip()
        if not target or target == "—": return
        self.write_code_to_disk(target, self.txt_editor.toPlainText())
        self.refresh_explorer()

    def write_code_to_disk(self, rel_path: str, content: str):
        full_path = os.path.normpath(os.path.join(self.project_path, rel_path))
        d = os.path.dirname(full_path)
        if d and not os.path.exists(d): os.makedirs(d, exist_ok=True)
        self._push_history(full_path)
        try:
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content + "\n")
            self.card_last_write.val_label.setText(os.path.basename(rel_path))
            self.add_log(f"Yazıldı: {rel_path}", "SUCCESS")
        except OSError as e:
            self.add_log(f"Yazılamadı: {e}", "ERROR")

    def _push_history(self, full_path: str):
        prev = None
        if os.path.exists(full_path):
            try:
                with open(full_path, "r", encoding="utf-8", errors="replace") as f: prev = f.read()
            except OSError: pass
        self.history_stack.append({"path": full_path, "prev": prev, "label": os.path.basename(full_path)})
        if len(self.history_stack) > 50: self.history_stack.pop(0)
        self.btn_undo.setEnabled(True)
        self.btn_undo.setText(f"⤺ Geri Al ({len(self.history_stack)})")
        self.card_undo_depth.val_label.setText(str(len(self.history_stack)))

    def undo_action(self):
        if not self.history_stack: return
        entry = self.history_stack.pop()
        full_path, prev = entry["path"], entry["prev"]
        try:
            if prev is None:
                if os.path.exists(full_path): os.remove(full_path)
            else:
                with open(full_path, "w", encoding="utf-8") as f: f.write(prev)
            self.add_log(f"Geri Alındı: {entry['label']}", "WARN")
        except OSError: pass
        count = len(self.history_stack)
        self.btn_undo.setEnabled(count > 0)
        self.btn_undo.setText(f"⤺ Geri Al ({count})")
        self.card_undo_depth.val_label.setText(str(count))
        self.refresh_explorer()

    def on_file_double_clicked(self, index):
        path = self.fs_model.filePath(index)
        if os.path.isfile(path):
            try:
                with open(path, "r", encoding="utf-8", errors="replace") as f: content = f.read()
                rel = os.path.relpath(path, self.project_path).replace("\\", "/")
                self.lbl_editing_target.setText(f"Dosya: {rel}")
                self.txt_editor.setPlainText(content)
                self.mid_tabs.setCurrentIndex(2)
            except Exception: pass

    def browse_directory(self):
        f = QFileDialog.getExistingDirectory(self, "Dizin Seç", self.project_path)
        if f:
            self.txt_path.setText(f)
            self.project_path = f
            self.refresh_explorer()

    def on_path_manually_changed(self, text: str):
        if os.path.isdir(text.strip()):
            self.project_path = text.strip()
            self.refresh_explorer()

    def refresh_explorer(self):
        if not os.path.exists(self.project_path): return
        self.tree_view.setRootIndex(self.fs_model.setRootPath(self.project_path))
        count, file_list = 0, []
        for root, dirs, files in os.walk(self.project_path):
            dirs[:] = [d for d in dirs if d not in (".git", "node_modules", "__pycache__", ".vscode")]
            for f in files:
                file_list.append(os.path.relpath(os.path.join(root, f), self.project_path).replace("\\", "/"))
                count += 1
        self.card_files.val_label.setText(str(count))
        if hasattr(self, "combo_target_override"):
            cur = self.combo_target_override.currentText()
            self.combo_target_override.blockSignals(True)
            self.combo_target_override.clear()
            self.combo_target_override.addItem("⚡ Otomatik Algıla (Derin Heuristic)")
            self.combo_target_override.addItems(sorted(file_list))
            idx = self.combo_target_override.findText(cur)
            if idx >= 0: self.combo_target_override.setCurrentIndex(idx)
            self.combo_target_override.blockSignals(False)

    def generate_project_memory(self):
        if not os.path.exists(self.project_path):
            self.add_log("Proje dizini bulunamadı.", "ERROR")
            return
        
        memory = "Aşağıda üzerinde çalıştığımız projenin GÜNCEL dosya mimarisi ve kodları yer almaktadır. "
        memory += "Bu bilgileri hafızana al ve sonraki üretimlerinde tamamen bu yapıya sadık kal, var olan fonksiyonları/değişkenleri koru.\n\n"
        memory += "### PROJE MİMARİSİ\n```text\n"
        
        file_contents = []
        allowed_exts = ('.py', '.js', '.jsx', '.ts', '.tsx', '.html', '.css', '.scss', '.json', '.md', '.txt', '.php', '.java', '.go', '.rs', '.sql', '.sh')
        
        for root, dirs, files in os.walk(self.project_path):
            dirs[:] = [d for d in dirs if d not in (".git", "node_modules", "__pycache__", ".vscode", "venv")]
            for f in files:
                rel_path = os.path.relpath(os.path.join(root, f), self.project_path).replace("\\", "/")
                memory += f"/{rel_path}\n"
                
                if f.lower().endswith(allowed_exts):
                    full_path = os.path.join(root, f)
                    try:
                        with open(full_path, "r", encoding="utf-8") as file:
                            content = file.read()
                            ext = f.split('.')[-1] if '.' in f else 'txt'
                            file_contents.append(f"### DOSYA: {rel_path}\n```{ext}\n{content}\n```\n")
                    except Exception:
                        pass
        
        memory += "```\n\n### MEVCUT DOSYA İÇERİKLERİ\n"
        memory += "\n".join(file_contents)
        
        QApplication.clipboard().setText(memory)
        self.add_log(f"Proje hafızası ({len(memory)} karakter) panoya kopyalandı.", "SUCCESS")

    def generate_tree_prompt(self):
        prompt = "Projenin ihtiyaç duyduğu tüm klasör hiyerarşisini ve dosyaları tek seferde diske oluşturacak bir script (Python veya Bash) yaz. Sadece çalıştırılabilir kodu ver."
        QApplication.clipboard().setText(prompt)
        self.add_log("Mimari oluşturma promptu panoya kopyalandı.", "SUCCESS")

    def add_log(self, message: str, level: str = "INFO"):
        time_str = QDateTime.currentDateTime().toString("hh:mm:ss")
        item = QListWidgetItem(f"[{time_str}] [{level}] {message}")
        palette = {"SUCCESS": "#34D399", "WARN": "#FBBF24", "ERROR": "#F87171", "INFO": "#94A3B8"}
        item.setForeground(QColor(palette.get(level, "#94A3B8")))
        self.list_logs.addItem(item)
        self.list_logs.scrollToBottom()

    def closeEvent(self, event):
        if hasattr(self, 'web_page'):
            self.web_page.deleteLater()
        if hasattr(self, 'web_view'):
            self.web_view.deleteLater()
        super().closeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    studio = ProjectArchitectStudioPro()
    studio.show()
    sys.exit(app.exec())