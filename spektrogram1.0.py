import matplotlib
matplotlib.use("TkAgg")
from matplotlib import style
style.use('ggplot')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

import tkinter as tk
from tkinter import ttk
from tkinter import Tk, Label, Button, Menu, messagebox

LARGE_FONT= ("Verdana", 12)

from random import *
from pylab import *
from matplotlib import *
from tkinter import *
import wave
import sys
from scipy.io import wavfile
from scipy import signal
from tkinter import Tk
from tkinter.filedialog import askopenfilename
import sys
from PIL import ImageTk, Image
from PIL.Image import core as image

class my_specgram():

	def __init__(self, f, x, NFFT=256, Fs=2, Fc=0, detrend=mlab.detrend_none,
		window=mlab.window_hanning, noverlap=128,
		cmap=None, xextent=None, pad_to=None, sides='default',
		scale_by_freq=None, minfreq = None, maxfreq = None, **kwargs):
		self.x=x
		self.NFFT=NFFT
		self.Fs=Fs
		self.Fc=Fc
		self.detrend=detrend
		self.window=window
		self.cmap=cmap
		self.noverlap=noverlap
		self.pad_to=pad_to
		self.sides=sides 
		self.scale_by_freq=scale_by_freq
		self.kwargs=kwargs
		self.f=f
		self.xextent=xextent
		self.ax = gca()
		self.Pxx, self.freqs, self.bins = mlab.specgram(x, NFFT, Fs, detrend,
			window, noverlap, pad_to, sides, scale_by_freq)


		if minfreq is not None and maxfreq is not None:
			self.Pxx = self.Pxx[(self.freqs >= minfreq) & (self.freqs <= maxfreq)]
			self.freqs = self.freqs[(self.freqs >= minfreq) & (self.freqs <= maxfreq)]

		self.Z = 10. * np.log10(self.Pxx)
		self.Z = np.flipud(self.Z)
		self.ax=subplot(212)
		if self.xextent is None: self.xextent = 0, np.amax(self.bins)
		self.xmin, self.xmax = self.xextent
		self.freqs += self.Fc
		self.extent = self.xmin, self.xmax, self.freqs[0], self.freqs[-1]
		self.a=self.f.add_subplot(212, sharex=self.ax)
		self.a.imshow(self.Z, self.cmap, extent=self.extent, **kwargs)
		self.ax.axis('auto')
		self.a.axis('auto')
		



class Sonogram(tk.Frame):
	def __init__(self, parent, controller, wav_file, startsecs=None, endsecs=None):
		'''Plot a sonogram for the given file,
		optionally specifying the start and end time in seconds.
		'''
		tk.Frame.__init__(self, parent)
		wav = wave.open(wav_file, 'r')
		frames = wav.readframes(-1)
		self.frame_rate = wav.getframerate()
		self.chans = wav.getnchannels()
		secs = wav.getnframes() / float(self.frame_rate)
		self.sound_info = pylab.fromstring(frames, 'Int16')
		wav.close()

		if startsecs or endsecs:
			if not startsecs:
				startsecs = 0.0
			if not endsecs:
				endsecs = secs - startsecs

			startpos = startsecs * self.frame_rate * self.chans
			endpos = endsecs * self.frame_rate * self.chans
			self.sound_info = self.sound_info[startpos:endpos]
			secs = endsecs - startsecs
		else:
			startsecs = 0.0

		t = arange(startsecs, startsecs + secs, 1.0 / self.frame_rate / self.chans)

		self.ax1 = subplot(211)
		title(wav_file)


		self.f = Figure(figsize=(5,5), dpi=100)
		self.a = self.f.add_subplot(211, sharex=self.ax1)
		self.a.plot(t, self.sound_info)
		
		self.spec = my_specgram(self.f,self.sound_info, 
		 Fs=self.frame_rate*self.chans,
										# cmap=cm.Accent,
										minfreq = 0, maxfreq = 10000)
		self.canvas = FigureCanvasTkAgg(self.f, self)
		self.canvas.draw()
		toolbar = NavigationToolbar2Tk( self.canvas, self )
		toolbar.update()
		self.canvas._tkcanvas.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
		
		
	def Update(self,NFFT, nwindow=mlab.window_hanning, overlap=128):
		self.spec=my_specgram(self.f,self.sound_info, 
		NFFT=NFFT, window=nwindow, noverlap=overlap,
		 Fs=self.frame_rate*self.chans, minfreq = 0, maxfreq = 10000)
		self.canvas.draw()
		self.canvas._tkcanvas.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
	def get_sound_info(self):
		return self.sound_info



class Application(tk.Tk):

	def __init__(self, *args, **kwargs):
		
		self.NFFT=256
		self.lap=128
		self.window=mlab.window_hanning
		tk.Tk.__init__(self, *args, **kwargs)

		tk.Tk.wm_title(self, "Sonogram i spektrogram")
		self.container = tk.Frame(self)
		self.container.pack(side="top", fill="both", expand = True)
		self.container.grid_rowconfigure(0, weight=1)
		self.container.grid_columnconfigure(0, weight=1)
		

		frame = StartPage(self.container, self)

		frame.grid(row=0, column=0, sticky="nsew")
		frame.tkraise()
		self.choose_file()
		
		
		menubar = Menu(self)
		filemenu = Menu(menubar, tearoff=0)
		editmenu = Menu(menubar, tearoff=0)
		bandmenu = Menu(editmenu, tearoff=0)
		windowmenu = Menu(editmenu, tearoff=0)
		menubar.add_cascade(label="Plik", menu=filemenu)
		filemenu.add_command(label="Załaduj plik", command=self.choose_file)
		menubar.add_cascade(label="Edytuj", menu=editmenu)
		editmenu.add_cascade(label="Rodzaj okna", menu=windowmenu)
		windowmenu.add_command(label="Hanning", command=self.hanning)
		windowmenu.add_command(label="Blackman", command=self.blackman)
		windowmenu.add_command(label="Hamming", command=self.hamming)
		windowmenu.add_command(label="Bartlett", command=self.bartlett)
		editmenu.add_command(label="Długość zakładki", command=self.len_overlap)
		editmenu.add_command(label="Długość sygnału", command=self.len_NFFT)
		menubar.add_command(label="Zakończ", command=self.quit)
		self.config(menu=menubar)

		self.title("Menu")
		self.geometry("100x100")
		self.minsize(800,600)
		
		
		
	def choose_file(self):
			Tk().withdraw() 
			filename = askopenfilename()
			self.sonogram = Sonogram(self.container, self, filename)
			self.sonogram.grid(row=0, column=0, sticky="nsew")
			self.sonogram.tkraise()
	def update(self):
		self.sonogram.Update(NFFT=self.NFFT, nwindow=self.window, overlap=self.lap)
	def hamming(self):
		self.window=numpy.hamming(self.NFFT)
		self.update()
	def hanning(self):
		self.window=mlab.window_hanning
		self.update()
	def blackman(self):
		self.window=numpy.blackman(self.NFFT)
		self.update()
	def bartlett(self):
		self.window=numpy.bartlett(self.NFFT)
		self.update()
	def len_overlap(self):
		try:
			self.child = GetData(tk.Toplevel(self), self, "Długość zakładki", self.lap, self.NFFT)
		except ValueError:
			messagebox.showerror("Błąd", "Błędne dane")
		self.update()
	def len_NFFT(self):
		try:
			self.child = GetData(tk.Toplevel(self), self, "Długość sygnału", self.lap, self.NFFT)
		except ValueError:
			messagebox.showerror("Błąd", "Błędne dane")
		self.update()
		print("update")
	def set_lap(self, lap):
		if lap < self.NFFT and lap >= 0:
			self.lap = lap
			self.update()
	def set_NFFT(self, NFFT):
		if NFFT > self.lap:
			self.NFFT = NFFT
			self.update()
class GetData(tk.Frame):
	def __init__(self, master,root, tekst, lap, NFFT):
		Frame.__init__(self, master)
		self.lap=lap
		self.NFFT = NFFT
		self.tekst = tekst
		self.master = master
		self.root = root
		self.master.title("Pobieranie danych")
		self.createWidgets()
		
	def createWidgets(self):
		Label(self.master, text=self.tekst).grid(row=0)

		self.e1 = Entry(self.master)

		self.e1.grid(row=0, column=1)

		self.okBtn = Button(self.master)
		self.okBtn["text"] = "OK",
		self.okBtn["command"] = self.okAction
		self.okBtn.grid(row=0,column=3)
		
	def okAction(self):
		try:
			first = int(self.e1.get())
			if self.tekst == "Długość zakładki" and (first >= self.NFFT or first < 0):
				messagebox.showerror("Błąd", "Podaj liczbę większą od zera i mniejszą od "+
				str(self.NFFT)+" lub zmień długość sygnału.")
				self.master.destroy()
			if self.tekst == "Długość sygnału" and (first <= self.lap):
				messagebox.showerror("Błąd", "Podaj liczbę większą od "+
				str(self.lap)+" lub zmień długość zakładki.")
				self.master.destroy()
		except ValueError:
			messagebox.showerror("Błąd", "Błędne dane")
			self.master.destroy()
		try:
			self.result = first
			if self.tekst == "Długość zakładki":
				self.root.set_lap(first)
			if self.tekst == "Długość sygnalu":
				self.root.set_NFFT(first)
		except UnboundLocalError:
			error=1
		self.master.destroy()
		
	def cancelAction(self):
		sys.exit()

class StartPage(tk.Frame):

	def __init__(self, parent, controller):
		tk.Frame.__init__(self,parent)
		label = tk.Label(self, text="Jeśli widzisz ten napis musisz wczytać plik .wav z dysku", font=LARGE_FONT)
		label.pack(pady=10,padx=10)


app = Application()
app.mainloop()
