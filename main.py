import sys
import os
import subprocess
import shutil
import numpy as np

from PyQt6.QtCore import Qt, QUrl, QThread, pyqtSignal, QSize
from PyQt6.QtGui import QKeyEvent, QColor, QPixmap, QPainter, QBrush, QPen
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QFileDialog, QLabel, QMessageBox,
    QGroupBox, QListWidget, QListWidgetItem, QSpinBox, QCheckBox, QFrame,
    QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QGraphicsRectItem
)
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput, QVideoSink

import pyqtgraph as pg


# --- FFmpeg & FFprobe beágyazott elérési útjának kezelése PyInstallerhez ---
def setup_embedded_ffmpeg():
    if getattr(sys, 'frozen', False):
        # Ha PyInstaller által generált executable / .app fut
        base_dir = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
    else:
        # Ha normál Python scriptként futtatod PyCharmban
        base_dir = os.path.dirname(os.path.abspath(__file__))

    bin_dir = os.path.join(base_dir, 'bin')

    # Hozzáadjuk a bin mappát a PATH környezeti változóhoz
    if os.path.exists(bin_dir):
        os.environ["PATH"] = bin_dir + os.pathsep + os.environ.get("PATH", "")


setup_embedded_ffmpeg()
# --------------------------------------------------------------------------
# --------------------------------------------------------------------------
# Modern "glass" dark theme (Apple-style: translucent panels, rounded
# corners, system accent colors). Applied once on the main window and
# cascades to all children via Qt Style Sheets.
# --------------------------------------------------------------------------

APP_STYLE_SHEET = """
QMainWindow, QWidget {
    background-color: #1c1c1e;
    color: #f2f2f7;
    font-size: 12px;
}

QGroupBox {
    background-color: rgba(255, 255, 255, 16);
    border: 1px solid rgba(255, 255, 255, 28);
    border-radius: 9px;
    margin-top: 11px;
    padding: 10px 8px 8px 8px;
    font-weight: 600;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 10px;
    top: 2px;
    padding: 0 4px;
    color: #a1a1aa;
    font-size: 11px;
    font-weight: 700;
}

QPushButton {
    background-color: rgba(255, 255, 255, 22);
    border: 1px solid rgba(255, 255, 255, 34);
    border-radius: 6px;
    padding: 5px 10px;
    color: #f2f2f7;
    font-weight: 500;
}
QPushButton:hover { background-color: rgba(255, 255, 255, 36); }
QPushButton:pressed { background-color: rgba(255, 255, 255, 14); }
QPushButton:checked {
    background-color: #0a84ff;
    border: 1px solid #0a84ff;
    color: white;
    font-weight: 600;
}
QPushButton:disabled {
    color: rgba(242, 242, 247, 70);
    background-color: rgba(255, 255, 255, 8);
    border: 1px solid rgba(255, 255, 255, 14);
}

QPushButton#btn_save_range {
    background-color: #0a84ff;
    border: 1px solid #0a84ff;
    color: white;
    font-weight: 700;
}
QPushButton#btn_save_range:hover { background-color: #3aa0ff; }

QPushButton#btn_open {
    background-color: #ffd60a;
    border: 1px solid #ffd60a;
    color: #1c1c1e;
    font-weight: 700;
}
QPushButton#btn_open:hover { background-color: #ffe45c; }

QPushButton#btn_play {
    background-color: #30d158;
    border: 1px solid #30d158;
    color: #04150a;
    font-weight: 700;
}
QPushButton#btn_play:hover { background-color: #5adc7a; }

QPushButton#btn_del_range:hover {
    background-color: rgba(255, 69, 58, 60);
    border: 1px solid rgba(255, 69, 58, 120);
}
QPushButton#btn_del_range {
    background-color: #ff453a;
    border: 1px solid #ff453a;
    color: white;
    font-weight: 700;
}
QPushButton#btn_del_range:hover { background-color: #ff6961; }

QPushButton#btn_export {
    background-color: #30d158;
    border: 1px solid #30d158;
    color: #04150a;
    font-weight: 700;
}
QPushButton#btn_export:hover { background-color: #5adc7a; }
QPushButton#btn_export:disabled {
    background-color: rgba(48, 209, 88, 70);
    color: rgba(4, 21, 10, 140);
    border: 1px solid rgba(48, 209, 88, 40);
}

QLabel { color: #e5e5ea; background: transparent; }

QListWidget {
    background-color: rgba(0, 0, 0, 55);
    border: 1px solid rgba(255, 255, 255, 22);
    border-radius: 6px;
    padding: 2px;
    outline: none;
}
QListWidget::item {
    border-radius: 4px;
    padding: 4px 6px;
    margin: 1px;
}
QListWidget::item:selected {
    background-color: rgba(10, 132, 255, 110);
    color: white;
}

QSpinBox {
    background-color: rgba(255, 255, 255, 14);
    border: 1px solid rgba(255, 255, 255, 30);
    border-radius: 5px;
    padding: 2px 4px;
    color: #f2f2f7;
}

QCheckBox { spacing: 8px; background: transparent; }
QCheckBox::indicator {
    width: 14px;
    height: 14px;
    border-radius: 4px;
    border: 1px solid rgba(255, 255, 255, 50);
    background: rgba(255, 255, 255, 10);
}
QCheckBox::indicator:checked {
    background-color: #0a84ff;
    border: 1px solid #0a84ff;
}

QScrollBar:vertical, QScrollBar:horizontal {
    background: transparent;
    width: 10px;
    height: 10px;
    margin: 0px;
}
QScrollBar::handle {
    background: rgba(255, 255, 255, 45);
    border-radius: 5px;
    min-height: 20px;
    min-width: 20px;
}
QScrollBar::add-line, QScrollBar::sub-line {
    height: 0px;
    width: 0px;
}
QScrollBar::add-page, QScrollBar::sub-page {
    background: none;
}

ResizableAnamorphicVideoWidget, InteractivePlotWidget {
    background-color: #000000;
    border: 1px solid rgba(255, 255, 255, 22);
    border-radius: 8px;
}
"""


# --------------------------------------------------------------------------
# Preview widget: manual pixmap rendering (guaranteed anamorphic desqueeze)
# --------------------------------------------------------------------------

class ResizableAnamorphicVideoWidget(QGraphicsView):
    """Live video preview.

    QMediaPlayer is connected directly to a bare QVideoSink (no
    QVideoWidget / QGraphicsVideoItem involved -- their own "aspect ratio
    mode" is unreliable across Qt6 backends and a plain QVideoWidget can
    never show a desqueeze at all, since it always preserves the source's
    native pixel aspect ratio).

    Every decoded frame is captured via `videoFrameChanged`, converted to a
    QPixmap, and explicitly, manually stretched
    (Qt.AspectRatioMode.IgnoreAspectRatio) onto a QGraphicsPixmapItem.

    Layout policy (two levels, like a real monitor):
      1) An outer "screen" frame is always letterboxed to exactly 16:9
         within the available space -- the preview panel itself always has
         a consistent 16:9 shape, like a broadcast monitor.
      2) The actual video content is then letterboxed/pillarboxed INSIDE
         that 16:9 screen according to its own aspect ratio (native, or
         desqueezed). A wider-than-16:9 desqueezed image is pinned to the
         screen's full width and appears vertically compressed (bars top
         and bottom) -- never stretched out horizontally.
    """

    MONITOR_AR = 16.0 / 9.0

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setFrameShape(QGraphicsView.Shape.NoFrame)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setRenderHints(self.renderHints() | QPainter.RenderHint.SmoothPixmapTransform)

        self._scene = QGraphicsScene(self)
        self.setScene(self._scene)

        # Subtle "screen bezel" behind the picture, always exactly 16:9.
        self.monitor_frame_item = QGraphicsRectItem()
        self.monitor_frame_item.setBrush(QBrush(QColor(8, 8, 10)))
        self.monitor_frame_item.setPen(QPen(QColor(255, 255, 255, 20), 1))
        self._scene.addItem(self.monitor_frame_item)

        self.preview_item = QGraphicsPixmapItem()
        self._scene.addItem(self.preview_item)

        self.video_sink = QVideoSink(self)
        self.video_sink.videoFrameChanged.connect(self._on_video_frame)

        self.aspect_ratio = 16.0 / 9.0
        self._draw_w = 16.0
        self._draw_h = 9.0

        self._last_source_pixmap = None

        self._relayout()

    def set_aspect_ratio(self, width, height):
        if height > 0 and width > 0:
            self.aspect_ratio = float(width) / float(height)
            self._relayout()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._relayout()

    def _relayout(self):
        vw = max(1, self.viewport().width())
        vh = max(1, self.viewport().height())

        # 1) Outer 16:9 "screen", letterboxed within the available space.
        if vw / vh > self.MONITOR_AR:
            mon_h = float(vh)
            mon_w = mon_h * self.MONITOR_AR
        else:
            mon_w = float(vw)
            mon_h = mon_w / self.MONITOR_AR

        # 2) Content aspect ratio, fit inside the 16:9 screen -- pinned to
        # the screen's full width whenever it's wider than 16:9 (desqueeze
        # case), which is what makes it look vertically compressed rather
        # than stretched.
        ar = self.aspect_ratio if self.aspect_ratio > 0 else self.MONITOR_AR
        if mon_w / mon_h > ar:
            draw_h = mon_h
            draw_w = draw_h * ar
        else:
            draw_w = mon_w
            draw_h = draw_w / ar

        self._draw_w, self._draw_h = draw_w, draw_h

        self.monitor_frame_item.setRect(-mon_w / 2.0, -mon_h / 2.0, mon_w, mon_h)

        self._scene.setSceneRect(-vw / 2.0, -vh / 2.0, vw, vh)
        self.centerOn(0, 0)
        self._repaint_preview()

    def _repaint_preview(self):
        if self._last_source_pixmap is None or self._last_source_pixmap.isNull():
            return
        w = max(1, int(round(self._draw_w)))
        h = max(1, int(round(self._draw_h)))
        stretched = self._last_source_pixmap.scaled(
            w, h, Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.SmoothTransformation
        )
        self.preview_item.setPixmap(stretched)
        self.preview_item.setPos(-self._draw_w / 2.0, -self._draw_h / 2.0)

    def _on_video_frame(self, frame):
        if not frame.isValid():
            return
        try:
            image = frame.toImage()
            if image.isNull():
                return

            work_w = 720
            if image.width() > work_w:
                image = image.scaledToWidth(work_w, Qt.TransformationMode.FastTransformation)

            self._last_source_pixmap = QPixmap.fromImage(image)
            self._repaint_preview()
        except Exception as e:
            print(f"Előnézet frissítési hiba: {e}")


class ExportThread(QThread):
    """Runs the ffmpeg cut export in the background so the GUI stays
    responsive. Running ffmpeg synchronously on the GUI thread was the
    actual cause of the app appearing to "freeze" during export -- a 4K
    re-encode can take minutes, and with no event loop running in that
    time the window looks hung even though it's just working."""

    progress = pyqtSignal(str)
    finished_ok = pyqtSignal(list)
    failed = pyqtSignal(str)

    def __init__(self, video_path, ranges, output_dir, precise=False, display_ar=None):
        super().__init__()
        self.video_path = video_path
        self.ranges = ranges  # list of {"in_ms": int, "out_ms": int}
        self.output_dir = output_dir
        # precise=False (default): true REWRAP -- "-c copy", no re-encode,
        # very fast, but cuts snap to the nearest keyframe (GOP boundary).
        # precise=True: re-encodes with libx264 for frame-accurate cuts,
        # much slower -- this is what made export "borzalmasan lassú".
        self.precise = precise
        # Display aspect ratio to tag into the output container (e.g. from
        # the Anamorph Desqueeze toggle). None = leave untouched. This is
        # metadata only (-aspect), it does not re-sample any pixels, so it
        # works even with stream copy.
        self.display_ar = display_ar
        self._cancel = False

    def cancel(self):
        self._cancel = True

    def run(self):
        base_name, ext = os.path.splitext(os.path.basename(self.video_path))
        exported_files = []

        try:
            for idx, r in enumerate(self.ranges):
                if self._cancel:
                    break

                suffix = "" if len(self.ranges) == 1 else f"_{idx + 1:02d}"
                out_filename = f"{base_name}_ANACORR{suffix}{ext}"
                out_path = os.path.join(self.output_dir, out_filename)
                mode_label = "pontos újrakódolás" if self.precise else "rewrap"
                self.progress.emit(f"Vágás {idx + 1}/{len(self.ranges)} ({mode_label}): {out_filename} ...")

                cmd = [
                    "ffmpeg", "-y",
                    "-ss", str(r["in_ms"] / 1000.0),
                    "-to", str(r["out_ms"] / 1000.0),
                    "-i", self.video_path,
                ]
                if self.precise:
                    cmd += ["-c:v", "libx264", "-crf", "18", "-preset", "fast", "-c:a", "copy"]
                else:
                    cmd += ["-c", "copy"]
                if self.display_ar:
                    cmd += ["-aspect", f"{self.display_ar:.6f}"]
                cmd += [out_path]

                result = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
                if result.returncode != 0:
                    err_tail = result.stderr.decode(errors="ignore")[-1000:]
                    self.failed.emit(f"ffmpeg hiba ({out_filename}):\n{err_tail}")
                    return

                exported_files.append(out_filename)

            if not self._cancel:
                self.finished_ok.emit(exported_files)
        except Exception as e:
            self.failed.emit(str(e))


class AudioWaveformThread(QThread):
    waveform_ready = pyqtSignal(np.ndarray, float)

    def __init__(self, video_path):
        super().__init__()
        self.video_path = video_path

    def run(self):
        if not shutil.which("ffmpeg"):
            return

        cmd = [
            "ffmpeg", "-y", "-i", self.video_path,
            "-ac", "1", "-ar", "8000", "-f", "s16le", "-"
        ]

        try:
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
            raw_audio, _ = process.communicate()

            if not raw_audio:
                return

            samples = np.frombuffer(raw_audio, dtype=np.int16)
            target_points = 4000
            step = max(1, len(samples) // target_points)
            reduced_samples = samples[::step]

            max_val = np.max(np.abs(reduced_samples))
            normalized = reduced_samples / max_val if max_val > 0 else reduced_samples
            duration_sec = len(samples) / 8000.0

            self.waveform_ready.emit(normalized, duration_sec)
        except Exception as e:
            print(f"Waveform hiba: {e}")


class InteractivePlotWidget(pg.PlotWidget):
    """Waveform view. A plain click (press+release with negligible movement)
    seeks the playhead there. A real drag is left to pyqtgraph's own default
    pan/zoom behaviour, so you can still navigate a long waveform.

    Segment marking itself is NOT done here -- it's done with the I / O
    keys at the current playhead position (see FullVideoCutterGUI).
    """

    single_clicked = pyqtSignal(float)
    zoom_requested = pyqtSignal(float)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self._press_pos_px = None

    def mousePressEvent(self, ev):
        if ev.button() == Qt.MouseButton.LeftButton:
            self._press_pos_px = ev.pos()
            self.setFocus()
        super().mousePressEvent(ev)

    def mouseReleaseEvent(self, ev):
        if ev.button() == Qt.MouseButton.LeftButton and self._press_pos_px is not None:
            dist = (ev.pos() - self._press_pos_px).manhattanLength()
            if dist <= 5:
                pos_view = self.plotItem.vb.mapSceneToView(ev.position())
                self.single_clicked.emit(pos_view.x())
            self._press_pos_px = None
        super().mouseReleaseEvent(ev)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Up:
            self.zoom_requested.emit(0.7)
            event.accept()
            return
        if event.key() == Qt.Key.Key_Down:
            self.zoom_requested.emit(1.4)
            event.accept()
            return
        super().keyPressEvent(event)


class FullVideoCutterGUI(QMainWindow):
    RANGE_COLORS = [
        (0, 120, 215, 120),
        (46, 125, 50, 120),
        (230, 81, 0, 120),
        (123, 31, 162, 120),
        (0, 131, 143, 120),
        (198, 40, 40, 120)
    ]

    MIN_REGION_LEN_MS = 20
    DESQUEEZE_PAR = 1.2  # fixed anamorphic pixel-aspect-ratio factor

    def __init__(self):
        super().__init__()

        self.setWindowTitle("CUTEKI | Region Video Cutter")
        self.resize(1200, 900)

        self.video_path = ""
        self.duration_ms = 0
        self.fps = 25.0
        self.saved_ranges = []

        self.active_region = None
        self.active_start_marker = None
        self.active_stop_marker = None
        self.active_start_ms = None
        self.active_stop_ms = None

        # Exclusive region-loop playback state.
        self.loop_active = False
        self.loop_in_ms = 0
        self.loop_out_ms = 0

        self.init_ui()
        self.setStyleSheet(APP_STYLE_SHEET)

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(8)

        # 1. TOP LAYOUT
        top_layout = QHBoxLayout()
        top_layout.setSpacing(8)

        self.video_widget = ResizableAnamorphicVideoWidget()
        top_layout.addWidget(self.video_widget, stretch=1)

        list_group = QGroupBox("Vágási Szakaszok")
        list_layout = QVBoxLayout(list_group)

        self.list_ranges = QListWidget()
        self.list_ranges.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.list_ranges.currentRowChanged.connect(self.on_range_selected)
        list_layout.addWidget(self.list_ranges)

        self.btn_save_range = QPushButton("✓ Szakasz Mentése (ENTER)")
        self.btn_save_range.setObjectName("btn_save_range")
        self.btn_save_range.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.btn_save_range.clicked.connect(self.commit_active_range)
        list_layout.addWidget(self.btn_save_range)

        self.btn_del_range = QPushButton("- Kijelölt Szakasz Törlése (DEL)")
        self.btn_del_range.setObjectName("btn_del_range")
        self.btn_del_range.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.btn_del_range.clicked.connect(self.delete_selected_range)
        list_layout.addWidget(self.btn_del_range)

        top_layout.addWidget(list_group, stretch=1)
        main_layout.addLayout(top_layout, stretch=3)

        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)
        self.player.setVideoSink(self.video_widget.video_sink)

        self.player.positionChanged.connect(self.on_position_changed)
        self.player.durationChanged.connect(self.on_duration_changed)

        # 2. VEZÉRLŐK
        ctrl_layout = QHBoxLayout()
        ctrl_layout.addStretch()

        self.btn_open = QPushButton(" Videó Megnyitása")
        self.btn_open.setObjectName("btn_open")
        self.btn_open.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.btn_open.clicked.connect(self.open_file)
        ctrl_layout.addWidget(self.btn_open)

        self.lbl_time = QLabel("00:00:00 / 00:00:00")
        self.lbl_time.setStyleSheet("color: #0a84ff; font-size: 16px; font-weight: 700;")
        ctrl_layout.addWidget(self.lbl_time)

        self.btn_play = QPushButton("Play / Pause (Space)")
        self.btn_play.setObjectName("btn_play")
        self.btn_play.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.btn_play.clicked.connect(self.toggle_play)
        ctrl_layout.addWidget(self.btn_play)

        ctrl_layout.addStretch()

        main_layout.addLayout(ctrl_layout)

        # 3. WAVEFORM
        self.plot_widget = InteractivePlotWidget()
        self.plot_widget.hideAxis('left')
        self.plot_widget.hideAxis('bottom')
        self.plot_widget.setMouseEnabled(x=True, y=False)
        self.plot_widget.setBackground('#0a0a0c')
        main_layout.addWidget(self.plot_widget, stretch=1)

        self.plot_widget.single_clicked.connect(self.on_waveform_single_click)
        self.plot_widget.zoom_requested.connect(self.zoom_waveform)

        self.play_head = pg.InfiniteLine(pos=0, angle=90, pen=pg.mkPen('#ff453a', width=2))
        self.play_head.setZValue(100)
        self.plot_widget.addItem(self.play_head)

        # 4. ANAMORPHIC DESQUEEZE
        settings_group = QGroupBox("Anamorf Desqueeze (Előnézet)")
        settings_layout = QVBoxLayout(settings_group)

        par_row = QHBoxLayout()
        self.btn_desqueeze = QPushButton(f"Anamorph Desqueeze ({self.DESQUEEZE_PAR:.1f}x)")
        self.btn_desqueeze.setCheckable(True)
        self.btn_desqueeze.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.btn_desqueeze.toggled.connect(self.on_toggle_desqueeze)
        par_row.addWidget(self.btn_desqueeze)

        par_row.addWidget(QLabel("Natív szélesség:"))
        self.spin_native_w = QSpinBox()
        self.spin_native_w.setRange(1, 16384)
        self.spin_native_w.setValue(1920)
        self.spin_native_w.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.spin_native_w.valueChanged.connect(self.on_native_size_changed)
        par_row.addWidget(self.spin_native_w)

        par_row.addWidget(QLabel("Natív magasság:"))
        self.spin_native_h = QSpinBox()
        self.spin_native_h.setRange(1, 16384)
        self.spin_native_h.setValue(1080)
        self.spin_native_h.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.spin_native_h.valueChanged.connect(self.on_native_size_changed)
        par_row.addWidget(self.spin_native_h)

        par_row.addStretch()

        export_buttons = QVBoxLayout()
        export_buttons.setSpacing(6)

        self.btn_export_markers = QPushButton("Markerek Exportálása DaVinci EDL-be")
        self.btn_export_markers.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.btn_export_markers.clicked.connect(self.export_markers_edl)
        export_buttons.addWidget(self.btn_export_markers)

        self.btn_export = QPushButton("Mentett Szakaszok Exportálása (Rewrap)")
        self.btn_export.setObjectName("btn_export")
        self.btn_export.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.btn_export.clicked.connect(self.export_all_ranges)
        export_buttons.addWidget(self.btn_export)

        par_row.addLayout(export_buttons)
        settings_layout.addLayout(par_row)

        info_row = QHBoxLayout()
        self.lbl_desqueeze_info = QLabel("Forrás: –")
        self.lbl_desqueeze_info.setStyleSheet("color: #64d2ff;")
        info_row.addWidget(self.lbl_desqueeze_info)
        info_row.addStretch()

        self.lbl_creator = QLabel("ECKERT ANDRÁS | Vibe Coder")
        self.lbl_creator.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.lbl_creator.setStyleSheet("color: #ffd60a; font-size: 10px;")
        info_row.addWidget(self.lbl_creator)
        settings_layout.addLayout(info_row)

        main_layout.addWidget(settings_group)

        self.lbl_export_status = QLabel("")
        self.lbl_export_status.setStyleSheet("color: #64d2ff;")
        main_layout.addWidget(self.lbl_export_status)

        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setFocus()

    # -- anamorphic desqueeze -------------------------------------------------

    def on_native_size_changed(self, _value=None):
        self.on_toggle_desqueeze(self.btn_desqueeze.isChecked())

    def on_toggle_desqueeze(self, checked):
        native_w = self.spin_native_w.value()
        native_h = self.spin_native_h.value()
        par = self.DESQUEEZE_PAR if checked else 1.0

        # Width stays pegged to the native pixel width; height is divided
        # by the PAR factor -- i.e. the correction SQUEEZES the picture
        # vertically (matches DaVinci's Pixel Aspect Ratio behaviour),
        # rather than stretching it out horizontally.
        eff_w = float(native_w)
        eff_h = float(native_h) / par
        self.video_widget.set_aspect_ratio(eff_w, eff_h)

        ar = eff_w / eff_h if eff_h else 0
        state = f"{self.DESQUEEZE_PAR:.1f}x" if checked else "1.0x (natív)"
        self.lbl_desqueeze_info.setText(
            f"Forrás: {native_w}×{native_h}  |  PAR: {state}  |  Megjelenítési képarány: {ar:.3f}:1"
        )

    def _current_display_ar(self):
        """The display aspect ratio to tag into exported files, or None if
        the desqueeze toggle is off (leave the file untouched)."""
        if not self.btn_desqueeze.isChecked():
            return None
        native_w = self.spin_native_w.value()
        native_h = self.spin_native_h.value()
        eff_h = float(native_h) / self.DESQUEEZE_PAR
        if eff_h <= 0:
            return None
        return float(native_w) / eff_h

    def keyPressEvent(self, event: QKeyEvent):
        key = event.key()
        modifiers = event.modifiers()

        if key == Qt.Key.Key_Escape:
            self.cancel_active_range()
            event.accept()
        elif self.spin_native_w.hasFocus() or self.spin_native_h.hasFocus():
            super().keyPressEvent(event)
        elif key == Qt.Key.Key_Space:
            self.toggle_play()
            event.accept()
        elif key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self.commit_active_range()
            event.accept()
        elif key == Qt.Key.Key_I:
            self.set_in_point()
            event.accept()
        elif key == Qt.Key.Key_O:
            self.set_out_point()
            event.accept()
        elif key in (Qt.Key.Key_Delete, Qt.Key.Key_Backspace):
            self.delete_selected_range()
            event.accept()
        elif key == Qt.Key.Key_Up:
            self.zoom_waveform(0.7)
            event.accept()
        elif key == Qt.Key.Key_Down:
            self.zoom_waveform(1.4)
            event.accept()
        elif key in (Qt.Key.Key_Left, Qt.Key.Key_Right):
            frame_time_ms = 1000.0 / self.fps
            step_frames = 20 if (modifiers & Qt.KeyboardModifier.AltModifier) else 1
            delta_ms = int(frame_time_ms * step_frames)

            curr_pos = self.player.position()
            new_pos = curr_pos + delta_ms if key == Qt.Key.Key_Right else curr_pos - delta_ms
            new_pos = max(0, min(self.duration_ms, new_pos))

            self.player.setPosition(new_pos)
            event.accept()
        else:
            super().keyPressEvent(event)

    def zoom_waveform(self, factor):
        vb = self.plot_widget.plotItem.vb
        center_x = self.player.position()
        vb.scaleBy(x=factor, center=(center_x, 0))

    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Videó Megnyitása", "",
                                                   "Video Files (*.mp4 *.mov *.mkv *.avi)")
        if file_path:
            self.clear_all_ranges()
            self.video_path = os.path.abspath(file_path)
            self.player.setSource(QUrl.fromLocalFile(self.video_path))

            self.detect_video_info()
            self.plot_widget.clearPlots()
            self.wf_thread = AudioWaveformThread(self.video_path)
            self.wf_thread.waveform_ready.connect(self.draw_waveform)
            self.wf_thread.start()
            self.setFocus()

    def detect_video_info(self):
        """Detects the source's REAL native pixel resolution and fps via
        ffprobe, and fills the (editable) native width/height fields with
        it. If detection fails for any reason, this says so explicitly
        instead of silently pretending the source is 1920x1080."""
        self.fps = 25.0
        detected_w, detected_h = 1920, 1080
        ok = False
        err = None

        if not shutil.which("ffprobe"):
            err = "az ffprobe nem található a rendszeren (nincs a PATH-on)"
        else:
            cmd = [
                "ffprobe", "-v", "error", "-of", "csv=p=0",
                "-select_streams", "v:0",
                "-show_entries", "stream=width,height,r_frame_rate",
                self.video_path
            ]
            try:
                res = subprocess.check_output(cmd, stderr=subprocess.STDOUT).decode().strip()
                first_line = res.splitlines()[0] if res else ""
                w_str, h_str, fps_str = first_line.split(',')
                detected_w = int(w_str)
                detected_h = int(h_str)
                num, den = map(int, fps_str.split('/'))
                self.fps = num / den if den > 0 else 25.0
                ok = True
            except Exception as e:
                err = str(e)

        self.spin_native_w.blockSignals(True)
        self.spin_native_h.blockSignals(True)
        self.spin_native_w.setValue(detected_w)
        self.spin_native_h.setValue(detected_h)
        self.spin_native_w.blockSignals(False)
        self.spin_native_h.blockSignals(False)
        self.on_toggle_desqueeze(self.btn_desqueeze.isChecked())

        if not ok:
            QMessageBox.warning(
                self, "Figyelem",
                "Nem sikerült automatikusan detektálni a videó valódi natív felbontását "
                f"({err}).\n\n1920×1080 került beállításra alapértelmezésként — kérlek, "
                "ellenőrizd és írd át kézzel a 'Natív szélesség/magasság' mezőkben, ha nem "
                "egyezik a forrásoddal!"
            )

    def draw_waveform(self, samples, duration_sec):
        x = np.linspace(0, duration_sec * 1000, len(samples))
        self.plot_widget.plot(x, samples, pen=pg.mkPen('#0a84ff', width=1))
        self.plot_widget.setXRange(0, duration_sec * 1000)

    def on_waveform_single_click(self, x_ms):
        if 0 <= x_ms <= self.duration_ms:
            self.player.setPosition(int(x_ms))

    def toggle_play(self):
        if self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.player.pause()
        else:
            if self.loop_active:
                self.player.setPosition(self.loop_in_ms)
            self.player.play()

    def on_position_changed(self, pos_ms):
        self.play_head.setPos(pos_ms)
        self.lbl_time.setText(f"{self.ms_to_ts(pos_ms)} / {self.ms_to_ts(self.duration_ms)}")

        if (self.loop_active
                and self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState
                and pos_ms >= self.loop_out_ms):
            self.player.setPosition(self.loop_in_ms)

    def on_duration_changed(self, dur_ms):
        self.duration_ms = dur_ms

    # -- I / O in/out-point marking (playhead-based, no mouse dragging) -----

    def _start_new_region(self, in_ms, out_ms, has_stop=False):
        in_ms = max(0, min(self.duration_ms, in_ms))
        out_ms = max(0, min(self.duration_ms, out_ms))
        marker_pen = pg.mkPen('#ffd60a', width=5)
        if has_stop:
            self.active_stop_ms = out_ms
            self.active_stop_marker = pg.InfiniteLine(
                pos=out_ms, angle=90, movable=False, pen=marker_pen
            )
            self.active_stop_marker.setZValue(30)
            self.plot_widget.addItem(self.active_stop_marker)
        else:
            self.active_start_ms = in_ms
            self.active_start_marker = pg.InfiniteLine(
                pos=in_ms, angle=90, movable=False, pen=marker_pen
            )
            self.active_start_marker.setZValue(30)
            self.plot_widget.addItem(self.active_start_marker)

    def _remove_active_markers(self):
        for marker_name in ('active_start_marker', 'active_stop_marker'):
            marker = getattr(self, marker_name)
            if marker is not None:
                self.plot_widget.removeItem(marker)
                setattr(self, marker_name, None)
        self.active_start_ms = None
        self.active_stop_ms = None

    def _connect_active_markers(self):
        if self.active_start_ms is None or self.active_stop_ms is None:
            return
        region_start = min(self.active_start_ms, self.active_stop_ms)
        region_stop = max(self.active_start_ms, self.active_stop_ms)
        if region_start == region_stop:
            return
        if self.active_region is not None:
            self.active_region.setRegion([region_start, region_stop])
            return

        self.active_region = pg.LinearRegionItem(
            values=[region_start, region_stop],
            movable=False,
            brush=QColor(255, 214, 10, 110),
        )
        self.active_region.setZValue(20)
        self.plot_widget.addItem(self.active_region)

    def cancel_active_range(self):
        if self.active_region is None and self.active_start_marker is None and self.active_stop_marker is None:
            return
        self._remove_active_markers()
        if self.active_region is not None:
            self.plot_widget.removeItem(self.active_region)
            self.active_region = None
        self.clear_loop_region()

    def _get_io_target_region(self):
        """The region I/O should act on: the in-progress (uncommitted)
        selection if there is one, otherwise the saved range currently
        selected in the list. None if neither exists.

        Note: right after saving a segment, nothing stays selected in the
        list (see commit_active_range) -- so pressing I/O again always
        starts a brand-new segment instead of re-editing the one you just
        saved."""
        if self.active_region is not None:
            return self.active_region
        idx = self.list_ranges.currentRow()
        if 0 <= idx < len(self.saved_ranges):
            return self.saved_ranges[idx]["region"]
        return None

    def set_in_point(self):
        """'I': moves the current region's START to the playhead. If there
        is no active/selected region yet, starts a brand-new one there."""
        if not self.duration_ms:
            return

        pos = self.player.position()
        region = self._get_io_target_region()

        if region is None:
            if self.active_start_marker is not None:
                self.plot_widget.removeItem(self.active_start_marker)
                self.active_start_marker = None
            self._start_new_region(pos, pos + self.MIN_REGION_LEN_MS, has_stop=False)
            self._connect_active_markers()
            return

        in_ms, out_ms = region.getRegion()
        in_ms = min(pos, out_ms - self.MIN_REGION_LEN_MS)
        region.setRegion([in_ms, out_ms])

    def set_out_point(self):
        """'O': moves the current region's END to the playhead. If there is
        no active/selected region yet, starts a new one ending there."""
        if not self.duration_ms:
            return

        pos = self.player.position()
        region = self._get_io_target_region()

        if region is None:
            if self.active_stop_marker is not None:
                self.plot_widget.removeItem(self.active_stop_marker)
                self.active_stop_marker = None
            self._start_new_region(0, pos, has_stop=True)
            self._connect_active_markers()
            return

        in_ms, out_ms = region.getRegion()
        out_ms = max(pos, in_ms + self.MIN_REGION_LEN_MS)
        region.setRegion([in_ms, out_ms])
        if self.active_region is region and self.active_stop_marker is None:
            self.active_stop_marker = pg.InfiniteLine(
                pos=out_ms, angle=90, movable=False,
                pen=pg.mkPen('#ffd60a', width=5)
            )
            self.active_stop_marker.setZValue(30)
            self.plot_widget.addItem(self.active_stop_marker)
            self.on_active_region_changed()

    def on_active_region_changed(self):
        if not self.active_region:
            return
        r_in, r_out = self.active_region.getRegion()
        r_in_ms = int(max(0, r_in))
        r_out_ms = int(min(self.duration_ms, r_out)) if self.duration_ms else int(r_out)
        # No auto-seek here: I/O marking shouldn't yank the playhead away
        # from where you're currently scrubbing.
        if self.active_start_marker is not None:
            self.active_start_marker.setValue(r_in_ms)
        if self.active_stop_marker is not None:
            self.active_stop_marker.setValue(r_out_ms)
        self.clear_loop_region()

    # -- exclusive region-loop playback -------------------------------------

    def set_loop_region(self, in_ms, out_ms, seek=True):
        in_ms = int(max(0, in_ms))
        out_ms = int(min(self.duration_ms, out_ms)) if self.duration_ms else int(out_ms)

        self.loop_in_ms = in_ms
        self.loop_out_ms = out_ms
        self.loop_active = out_ms > in_ms

        if seek and self.loop_active:
            self.player.setPosition(self.loop_in_ms)

        self.update_loop_label()

    def clear_loop_region(self):
        self.loop_active = False
        self.update_loop_label()

    def update_loop_label(self):
        return

    def on_range_selected(self, idx):
        self.clear_loop_region()
        if 0 <= idx < len(self.saved_ranges):
            self.player.setPosition(self.saved_ranges[idx]["in_ms"])

    def commit_active_range(self):
        if self.active_region is None and (self.active_start_ms is None or self.active_stop_ms is None):
            QMessageBox.information(self, "Figyelem", "Jelölj ki egy szakaszt: állj a lejátszófejjel a kezdésre, nyomj I-t, majd a végére, nyomj O-t!")
            return

        if self.active_region is not None:
            r_in, r_out = self.active_region.getRegion()
            in_ms = int(max(0, r_in))
            out_ms = int(min(self.duration_ms, r_out))
        else:
            in_ms = int(self.active_start_ms)
            out_ms = int(self.active_stop_ms)

        if out_ms - in_ms < self.MIN_REGION_LEN_MS:
            return

        color_idx = len(self.saved_ranges) % len(self.RANGE_COLORS)
        rgba = self.RANGE_COLORS[color_idx]
        brush_color = QColor(*rgba)

        if self.active_region is not None:
            self.plot_widget.removeItem(self.active_region)
            self.active_region = None
        self._remove_active_markers()

        saved_region = pg.LinearRegionItem(values=[in_ms, out_ms], movable=False, brush=brush_color)
        saved_region.setZValue(10)
        saved_region.sigRegionChanged.connect(lambda: self.on_saved_region_updated(saved_region))
        self.plot_widget.addItem(saved_region)

        range_data = {
            "region": saved_region,
            "in_ms": in_ms,
            "out_ms": out_ms,
            "color_idx": color_idx
        }
        self.saved_ranges.append(range_data)
        # Intentionally NOT auto-selecting the new row in the list: leaving
        # nothing selected means the next I/O press starts a fresh segment
        # instead of re-editing the one that was just saved.
        self.update_list_widget()

    def on_saved_region_updated(self, region):
        for idx, r_data in enumerate(self.saved_ranges):
            if r_data["region"] == region:
                r_in, r_out = region.getRegion()
                r_data["in_ms"] = int(max(0, r_in))
                r_data["out_ms"] = int(min(self.duration_ms, r_out))

                item_text = f"Szakasz #{idx + 1} | {self.ms_to_ts(r_data['in_ms'])} -> {self.ms_to_ts(r_data['out_ms'])}"
                if idx < self.list_ranges.count():
                    self.list_ranges.item(idx).setText(item_text)

                break

    def delete_selected_range(self):
        idx = self.list_ranges.currentRow()
        if idx >= 0 and idx < len(self.saved_ranges):
            r_item = self.saved_ranges.pop(idx)
            self.plot_widget.removeItem(r_item["region"])
            self.update_list_widget()

    def clear_all_ranges(self):
        if self.active_region:
            if self.active_region is not None:
                self.plot_widget.removeItem(self.active_region)
                self.active_region = None
            self._remove_active_markers()
        for r in self.saved_ranges:
            self.plot_widget.removeItem(r["region"])
        self.saved_ranges.clear()
        self.list_ranges.clear()
        self.clear_loop_region()

    def ms_to_ts(self, ms):
        s = int((ms / 1000) % 60)
        m = int((ms / (1000 * 60)) % 60)
        h = int((ms / (1000 * 60 * 60)) % 24)
        return f"{h:02d}:{m:02d}:{s:02d}"

    def ms_to_smpte(self, ms):
        """HH:MM:SS:FF timecode at the source's detected fps (rounded to
        the nearest integer frame rate -- non-drop-frame)."""
        fps_int = max(1, int(round(self.fps)))
        total_frames = int(round(ms / 1000.0 * fps_int))
        frames = total_frames % fps_int
        total_seconds = total_frames // fps_int
        seconds = total_seconds % 60
        minutes = (total_seconds // 60) % 60
        hours = (total_seconds // 3600) % 24
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}:{frames:02d}"

    def update_list_widget(self):
        self.list_ranges.clear()
        for idx, r in enumerate(self.saved_ranges):
            rgba = self.RANGE_COLORS[r["color_idx"]]
            color_hex = f"rgb({rgba[0]}, {rgba[1]}, {rgba[2]})"
            txt = f"Szakasz #{idx + 1}  |  {self.ms_to_ts(r['in_ms'])} → {self.ms_to_ts(r['out_ms'])}"

            item = QListWidgetItem()
            item.setSizeHint(QSize(0, 40))
            self.list_ranges.addItem(item)

            row = QWidget()
            row.setStyleSheet("background: transparent;")
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(4, 4, 8, 4)
            row_layout.setSpacing(10)

            # A vivid colored stripe -- the same color used for this
            # segment's region on the waveform -- so it's immediately
            # identifiable in the list too.
            swatch = QFrame()
            swatch.setFixedWidth(6)
            swatch.setStyleSheet(f"background-color: {color_hex}; border-radius: 3px;")
            row_layout.addWidget(swatch)

            label = QLabel(txt)
            label.setStyleSheet("background: transparent; color: #f2f2f7;")
            row_layout.addWidget(label, stretch=1)

            self.list_ranges.setItemWidget(item, row)

    # -- DaVinci Resolve marker EDL export -----------------------------------

    def export_markers_edl(self):
        """Writes an EDL containing an IN and an OUT point marker for every
        saved segment, in DaVinci Resolve's own marker-EDL format. Import in
        Resolve via: right-click the timeline in the Media Pool ->
        Timelines > Import > Timeline Markers from EDL."""
        if not self.saved_ranges:
            QMessageBox.warning(self, "Hiba", "Nincs elmentett vágási szakasz, amiből markert lehetne exportálni!")
            return

        default_name = "markerek.edl"
        if self.video_path:
            default_name = os.path.splitext(os.path.basename(self.video_path))[0] + "_markerek.edl"

        path, _ = QFileDialog.getSaveFileName(self, "Marker EDL Mentése", default_name, "EDL Files (*.edl)")
        if not path:
            return
        if not path.lower().endswith(".edl"):
            path += ".edl"

        frame_ms = 1000.0 / max(1.0, self.fps)
        lines = ["TITLE: Vagasi Markerek", "FCM: NON-DROP FRAME", ""]

        event_num = 1
        for idx, r in enumerate(self.saved_ranges, start=1):
            markers = [
                (f"Szakasz {idx} IN", r["in_ms"], "ResolveColorGreen"),
                (f"Szakasz {idx} OUT", r["out_ms"], "ResolveColorRed"),
            ]
            for label, ms, color in markers:
                tc_in = self.ms_to_smpte(ms)
                tc_out = self.ms_to_smpte(ms + frame_ms)
                lines.append(f"{event_num:03d}  001      V     C        {tc_in} {tc_out} {tc_in} {tc_out}  ")
                lines.append(f" |C:{color} |M:{label} |D:1")
                lines.append("")
                event_num += 1

        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))
        except Exception as e:
            QMessageBox.critical(self, "Hiba", f"Nem sikerült elmenteni az EDL fájlt:\n{e}")
            return

        QMessageBox.information(
            self, "Marker EDL Kész",
            f"Elmentve:\n{path}\n\n"
            "Importálás DaVinci Resolve-ban:\n"
            "Media Pool -> jobbklikk a timeline-on -> "
            "Timelines > Import > Timeline Markers from EDL"
        )

    # -- cut export (threaded, so the UI stays responsive) --------------------

    def export_all_ranges(self):
        if not self.video_path or not self.saved_ranges:
            QMessageBox.warning(self, "Hiba", "Nincs megnyitott videó vagy elmentett vágási szakasz!")
            return

        output_dir = QFileDialog.getExistingDirectory(self, "Válaszd ki a mentési mappát")
        if not output_dir:
            return

        # Snapshot only the plain values the worker thread needs -- never
        # hand pyqtgraph/Qt objects to a background thread.
        ranges_snapshot = [{"in_ms": r["in_ms"], "out_ms": r["out_ms"]} for r in self.saved_ranges]

        self.btn_export.setEnabled(False)
        self.btn_export_markers.setEnabled(False)
        self.btn_export.setText("Exportálás folyamatban...")
        self.lbl_export_status.setText(f"Indítás... (0/{len(ranges_snapshot)})")

        self._export_thread = ExportThread(
            self.video_path, ranges_snapshot, output_dir,
            precise=False,
            display_ar=self._current_display_ar(),
        )
        self._export_thread.progress.connect(self._on_export_progress)
        self._export_thread.finished_ok.connect(self._on_export_finished)
        self._export_thread.failed.connect(self._on_export_failed)
        self._export_thread.start()

    def _on_export_progress(self, text):
        self.lbl_export_status.setText(text)

    def _reset_export_buttons(self):
        self.btn_export.setEnabled(True)
        self.btn_export_markers.setEnabled(True)
        self.btn_export.setText(" Mentett Szakaszok Exportálása (Rewrap)")

    def _on_export_finished(self, exported_files):
        self._reset_export_buttons()
        self.lbl_export_status.setText(f"Kész: {len(exported_files)} vágat exportálva.")
        mode_note = "(rewrap – a vágáspontok a legközelebbi keyframe-hez igazodhatnak)"
        ar_note = " A fájlokba be lett égetve a helyes megjelenítési arány (Anamorph Desqueeze)." \
            if self._current_display_ar() else ""
        msg = (f"Sikeresen elmentve {len(exported_files)} vágat {mode_note}:{ar_note}\n\n"
               + "\n".join(exported_files))
        QMessageBox.information(self, "Exportálás Kész", msg)

    def _on_export_failed(self, err):
        self._reset_export_buttons()
        self.lbl_export_status.setText("Exportálás sikertelen.")
        QMessageBox.critical(self, "Export Hiba", err)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FullVideoCutterGUI()
    window.show()
    sys.exit(app.exec())
