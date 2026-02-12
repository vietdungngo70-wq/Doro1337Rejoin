#!/data/data/com.termux/files/usr/bin/python

import os
import time
import subprocess
import sys
import psutil
import requests
from datetime import datetime

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
RESET = "\033[0m"

place_id = ""
package_name = ""
webhook_url = ""
check_interval = 10
status_interval = 60  # gửi status mỗi 60s


# ===== UI =====
def clear():
    os.system("clear")


def banner():
    print(CYAN + r"""
   ____    ___    ____    ___
  |  _ \  / _ \  |  _ \  / _ \
  | | | || | | | | |_) || | | |
  | |_| || |_| | |  _ < | |_| |
  |____/  \___/  |_| \_\ \___/

        Doro1337's Rejoin
""" + RESET)


def device_status():
    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory()
    ram_used = ram.used / (1024**3)
    ram_total = ram.total / (1024**3)
    instances = len(psutil.pids())

    print("────────────────────────────────────")
    print(f"🖥 CPU: {cpu:.1f}% | 💾 RAM: {ram_used:.2f}/{ram_total:.2f}GB")
    print(f"🔥 Instances: {instances}")
    print("────────────────────────────────────")


def settings_status():
    print(f"🎮 Package : {package_name if package_name else RED+'Auto Detect'+RESET}")
    print(f"🌍 PlaceID : {place_id if place_id else RED+'Not Set'+RESET}")
    print(f"🔗 Webhook : {'Enabled' if webhook_url else 'Disabled'}")
    print("────────────────────────────────────\n")


# ===== WEBHOOK =====
def send_webhook(message):
    if not webhook_url:
        return

    data = {
        "content": f"📡 **Doro1337's Rejoin**\n{message}\n⏰ {datetime.now()}"
    }

    try:
        requests.post(webhook_url, json=data, timeout=5)
    except:
        pass


def send_status():
    if not webhook_url:
        return

    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory().percent
    instances = len(psutil.pids())

    msg = f"📊 Status Update\n🖥 CPU: {cpu}%\n💾 RAM: {ram}%\n🔥 Instances: {instances}"
    send_webhook(msg)


# ===== AUTO DETECT ROBLOX =====
def auto_detect_package():
    try:
        result = subprocess.check_output(["pm", "list", "packages"]).decode()
        for line in result.splitlines():
            if "roblox" in line.lower():
                return line.replace("package:", "").strip()
    except:
        pass
    return None


# ===== CONFIG =====
def set_package():
    global package_name
    pkg = input("🎮 Enter Package (leave empty = auto): ").strip()
    if pkg:
        package_name = pkg
        print(GREEN + "✔ Package set successfully" + RESET)
    else:
        detected = auto_detect_package()
        if detected:
            package_name = detected
            print(GREEN + f"✔ Auto detected: {detected}" + RESET)
        else:
            print(RED + "✖ Could not detect Roblox" + RESET)


def set_place():
    global place_id
    pid = input("🌍 Enter Place ID: ").strip()
    if pid:
        place_id = pid
        print(GREEN + "✔ Place ID set successfully" + RESET)
    else:
        print(RED + "✖ Place ID cannot be empty" + RESET)


def set_webhook():
    global webhook_url
    url = input("🔗 Enter Webhook (leave empty = disable): ").strip()
    if url:
        webhook_url = url
        print(GREEN + "✔ Webhook enabled" + RESET)
    else:
        webhook_url = ""
        print(YELLOW + "⚠ Webhook disabled" + RESET)


# ===== GAME CHECK =====
def game_running():
    if not package_name:
        return False

    try:
        subprocess.check_output(["pidof", package_name])
        return True
    except:
        return False


def rejoin():
    print(YELLOW + "⚠ Rejoining..." + RESET)
    send_webhook("⚠ Game Offline → Rejoining")

    os.system(f"am force-stop {package_name}")
    time.sleep(2)
    os.system(
        f'am start -a android.intent.action.VIEW -d "roblox://placeId={place_id}"'
    )


# ===== MAIN LOOP =====
def start_tool():
    if not place_id:
        print(RED + "✖ Please set Place ID first!" + RESET)
        time.sleep(2)
        return

    global package_name
    if not package_name:
        package_name = auto_detect_package()

    if not package_name:
        print(RED + "✖ No package detected!" + RESET)
        time.sleep(2)
        return

    print(GREEN + "🟢 Tool Started" + RESET)
    send_webhook("🟢 Tool Started")

    last_status_time = time.time()

    while True:
        if game_running():
            print(GREEN + "🟢 Game Online" + RESET)
        else:
            print(RED + "🔴 Game Offline" + RESET)
            rejoin()

        # gửi status định kỳ
        if time.time() - last_status_time >= status_interval:
            send_status()
            last_status_time = time.time()

        time.sleep(check_interval)


# ===== MENU =====
def menu():
    while True:
        clear()
        banner()
        device_status()
        settings_status()

        print("1️⃣  Start Tool")
        print("2️⃣  Set Package / Auto Detect")
        print("3️⃣  Set Place ID")
        print("4️⃣  Set / Disable Webhook")
        print("5️⃣  Exit\n")

        choice = input("👉 Select Option: ")

        if choice == "1":
            start_tool()
        elif choice == "2":
            set_package()
            input("Press Enter...")
        elif choice == "3":
            set_place()
            input("Press Enter...")
        elif choice == "4":
            set_webhook()
            input("Press Enter...")
        elif choice == "5":
            send_webhook("🔴 Tool Stopped")
            sys.exit()
        else:
            print(RED + "Invalid option" + RESET)
            time.sleep(1)


if __name__ == "__main__":
    try:
        menu()
    except KeyboardInterrupt:
        send_webhook("🔴 Tool Stopped Manually")
        print("\nExiting...")
        