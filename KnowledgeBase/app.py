import tkinter as tk
from tkinter import *
from tkinter import ttk
from PIL import ImageTk, Image
from PyQt5 import QtGui 
import os
from core import Akinator


if __name__ == '__main__':

	print('Loading...')

	# init gui

	window = tk.Tk()
	window.title('White House Quiz')
	window.geometry("720x450")

	background_image = Image.open('data/img/bg.jpg')
	background_image = background_image.resize((720, 450), Image.ANTIALIAS)
	background_image = ImageTk.PhotoImage(background_image)
	background_label = tk.Label(window, image=background_image)
	background_label.place(x=0, y=0, relwidth=1, relheight=1)
	font_family = "Helvetica"

	gui_components = {
		'TEXT':					tk.Message(window, width = 350, font=(font_family, 14)), 
		'START_BUTTON': 		tk.Button(window, text="Start", font=(font_family, 12), width=10), 
		'PHOTO_PANEL': 			tk.Label(window, width=100, height=100),
		'ANSWER_BUTTON': 		tk.Button(window, text="Ok", font=(font_family, 12), width=10), 
		'NEW_GAME_BUTTON': 		tk.Button(window, text="Play again", font=(font_family, 12)),
		'CHOICE_COMBOBOX': 		ttk.Combobox(window, height=20, width=20, state="readonly", font=(font_family, 10)), 
		'CONTEXT_LISTBOX': 		tk.Listbox(window, font=(font_family, 12))
	}

	# run akinator

	akinator = Akinator(gui_components)
	akinator.load()
	window.mainloop()
