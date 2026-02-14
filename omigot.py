import os
import sys
import time
import json
import random
import threading
import subprocess
import datetime
import requests

# ==========================================
# 🍊 DORO1337 CONFIG v5.0 (EMOJI EDITION)
# ==========================================
CONFIG_FILE = "config_ultimate.json"
VERSION = "v5.0 EMOJI VIP"
BANNER_NAME = "🍊 DORO1337"

# ANSI Colors & Styles
class Col:
    RESET = "\033[0m"
    RED = "\033[38;5;196m"
    GREEN = "\033[38;5;46m"
    YELLOW = "\033[38;5;226m"
    BLUE = "\033[38;5;39m"
    PURPLE = "\033[38;5;129m"
    CYAN = "\033[38;5;51m"
    ORANGE = "\033[38;5;208m"
    GRAY = "\033[38;5;240m"
    WHITE = "\033[38;5;255m"
    BOLD = "\033[1m"
    BG_BLUE = "\033[48;5;17m"

DEFAULT_CONFIG = {
    "place_id": "2753915549",
    "prefix": "com.roblox.client",
    "webhook_url": "",
    "smart_hop": True,
    "hop_min": 10,
    "hop_max": 20,
    "auto_restart": True,
    "auto_optimize": True,
    "cpu_limit": 95,
    "ram_limit": 90
}

# Global Variables
running = False
packages = []
global_stats = {
    "start_time": time.time(),
    "total_rejoins": 0,
    "cpu": 0, "ram": 0, "battery": 0, "temp": 0
}

# ==========================================
# 🛠️ SYSTEM CORE
# ==========================================
def clear(): os.system("clear")

def su_exec(command):
    try:
        res = subprocess.run(f"su -c '{command}'", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=5)
        return res.stdout.decode().strip()
    except: return ""

def check_root(): return "uid=0(root)" in su_exec("id")

def save_config(cfg):
    with open(CONFIG_FILE, "w") as f: json.dump(cfg, f, indent=4)

def load_config():
    if not os.path.exists(CONFIG_FILE): save_config(DEFAULT_CONFIG)
    with open(CONFIG_FILE, "r") as f: return json.load(f)

# ==========================================
# ⚙️ MENU GIAO DIỆN EMOJI
# ==========================================
def show_menu():
    cfg = load_config()
    while True:
        clear()
        # Header đẹp hơn với Gradient giả lập
        print(f"{Col.ORANGE}╔══════════════════════════════════════════╗{Col.RESET}")
        print(f"{Col.ORANGE}║ {Col.BOLD}🍊 GHOSTSPECTRE MANAGER {Col.WHITE}{VERSION:<15}{Col.ORANGE}║{Col.RESET}")
        print(f"{Col.ORANGE}╠══════════════════════════════════════════╣{Col.RESET}")
        
        # Status Line
        sh_icon = "🟢" if cfg['smart_hop'] else "🔴"
        sh_text = f"{Col.GREEN}ON " if cfg['smart_hop'] else f"{Col.RED}OFF"
        
        # Menu Options với Emoji Số
        print(f"{Col.ORANGE}║ {Col.WHITE}1️⃣  Start Automation     {Col.GREEN}🚀 RUN TOOL     {Col.ORANGE}║{Col.RESET}")
        print(f"{Col.ORANGE}║ {Col.WHITE}2️⃣  SmartHop Mode        {sh_icon} {sh_text:<11}{Col.RESET}{Col.ORANGE}║{Col.RESET}")
        print(f"{Col.ORANGE}║ {Col.WHITE}3️⃣  Set Place ID         {Col.CYAN}🎮 GAME ID      {Col.ORANGE}║{Col.RESET}")
        print(f"{Col.ORANGE}║ {Col.WHITE}4️⃣  Hop Time (Min/Max)   {Col.BLUE}⏱️  TIMER       {Col.ORANGE}║{Col.RESET}")
        print(f"{Col.ORANGE}║ {Col.WHITE}5️⃣  Webhook Config       {Col.PURPLE}👾 DISCORD      {Col.ORANGE}║{Col.RESET}")
        print(f"{Col.ORANGE}║ {Col.WHITE}0️⃣  Exit Tool            {Col.RED}🚪 QUIT         {Col.ORANGE}║{Col.RESET}")
        print(f"{Col.ORANGE}╚══════════════════════════════════════════╝{Col.RESET}")
        
        # Input vẫn dùng số thường
        choice = input(f"\n{Col.YELLOW}⚡ Enter Command (1-5): {Col.RESET}")
        
        if choice == "1": return cfg
        elif choice == "2":
            cfg["smart_hop"] = not cfg["smart_hop"]
            save_config(cfg)
        elif choice == "3":
            print(f"\n{Col.CYAN}💎 PRESETS:{Col.RESET}")
            print("1. 🏴‍☠️ Blox Fruit")
            print("2. 🐾 Pet Sim 99")
            print("3. ✍️ Custom ID")
            s = input("👉 Select: ")
            if s == "1": cfg["place_id"] = "2753915549"
            elif s == "2": cfg["place_id"] = "8737899170"
            else: cfg["place_id"] = input("Enter ID: ")
            save_config(cfg)
        elif choice == "4":
            try:
                cfg["hop_min"] = int(input(f"⏱️ Min Minutes: "))
                cfg["hop_max"] = int(input(f"⏱️ Max Minutes: "))
                save_config(cfg)
            except: pass
        elif choice == "5":
            cfg["webhook_url"] = input("🔗 Webhook URL: ")
            save_config(cfg)
        elif choice == "0":
            sys.exit()

# ==========================================
# 📦 ENGINE & DASHBOARD
# ==========================================
def get_hw_info():
    try:
        mem = su_exec("free -m | grep Mem").split()
        ram = round((int(mem[2]) / int(mem[1])) * 100, 1)
        cpu_raw = su_exec("top -n 1 | grep %Cpu").split()
        cpu = float(cpu_raw[1]) if len(cpu_raw) > 1 else 0
        batt = su_exec("dumpsys battery | grep level").split()
        battery = int(batt[1]) if len(batt) > 1 else 0
        temp = int(su_exec("cat /sys/class/thermal/thermal_zone0/temp") or 0)/1000
        return cpu, ram, battery, temp
    except: return 0,0,0,0

class Package:
    def __init__(self, name, cfg):
        self.name = name
        self.cfg = cfg
        self.status = "INIT"
        self.last_hop = time.time()
        self.next_hop_duration = random.randint(cfg["hop_min"]*60, cfg["hop_max"]*60)
        self.restarts = 0

    def launch(self, reason):
        su_exec(f"am force-stop {self.name}")
        time.sleep(1)
        su_exec(f"am start -n {self.name}/com.roblox.client.Activity -d \"roblox://experiences/start?placeId={self.cfg['place_id']}\"")
        self.restarts += 1
        self.last_hop = time.time()
        self.next_hop_duration = random.randint(self.cfg["hop_min"]*60, self.cfg["hop_max"]*60)
        self.status = "RUN"
        global_stats["total_rejoins"] += 1

    def check(self):
        if su_exec(f"pidof {self.name}"):
            self.status = "RUN"
            if self.cfg["smart_hop"] and (time.time() - self.last_hop >= self.next_hop_duration):
                self.launch("🧠 SmartHop")
        else:
            self.status = "DOWN"
            if self.cfg["auto_restart"]: self.launch("Auto Recovery")

def draw_ui(cfg):
    clear()
    uptime = str(datetime.timedelta(seconds=int(time.time()-global_stats['start_time'])))
    c, r, b, t = global_stats['cpu'], global_stats['ram'], global_stats['battery'], global_stats['temp']
    
    # Header Dashboard
    print(f"{Col.ORANGE}╔══════════════════════════════════════════════════╗{Col.RESET}")
    print(f"{Col.ORANGE}║ {Col.BOLD}👻 GHOSTSPECTRE {Col.WHITE}MONITOR {Col.GREEN}● LIVE{Col.RESET}                  {Col.ORANGE}║{Col.RESET}")
    print(f"{Col.ORANGE}╠══════════════════════════════════════════════════╣{Col.RESET}")
    
    # System Stats Row 1
    print(f"{Col.ORANGE}║{Col.RESET} 🧠 CPU: {Col.CYAN}{int(c)}%{Col.RESET}   💾 RAM: {Col.PURPLE}{int(r)}%{Col.RESET}   🔋 PIN: {Col.GREEN}{b}%{Col.RESET}   🌡️ {t}°C {Col.ORANGE}║{Col.RESET}")
    
    # System Stats Row 2
    print(f"{Col.ORANGE}║{Col.RESET} ⏱️ UP : {Col.WHITE}{uptime:<9}{Col.RESET} 🔄 RST: {Col.YELLOW}{global_stats['total_rejoins']:<4}{Col.RESET} 🎮 ID : {cfg['place_id'][:6]}.. {Col.ORANGE}║{Col.RESET}")
    
    print(f"{Col.ORANGE}╠══════════════════════════════════════════════════╣{Col.RESET}")
    print(f"{Col.ORANGE}║ {Col.BOLD}📦 PACKAGE LIST {Col.RESET}                                 {Col.ORANGE}║{Col.RESET}")
    print(f"{Col.ORANGE}╟──────┬──────┬──────────────────────┬─────────────╢{Col.RESET}")
    
    for p in packages:
        # Tên ngắn gọn
        p_name = p.name.split('.')[-1][-4:]
        if "client" in p.name: p_name = "MAIN"
        
        # Icon Status
        if p.status == "RUN": s_icon = "🟢"
        else: s_icon = "🔴"
        
        # Thanh Progress Bar đẹp mắt
        if cfg["smart_hop"]:
            elapsed = time.time() - p.last_hop
            pct = min(1.0, elapsed/p.next_hop_duration)
            filled = int(pct * 12)
            # Dùng ký tự block đẹp hơn
            bar = f"{Col.BLUE}{'━'*filled}{Col.GRAY}{'┄'*(12-filled)}{Col.RESET}"
            timer = f"{int(p.next_hop_duration - elapsed)}s"
        else:
            bar = f"{Col.GRAY}🚫 SMART HOP OFF{Col.RESET}"
            timer = "--"

        print(f"{Col.ORANGE}║{Col.RESET} {p_name:<4} {Col.ORANGE}│{Col.RESET} {s_icon} {Col.ORANGE}│{Col.RESET} {bar} {Col.ORANGE}│{Col.RESET} {timer:<11} {Col.ORANGE}║{Col.RESET}")

    print(f"{Col.ORANGE}╚══════╧══════╧══════════════════════╧═════════════╝{Col.RESET}")

# ==========================================
# 🚀 MAIN RUN
# ==========================================
def main():
    if not check_root():
        print(f"{Col.RED}🚫 ERROR: Cần quyền Root (tsu)!{Col.RESET}")
        return

    # Hiện Menu đầu tiên
    cfg = show_menu()
    
    # Quét Package
    print(f"{Col.YELLOW}🔍 Đang quét clone...{Col.RESET}")
    raw_pkgs = su_exec(f"pm list packages | grep {cfg['prefix']}").replace("package:", "").split()
    if not raw_pkgs:
        # Fallback test mode
        packages.append(Package("com.roblox.client", cfg))
    else:
        for p in raw_pkgs: packages.append(Package(p, cfg))

    global running
    running = True
    
    try:
        while running:
            # Update Info
            c, r, b, t = get_hw_info()
            global_stats.update({"cpu": c, "ram": r, "battery": b, "temp": t})
            
            # Check Pkg
            for p in packages: p.check()
            
            # Draw
            draw_ui(cfg)
            time.sleep(1)
            
    except KeyboardInterrupt:
        running = False
        print(f"\n{Col.RED}👋 Đã tắt Tool!{Col.RESET}")

if __name__ == "__main__":
    main()
    