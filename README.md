# DataRescueX

DataRescueX is a simple and user-friendly file recovery tool built with Python and Tkinter. It allows you to scan drives, preview recoverable files, and recover selected files to a safe location.

---

## Features

- Scan selected drives for recoverable files
- Filter files by categories (Pictures, Music, Documents, Videos, Compressed, All Files)
- Deep Scan, Full Scan, Find Lost Files, and Scan Custom List options
- File preview for images and text files
- Select multiple files and recover them to a chosen folder
- Progress bar and real-time scan updates
- Customizable file extensions for scanning

---

## Requirements

- Python 3.7+
- Tkinter (usually included with Python)
- `psutil` package (`pip install psutil`)
- `Pillow` package for image preview (`pip install pillow`)

---

## Usage

1. Run the Python script:
   ```bash
   python datarescuex.py
   ```
2. Select a drive from the list.
3. Choose a file category or use the custom list.
4. Click **Scan** to start scanning the drive.
5. Select files from the results and click **Recover** to save them to a folder of your choice.
6. Use the preview pane to view image or text file previews.

---

## License

This project is licensed under the [MIT License](https://opensource.org/licenses/MIT).

---

## Author

Fahim Ahamed
