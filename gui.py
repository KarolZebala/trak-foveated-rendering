import tkinter as tk
from tkinter import filedialog, messagebox
import scene_loader

def run_gui():
    root = tk.Tk()
    root.title("Foveated Rendering")
    root.geometry("400x250")

    # Scene File
    tk.Label(root, text="Scene JSON:").pack()
    frame_scene = tk.Frame(root)
    frame_scene.pack()
    entry_scene = tk.Entry(frame_scene, width=30)
    entry_scene.pack(side=tk.LEFT)
    
    def browse():
        filename = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if filename:
            entry_scene.delete(0, tk.END)
            entry_scene.insert(0, filename)
            
    tk.Button(frame_scene, text="Browse", command=browse).pack(side=tk.LEFT)

    # Output File
    tk.Label(root, text="Output File:").pack()
    entry_output = tk.Entry(root)
    entry_output.insert(0, "output.png")
    entry_output.pack()

    # Width
    tk.Label(root, text="Width:").pack()
    entry_width = tk.Entry(root)
    entry_width.insert(0, "800")
    entry_width.pack()

    # Height
    tk.Label(root, text="Height:").pack()
    entry_height = tk.Entry(root)
    entry_height.insert(0, "400")
    entry_height.pack()

    # Rays
    tk.Label(root, text="Rays:").pack()
    entry_rays = tk.Entry(root)
    entry_rays.insert(0, "4")
    entry_rays.pack()

    def on_render():
        scene = entry_scene.get()
        output = entry_output.get()
        width = entry_width.get()
        height = entry_height.get()
        rays = entry_rays.get()

        if not scene or not output:
            messagebox.showerror("Error", "Please provide scene and output paths.")
            return

        # Construct arguments list
        args = [
            '--scene', scene,
            '--output', output,
            '--width', width,
            '--height', height,
            '--rays', rays
        ]

        try:
            scene_loader.main(args)
            messagebox.showinfo("Success", "Rendering finished!")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    tk.Button(root, text="Render", command=on_render).pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    run_gui()
