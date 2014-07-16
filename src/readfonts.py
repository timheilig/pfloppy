import os
import pdfbox.fonts.builders


for root, dirs, files in os.walk('/Library/WebServer/Documents/font-images.pdf'):
    if root.endswith('build'):
        for found_file in files:
            if found_file.endswith('pfa'):
                pdfbox.fonts.builders.parse_file(os.path.join(root, found_file))
        print root, dirs, files
