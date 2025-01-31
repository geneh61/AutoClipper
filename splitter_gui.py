import os
import threading
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox
from pydub import AudioSegment
from pydub.silence import detect_nonsilent


def select_file():
    file_path = filedialog.askopenfilename(filetypes=[("Video Files", "*.mp4 *.mkv *.mov *.avi *.flv *.wmv")])
    if file_path:
        entry_video_path.delete(0, tk.END)
        entry_video_path.insert(0, file_path)

def select_output_folder():
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        entry_output_dir.delete(0, tk.END)
        entry_output_dir.insert(0, folder_selected)

def process_video():
    video_path = entry_video_path.get()
    output_dir = entry_output_dir.get()
    min_segment_length = int(entry_min_segment.get())
    max_segment_length = int(entry_max_segment.get())
    auto_threshold = auto_threshold_var.get()
    
    if not video_path:
        messagebox.showerror("Error", "Please select a video file.")
        return
    
    if not output_dir:
        output_dir = "clips"
    os.makedirs(output_dir, exist_ok=True)
    
    log_text.set("Extracting audio...")
    window.update()
    
    print("1")
    # extract audio
    temp_audio_path = "splitter_temp_audio.wav"
    subprocess.run(["ffmpeg", "-i", video_path, "-vn", "-ac", "1", "-ar", "16000", "-f", "wav", "splitter_temp_audio.wav"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    audio = AudioSegment.from_wav("splitter_temp_audio.wav")
    os.remove(temp_audio_path)

    
    print("2")
    # calc volume threshold
    if auto_threshold:
        loudness = audio.dBFS  
        volume_threshold = max(loudness - 20, -60)  # limit threshold
        log_text.set(f"Detected avg volume: {loudness:.2f} dB, setting threshold to {volume_threshold:.2f} dB")
    else:
        volume_threshold = int(entry_volume_threshold.get())
    
    window.update()
    
    print("3")
    log_text.set("Detecting loud parts...")
    window.update()
    
    loud_segments = detect_nonsilent(audio, min_silence_len=min_segment_length, silence_thresh=volume_threshold, seek_step=10)
    clip_timestamps = [(start / 1000, end / 1000) for start, end in loud_segments if (end - start) <= max_segment_length]
    
    print("4")
    if not clip_timestamps:
        log_text.set("⚠️ No loud segments detected. Try adjusting the threshold or min segment length.")
        return
    
    log_text.set(f"Found {len(clip_timestamps)} clips. Splitting video...")
    window.update()
    
    print("5")

    for i, (start, end) in enumerate(clip_timestamps):
        output_filename = os.path.join(output_dir, f"clip_{i+1}.mp4")
        duration = end - start  # clip len
        
        command = [
            "ffmpeg", "-ss", str(start), "-i", video_path,
            "-c:v", "libx264", "-preset", "fast", "-crf", "23",
            "-c:a", "aac", "-b:a", "128k",
            "-t", str(duration),
            "-movflags", "+faststart", "-y", output_filename
        ]
        subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    log_text.set(f"✅ Done! {len(clip_timestamps)} clips saved in '{output_dir}'")
    window.update()

def start_processing():
    threading.Thread(target=process_video, daemon=True).start()

def open_output_folder():
    output_dir = entry_output_dir.get()
    if os.path.exists(output_dir):
        os.startfile(output_dir) if os.name == "nt" else subprocess.run(["open", output_dir] if os.name == "darwin" else ["xdg-open", output_dir])
    else:
        messagebox.showerror("Error", "No output folder found.")

# GUI
window = tk.Tk()
window.title("Video Splitter by Volume")
window.geometry("600x650")

tk.Label(window, text="Select Video:").pack(pady=5)
entry_video_path = tk.Entry(window, width=50)
entry_video_path.pack(pady=5)
tk.Button(window, text="Browse", command=select_file).pack(pady=5)

tk.Label(window, text="Select Output Folder:").pack(pady=5)
entry_output_dir = tk.Entry(window, width=50)
entry_output_dir.pack(pady=5)
tk.Button(window, text="Browse", command=select_output_folder).pack(pady=5)

tk.Label(window, text="Volume Threshold (dB, e.g., -30):").pack(pady=5)
entry_volume_threshold = tk.Entry(window)
entry_volume_threshold.pack(pady=5)
entry_volume_threshold.insert(0, "-30")

auto_threshold_var = tk.IntVar()
tk.Checkbutton(window, text="Auto-Detect Threshold", variable=auto_threshold_var).pack(pady=5)

tk.Label(window, text="Min Loud Segment Length (ms):").pack(pady=5)
entry_min_segment = tk.Entry(window)
entry_min_segment.pack(pady=5)
entry_min_segment.insert(0, "700")

tk.Label(window, text="Max Loud Segment Length (ms):").pack(pady=5)
entry_max_segment = tk.Entry(window)
entry_max_segment.pack(pady=5)
entry_max_segment.insert(0, "10000")

tk.Button(window, text="Start Processing", command=start_processing).pack(pady=10)

log_text = tk.StringVar()
log_label = tk.Label(window, textvariable=log_text)
log_label.pack(pady=5)

tk.Button(window, text="Open Output Folder", command=open_output_folder).pack(pady=5)

window.mainloop()
