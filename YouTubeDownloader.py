import tkinter as tk
from tkinter import filedialog, ttk
import pandas as pd
from pytube import YouTube, Playlist
import os
import threading

# Initialize the main window
root = tk.Tk()
root.title("YouTube Video Downloader")

# Set default download directory
download_directory = os.getcwd()

def set_download_directory():
    global download_directory
    directory = filedialog.askdirectory()
    if directory:
        download_directory = directory
        label_feedback.config(text=f"Download directory set to: {download_directory} ✅")

def load_csv():
    filepath = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if filepath:
        entry_csv_file.delete(0, tk.END)
        entry_csv_file.insert(0, filepath)

def update_label(message):
    label_feedback.config(text=message)

def show_progress(stream, chunk, bytes_remaining):
    total_size = stream.filesize
    bytes_downloaded = total_size - bytes_remaining
    percentage_of_completion = int((bytes_downloaded / total_size) * 100)
    update_label(f"Downloading... {percentage_of_completion}% of the video 🔄")

def download_video():
    url = entry_video_url.get()
    resolution = combo_resolution.get()
    try:
        yt = YouTube(url, on_progress_callback=show_progress)
        stream = yt.streams.filter(res=resolution, file_extension='mp4').first()
        if stream:
            stream.download(download_directory)
            update_label("Video downloaded successfully! ✅")
        else:
            update_label("Requested resolution not available. ❌")
    except Exception as e:
        update_label(f"Error: {str(e)} ❌")

def download_playlist():
    url = entry_playlist_url.get()
    resolution = combo_playlist_resolution.get()
    try:
        pl = Playlist(url)
        folder_name = pl.title
        path = os.path.join(download_directory, folder_name)
        os.makedirs(path, exist_ok=True)
        total_videos = len(pl.video_urls)
        for i, video in enumerate(pl.videos, start=1):
            yt = YouTube(video.watch_url, on_progress_callback=show_progress)
            yt.streams.filter(res=resolution, file_extension='mp4').first().download(path)
            update_label(f"Playlist video {i}/{total_videos} downloaded successfully! ✅")
    except Exception as e:
        update_label(f"Error: {str(e)} ❌")

def start_csv_download():
    resolution = combo_csv_resolution.get()
    file_path = entry_csv_file.get()
    try:
        df = pd.read_csv(file_path)
        folder_name = os.path.basename(file_path).split('.')[0]
        path = os.path.join(download_directory, folder_name)
        os.makedirs(path, exist_ok=True)
        total_videos = len(df['URL'])
        for i, url in enumerate(df['URL'], start=1):
            yt = YouTube(url, on_progress_callback=show_progress)
            yt.streams.filter(res=resolution, file_extension='mp4').first().download(path)
            update_label(f"CSV video {i}/{total_videos} downloaded successfully! ✅")
    except Exception as e:
        update_label(f"Error: {str(e)} ❌")

def threaded_download(function, *args):
    thread = threading.Thread(target=function, args=args)
    thread.daemon = True
    thread.start()

# Create notebook for separate tabs
notebook = ttk.Notebook(root)
tab1 = ttk.Frame(notebook)
tab2 = ttk.Frame(notebook)
tab3 = ttk.Frame(notebook)
notebook.add(tab1, text="Download Video")
notebook.add(tab2, text="Download Playlist")
notebook.add(tab3, text="Download from CSV")
notebook.pack(expand=True, fill="both")

# Common resolutions
resolutions = ["144p", "240p", "360p", "480p", "720p", "1080p", "1440p", "2160p"]

# Tab 1: Download single video
tk.Label(tab1, text="Enter Video URL:").pack()
entry_video_url = tk.Entry(tab1, width=50)
entry_video_url.pack()
tk.Label(tab1, text="Select Resolution:").pack()
combo_resolution = ttk.Combobox(tab1, values=resolutions, state="readonly")
combo_resolution.set("720p")  # Set default value
combo_resolution.pack()
tk.Button(tab1, text="Download Video", command=lambda: threaded_download(download_video)).pack()

# Tab 2: Download playlist
tk.Label(tab2, text="Enter Playlist URL:").pack()
entry_playlist_url = tk.Entry(tab2, width=50)
entry_playlist_url.pack()
tk.Label(tab2, text="Select Resolution:").pack()
combo_playlist_resolution = ttk.Combobox(tab2, values=resolutions, state="readonly")
combo_playlist_resolution.set("720p")  # Set default value
combo_playlist_resolution.pack()
tk.Button(tab2, text="Download Playlist", command=lambda: threaded_download(download_playlist)).pack()

# Tab 3: Download from CSV
tk.Label(tab3, text="Select CSV File:").pack()
entry_csv_file = tk.Entry(tab3, width=50)
entry_csv_file.pack()
tk.Button(tab3, text="Load CSV", command=load_csv).pack()
tk.Label(tab3, text="Select Resolution for CSV Downloads:").pack()
combo_csv_resolution = ttk.Combobox(tab3, values=resolutions, state="readonly")
combo_csv_resolution.set("720p")  # Set default value
combo_csv_resolution.pack()
tk.Button(tab3, text="Start CSV Download", command=lambda: threaded_download(start_csv_download)).pack()

# Feedback label
label_feedback = tk.Label(root, text="Ready to download. 🔄")
label_feedback.pack()

# Set download directory button
tk.Button(root, text="Set Download Directory", command=set_download_directory).pack()

root.mainloop()
