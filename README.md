# ocr2yomitan
Realtime Japanese OCR from **desktop** clipboard to web text output, for use with yomitan. Powered by Manga OCR.

The main purpose of ocr2yomitan is to extract text from apps, games and other sources to a constantly updated text format on a browser to be read by yomichan/yomitan.

It was created as a tool for Japanese learners that want to learn through games in Japanese, without having to use a mobile OCR or having to look up kanji by hand.

# Examples

<img src="https://i.imgur.com/oARckxH.png" alt="Demon's Souls OCR" width="800"/>

<img src="https://i.imgur.com/oQrDDCt.png" alt="Demon's Souls Translation" width="800"/>

# Usage

1. **Clone the repository**  
   ```bash
   git clone https://github.com/yourusername/ocr2yomitan.git
   cd ocr2yomitan
2. **Install dependencies**
    ```bash
    pip install -r requirements.txt
3. **Run OCR script**
    ```bash
    python jp_ocr.py
4. **Take screenshot**
   Use win + shift + s or cmd + shift + 4 to take an area screenshot.

**And you should see the site update!**

# Acknowledgements & Links

- [Manga OCR](https://github.com/kha-white/manga-ocr) — Japanese OCR engine used for text recognition.  
- [Yomitan](https://github.com/themoeway/yomitan) — Browser extension for dictionary lookups.  
