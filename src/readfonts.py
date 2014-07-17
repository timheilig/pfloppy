import os
import fontTools.cffLib
import fonts.builders
import argparse


def print_font(file_name):
    font_file = open(file_name, "rb")
    font = fontTools.cffLib.CFFFontSet()
    font.decompile(font_file, 'unused')
    new_font = fonts.builders.parse_file(file_name)
    for item in new_font:
        print item


parser = argparse.ArgumentParser(description='Parse and print font information')
parser.add_argument('--directory', help="treat file name as a directory structure to walk")
parser.add_argument('target', help="File or directory to open")
args = parser.parse_args()
if args.directory:
    for root, dirs, files in os.walk(args.target):
        for found_file in files:
            print_font(os.path.join(root, found_file))
else:
    print_font(args.target)

