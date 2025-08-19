import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import random, os, time, json

class MemoryGameImages:
    def __init__(self, root, img_folder=r"C:\Users\phoom\OneDrive\Documents\Stack project\Images", cols=4, highscore_file="highscore.json"):
        self.root = root
        self.root.title("🎴 Memory Game")
        self.cols = cols
        self.first_card = None
        self.buttons = []
        self.cards = []
        self.flipped = {}
        self.score = 0
        self.tries = 0
        self.start_time = None
        self.flip_count = 0
        self.highscore_file = highscore_file

        # โหลด Highscore
        self.highscore = self.load_highscore()

        # โหลดรูปภาพ
        self.load_images(img_folder)

        # สร้างการ์ด
        self.setup_game()

    def load_images(self, img_folder):
        all_files = os.listdir(img_folder)
        back_candidates = [f for f in all_files if f.lower() == "back.png"]
        if not back_candidates:
            raise Exception("ต้องมีไฟล์ Back.png สำหรับหลังการ์ด")
        self.back_file = os.path.join(img_folder, back_candidates[0])

        files = [f for f in all_files if f.lower().endswith((".png", ".jpg", ".jpeg")) and f.lower() != "back.png"]
        if len(files) < 2:
            raise Exception("ต้องมีรูปอย่างน้อย 2 รูปในโฟลเดอร์ Images")

        self.image_files = [os.path.join(img_folder, f) for f in files]

        back_img = Image.open(self.back_file).resize((100, 100))
        self.card_back = ImageTk.PhotoImage(back_img)

        self.images = []
        for f in self.image_files:
            img = Image.open(f).resize((100, 100))
            tk_img = ImageTk.PhotoImage(img)
            self.images.append(tk_img)
            self.images.append(tk_img)

    def setup_game(self):
        random.shuffle(self.images)
        self.cards = self.images
        self.score = 0
        self.tries = 0
        self.start_time = time.time()
        self.first_card = None
        self.flipped.clear()
        self.flip_count = 0

        for widget in self.root.winfo_children():
            widget.destroy()

        # Labels
        self.timer_label = tk.Label(self.root, text="เวลา: 0 วินาที", font=("Arial", 12))
        self.timer_label.grid(row=0, column=0, columnspan=self.cols)

        self.flip_label = tk.Label(self.root, text="จำนวนครั้งที่ flip: 0", font=("Arial", 12))
        self.flip_label.grid(row=1, column=0, columnspan=self.cols)

        self.score_label = tk.Label(self.root, text="คะแนน: 0", font=("Arial", 12))
        self.score_label.grid(row=2, column=0, columnspan=self.cols)

        self.highscore_label = tk.Label(self.root, text=f"Highscore: {self.highscore}", font=("Arial", 12, "bold"), fg="blue")
        self.highscore_label.grid(row=3, column=0, columnspan=self.cols)

        self.update_timer()

        self.buttons = []
        for i, img in enumerate(self.cards):
            row = (i // self.cols) + 4
            btn = tk.Button(self.root, image=self.card_back, command=lambda i=i: self.flip_card(i))
            btn.grid(row=row, column=i % self.cols, padx=5, pady=5)
            self.buttons.append(btn)

    def update_timer(self):
        if self.start_time is not None:
            elapsed = int(time.time() - self.start_time)
            self.timer_label.config(text=f"เวลา: {elapsed} วินาที")
            self.update_score_label()
            self.root.after(1000, self.update_timer)

    def flip_card(self, i):
        if i in self.flipped or self.buttons[i]["state"] == "disabled":
            return

        self.flip_count += 1
        self.flip_label.config(text=f"จำนวนครั้งที่ flip: {self.flip_count}")

        self.buttons[i].config(image=self.cards[i])
        self.root.update()

        if self.first_card is None:
            self.first_card = i
        else:
            self.tries += 1
            if self.cards[self.first_card] == self.cards[i]:
                self.flipped[self.first_card] = True
                self.flipped[i] = True
                self.score += 10
                self.buttons[self.first_card].config(state="disabled")
                self.buttons[i].config(state="disabled")
            else:
                self.root.after(800, self.hide_cards, self.first_card, i)
            self.first_card = None

        self.update_score_label()

        if len(self.flipped) == len(self.cards):
            self.game_over()

    def update_score_label(self):
        elapsed_time = int(time.time() - self.start_time)
        # คะแนนลดเฉพาะคู่ไม่ตรงและเวลา
        current_score = max(0, self.score - (self.tries * 2) - elapsed_time // 2)
        self.score_label.config(text=f"คะแนน: {current_score}")
        if current_score > self.highscore:
            self.highscore = current_score
            self.highscore_label.config(text=f"Highscore: {self.highscore}")

    def hide_cards(self, i, j):
        self.buttons[i].config(image=self.card_back)
        self.buttons[j].config(image=self.card_back)

    def game_over(self):
        elapsed_time = int(time.time() - self.start_time)
        final_score = max(0, self.score - (self.tries * 2) - elapsed_time // 2)

        if final_score > self.load_highscore():
            self.save_highscore(final_score)

        message = f"🎉 คุณชนะ!\nคะแนน: {final_score}\nHighscore: {self.highscore}"

        if messagebox.askyesno("Game Over", message + "\n\nเล่นใหม่ไหม?"):
            self.setup_game()
        else:
            self.root.quit()

    def load_highscore(self):
        if os.path.exists(self.highscore_file):
            with open(self.highscore_file, "r") as f:
                data = json.load(f)
                return data.get("highscore", 0)
        return 0

    def save_highscore(self, score):
        with open(self.highscore_file, "w") as f:
            json.dump({"highscore": score}, f)


if __name__ == "__main__":
    root = tk.Tk()
    game = MemoryGameImages(root)
    root.mainloop()
  