# Book diagrams (TikZ)

The flowcharts, chapter maps and schematics of the book are drawn with XeLaTeX/TikZ from Python:

- `tk.py` – small toolkit (right-to-left Arabic text, cards, connectors, one colour identity)
- `figs_flow.py` – book roadmap, workflow flowchart, monitoring and retrieval pipelines, digital-twin levels
- `figs_tech.py` – the 18 chapter maps and the technical schematics (k-fold, confusion matrix, CNN, U-Net, slope, signal plan, corrosion set-up)

Requirements: XeLaTeX with TikZ, `pdftoppm`, and the IBM Plex Sans Arabic fonts (Regular, SemiBold) in a folder given by `BOOK_FONTS`.

    BOOK_FONTS=/path/to/fonts BOOK_FIG_OUT=../../../figures python3 figs_flow.py
    BOOK_FONTS=/path/to/fonts BOOK_FIG_OUT=../../../figures python3 figs_tech.py
