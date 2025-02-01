import cv2
import tkinter as tk
from tkinter import simpledialog, filedialog
from PIL import Image, ImageTk
import json
import colorsys
import gc
import numpy as np

def id_to_hex_color(id):
    # Map ID to a hue value (cyclic, 0 to 360 degrees)
    hue = ((id * 137.5) % 360) / 360.0  # Normalize the hue to a value between 0 and 1
    
    # Fixed saturation and value for vibrant colors
    saturation = 1.0
    value = 1.0
    
    # Convert HSV to RGB
    r, g, b = colorsys.hsv_to_rgb(hue, saturation, value)
    
    # Convert RGB to 0-255 range
    r = int(r * 255)
    g = int(g * 255)
    b = int(b * 255)
    
    # Convert RGB to hex color code
    hex_color = f"#{r:02x}{g:02x}{b:02x}"
    
    return hex_color


IMAGE_WIDTH = 1280
IMAGE_HEIGHT = 720
MAX_OBJECTS = 100

class VideoTrackerApp:
    def __init__(self, root, video_path):
        self.root = root
        self.root.title("Video Tracking Labeler")
        
        #print(self.total_frames)

        self.current_frame = 0
        self.is_playing = False
        self.is_tracking = False
        self.trackers = {}
        self.temp_bbox = None
        self.drawing = False
        
        # GUI Setup
        self.canvas = tk.Canvas(root, width=IMAGE_WIDTH, height=IMAGE_HEIGHT)
        self.canvas.pack()
        
        control_frame = tk.Frame(root)
        control_frame.pack(fill=tk.X)
        
        self.opn_video = tk.Button(control_frame, text="Open", command=self.open_video)
        self.opn_video.pack(side=tk.LEFT)

        self.btn_play = tk.Button(control_frame, text="Play", command=self.toggle_play)
        self.btn_play.pack(side=tk.LEFT)

        self.checkbox_var = tk.BooleanVar()
        checkbox = tk.Checkbutton(control_frame, text="Track", variable=self.checkbox_var, command=self.toggle_track)
        checkbox.pack(side=tk.LEFT)

        self.btn_rmtrack = tk.Button(control_frame, text="Stop Track", command=self.remove_track)
        self.btn_rmtrack.pack(side=tk.LEFT)

        self.scale = tk.Scale(control_frame, from_=0, to=1, orient=tk.HORIZONTAL, command=self.on_scale)
        self.scale.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.btn_del = tk.Button(control_frame, text="Del", command=self.delete_bbox)
        self.btn_del.pack(side=tk.RIGHT)

        self.btn_list = tk.Button(control_frame, text="List", command=self.list_objects)
        self.btn_list.pack(side=tk.RIGHT)
        
        self.btn_export = tk.Button(control_frame, text="Export JSON", command=self.export_data)
        self.btn_export.pack(side=tk.RIGHT)
        
        # Mouse events
        self.canvas.bind("<ButtonPress-1>", self.start_draw)
        self.canvas.bind("<B1-Motion>", self.draw_bbox)
        self.canvas.bind("<ButtonRelease-1>", self.finish_draw)
        self.canvas.bind("<Button-3>", self.delete_bbox)

    def open_video(self):
        file_path = filedialog.askopenfilename(title="Select a file", filetypes=(("Video Files", "*.mp4"), ("All Files", "*.*")))
    
        if file_path:  
            self.cap = cv2.VideoCapture(file_path)
            self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
            self.tracking_data = np.zeros((self.total_frames, MAX_OBJECTS, 4), dtype=np.uint32)
            self.scale.config(to=self.total_frames-1)
            self.update_frame()

    def __read(self):
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.frame = cv2.resize(frame, (IMAGE_WIDTH, IMAGE_HEIGHT))

        return ret

    def draw_boxes(self):

        object_ids = np.where(self.tracking_data[self.current_frame, :, -1] > 0)[0]
        
        for obj_id in object_ids:
            
            x, y, w, h = self.tracking_data[self.current_frame, obj_id, :].tolist()

            color = id_to_hex_color(obj_id)

            #print(color)

            self.canvas.create_rectangle(x, y, x+w, y+h, outline=color, width=2)
            self.canvas.create_text(x+5, y+5, text=obj_id, fill=color, anchor=tk.NW)
        

    def update_frame(self, set_current_frame = True):
        if set_current_frame:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.current_frame)

        if self.__read():

            if not set_current_frame:
                self.current_frame += 1

            self.photo = ImageTk.PhotoImage(image=Image.fromarray(self.frame))
            self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)

            self.draw_boxes()

            self.scale.set(self.current_frame) 
        else:
            self.is_playing = False
            self.btn_play.config(text="Play")
            self.scale.set(self.current_frame)

    def toggle_play(self):
        if self.is_playing:
            self.is_playing = False
            self.btn_play.config(text="Play")
        else:
            self.is_playing = True
            self.btn_play.config(text="Pause")
            self.play_video()

    def toggle_track(self):
        if self.is_tracking:
            self.is_tracking = False
        else:
            self.is_tracking = True

    def play_video(self):
        if self.is_playing and self.current_frame < self.total_frames-1:
            
            self.update_frame(False)

            if self.checkbox_var.get():
                self.process_frame()

            self.root.after(10, self.play_video)

    def process_frame(self):

        to_remove = []
        for obj_id in list(self.trackers.keys()):
            success, bbox = self.trackers[obj_id].update(self.frame)
            
            if success:

                self.tracking_data[self.current_frame, obj_id, :] = list(map(int, bbox))
                self.draw_boxes()

            else:
                to_remove.append(obj_id)
                self.is_playing = False
        
        # Remove failed trackers
        for obj_id in to_remove:
            del self.trackers[obj_id]
            gc.collect()

    def on_scale(self, value):
        self.current_frame = int(value)
        if not self.is_playing:
            self.update_frame()

    def start_draw(self, event):
        if not self.is_playing:
            self.drawing = True
            self.start_x = event.x
            self.start_y = event.y
            self.temp_bbox = self.canvas.create_rectangle(event.x, event.y, event.x, event.y, outline='blue')

    def draw_bbox(self, event):
        if self.drawing and self.temp_bbox:
            self.canvas.coords(self.temp_bbox, self.start_x, self.start_y, event.x, event.y)

    def finish_draw(self, event):
        if self.drawing:
            self.drawing = False
            x1, y1, x2, y2 = self.canvas.coords(self.temp_bbox)
            self.canvas.delete(self.temp_bbox)
            
            obj_id = int(simpledialog.askstring("Object ID", "Enter object ID:"))

            # Normalize coordinates
            x = int(min(x1, x2))
            y = int(min(y1, y2))
            w = int(abs(x2 - x1))
            h = int(abs(y2 - y1))

            if obj_id in self.trackers:
                del self.trackers[obj_id]
                gc.collect()
            
            if not obj_id in self.trackers:
                #self.trackers[obj_id] = cv2.TrackerCSRT_create()
                self.trackers[obj_id] = cv2.TrackerKCF_create()
                #self.trackers[obj_id] = cv2.legacy.TrackerMOSSE_create()

            bbox = (x, y, w, h)
            self.trackers[obj_id].init(self.frame, bbox)

            self.tracking_data[self.current_frame, obj_id, :] = list(map(int, bbox))
            
            self.update_frame(True)

    def delete_bbox(self):

        if not self.is_tracking:

            obj_id = int(simpledialog.askstring("Object ID", "Enter object ID to delete all associated data:"))
            self.tracking_data[:, obj_id, :] = 0

            del self.trackers[obj_id]
            gc.collect()
        
            self.update_frame()

            print("Object deleted")

    def remove_track(self):
        
        if not self.is_tracking:

            obj_id = int(simpledialog.askstring("Object ID", "Enter object ID to stop and remove tracker:"))

            del self.trackers[obj_id]
            gc.collect()


    def list_objects(self):
        objects = np.unique(np.where(self.tracking_data[:, :, -1] > 0)[-1])
        print("Objects:", objects)
        return [int(o) for o in objects]

    def export_data(self):

        file_path = filedialog.asksaveasfilename(defaultextension=".json", 
                                             filetypes=[("Text Files", "*.json"), 
                                                      ("All Files", "*.*")],
                                             title="Save As")

        data = {}
        
        for obj in self.list_objects():

            track = self.tracking_data[:, obj, 0].tolist()

            data[obj] = []

            v_prev = 0

            segment_start = 0
            segment_end = 0

            for i, v in enumerate(track):
                if v > 0 and v_prev == 0:
                    segment_start = int(i)
                elif v == 0 and v_prev > 0:
                    segment_end = int(i)
                    data[obj].append([segment_start, segment_end])
                v_prev = v

            if segment_end > segment_start:
                data[obj].append([segment_start, segment_end])
                    

        if file_path:
            with open(file_path, "w") as f:
                json.dump(data, f, indent=2)
        
        print(f"Tracking data exported to {file_path}")

if __name__ == "__main__":
    root = tk.Tk()
    app = VideoTrackerApp(root, "data/video/actionrec_sample_5.mp4")  # Replace with your video path
    root.mainloop()