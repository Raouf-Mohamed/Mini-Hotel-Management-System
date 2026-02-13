import tkinter as tk
from tkinter import messagebox
import json
import os
from datetime import datetime


# ==========================================
# 1. DAS BACKEND (Logik, Daten, Vererbung)
# ==========================================

class Room:
    """Basis-Klasse für ein Standard-Zimmer."""

    def __init__(self, room_number: int, capacity: int, price: float):
        self.room_number = room_number
        self.capacity = capacity
        self.price = price
        self.is_occupied = False
        self.guest_name = None
        self.check_in_time = None  # Neu: Für die Rechnung

    def check_in(self, guest_name: str):
        if not self.is_occupied:
            self.is_occupied = True
            self.guest_name = guest_name
            self.check_in_time = datetime.now().isoformat()  # Zeit speichern
            return True
        return False

    def check_out(self):
        """Gibt ein Dictionary mit Rechnungsdaten zurück."""
        if self.is_occupied:
            guest = self.guest_name

            # --- Business Logic: Rechnung berechnen ---
            # Wir simulieren hier: Jede angefangene Sekunde ist eine "Nacht" für die Demo
            # Im echten Leben würde man days berechnen.
            bill_amount = self.price

            # Daten zurücksetzen
            self.is_occupied = False
            self.guest_name = None
            self.check_in_time = None

            return {"guest": guest, "amount": bill_amount}
        return None

    def to_dict(self):
        """Hilfsfunktion, um das Objekt speicherbar (JSON) zu machen."""
        return {
            "type": "Standard",
            "number": self.room_number,
            "capacity": self.capacity,
            "price": self.price,
            "occupied": self.is_occupied,
            "guest": self.guest_name,
            "time": self.check_in_time
        }

    def __str__(self):
        status = f"Belegt ({self.guest_name})" if self.is_occupied else "Frei"
        return f"Nr. {self.room_number} (Standard) - {status} - {self.price}€/Nacht"


class Suite(Room):
    """ERWEITERUNG: Eine Suite erbt von Room (Vererbung)."""

    def __init__(self, room_number: int, capacity: int, price: float, has_whirlpool: bool):
        # Wir rufen den Konstruktor der Basis-Klasse auf (super)
        super().__init__(room_number, capacity, price)
        self.has_whirlpool = has_whirlpool

    def to_dict(self):
        """Überschreibt die to_dict Methode für Suiten."""
        data = super().to_dict()
        data["type"] = "Suite"
        data["whirlpool"] = self.has_whirlpool
        return data

    def __str__(self):
        status = f"Belegt ({self.guest_name})" if self.is_occupied else "Frei"
        extra = "mit Whirlpool" if self.has_whirlpool else ""
        return f"Nr. {self.room_number} (SUITE {extra}) - {status} - {self.price}€/Nacht"


class Hotel:
    def __init__(self, name: str):
        self.name = name
        self.rooms = []
        self.filename = "hotel_data.json"
        self.load_data()  # Automatisch laden beim Start

    def add_room(self, room: Room):
        # Wir fügen nur hinzu, wenn die Nummer noch nicht existiert
        for r in self.rooms:
            if r.room_number == room.room_number:
                return
        self.rooms.append(room)
        self.save_data()

    def get_room_by_number(self, number):
        for room in self.rooms:
            if room.room_number == number:
                return room
        return None

    # --- ERWEITERUNG: PERSISTENZ (Speichern & Laden) ---
    def save_data(self):
        data_list = [room.to_dict() for room in self.rooms]
        try:
            with open(self.filename, "w") as f:
                json.dump(data_list, f, indent=4)
            print("Daten erfolgreich gespeichert.")
        except Exception as e:
            print(f"Fehler beim Speichern: {e}")

    def load_data(self):
        if not os.path.exists(self.filename):
            return  # Datei gibt es noch nicht

        try:
            with open(self.filename, "r") as f:
                data_list = json.load(f)

            self.rooms = []  # Liste leeren und neu aufbauen
            for item in data_list:
                # Hier entscheiden wir: Ist es eine Suite oder ein Zimmer?
                if item["type"] == "Suite":
                    room = Suite(item["number"], item["capacity"], item["price"], item.get("whirlpool", False))
                else:
                    room = Room(item["number"], item["capacity"], item["price"])

                # Status wiederherstellen
                room.is_occupied = item["occupied"]
                room.guest_name = item["guest"]
                room.check_in_time = item.get("time")
                self.rooms.append(room)
            print("Daten erfolgreich geladen.")
        except Exception as e:
            print(f"Fehler beim Laden: {e}")


# ==========================================
# 2. DAS FRONTEND (GUI)
# ==========================================
class HotelGUI:
    def __init__(self, root, hotel):
        self.hotel = hotel
        self.root = root
        self.root.title(f"Rezeption Pro - {self.hotel.name}")
        self.root.geometry("500x550")

        # Header
        tk.Label(root, text="🏨 Hotel Management Pro", font=("Arial", 18, "bold")).pack(pady=10)
        tk.Label(root, text="System läuft. Daten werden automatisch gespeichert.", fg="gray").pack()

        # Input Frame
        frame_input = tk.Frame(root, pady=10)
        frame_input.pack()

        tk.Label(frame_input, text="Gast Name:").grid(row=0, column=0)
        self.entry_guest = tk.Entry(frame_input, width=25)
        self.entry_guest.grid(row=0, column=1, padx=5)

        tk.Label(frame_input, text="Zimmernummer:").grid(row=1, column=0)
        self.entry_room = tk.Entry(frame_input, width=25)
        self.entry_room.grid(row=1, column=1, padx=5)

        # Buttons
        frame_btn = tk.Frame(root, pady=10)
        frame_btn.pack()

        tk.Button(frame_btn, text="Einchecken", bg="#90EE90", width=15, command=self.gui_check_in).grid(row=0, column=0,
                                                                                                        padx=5)
        tk.Button(frame_btn, text="Check-out & Rechnung", bg="#FFB6C1", width=18, command=self.gui_check_out).grid(
            row=0, column=1, padx=5)

        tk.Button(root, text="Aktuelle Belegung anzeigen", bg="#ADD8E6", width=35, command=self.gui_show_status).pack(
            pady=10)

        # Info Box (Listbox) für die Zimmer
        self.listbox = tk.Listbox(root, width=60, height=10)
        self.listbox.pack(pady=10)
        self.update_listbox()  # Beim Start füllen

    def update_listbox(self):
        """Aktualisiert die Anzeige der Zimmer."""
        self.listbox.delete(0, tk.END)
        for room in self.hotel.rooms:
            self.listbox.insert(tk.END, str(room))

    def gui_check_in(self):
        guest = self.entry_guest.get()
        room_str = self.entry_room.get()

        if not guest or not room_str:
            messagebox.showwarning("Fehler", "Bitte Name und Nummer eingeben!")
            return

        try:
            room_num = int(room_str)
            room = self.hotel.get_room_by_number(room_num)

            if room:
                if room.check_in(guest):
                    self.hotel.save_data()  # SOFORT SPEICHERN
                    self.update_listbox()
                    self.entry_guest.delete(0, tk.END)
                    self.entry_room.delete(0, tk.END)
                    messagebox.showinfo("Erfolg", f"{guest} in Zimmer {room_num} eingecheckt.")
                else:
                    messagebox.showerror("Fehler", "Zimmer ist schon belegt!")
            else:
                messagebox.showerror("Fehler", "Zimmernummer nicht gefunden.")

        except ValueError:
            messagebox.showerror("Fehler", "Zimmernummer muss eine Zahl sein.")

    def gui_check_out(self):
        room_str = self.entry_room.get()
        if not room_str:
            messagebox.showwarning("Fehler", "Bitte Zimmernummer für Checkout eingeben!")
            return

        try:
            room_num = int(room_str)
            room = self.hotel.get_room_by_number(room_num)

            if room:
                bill_data = room.check_out()
                if bill_data:
                    self.hotel.save_data()  # SOFORT SPEICHERN
                    self.update_listbox()
                    # --- RECHNUNG ANZEIGEN ---
                    text = f"Gast: {bill_data['guest']}\nZimmer: {room_num}\nZu zahlen: {bill_data['amount']:.2f} €"
                    messagebox.showinfo("Rechnung erstellt", text)
                else:
                    messagebox.showwarning("Info", "Zimmer war gar nicht belegt.")
            else:
                messagebox.showerror("Fehler", "Zimmernummer nicht gefunden.")
        except ValueError:
            messagebox.showerror("Fehler", "Zimmernummer muss eine Zahl sein.")

    def gui_show_status(self):
        self.update_listbox()


# ==========================================
# HAUPTPROGRAMM
# ==========================================
if __name__ == "__main__":
    # 1. Hotel erstellen (lädt Daten automatisch, falls vorhanden)
    my_hotel = Hotel("Grand Hotel Python")

    # 2. Zimmer nur hinzufügen, wenn die Datei leer war (Initialisierung)
    if not my_hotel.rooms:
        print("Erstelle neue Zimmer (Erster Start)...")
        # Standard Zimmer
        my_hotel.add_room(Room(101, 2, 80.00))
        my_hotel.add_room(Room(102, 1, 60.00))
        # Suiten (Vererbung!)
        my_hotel.add_room(Suite(201, 2, 150.00, has_whirlpool=True))
        my_hotel.add_room(Suite(202, 4, 200.00, has_whirlpool=True))

    # 3. GUI starten
    root = tk.Tk()
    app = HotelGUI(root, my_hotel)
    root.mainloop()
