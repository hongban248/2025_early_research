#!/usr/bin/env python3
import os, json, subprocess, sys
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox

# ---------- 1. 基础路径 ----------
DEFAULT_GAME_DIR = "/mnt/disk1/Program Files/pcl2/.minecraft"
VERSION_ID       = "1.20.1-Forge_47.2.18"

# ---------- 2. 从 version.json 读取 Forge 启动参数 ----------
def load_version_json(game_dir, vid):
    vjson = Path(game_dir) / "versions" / vid / f"{vid}.json"
    with open(vjson) as f:
        return json.load(f)

# ---------- 3. 拼出完整类路径 ----------
def build_classpath(game_dir, version_data):
    libs = [Path(game_dir) / "libraries" / lib["path"] for lib in version_data["libraries"]]
    client_jar = Path(game_dir) / "versions" / version_data["id"] / f"{version_data['id']}.jar"
    return os.pathsep.join([str(p) for p in libs + [client_jar]])

# ---------- 4. 组装 JVM 命令 ----------
def build_command(game_dir, version_data, username="Steve", uuid=None, access_token="0"):
    jvm  = "java"
    main = version_data["mainClass"]
    cp   = build_classpath(game_dir, version_data)
    game_args = version_data["minecraftArguments"].replace(
        "${auth_player_name}", username
    ).replace(
        "${version_name}", version_data["id"]
    ).replace(
        "${game_directory}", str(Path(game_dir))
    ).replace(
        "${assets_root}", str(Path(game_dir) / "assets")
    ).replace(
        "${assets_index_name}", version_data.get("assets", "legacy")
    ).replace(
        "${auth_uuid}", uuid or "00000000-0000-0000-0000-000000000000"
    ).replace(
        "${auth_access_token}", access_token
    )

    return [
        jvm,
        "-Xmx4G", "-Xms2G",
        "-Djava.library.path=" + str(Path(game_dir) / "versions" / version_data["id"] / "natives"),
        "-cp", cp,
        main,
        *game_args.split()
    ]

# ---------- 5. GUI ----------
class LauncherGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("MC Launcher (Ubuntu)")
        self.geometry("420x120")
        self.resizable(False, False)

        tk.Label(self, text="游戏目录：").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.path_var = tk.StringVar(value=DEFAULT_GAME_DIR)
        tk.Entry(self, textvariable=self.path_var, width=45).grid(row=0, column=1, padx=5)
        tk.Button(self, text="浏览…", command=self.browse).grid(row=0, column=2, padx=5)

        tk.Button(self, text="启动游戏", command=self.launch, width=15, height=2).grid(
            row=1, column=0, columnspan=3, pady=10)

    def browse(self):
        new_dir = filedialog.askdirectory(initialdir=self.path_var.get())
        if new_dir:
            self.path_var.set(new_dir)

    def launch(self):
        game_dir = Path(self.path_var.get())
        try:
            vdata = load_version_json(game_dir, VERSION_ID)
            cmd   = build_command(game_dir, vdata)
            subprocess.Popen(cmd)
        except Exception as e:
            messagebox.showerror("启动失败", str(e))

# ---------- 6. 入口 ----------
if __name__ == "__main__":
    LauncherGUI().mainloop()