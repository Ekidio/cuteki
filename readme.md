# CUTEKI — Region Video Cutter & Anamorphic Preview Tool

<img width="1191" height="838" alt="Screenshot 2026-09-16 at 22 00 04" src="https://github.com/user-attachments/assets/d52b4ada-3753-4476-99b6-8662eaf7e82e" />


[English](#english) | [Magyar](#magyar)

---

## English

### Overview
**CUTEKI** is a desktop video trimming and preview utility built with Python 6 (PyQt6), PySide/PyQtGraph, and FFmpeg. Designed for video editors and filmmakers working with non-standard pixel aspect ratios (such as 1.2x anamorphic footage), CUTEKI enables fast waveform-based cutting, instant desqueeze preview, stream-copy rewrapping export, and DaVinci Resolve marker EDL generation.

### Key Features
- **Instant Anamorphic Desqueeze Preview**: Correct vertically or horizontally squeezed anamorphic footage (e.g., 1.2x PAR factor) in real time during playback without touching the original pixel data.
- **Auto Source Detection**: Automatically probes video resolution and native frame rates via embedded/system `ffprobe`.
- **Waveform-Based Navigation**: High-performance interactive audio waveform graph powered by `pyqtgraph` with frame-accurate scrubbing and playhead seeking.
- **Keyboard-Driven Region Cutting**: Easily set **In** (`I`) and **Out** (`O`) points directly from the playhead during playback or scrubbing.
- **Lossless Export (Rewrap)**: Super-fast cut generation using FFmpeg stream copy (`-c copy`) preserving full quality without lengthy re-encoding. Automatically embeds correct display aspect ratio tags (`-aspect`).
- **DaVinci Resolve EDL Marker Export**: Export marked In/Out regions directly as timecode-accurate EDL markers for seamless import into DaVinci Resolve timelines.
- **Modern UI Theme**: Dark translucent "glass" interface design with color-coded region clips.

### Keyboard Shortcuts

| Key | Action |
| :--- | :--- |
| `Space` | Play / Pause video |
| `I` | Set Region **In** point at current playhead position |
| `O` | Set Region **Out** point at current playhead position |
| `Enter` / `Return` | Save/commit active marked region to saved cut list |
| `Escape` | Cancel / clear current active marked region |
| `Delete` / `Backspace` | Delete selected range from list |
| `Left Arrow` / `Right Arrow` | Step 1 frame backward / forward |
| `Alt` + `Left` / `Right` | Step 20 frames backward / forward |
| `Up Arrow` / `Down Arrow` | Zoom in / out on the audio waveform graph |

### Installation & Setup

#### Prerequisites
- Python 3.9+
- FFmpeg and FFprobe installed on your system (or placed in a `./bin/` subfolder alongside `main.py`).

#### 1. Clone or Download Repository
```bash
git clone https://github.com/your-username/cuteki.git
cd cuteki
```

#### 2. Install Dependencies
```bash
pip install -r requirements.txt
```
*(Dependencies: `PyQt6`, `pyqtgraph`, `numpy`)*

#### 3. Running the Application
```bash
python main.py
```

---

## Magyar

### Áttekintés
A **CUTEKI** egy asztali videóvágó és előnézeti célszerszám, amely Python 6 (PyQt6), PyQtGraph és FFmpeg alapon működik. Kifejezetten videóvágók és filmesek számára készült, akik nem szabványos képarányú (pl. 1.2x anamorf) nyersanyagokkal dolgoznak. A szoftver gyors hullámforma-alapú vágást, azonnali anamorf desqueeze előnézetet, veszteségmentes (rewrap) exportálást és DaVinci Resolve marker EDL generálást tesz lehetővé.

### Főbb Funkciók
- **Azonnali Anamorf Desqueeze Előnézet**: Torzított anamorf felvételek (pl. 1.2x PAR) valós idejű helyreállítása és megjelenítése a lejátszás során a forrásfájl módosítása nélkül.
- **Automatikus Forrásdetektálás**: A videó valódi natív felbontásának és képkockasebességének (fps) automatikus kiolvasása a beépített/rendszer `ffprobe` segítségével.
- **Interaktív Hullámforma Sáv**: Nagyteljesítményű audio hullámforma megjelenítés `pyqtgraph` alapon, közvetlen lejátszófej-pozicionálással és zoomolással.
- **Billentyűzettel Vezérelt Vágás**: Gyors kijelölés **Kezdő-** (`I`) és **Végpontok** (`O`) megadásával a lejátszófej aktuális pozíciójában.
- **Veszteségmentes Exportálás (Rewrap)**: Rendkívül gyors vágás újrakódolás nélkül (`-c copy`), az eredeti videóminőség megőrzésével. Automatikusan beégeti a helyes megjelenítési képarányt (`-aspect`) az kimeneti konténerbe.
- **DaVinci Resolve Marker EDL Export**: A mentett vágási szakaszok exportálása időkód-pontos EDL fájlba, amely közvetlenül importálható DaVinci Resolve idővonal markerekiként.
- **Modern Sötét "Glass" UI**: Átlátszó panelekből álló, színkódolt szakaszkezelést biztosító felhasználói felület.

### Billentyűparancsok

| Billentyű | Funkció |
| :--- | :--- |
| `Space` | Lejátszás / Szünet |
| `I` | Kijelölés **Kezdőpontjának** (In) megadása a lejátszófejnél |
| `O` | Kijelölés **Végpontjának** (Out) megadása a lejátszófejnél |
| `Enter` / `Return` | Az aktív kijelölés elmentése a vágási listába |
| `Escape` | Aktív kijelölés megszakítása / törlése |
| `Delete` / `Backspace` | Kijelölt szakasz törlése a listából |
| `Balra` / `Jobbra` Nyíl | Léptetés 1 képkockát vissza / előre |
| `Alt` + `Balra` / `Jobbra` | Léptetés 20 képkockát vissza / előre |
| `Felfelé` / `Lefelé` Nyíl | Hullámforma nagyítása (Zoom In) / kicsinyítése (Zoom Out) |

### Telepítés és Használat

#### Előfeltételek
- Python 3.9+
- FFmpeg és FFprobe telepítve a rendszeren (vagy a `main.py` melletti `./bin/` mappába helyezve).

#### 1. Munkamenet Indítása
```bash
git clone https://github.com/your-username/cuteki.git
cd cuteki
```

#### 2. Függőségek Telepítése
```bash
pip install -r requirements.txt
```
*(Függőségek: `PyQt6`, `pyqtgraph`, `numpy`)*

#### 3. Alkalmazás Indítása
```bash
python main.py
```

#### 4. Marker Importálás DaVinci Resolve-ban
1. Hozz létre egy új idővonalat vagy nyiss meg egy meglévőt.
2. Kattints a jobb egérgombbal az idővonalra a **Media Pool**-ban.
3. Válaszd ki: **Timelines > Import > Timeline Markers from EDL...**
4. Tallózd be a CUTEKI által generált `.edl` fájlt.
