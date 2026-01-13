import tkinter as tk
import time
from tkinter import filedialog, messagebox
import scene_loader

def run_gui():
    root = tk.Tk()
    root.title("Foveated Rendering Raytracer")
    root.geometry("450x380") 

    # --- Scene File ---
    tk.Label(root, text="Scene JSON:").pack(pady=(10, 0))
    frame_scene = tk.Frame(root)
    frame_scene.pack()
    entry_scene = tk.Entry(frame_scene, width=35)
    entry_scene.pack(side=tk.LEFT)
    
    def browse():
        filename = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if filename:
            entry_scene.delete(0, tk.END)
            entry_scene.insert(0, filename)
            
    tk.Button(frame_scene, text="Browse", command=browse).pack(side=tk.LEFT, padx=5)

    # --- Output File ---
    tk.Label(root, text="Output File:").pack(pady=(5, 0))
    entry_output = tk.Entry(root, width=30)
    entry_output.insert(0, "output.png")
    entry_output.pack()

    # --- Settings Frame ---
    frame_settings = tk.Frame(root)
    frame_settings.pack(pady=10)

    # Width
    tk.Label(frame_settings, text="Width:").grid(row=0, column=0, padx=5, pady=2)
    entry_width = tk.Entry(frame_settings, width=10)
    entry_width.insert(0, "800")
    entry_width.grid(row=0, column=1, padx=5, pady=2)

    # Height
    tk.Label(frame_settings, text="Height:").grid(row=1, column=0, padx=5, pady=2)
    entry_height = tk.Entry(frame_settings, width=10)
    entry_height.insert(0, "600")
    entry_height.grid(row=1, column=1, padx=5, pady=2)

    # Rays
    tk.Label(frame_settings, text="Rays/Pixel:").grid(row=2, column=0, padx=5, pady=2)
    entry_rays = tk.Entry(frame_settings, width=10)
    entry_rays.insert(0, "4")
    entry_rays.grid(row=2, column=1, padx=5, pady=2)

    # --- Foveation Settings (X, Y) ---
    tk.Label(root, text="--- Foveation Point (Pixels) ---", font=("Arial", 10, "bold")).pack(pady=(10, 5))
    frame_fovea = tk.Frame(root)
    frame_fovea.pack()

    tk.Label(frame_fovea, text="Center X:").grid(row=0, column=0, padx=5)
    entry_fov_x = tk.Entry(frame_fovea, width=10)
    entry_fov_x.insert(0, "400") # Domyślnie środek dla szerokości 800
    entry_fov_x.grid(row=0, column=1, padx=5)

    tk.Label(frame_fovea, text="Center Y:").grid(row=0, column=2, padx=5)
    entry_fov_y = tk.Entry(frame_fovea, width=10)
    entry_fov_y.insert(0, "300") # Domyślnie środek dla wysokości 600
    entry_fov_y.grid(row=0, column=3, padx=5)

    # --- Render Button ---
    def on_render():
        scene = entry_scene.get()
        output = entry_output.get()
        width = entry_width.get()
        height = entry_height.get()
        rays = entry_rays.get()
        fov_x = entry_fov_x.get()
        fov_y = entry_fov_y.get()

        if not scene or not output:
            messagebox.showerror("Error", "Please provide scene and output paths.")
            return

        # Budujemy listę argumentów
        args = [
            '--scene', scene,
            '--output', output,
            '--width', width,
            '--height', height,
            '--rays', rays,
            '--fovea_x', fov_x,
            '--fovea_y', fov_y
        ]

        try:
            # Uruchomienie renderowania
            start_time = time.time()
            scene_loader.main(args)
            end_time = time.time()
            render_time = end_time - start_time
            messagebox.showinfo("Success", f"Rendering finished! \n Render time: {render_time:.2f} seconds.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
            print(e) # Wypisz błąd w konsoli

    tk.Button(root, text="RENDER", command=on_render, width=15).pack(pady=20)

    root.mainloop()

if __name__ == "__main__":
    run_gui()