import tkinter as tk
from tkinter import messagebox, filedialog, ttk, Menu, Scale, Toplevel
import yt_dlp
import os
from PIL import Image, ImageTk
import urllib.request
from io import BytesIO
import threading
import json

cancel_download = False
current_download_file = None
blur_intensity = 85  # Default blur intensity for glass themes
blur_popup = None  # To track if popup is already open

CONFIG_FILE = "theme_config.json"

def get_unique_filename(folder, base_filename):
    name, ext = os.path.splitext(base_filename)
    counter = 1
    new_filename = base_filename
    while os.path.exists(os.path.join(folder, new_filename)):
        new_filename = f"{name}_{counter}{ext}"
        counter += 1
    return new_filename

def reset_all_fields():
    link_entry.delete(0, tk.END)
    title_display.config(text="Title: ")
    status_label.config(text="")
    download_status_label.config(text="")
    progress_bar["value"] = 0
    progress_label.config(text="Progress: 0%")
    placeholder_img = Image.new("RGB", (300, 200), color=current_theme_colors['thumbnail_bg'])
    thumbnail_img = ImageTk.PhotoImage(placeholder_img)
    thumbnail_canvas.create_image(0, 0, anchor="nw", image=thumbnail_img)
    thumbnail_canvas.image = thumbnail_img

def save_theme_preference():
    data = {"theme": current_theme, "blur_intensity": blur_intensity}
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f)

def load_theme_preference():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                data = json.load(f)
            return data.get("theme", "Dark"), data.get("blur_intensity", 85)
        except:
            pass
    return "Dark", 85

def show_blur_popup():
    global blur_popup
    if blur_popup and blur_popup.winfo_exists():
        return
    blur_popup = Toplevel(root)
    blur_popup.title("Blur Intensity")
    blur_popup.geometry("250x100")
    blur_popup.resizable(False, False)
    blur_popup.configure(bg=current_theme_colors['bg'])

    label = tk.Label(blur_popup, text="Adjust Blur Intensity:", bg=current_theme_colors['bg'], fg=current_theme_colors['fg'])
    label.pack(pady=5)

    scale = Scale(blur_popup, from_=10, to=100, orient="horizontal", command=set_blur_intensity)
    scale.set(blur_intensity)
    scale.pack(pady=5)

def set_blur_intensity(val):
    global blur_intensity
    blur_intensity = int(val)
    if "Glass" in current_theme:
        apply_theme(current_theme)

def apply_theme(theme):
    global current_theme_colors, current_theme
    themes = {
        "Dark": {"bg": "#2b2b2b", "fg": "white", "highlight": "#4caf50", "button": "#555555", "thumbnail_bg": "#444444", "alpha": 1},
        "Light": {"bg": "#f2f2f2", "fg": "black", "highlight": "#4caf50", "button": "#d9d9d9", "thumbnail_bg": "#d9d9d9", "alpha": 1},
        "Glass Dark": {"bg": "#2b2b2b", "fg": "white", "highlight": "#4caf50", "button": "#555555", "thumbnail_bg": "#333333", "alpha": blur_intensity/100},
        "Glass Light": {"bg": "#f2f2f2", "fg": "black", "highlight": "#4caf50", "button": "#d9d9d9", "thumbnail_bg": "#d9d9d9", "alpha": blur_intensity/100},
    }
    current_theme_colors = themes[theme]
    current_theme = theme
    save_theme_preference()

    root.configure(bg=current_theme_colors['bg'])
    root.attributes('-alpha', current_theme_colors['alpha'])
    for widget in [main_frame, thumb_frame, controls_frame]:
        widget.config(bg=current_theme_colors['bg'])
    title_display.config(bg=current_theme_colors['bg'], fg=current_theme_colors['fg'])
    status_label.config(bg=current_theme_colors['bg'], fg=current_theme_colors['highlight'])
    download_status_label.config(bg=current_theme_colors['bg'], fg=current_theme_colors['fg'])
    progress_label.config(bg=current_theme_colors['bg'], fg=current_theme_colors['fg'])
    link_label.config(bg=current_theme_colors['bg'], fg=current_theme_colors['fg'])
    type_frame.config(bg=current_theme_colors['bg'], fg=current_theme_colors['fg'])
    quality_frame.config(bg=current_theme_colors['bg'], fg=current_theme_colors['fg'])
    for child in type_frame.winfo_children() + quality_frame.winfo_children():
        child.config(bg=current_theme_colors['bg'], fg=current_theme_colors['fg'], selectcolor=current_theme_colors['thumbnail_bg'])
    reset_button.config(bg=current_theme_colors['button'], fg=current_theme_colors['fg'])
    paste_button.config(bg=current_theme_colors['button'], fg=current_theme_colors['fg'])
    download_button.config(bg="#4caf50", fg="white")
    cancel_button.config(bg="#f44336", fg="white")
    menu_button.config(bg=current_theme_colors['button'], fg=current_theme_colors['fg'])
    reset_all_fields()

def fetch_video_info(url):
    try:
        with yt_dlp.YoutubeDL({}) as ydl:
            info = ydl.extract_info(url, download=False)
            video_title = info.get('title', 'Unknown Title')
            thumbnail_url = info.get('thumbnail')

        def update_gui():
            title_display.config(text=video_title)
            if thumbnail_url:
                with urllib.request.urlopen(thumbnail_url) as u:
                    raw_data = u.read()
                im = Image.open(BytesIO(raw_data)).resize((300, 200))
                thumbnail_img = ImageTk.PhotoImage(im)
                thumbnail_canvas.create_image(0, 0, anchor="nw", image=thumbnail_img)
                thumbnail_canvas.image = thumbnail_img
            status_label.config(text="Video info fetched successfully!")

        root.after(0, update_gui)
    except Exception as e:
        root.after(0, lambda: messagebox.showerror("Error", f"Failed to fetch video info:\n{e}"))

def fetch_and_download():
    url = link_entry.get()
    if not url:
        messagebox.showwarning("Warning", "Please enter a YouTube link")
        return
    folder_selected = filedialog.askdirectory(title="Select Download Folder")
    if not folder_selected:
        return
    status_label.config(text="Fetching video info...")
    download_status_label.config(text="⏳ Download Starting...", fg="orange")
    progress_bar["value"] = 0
    progress_label.config(text="Progress: 0%")
    threading.Thread(target=fetch_video_info, args=(url,)).start()
    threading.Thread(target=start_download, args=(url, folder_selected)).start()

def start_download(url, folder_selected):
    try:
        mode = mode_var.get()
        quality = quality_var.get()

        if mode == "Audio Only":
            format_selection = "bestaudio[ext=m4a]/bestaudio"
        else:
            if quality == "Best":
                format_selection = "bestvideo+bestaudio/best"
            elif quality == "1080p":
                format_selection = "bestvideo[height<=1080]+bestaudio/best"
            elif quality == "720p":
                format_selection = "bestvideo[height<=720]+bestaudio/best"
            elif quality == "480p":
                format_selection = "bestvideo[height<=480]+bestaudio/best"
            elif quality == "360p":
                format_selection = "bestvideo[height<=360]+bestaudio/best"
            elif quality == "240p":
                format_selection = "bestvideo[height<=240]+bestaudio/best"
            else:
                format_selection = "bestvideo+bestaudio/best"

            if mode == "Video Only":
                format_selection = format_selection.replace("+bestaudio", "")

        ydl_opts = {
            'format': format_selection,
            'outtmpl': os.path.join(folder_selected, '%(title)s.%(ext)s'),
            'progress_hooks': [progress_hook]
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            filename = ydl.prepare_filename(info)
            base_filename = os.path.basename(filename)
            unique_filename = get_unique_filename(folder_selected, base_filename)
            ydl_opts['outtmpl'] = os.path.join(folder_selected, unique_filename)

            with yt_dlp.YoutubeDL(ydl_opts) as ydl_final:
                ydl_final.download([url])

        root.after(0, lambda: download_status_label.config(text="✅ Download Completed!", fg="lightgreen"))

    except Exception as e:
        root.after(0, lambda: messagebox.showerror("Error", f"Download Error:\n{e}"))

def progress_hook(d):
    if d['status'] == 'downloading':
        total = d.get('total_bytes') or d.get('total_bytes_estimate')
        downloaded = d.get('downloaded_bytes', 0)
        if total:
            percent = downloaded / total * 100
            progress_bar["value"] = percent
            progress_label.config(text=f"Progress: {percent:.2f}%")
    elif d['status'] == 'finished':
        progress_bar["value"] = 100
        progress_label.config(text="Download Completed!")

def show_theme_menu(event=None):
    theme_menu.post(menu_button.winfo_rootx(), menu_button.winfo_rooty() + menu_button.winfo_height())

def paste_link():
    try:
        link_entry.delete(0, tk.END)
        link_entry.insert(0, root.clipboard_get())
    except:
        pass

root = tk.Tk()
root.title("YouTube Downloader")
root.geometry("820x600")
root.minsize(820, 500)

current_theme_colors = {}
current_theme, blur_intensity = load_theme_preference()

menu_button = tk.Button(root, text="☰ Theme", command=show_theme_menu, font=("Arial", 12, "bold"))
menu_button.place(x=-9, y=10, width=90, height=35)

main_frame = tk.Frame(root)
main_frame.pack(fill="both", expand=True, padx=20)

thumb_frame = tk.Frame(main_frame)
thumb_frame.pack(side="left", padx=10, pady=10)

thumbnail_canvas = tk.Canvas(thumb_frame, width=300, height=200)
thumbnail_canvas.pack()

title_display = tk.Label(thumb_frame, text="Title: ", font=("Arial", 11, "bold"), wraplength=300, justify="center")
title_display.pack(pady=8)

controls_frame = tk.Frame(main_frame)
controls_frame.pack(side="right", fill="both", expand=True, padx=10)

link_label = tk.Label(controls_frame, text="YouTube Link:", font=("Arial", 12))
link_label.pack(anchor="w", pady=5)

link_entry = tk.Entry(controls_frame, font=("Arial", 11), width=35)
link_entry.pack(pady=2)

btn_frame = tk.Frame(controls_frame)
btn_frame.pack(pady=5)

reset_button = tk.Button(btn_frame, text="Reset", width=10, command=reset_all_fields)
reset_button.pack(side="left", padx=5)

paste_button = tk.Button(btn_frame, text="Paste", width=10, command=paste_link)
paste_button.pack(side="left", padx=5)

status_label = tk.Label(controls_frame, text="", font=("Arial", 11))
status_label.pack(pady=5)

type_frame = tk.LabelFrame(controls_frame, text="Download Type", padx=10, pady=5)
type_frame.pack(fill="x", pady=5)

mode_var = tk.StringVar(value="Video + Audio")
tk.Radiobutton(type_frame, text="Video + Audio", variable=mode_var, value="Video + Audio").pack(anchor="w")
tk.Radiobutton(type_frame, text="Video Only", variable=mode_var, value="Video Only").pack(anchor="w")
tk.Radiobutton(type_frame, text="Audio Only", variable=mode_var, value="Audio Only").pack(anchor="w")

quality_frame = tk.LabelFrame(controls_frame, text="Quality", padx=10, pady=5)
quality_frame.pack(fill="x", pady=5)

quality_var = tk.StringVar(value="Best")
tk.Radiobutton(quality_frame, text="Best", variable=quality_var, value="Best").pack(anchor="w")
tk.Radiobutton(quality_frame, text="1080p", variable=quality_var, value="1080p").pack(anchor="w")
tk.Radiobutton(quality_frame, text="720p", variable=quality_var, value="720p").pack(anchor="w")
tk.Radiobutton(quality_frame, text="480p", variable=quality_var, value="480p").pack(anchor="w")
tk.Radiobutton(quality_frame, text="360p", variable=quality_var, value="360p").pack(anchor="w")
tk.Radiobutton(quality_frame, text="240p", variable=quality_var, value="240p").pack(anchor="w")

download_button = tk.Button(controls_frame, text="⬇️ Start Download", command=fetch_and_download)
download_button.pack(pady=5)

cancel_button = tk.Button(controls_frame, text="❌ Cancel Download")
cancel_button.pack(pady=5)

download_status_label = tk.Label(controls_frame, text="", font=("Arial", 11, "bold"))
download_status_label.pack(pady=5)

progress_label = tk.Label(controls_frame, text="Progress: 0%", font=("Arial", 11))
progress_label.pack(pady=5)

style = ttk.Style()
style.theme_use('clam')
style.configure("TProgressbar", foreground="#4caf50", background="#4caf50")

progress_bar = ttk.Progressbar(controls_frame, orient="horizontal", length=300, mode="determinate")
progress_bar.pack()

theme_menu = Menu(root, tearoff=0)
theme_menu.add_command(label="Dark Theme", command=lambda: apply_theme("Dark"))
theme_menu.add_command(label="Light Theme", command=lambda: apply_theme("Light"))
theme_menu.add_command(label="Blur Glass Dark", command=lambda: apply_theme("Glass Dark"))
theme_menu.add_command(label="Blur Glass White", command=lambda: apply_theme("Glass Light"))
theme_menu.add_separator()
theme_menu.add_command(label="Adjust Blur Intensity", command=show_blur_popup)

apply_theme(current_theme)
root.mainloop()
