#!/usr/bin/env python3

import argparse
import os
import shutil
import subprocess
import sys


#Get colors via imagemagick
def get_colors(fullpath):
	command = "convert {} -resize 25% +dither -colors 16 -unique-colors txt:- | grep -E -o \" \\#.{{6}}\"".format(fullpath)
	print("Extracting color scheme from wallpaper. This can take a few seconds.")
	output = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	colors = [i.strip() for i in output.communicate()[0].decode('utf-8').split('\n') if i.strip()]
	colors = colors[:1] + colors[9:] + colors[8:]

	# Get the best matching grey color
	grey_choices = {
        "0": "#666666",
        "1": "#666666",
        "2": "#757575",
        "3": "#999999",
        "4": "#999999",
        "5": "#8a8a8a",
        "6": "#a1a1a1",
        "7": "#a1a1a1",
        "8": "#a1a1a1",
        "9": "#a1a1a1",
	}
	colors[8] = grey_choices.get(colors[0][1], colors[7])
	colors = [line.strip().lstrip("#") for line in colors]
	deccolors = []

	#Convert colors to decimal RGB
	for hexcolor in colors:
		rgbcolor = tuple(int(hexcolor[i:i+2], 16) for i in (0, 2 ,4))
		deccolor = (rgbcolor[0]/255,rgbcolor[1]/255,rgbcolor[2]/255)
		deccolors.append(deccolor)
	return deccolors


#Set wallpaper
def set_wallpaper(filename):

	print("Setting wallpaper")
	command = "osascript -e 'tell application \"System Events\" to set picture of every desktop to (\"{}\" as POSIX file as alias)'".format(filename)
	subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)


#Create an iTerm2 color scheme
def make_iterm_colorscheme(colors, filename):

	print("Creating iTerm color scheme")
	specialcolors = (
					("Background Color", colors[0]),
					("Foreground Color", colors[15]),
					("Cursor Color", colors[15]),
					("Cursor Text Color", colors[0]),
					("Selection Color", colors[15]),
					("Selection Text Color", colors[0])
					)

	file = open("{}/{}.itermcolors".format(os.path.expanduser("~/Desktop"), os.path.splitext(filename)[0]), "w")
	file.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n")
	file.write("<!DOCTYPE plist PUBLIC \"-//Apple//DTD PLIST 1.0//EN\" \"http://www.apple.com/DTDs/PropertyList-1.0.dtd\">\n")
	file.write("<plist version=\"1.0\">\n")
	file.write("<dict>\n")
		
	#Write Ansi colors
	for id, color in enumerate(colors):
		file.write("\t<key>Ansi {} Color</key>\n".format(id))
		file.write("\t<dict>\n")
		file.write("\t\t<key>Blue Component</key>\n")
		file.write("\t\t<real>{}</real>\n".format(color[2]))
		file.write("\t\t<key>Green Component</key>\n")
		file.write("\t\t<real>{}</real>\n".format(color[1]))
		file.write("\t\t<key>Red Component</key>\n")
		file.write("\t\t<real>{}</real>\n".format(color[0]))
		file.write("\t</dict>\n")
		
	#Write Special colors
	for item, color in specialcolors:
		file.write("\t<key>{}</key>\n".format(item))
		file.write("\t<dict>\n")
		file.write("\t\t<key>Blue Component</key>\n")
		file.write("\t\t<real>{}</real>\n".format(color[2]))
		file.write("\t\t<key>Green Component</key>\n")
		file.write("\t\t<real>{}</real>\n".format(color[1]))
		file.write("\t\t<key>Red Component</key>\n")
		file.write("\t\t<real>{}</real>\n".format(color[0]))
		file.write("\t</dict>\n")

	file.write("</dict>\n")
	file.write("</plist>\n")
	file.close()


if __name__ == "__main__":
	#Check for imagemagick
	if not shutil.which("convert"):
		print("ERROR: Cannot find imagemagick")
		sys.exit()

	#Get command line arguments
	parser = argparse.ArgumentParser()
	parser.add_argument("-i", help="specify the path to the wallpaper/image file", required=True)
	parser.add_argument("-n", action="store_true", help="do not set wallpaper")
	args = parser.parse_args()

	#Check input file
	if args.i:
		allowed_formats = [".jpg", ".jpeg", ".png"]
		fullpath = args.i
		filename = os.path.basename(args.i)
		extension = os.path.splitext(filename)[1]
		if not extension in allowed_formats:
			print("ERROR: walmac only supports the following file formats: jpg, jpeg, png.")
			sys.exit()
	if args.n:
		print("Wallpaper will not be set automatically.")
	else:
		set_wallpaper(fullpath)

	make_iterm_colorscheme(get_colors(fullpath), filename)
