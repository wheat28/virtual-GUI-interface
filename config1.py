import os
import tarfile
import argparse
import tkinter as tk
from tkinter import scrolledtext
from datetime import datetime


class VirtualFileSystem:
    def __init__(self, tar_path):
        self.tar_path = tar_path
        self.tar = tarfile.open(tar_path, 'r')
        self.current_dir = '/bs'
        self.file_tree = self.build_file_tree()

    def build_file_tree(self):
        file_tree = {}
        for member in self.tar.getmembers():
            path_parts = member.name.strip('/').split('/')
            current = file_tree
            for part in path_parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]
            if member.isdir():
                current[path_parts[-1]] = {}
            else:
                current[path_parts[-1]] = member
        return file_tree

    def list_dir(self, path):
        node = self.get_node(path)
        if node is not None and isinstance(node, dict):
            dirs = [item + '/' for item in node if isinstance(node[item], dict)]
            files = [item for item in node if not isinstance(node[item], dict)]
            return dirs, files
        return [], []

    def change_dir(self, path):
        if path == "/":
            self.current_dir = "/bs"
            return

        parts = path.split('/')
        if path.startswith('/'):
            new_dir = ["bs"]
        else:
            new_dir = self.current_dir.strip('/').split('/')

        for part in parts:
            if part == "..":
                if len(new_dir) > 1:
                    new_dir.pop()
            elif part == "." or part == "":
                continue
            else:
                new_dir.append(part)

        full_path = "/" + "/".join(new_dir).strip('/')
        if self.get_node(full_path) is not None:
            self.current_dir = full_path
        else:
            raise FileNotFoundError(f"cd: no such file or directory: {path}")

    def get_node(self, path):
        parts = path.strip("/").split('/')
        current = self.file_tree
        for part in parts:
            if part and part in current:
                current = current[part]
            else:
                return None
        return current

    def copy(self, source, destination):
        source_path = os.path.join(self.current_dir, source).replace("\\", "/").strip('/')
        src_node = self.get_node(source_path)

        if src_node is None:
            raise FileNotFoundError(f"cp: cannot copy '{source}': No such file or directory")

        if destination.startswith('/'):
            dest_path = destination.strip('/')
        else:
            dest_path = os.path.join(self.current_dir, destination).replace("\\", "/").strip('/')

        dest_parts = dest_path.split('/')
        dest_dir = "/".join(dest_parts[:-1])
        dest_name = dest_parts[-1]

        dest_dir_node = self.get_node(dest_dir) if dest_dir else self.file_tree
        if dest_dir and dest_dir_node is None:
            raise FileNotFoundError(f"cp: cannot copy to '{destination}': Directory does not exist")

        if isinstance(src_node, tarfile.TarInfo) and src_node.isfile():
            if dest_dir:
                dest_dir_node[dest_name] = src_node
            else:
                self.file_tree[dest_name] = src_node
        elif isinstance(src_node, dict):
            def recursive_copy(src, dest):
                for name, node in src.items():
                    if isinstance(node, dict):
                        dest[name] = {}
                        recursive_copy(node, dest[name])
                    else:
                        dest[name] = node

            if dest_dir:
                dest_dir_node[dest_name] = {}
                recursive_copy(src_node, dest_dir_node[dest_name])
            else:
                self.file_tree[dest_name] = {}
                recursive_copy(src_node, self.file_tree[dest_name])


class ShellEmulator:
    def __init__(self, root, username, vfs, log_file=None):
        self.root = root
        self.root.title("Shell Emulator")
        self.prompt_length = 0

        self.output = scrolledtext.ScrolledText(root, height=30, width=80, state=tk.DISABLED, bg="black", fg="white")
        self.output.pack()

        self.input = tk.Entry(root, width=80)
        self.input.pack()
        self.input.bind("<Return>", self.run_command)
        self.input.bind("<KeyPress>", self.on_key_press)

        self.username = username
        self.vfs = vfs
        self.log_file = log_file

        # Вывод содержимого лог-файла
        self.display_log()
        self.update_prompt()

    def display_log(self):
        if self.log_file and os.path.exists(self.log_file):
            with open(self.log_file, 'r') as log:
                log_contents = log.read()
                if log_contents:
                    self.output.config(state=tk.NORMAL)
                    self.output.insert(tk.END, "Log file contents:\n")
                    self.output.insert(tk.END, log_contents)
                    self.output.insert(tk.END, "\n---------------------------------\n")
                    self.output.config(state=tk.DISABLED)

    def run_command(self, event):
        command_input = self.input.get().split('$', 1)[-1].strip()

        self.log_action(command_input)

        if self.vfs.current_dir == "/bs":
            display_dir = "~"
        else:
            display_dir = self.vfs.current_dir.replace("/bs", "~", 1)

        self.output.config(state=tk.NORMAL)
        self.output.insert(tk.END, f"{self.username}@virtual:{display_dir}$ {command_input}\n")
        self.execute_command(command_input)
        self.update_prompt()
        self.output.config(state=tk.DISABLED)

    def log_action(self, command_input):
        if self.log_file:
            # Splitting the command input into command and operands
            parts = command_input.split(maxsplit=1)
            command = parts[0]
            operands = parts[1] if len(parts) > 1 else ""

            # Writing the log entry with the correct format
            with open(self.log_file, 'a') as log:
                log.write(f"{datetime.now().strftime('%Y-%m-%d,%H:%M:%S')},{command},{operands}\n")


    def on_key_press(self, event):
        if self.input.index(tk.INSERT) < self.prompt_length and event.keysym in ("BackSpace", "Left"):
            return "break"

    def human_readable_size(self, size):
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024:
                return f"{size:.1f}{unit}"
            size /= 1024
        return f"{size:.1f}PB"

    def update_prompt(self):
        if self.vfs.current_dir == "/bs":
            prompt_dir = "~"
        else:
            prompt_dir = self.vfs.current_dir.replace("/bs", "~", 1)

        prompt = f"{self.username}@virtual:{prompt_dir}$ "
        self.input.delete(0, tk.END)
        self.input.insert(0, prompt)
        self.input.icursor(len(prompt))
        self.prompt_length = len(prompt)

    def execute_command(self, command):
        parts = command.split()
        if not parts:
            return
        cmd = parts[0]

        if cmd == "ls":
            flags = [p for p in parts if p.startswith('-')]
            self.ls(flags)
        elif cmd == "cd":
            if len(parts) > 1:
                self.cd(parts[1])
            else:
                self.write_output("cd: missing operand\n")
        elif cmd == "cp":
            if len(parts) == 3:
                self.cp(parts[1], parts[2])
            else:
                self.write_output("cp: missing operands\n")
        elif cmd == "clear":
            self.clear()
        elif cmd == "exit":
            self.root.quit()
            raise SystemExit
        else:
            self.write_output(f"{cmd}: command not found\n")

    def ls(self, flags=[]):
        try:
            dirs, files = self.vfs.list_dir(self.vfs.current_dir)
            output = []
            if '-l' in flags:
                for d in dirs:
                    output.append(self.format_entry(d, is_dir=True, flags=flags))
                for f in files:
                    output.append(self.format_entry(f, is_dir=False, flags=flags))
            else:
                output = dirs + files

            if not output:
                self.write_output("\n")
            else:
                self.write_output("\n".join(output) + "\n")
        except FileNotFoundError:
            self.write_output(f"ls: cannot access '{self.vfs.current_dir}': No such directory")

    def format_entry(self, entry, is_dir, flags):
        node = self.vfs.get_node(os.path.join(self.vfs.current_dir, entry.strip('/')))
        info = node if not isinstance(node, dict) else None
        size = info.size if info else 0
        size_str = self.human_readable_size(size) if '-h' in flags else str(size)
        file_type = 'd' if is_dir else '-'
        permissions = 'rw-r--r--'
        links = 1
        owner = 'root'
        group = 'root'
        mtime = datetime.fromtimestamp(info.mtime).strftime('%b %d %Y') if info else ''
        return f"{file_type}{permissions} {links} {owner} {group} {size_str:>8} {mtime} {entry}"

    def cd(self, path):
        try:
            self.vfs.change_dir(path)
        except FileNotFoundError:
            self.write_output(f"cd: no such file or directory: {path}\n")

    def clear(self):
        self.output.config(state=tk.NORMAL)
        self.output.delete(1.0, tk.END)
        self.output.config(state=tk.DISABLED)

    def cp(self, source, destination):
        try:
            self.vfs.copy(source, destination)
            self.write_output(f"Copied {source} to {destination}\n")
        except FileNotFoundError:
            self.write_output(f"cp: cannot copy '{source}': No such file or directory\n")

    def write_output(self, text):
        self.output.config(state=tk.NORMAL)
        self.output.insert(tk.END, text)
        self.output.see(tk.END)
        self.output.config(state=tk.DISABLED)

    def get_output_content(self):
        return self.output.get("1.0", tk.END).strip()


def main():
    parser = argparse.ArgumentParser(description="Shell Emulator")
    parser.add_argument('--user', required=True, help="Username for shell prompt")
    parser.add_argument('--vfs', required=True, help="Path to the virtual file system (tar archive)")
    parser.add_argument('--log', required=True, help="Path to the log file")

    args = parser.parse_args()

    vfs = VirtualFileSystem(args.vfs)
    root = tk.Tk()
    shell = ShellEmulator(root, args.user, vfs, args.log)

    root.mainloop()


if __name__ == "__main__":
    main()
