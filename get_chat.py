from tkinter import *
from tkinter import ttk, messagebox
import socket
import csv
import datetime
import time
import threading
import os
import requests

# Configuration Twitch IRC
SERVER = 'irc.chat.twitch.tv'
PORT = 6667
NICKNAME = 'YourNameWithoutMaj'
TOKEN = 'oauth:YourTokenHere'

SAVE_INTERVAL = 15 * 60  # 15 minutes en secondes
HISTORY_FILE = "channels_history.txt"

active_bots = {}
messages_buffers = {}
threads = {}
connected_status = {}
channels = set()

import requests

# Tes identifiants Twitch (remplace par les tiens)
# Vous devez aller ici : https://dev.twitch.tv/console/apps
# Pour creer vos clef client
CLIENT_ID = 'Id Client Key'
CLIENT_SECRET = 'Id Secret Client Key'

def get_token():
    url = "https://id.twitch.tv/oauth2/token"
    params = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "client_credentials"
    }
    try:
        resp = requests.post(url, params=params)
        resp.raise_for_status()
        data = resp.json()
        return data['access_token']
    except Exception as e:
        print(f"Erreur lors de la récupération du token : {e}")
        return None

def validate_username(username):
    token = get_token()
    if not token:
        print("Impossible d'obtenir un token valide.")
        return False

    url = f"https://api.twitch.tv/helix/users?login={username}"
    headers = {
        'Client-ID': CLIENT_ID,
        'Authorization': f'Bearer {token}'
    }
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            return bool(data.get('data'))
        else:
            print(f"Erreur API Twitch: status code {response.status_code}")
            return False
    except Exception as e:
        print(f"Erreur lors de la validation de l'utilisateur {username}: {e}")
        return False

def parse_message(raw_msg):
    try:
        parts = raw_msg.split(' ', 3)
        if len(parts) < 4:
            return None, None
        prefix = parts[0]
        command = parts[1]
        msg = parts[3][1:].strip()
        if command == 'PRIVMSG':
            username = prefix.split('!')[0][1:]
            return username, msg
    except Exception:
        pass
    return None, None


def save_messages(messages, base_name):
    if not messages:
        return
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{base_name}_{timestamp}.csv"
    try:
        with open(filename, mode='w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['timestamp', 'username', 'message'])
            writer.writerows(messages)
        print(f"[{datetime.datetime.now().isoformat(timespec='seconds')}] Sauvegarde {len(messages)} messages dans {filename}")
    except Exception as e:
        print(f"Erreur lors de la sauvegarde des messages : {e}")


def bot_thread(channel_name):
    channel = f"#{channel_name}"
    sock = socket.socket()
    try:
        sock.connect((SERVER, PORT))
        sock.send(f"PASS {TOKEN}\n".encode('utf-8'))
        sock.send(f"NICK {NICKNAME}\n".encode('utf-8'))
        sock.send(f"JOIN {channel}\n".encode('utf-8'))
        connected_status[channel_name].set("green")
    except Exception as e:
        print(f"Erreur de connexion pour {channel_name} : {e}")
        connected_status[channel_name].set("red")
        return

    messages_buffer = []
    messages_buffers[channel_name] = messages_buffer
    last_save = time.time()

    try:
        while active_bots.get(channel_name, False):
            resp = sock.recv(2048).decode('utf-8')
            if resp.startswith('PING'):
                sock.send("PONG\n".encode('utf-8'))
            elif resp:
                for line in resp.split('\r\n'):
                    if line:
                        user, message = parse_message(line)
                        if user and message:
                            timestamp = datetime.datetime.now().isoformat(timespec='seconds')
                            print(f"[{channel_name}] {timestamp} {user}: {message}")
                            messages_buffer.append([timestamp, user, message])

            if time.time() - last_save > SAVE_INTERVAL:
                save_messages(messages_buffer, f"chat_{channel_name}")
                messages_buffer.clear()
                last_save = time.time()

    except Exception as e:
        print(f"Erreur dans le thread du bot {channel_name} : {e}")
    finally:
        save_messages(messages_buffer, f"chat_{channel_name}")
        sock.close()
        connected_status[channel_name].set("red")
        active_bots[channel_name] = False


def toggle_bot(event):
    selection = listbox.curselection()
    if not selection:
        return
    index = selection[0]
    channel_name = listbox.get(index)

    if not active_bots.get(channel_name, False):
        if validate_username(channel_name):
            active_bots[channel_name] = True
            connected_status[channel_name] = StringVar(value="green")
            thread = threading.Thread(target=bot_thread, args=(channel_name,), daemon=True)
            thread.start()
            threads[channel_name] = thread
        else:
            messagebox.showerror("Erreur", f"Le pseudo '{channel_name}' n'existe pas.")
    else:
        active_bots[channel_name] = False


def add_channel():
    channel_name = entry.get().strip().lower()
    if not channel_name:
        return
    if channel_name in channels:
        messagebox.showinfo("Info", f"Le canal '{channel_name}' est déjà dans la liste.")
        return
    channels.add(channel_name)
    listbox.insert(END, channel_name)
    connected_status[channel_name] = StringVar(value="red")
    entry.delete(0, END)
    save_history()


def remove_channel():
    selection = listbox.curselection()
    if not selection:
        return
    index = selection[0]
    channel_name = listbox.get(index)
    active_bots[channel_name] = False
    listbox.delete(index)
    if channel_name in connected_status:
        del connected_status[channel_name]
    if channel_name in channels:
        channels.remove(channel_name)
    save_history()


def save_history():
    try:
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            for i in range(listbox.size()):
                f.write(listbox.get(i) + '\n')
    except Exception as e:
        print(f"Erreur lors de la sauvegarde de l'historique : {e}")


def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                for line in f:
                    name = line.strip()
                    if name:
                        channels.add(name)
                        listbox.insert(END, name)
                        connected_status[name] = StringVar(value="red")
        except Exception as e:
            print(f"Erreur lors du chargement de l'historique : {e}")


def update_status():
    for name in connected_status:
        color = connected_status[name].get()
        if name not in status_labels:
            lbl = Canvas(status_frame, width=15, height=15, bg="white", highlightthickness=0)
            lbl.grid()
            status_labels[name] = lbl
        canvas = status_labels[name]
        canvas.delete("all")
        canvas.create_oval(2, 2, 13, 13, fill=color)
    root.after(1000, update_status)


# --- Création de l'interface ---
root = Tk()
root.title("Twitch Bot Interface")

mainframe = ttk.Frame(root, padding="10")
mainframe.grid(column=0, row=0, sticky=(N, W, E, S))

entry = ttk.Entry(mainframe)
entry.grid(column=1, row=1, columnspan=2, sticky=(W, E))

add_button = ttk.Button(mainframe, text="Ajouter", command=add_channel)
add_button.grid(column=3, row=1, sticky=W)

remove_button = ttk.Button(mainframe, text="Supprimer", command=remove_channel)
remove_button.grid(column=4, row=1, sticky=W)

listbox = Listbox(mainframe, height=10)
listbox.grid(column=1, row=2, columnspan=3, sticky=(W, E))
listbox.bind("<Double-Button-1>", toggle_bot)

status_frame = ttk.Frame(mainframe)
status_frame.grid(column=4, row=2, sticky=N)

status_labels = {}

load_history()
update_status()
root.mainloop()
save_history()
