import tkinter
import pygame
from tkinter import messagebox, PhotoImage

NEXT = pygame.USEREVENT + 0
casual = False
index = 0
sound_running = True
stop_thread = False
mixer = pygame.mixer
list_directory = []
list_of_songs = []
real_names = []


def init_root(root):
    root.minsize(400, 400)
    root.title("PyPlayer")
    root.iconbitmap(r'Logo.ico')


def about_us():
    tkinter.messagebox.showinfo('About PyPlayer', 'This is a music player application build with Python Tkinter by '
                                                      'Geghi.')


def set_volume(value):
    volume = int(value) / 100
    mixer.music.set_volume(volume)


def queue_song():
    mixer.music.queue(list_of_songs[index + 1])



