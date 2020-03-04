import ctypes
import os
import random

from songInfo import *
from functions import *

import time

import threading

from os.path import realpath
from tkinter.filedialog import askdirectory
from tkinter import *

from mutagen.id3 import ID3, ID3NoHeaderError
from mutagen.mp3 import MP3

# Initializing layout and mixer.
root = Tk()
init_root(root)
pygame.init()
mixer.pre_init(44100, 16, 2, 4096)
mixer.init()

# Loading images
play_image = PhotoImage(file="images/play_button.png").subsample(3)
pause_image = PhotoImage(file="images/pause_button.png").subsample(3)
next_song_image = PhotoImage(file="images/next_button.png").subsample(3)
stop_song_image = PhotoImage(file="images/next_button.png").subsample(3)
previous_song_image = PhotoImage(file="images/previous_button.png").subsample(3)
add_shuffling_image = PhotoImage(file="images/shuffle_button.png").subsample(12)
remove_shuffling_image = PhotoImage(file="images/remove_shuffle_button.png").subsample(12)

# Menu initialization
menu_bar = Menu(root)
root.config(menu=menu_bar)


def on_closing():
    mixer.music.stop()
    root.destroy()


def directory_chooser():
    global list_of_songs
    global real_names
    global list_directory
    global index

    # Reset lists.
    index = 0
    list_directory = []
    list_of_songs = []
    real_names = []

    directory = askdirectory()
    os.chdir(directory)
    list_directory.append(directory)
    print("LOADING SONGS FROM DIRECTORY AND SUB-DIRECTORIES.")
    find_songs_in_directory(directory)

    print("LOADING COMPLETE, ENJOY THE MUSIC")
    # Loading and starting the first song.
    play_new_music()

    add_songs_to_listbox()


def add_songs_to_listbox():
    listbox.delete(0, 'end')
    real_names.reverse()
    for song in real_names:
        listbox.insert(0, song)
    real_names.reverse()


# File - sub menu
sub_menu = Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="File", menu=sub_menu)
sub_menu.add_command(label="Open", command=directory_chooser)
sub_menu.add_command(label="Exit", command=on_closing)

# About us  - sub menu
sub_menu = Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="Help", menu=sub_menu)
sub_menu.add_command(label="About Us", command=about_us)

# Status bar at the bottom.
status_bar = Label(root, text="Welcome to PyPlayer", relief=SUNKEN, anchor=W)
status_bar.pack(side=BOTTOM, fill=X)

# Label at the top of the page.
label = Label(root, text='Songs list')
label.pack()

# List of songs.
listbox = Listbox(root, width=50)
listbox.pack(pady=10)

# Title of the song playing.
playing_song = StringVar()
song_name = Label(root, textvariable=playing_song, width=35)

# Frame containing buttons
bottom_frame = Frame(root)
bottom_frame.pack(pady=10)

# Time Playing of the current song.
song_time_playing = StringVar()
time_playing = Label(bottom_frame, textvariable=song_time_playing)

# Length of the song playing.
playing_song_length = StringVar()
song_length = Label(bottom_frame, textvariable=playing_song_length)

# Frame containing buttons
middle_frame = Frame(root)
middle_frame.pack(pady=10)

# Stop Song button
stop_button = Button(middle_frame, image=stop_song_image)
stop_button.grid(row=0, column=0, padx=10)

# Previous Song Button
previous_button = Button(middle_frame, image=previous_song_image)
previous_button.grid(row=0, column=1, padx=10)

# Play/Pause Song Button
play_pause_button = Button(middle_frame, image=pause_image)
play_pause_button.grid(row=0, column=2, padx=10)

# Next Song button
next_button = Button(middle_frame, image=next_song_image)
next_button.grid(row=0, column=3, padx=10)

# Add/Remove shuffle Button
shuffle_button = Button(middle_frame, image=add_shuffling_image)
shuffle_button.grid(row=0, column=4, padx=10)

# Volume bar
scale = Scale(root, from_=0, to=100, orient=HORIZONTAL, command=set_volume)
scale.set(70)
mixer.music.set_volume(0.7)
scale.pack()


def stop_song(event):
    mixer.music.set_endevent()
    mixer.music.stop()
    status_bar['text'] = "Music Stopped"
    play_pause_button['image'] = play_image


def next_song(event):
    global index
    global sound_running
    if shuffle_flag:
        if len(list_of_songs) > 1:
            select_new_index()
    else:
        index += 1
        if index >= len(list_of_songs):
            index = 0
    mixer.music.set_endevent()
    play_new_music()


def previous_song(event):
    global index
    global sound_running
    index -= 1
    if index < 0:
        index = len(list_of_songs) - 1
    mixer.music.set_endevent()
    play_new_music()


def switch_shuffle_flag(event):
    global shuffle_flag
    shuffle_button['image'] = add_shuffling_image if shuffle_flag else remove_shuffling_image
    shuffle_flag = not shuffle_flag


def play_pause_song(event):
    global sound_running
    if not mixer.music.get_busy():
        play_new_music()
    elif sound_running:
        play_pause_button['image'] = play_image
        mixer.music.pause()
        sound_running = False
        status_bar['text'] = "Music Paused"
    else:
        play_pause_button['image'] = pause_image
        mixer.music.unpause()
        sound_running = True
        status_bar['text'] = "Playing music"


def play_new_music():
    global list_of_songs
    global stop_thread
    mixer.music.stop()
    stop_thread = True
    os.chdir(list_of_songs[index].songPath)
    print("Index:", + index + 1)
    print("Play: " + list_of_songs[index].song)
    print("Title: " + real_names[index] + "\n")
    mixer.music.load(list_of_songs[index].song)
    mixer.music.play()
    mixer.music.set_endevent(NEXT)
    update_song_info()


def load_selected_song(event):
    global index
    selected_song = listbox.curselection()
    selected_song = int(selected_song[0])
    index = selected_song
    mixer.music.set_endevent()
    play_new_music()


def update_song_info():
    global sound_running
    global count_thread

    # Update status bar.
    status_bar['text'] = "Playing music"

    # Update play/pause button.
    play_pause_button['image'] = pause_image
    sound_running = True

    # Update song name.
    playing_song.set("Playing: " + real_names[index])

    # Update song Length.
    audio = MP3(list_of_songs[index].song)
    total_length = audio.info.length
    minutes, seconds = divmod(total_length, 60)
    minutes = round(minutes)
    seconds = round(seconds)
    time_format = '{:02d}:{:02d}'.format(minutes, seconds)
    playing_song_length.set("Total length - " + time_format)

    # create thread for increasing current time of the song.
    count_thread = threading.Thread(target=start_count, args=(total_length,))
    count_thread.start()


def start_count(length):
    global sound_running
    global stop_thread
    current_time = 1
    song_time_playing.set("Current Time - " + "00:00")
    time.sleep(1)
    stop_thread = False
    while current_time <= length and mixer.music.get_busy() and stop_thread is not True:
        if sound_running:
            minutes, seconds = divmod(current_time, 60)
            minutes = round(minutes)
            seconds = round(seconds)
            time_format = '{:02d}:{:02d}'.format(minutes, seconds)
            song_time_playing.set("Current Time - " + time_format)
            time.sleep(1)
            current_time += 1
        else:
            continue


def find_songs_in_directory(directory):
    global real_names
    global list_of_songs
    global list_directory

    mixer.music.set_endevent()

    # The directory is NOT empty
    if len(os.listdir(directory)) != 0:
        os.chdir(directory)

        # Browsing files in the directory
        for file in os.listdir(directory):

            # MP3 file found
            if file.endswith(".mp3"):
                song_path = os.path.realpath(file)

                # Store song name and directory
                song_file = songInfo(file, directory)
                list_of_songs.append(song_file)

                try:
                    audio = ID3(song_path)
                    if 'TIT2' in audio:
                        real_names.append(audio['TIT2'].text[0])
                    else:
                        real_names.append(song_file.song)
                except ID3NoHeaderError:
                    real_names.append(song_file.song)

            # Directory file found
            else:
                if os.path.isdir(file):
                    path = os.path.realpath(file)
                    list_directory.append(path)

                    # Browse in the directory recursively
                    find_songs_in_directory(path)

                    # set the directory back to the previous one to keep browsing
                    os.chdir(directory)


stop_button.bind("<Button-1>", stop_song)
next_button.bind("<Button-1>", next_song)
previous_button.bind("<Button-1>", previous_song)
play_pause_button.bind("<Button-1>", play_pause_song)
shuffle_button.bind("<Button-1>", switch_shuffle_flag)
listbox.bind("<<ListboxSelect>>", load_selected_song)

# Select the best songs directory
directory_chooser()

# Show playing song's name.
song_name.pack()
time_playing.grid(row=0, column=0, padx=10)
song_length.grid(row=0, column=1, padx=10)


def select_new_index():
    global index
    new_index = index
    while new_index == index:
        new_index = random.randrange(0, len(list_of_songs))
    index = new_index

def check_event():
    global index
    for event in pygame.event.get():
        if event.type == NEXT:
            if shuffle_flag:
                if len(list_of_songs) > 1:
                    select_new_index()
            else:
                if len(list_of_songs) > index + 1:
                    index += 1
                else:
                    index = 0
            play_new_music()

    root.after(100, check_event)

check_event()

root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()





