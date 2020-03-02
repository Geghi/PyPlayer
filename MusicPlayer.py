import os

from songInfo import *
from functions import *
from os.path import realpath
from tkinter.filedialog import askdirectory

from mutagen.id3 import ID3
from tkinter import *

# Initializing layout and mixer.
root = Tk()
init_root(root)
mixer.init()

# Loading images
play_image = PhotoImage(file="images/play_button.png").subsample(3)
pause_image = PhotoImage(file="images/pause_button.png").subsample(3)
next_song_image = PhotoImage(file="images/next_button.png").subsample(3)
previous_song_image = PhotoImage(file="images/previous_button.png").subsample(3)

# Menu initialization
menu_bar = Menu(root)
root.config(menu=menu_bar)

# File sub menu
sub_menu = Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="File", menu=sub_menu)
sub_menu.add_command(label="Open")
sub_menu.add_command(label="Exit", command=root.destroy)

# About us sub menu
sub_menu = Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="Help", menu=sub_menu)
sub_menu.add_command(label="About Us", command=about_us)

# Status bar at the bottom.
status_bar = Label(root, text="Welcome to PyPlayer", relief=SUNKEN, anchor=W)
status_bar.pack(side=BOTTOM, fill=X)

# Label at the top of the page.
label = Label(root, text='Song list')
label.pack()

# List of songs.
listbox = Listbox(root, width=50)
listbox.pack(pady=10)

# Title of the song playing.
playing_song = StringVar()
song_name = Label(root, textvariable=playing_song, width=35)

# Frame containing buttons
middle_frame = Frame(root)
middle_frame.pack(pady=10)

# Previous Song Button
previous_button = Button(middle_frame, image=previous_song_image)
previous_button.grid(row=0, column=0, padx=10)

# Play/Pause Song Button
play_pause_button = Button(middle_frame, image=pause_image)
play_pause_button.grid(row=0, column=1, padx=10)

# Next Song button
next_button = Button(middle_frame, image=next_song_image)
next_button.grid(row=0, column=2, padx=10)

# Volume bar
scale = Scale(root, from_=0, to=100, orient=HORIZONTAL, command=set_volume)
scale.set(70)
mixer.music.set_volume(0.7)
scale.pack()


def next_song(event):
    global index
    global sound_running
    index += 1
    if index >= len(list_of_songs):
        index = 0
    load_song(list_of_songs)


def previous_song(event):
    global index
    global sound_running
    index -= 1
    if index < 0:
        index = len(list_of_songs) - 1
    load_song(list_of_songs)


def play_pause_song(event):
    global sound_running
    if sound_running:
        play_pause_button['image'] = play_image
        mixer.music.pause()
        sound_running = False
        status_bar['text'] = "Music Paused"
    else:
        play_pause_button['image'] = pause_image
        mixer.music.unpause()
        sound_running = True
        status_bar['text'] = "Playing music"


def load_song(songs):
    global sound_running
    os.chdir(songs[index].songPath)
    mixer.music.load(songs[index].song)
    mixer.music.play()
    update_song_label()
    status_bar['text'] = "Playing music"
    play_pause_button['image'] = pause_image
    sound_running = True


def update_song_label():
    playing_song.set(real_names[index])
    return song_name


def find_songs(directory):
    global real_names
    global list_of_songs
    global list_directory

    # The directory is NOT empty
    if len(os.listdir(directory)) != 0:
        os.chdir(directory)

        # Browsing files in the directory
        for file in os.listdir(directory):

            # MP3 file found
            if file.endswith(".mp3"):
                song_path = os.path.realpath(file)
                audio = ID3(song_path)
                real_names.append(audio['TIT2'].text[0])

                # Store song name and directory
                song_file = songInfo(file, directory)
                list_of_songs.append(song_file)

            # Directory file found
            else:
                if os.path.isdir(file):
                    path = os.path.realpath(file)
                    list_directory.append(path)

                    # Browse in the directory recursively
                    find_songs(path)

                    # set the directory back to the previous one to keep browsing
                    os.chdir(directory)


def directory_chooser():
    directory = askdirectory()
    os.chdir(directory)
    list_directory.append(directory)
    print("LOADING SONGS FROM DIRECTORY AND SUB-DIRECTORIES.")
    find_songs(directory)

    print("LOADING COMPLETE, ENJOY THE MUSIC")
    # Initialize Mixer
    load_song(list_of_songs)


next_button.bind("<Button-1>", next_song)
previous_button.bind("<Button-1>", previous_song)
play_pause_button.bind("<Button-1>", play_pause_song)

# Select the best songs directory
directory_chooser()

# Show the list of songs
real_names.reverse()
for song in real_names:
    listbox.insert(0, song)
real_names.reverse()

# Show playing song's name.
song_name.pack()

root.mainloop()
