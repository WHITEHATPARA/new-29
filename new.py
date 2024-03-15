import datetime
import csv
import cv2
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import numpy as np

class FaceRecognitionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Face Recognition App")
        self.root.geometry("800x600")
        self.root.configure(background="black")

        self.header_label = tk.Label(root, text="Face Recognition App", font=("Arial", 24, "bold"), fg="white", bg="black")
        self.header_label.pack(pady=20)

        self.name_label = tk.Label(root, text="Enter your name:", font=("Arial", 14), fg="white", bg="black")
        self.name_label.pack()

        self.name_entry = tk.Entry(root, font=("Arial", 12))
        self.name_entry.pack()

        self.status_label = tk.Label(root, text="", font=("Arial", 14), fg="white", bg="black")
        self.status_label.pack()

        self.clock_label = tk.Label(root, text="", font=("Arial", 14, "bold"), fg="white", bg="black")
        self.clock_label.pack()

        self.canvas_frame = tk.Frame(root, bg="white", bd=5)
        self.canvas_frame.pack(pady=20)

        self.canvas = tk.Canvas(self.canvas_frame, width=640, height=480)
        self.canvas.pack()

        self.face_detected = False
        self.last_frame_rgb = None

        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.smile_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_smile.xml')

        self.detect_faces()

    def save_data(self, name):
        if name:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%I-%M-%p")
            image_filename = f"{name}_{timestamp}.jpg"
            cv2.imwrite(image_filename, cv2.cvtColor(self.last_frame_rgb, cv2.COLOR_RGB2BGR))  # Save image
            self.save_to_csv(name, timestamp, image_filename)
            messagebox.showinfo("Success", "Name, timestamp, and image saved successfully!")
            self.name_entry.delete(0, tk.END)  # Clear name entry field after saving
        else:
            messagebox.showwarning("Error", "Please enter your name before saving the image.")

    def save_to_csv(self, name, timestamp, image_filename):
        formatted_timestamp = datetime.datetime.strptime(timestamp, "%Y-%m-%d_%I-%M-%p").strftime("%Y-%m-%d %I:%M %p")
        with open("data.csv", "a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([name, formatted_timestamp, image_filename])

    def recognize_faces(self, frame):
        # Convert the frame to grayscale for face detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect faces in the frame
        faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)

        # Initialize flag to check if any face is detected
        face_detected = False

        # Recognize faces and update GUI
        for (x, y, w, h) in faces:
            face_detected = True  # Set flag to True if at least one face is detected

            # Draw bounding box around detected face
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

            # Extract face region
            face_region_gray = gray[y:y+h, x:x+w]
            face_region_color = frame[y:y+h, x:x+w]

            # Detect smile within the face region
            smile = self.detect_smile(face_region_gray)
            if smile:
                self.save_data(name="smile")

        # Update label if at least one face is detected
        if face_detected:
            self.status_label.config(text="Face Detected", fg="green")
        else:
            self.status_label.config(text="No Face Detected", fg="red")

        return frame

    def detect_smile(self, face_gray):
        # Detect smile in the face region
        smiles = self.smile_cascade.detectMultiScale(face_gray, scaleFactor=1.8, minNeighbors=20, minSize=(25, 25))
        return len(smiles) > 0

    def detect_faces(self):
        # Initialize the video capture object
        cap = cv2.VideoCapture(0)  # Use 0 for default webcam, or an index for another camera

        while True:
            # Capture a frame from the webcam
            ret, frame = cap.read()

            if ret:
                # Convert the frame to RGB format
                self.last_frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                # Recognize faces and update GUI
                frame_with_faces = self.recognize_faces(frame)

                # Convert the frame to RGB format and display it on the canvas
                img = Image.fromarray(cv2.cvtColor(frame_with_faces, cv2.COLOR_BGR2RGB))
                imgtk = ImageTk.PhotoImage(image=img)
                self.canvas.create_image(0, 0, anchor=tk.NW, image=imgtk)

                # Update the clock label
                current_time = datetime.datetime.now().strftime("%H:%M:%S")
                self.clock_label.config(text=current_time)

                # Update the window and handle events
                self.root.update_idletasks()
                self.root.update()

            # Exit the loop if the window is closed
            if not self.root.winfo_exists():
                break

        # Release the capture object and close all windows
        cap.release()

if __name__ == "__main__":
    root = tk.Tk()
    app = FaceRecognitionApp(root)
    root.mainloop()
