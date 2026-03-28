import tkinter as tk
from coincurve import PrivateKey, PublicKey


class InputDialog(tk.Toplevel):
    def __init__(self, parent, title, fields):
        super().__init__(parent)
        self.title(title)
        self.result = None
        self.entries = []

        w, h = 340, 50 + len(fields) * 62
        px = parent.winfo_rootx() + (480 - w) // 2
        py = parent.winfo_rooty() + (320 - h) // 2
        self.geometry(f"{w}x{h}+{px}+{py}")
        self.resizable(False, False)
        self.configure(bg="#1a1a2e")
        self.grab_set()

        for label_text, _ in fields:
            tk.Label(
                self, text=label_text, bg="#1a1a2e", fg="#a0a0c0",
                font=("Helvetica", 9)
            ).pack(anchor="w", padx=12, pady=(10, 0))
            entry = tk.Entry(
                self, bg="#0f0f23", fg="#e0e0ff", font=("Courier", 9),
                relief=tk.FLAT, insertbackground="white",
                highlightbackground="#3a3a5c", highlightthickness=1
            )
            entry.pack(fill=tk.X, padx=12)
            self.entries.append(entry)

        btn_row = tk.Frame(self, bg="#1a1a2e")
        btn_row.pack(fill=tk.X, padx=12, pady=10)
        tk.Button(
            btn_row, text="Cancel", command=self.destroy,
            bg="#2d0a0a", fg="#ef9a9a", font=("Helvetica", 9, "bold"),
            relief=tk.FLAT, width=8, cursor="hand2"
        ).pack(side=tk.RIGHT, padx=(4, 0))
        tk.Button(
            btn_row, text="OK", command=self._ok,
            bg="#16213e", fg="#4fc3f7", font=("Helvetica", 9, "bold"),
            relief=tk.FLAT, width=8, cursor="hand2"
        ).pack(side=tk.RIGHT)

        if self.entries:
            self.entries[0].focus_set()
        self.wait_window()

    def _ok(self):
        self.result = [e.get() for e in self.entries]
        self.destroy()


class KeyGenApp:
    BG       = "#1a1a2e"
    PANEL_BG = "#0f0f23"
    BTN_BG   = "#16213e"
    BTN_EXIT = "#2d0a0a"

    BUTTONS = [
        ("1  Create Key Pair",   "#4fc3f7"),
        ("2  Verify Signature",  "#81c784"),
        ("3  Sign Message",      "#ffb74d"),
        ("4  Display Keys",      "#ce93d8"),
        ("5  Exit",              "#ef9a9a"),
    ]

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Key Generator")
        self.root.geometry("480x320")
        self.root.resizable(False, False)
        self.root.configure(bg=self.BG)

        self.private_key = None
        self.public_key  = None

        self._build_ui()
        self._show("Welcome!\n\nSelect an option to get started.")

    # ------------------------------------------------------------------ UI --

    def _build_ui(self):
        # ---- left: output pane ----
        left = tk.Frame(self.root, bg=self.BG)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(8, 4), pady=8)

        tk.Label(
            left, text="Output", bg=self.BG, fg="#606080", font=("Courier", 8)
        ).pack(anchor="w")

        self.output = tk.Text(
            left, bg=self.PANEL_BG, fg="#dde0ff", font=("Courier", 9),
            wrap=tk.WORD, state=tk.DISABLED, relief=tk.FLAT,
            highlightbackground="#3a3a5c", highlightthickness=1,
            padx=6, pady=6
        )
        self.output.pack(fill=tk.BOTH, expand=True)

        # ---- right: button pane ----
        right = tk.Frame(self.root, bg=self.BG, width=148)
        right.pack(side=tk.RIGHT, fill=tk.Y, padx=(4, 8), pady=8)
        right.pack_propagate(False)

        actions = [
            self.create_key,
            self.verify_signature,
            self.sign_message,
            self.display_keys,
            self.exit_app,
        ]

        for (label, color), cmd in zip(self.BUTTONS, actions):
            bg = self.BTN_EXIT if "Exit" in label else self.BTN_BG
            btn = tk.Button(
                right, text=label, command=cmd,
                bg=bg, fg=color, font=("Helvetica", 9, "bold"),
                relief=tk.FLAT, activebackground="#2a2a4e",
                activeforeground=color, bd=0, cursor="hand2",
                anchor="w", padx=10
            )
            btn.pack(fill=tk.X, pady=3, ipady=9)

    # --------------------------------------------------------------- helpers --

    def _show(self, message: str):
        self.output.config(state=tk.NORMAL)
        self.output.delete("1.0", tk.END)
        self.output.insert(tk.END, message)
        self.output.config(state=tk.DISABLED)

    def _ask(self, title: str, fields: list[tuple[str, bool]]):
        dlg = InputDialog(self.root, title, fields)
        return dlg.result

    # ------------------------------------------------------------- actions --

    def create_key(self):
        self.private_key = PrivateKey()
        self.public_key  = self.private_key.public_key
        self._show("Key pair generated successfully!\n\nUse  4  Display Keys  to view them.")

    def verify_signature(self):
        result = self._ask("Verify Signature", [
            ("Message",           False),
            ("Signature (hex)",   False),
            ("Public Key (hex)",  False),
        ])
        if result is None:
            return
        message, sig_hex, pub_hex = result
        try:
            sig_bytes = bytes.fromhex(sig_hex)
            pub_bytes = bytes.fromhex(pub_hex)
            PublicKey(pub_bytes).verify(sig_bytes, message.encode())
            self._show("✓  Signature is VALID.")
        except Exception as exc:
            self._show(f"✗  Signature is INVALID.\n\n{exc}")

    def sign_message(self):
        if self.private_key is None:
            self._show("No key pair found.\nUse  1  Create Key Pair  first.")
            return
        result = self._ask("Sign Message", [("Message", False)])
        if result is None:
            return
        signature = self.private_key.sign(result[0].encode())
        self._show(f"Signature (hex):\n\n{signature.hex()}")

    def display_keys(self):
        if self.private_key is None:
            self._show("No keys generated yet.\nUse  1  Create Key Pair  first.")
            return
        pri = self.private_key.to_hex()
        pub = self.public_key.format().hex()
        self._show(f"Private Key:\n{pri}\n\nPublic Key:\n{pub}")

    def exit_app(self):
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    KeyGenApp(root)
    root.mainloop()
