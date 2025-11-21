import configparser, tkinter as tk
from tkinter import ttk, messagebox

def cfg(a, s, k, d):
    i = configparser.ConfigParser()
    try:
        i.read(a, encoding="utf-8")
        return i.get(s, k, fallback=d)
    except:
        return d

def cfgi(a, s, k, d):
    i = configparser.ConfigParser()
    try:
        i.read(a, encoding="utf-8")
        return i.getint(s, k, fallback=d)
    except:
        return d

C = {k: cfg("color.ini", "colors", k, "#000") for k in [
    "fundo", "header", "card", "destaque", "texto", "botao", "botao_txt",
    "botao_ativo", "botao_ativo_txt", "quadro_selec", "quadro_normal",
    "quadro_texto", "quadro_null", "borda"
]}
F = (cfg("font.ini", "font", "nome", "Arial"), cfgi("font.ini", "font", "tamanho", 9))

I = configparser.ConfigParser()
I.read("interface.ini", encoding="utf-8")
D = ({s + "_" + k: I.getint(s, k, fallback=0)
      for s in ["janela", "toolbar", "statusbar", "celula", "botao", "label", "entry", "espacamento"]
      for k in I.options(s)} if I.sections() else {})

FCONF = configparser.ConfigParser()
FCONF.optionxform = str
FCONF.read("flags.ini", encoding="utf-8")

def load_flags():
    r = [(v, int(k, 0)) for k, v in FCONF["item"].items()]
    e = [(v, int(k, 0)) for k, v in FCONF["enchant"].items()]
    c = [(s.split("_", 1)[1], [(v, k) for k, v in FCONF[s].items()])
         for s in FCONF.sections() if s.startswith("class_")]
    p = [(v, int(k, 0)) for k, v in FCONF["ItemPlus"].items()] if "ItemPlus" in FCONF else []
    return r, e, c, p

R, E, CLS, P = load_flags()

h2i = lambda h: int(h, 16)
i2h = lambda v: f"{v:X}"
is_hex = lambda v: all(c in "0123456789abcdefABCDEF" for c in (v[2:] if v.lower().startswith("0x") else v)) and v != ""

class Tab(tk.Frame):
    def __init__(self, p, cb):
        super().__init__(p, bg=C["fundo"])
        self.s = set()
        self.cs = {}
        self.t = 0
        self.cb = cb

    def mk_cell(self, p, txt, val, b=False):
        f = tk.Frame(p, bg=C["quadro_normal"], highlightbackground=C["borda"],
                     highlightthickness=D.get("celula_borda", 1), cursor="hand2",
                     width=D.get("celula_largura", 140), height=D.get("celula_altura", 36))
        f.pack_propagate(False)
        ft = (F[0], F[1], "bold") if b else F
        l = tk.Label(f, text=txt, font=ft, fg=C["texto"], bg=C["quadro_normal"], anchor="center")
        l.pack(expand=True, fill=tk.BOTH, padx=D.get("celula_padx", 6), pady=D.get("celula_pady", 6))
        for w in [f, l]:
            w.bind("<Button-1>", lambda e, v=val: self.tog(v))
            w.bind("<Enter>", lambda e, fr=f: fr.config(highlightbackground=C["destaque"]))
            w.bind("<Leave>", lambda e, fr=f, vl=val: fr.config(highlightbackground=(C["quadro_selec"] if vl in self.s else C["borda"])))
        self.cs[val] = f
        return f

    def mk_null(self, p):
        return tk.Frame(p, bg=C["quadro_null"], highlightthickness=0)

    def tog(self, v):
        f, l = self.cs[v], self.cs[v].winfo_children()[0]
        if v in self.s:
            self.s.remove(v)
            f.config(bg=C["quadro_normal"], highlightbackground=C["borda"])
            l.config(bg=C["quadro_normal"], fg=C["texto"])
        else:
            self.s.add(v)
            f.config(bg=C["quadro_selec"], highlightbackground=C["quadro_selec"])
            l.config(bg=C["quadro_selec"], fg=C["quadro_texto"])
        self.upd()

    def upd(self):
        pass

    def mark_all(self):
        self.s = set(self.cs.keys())
        for f in self.cs.values():
            f.config(bg=C["quadro_selec"], highlightbackground=C["quadro_selec"])
            f.winfo_children()[0].config(bg=C["quadro_selec"], fg=C["quadro_texto"])
        self.upd()

    def clear_all(self):
        self.s.clear()
        self.t = 0
        for f in self.cs.values():
            f.config(bg=C["quadro_normal"], highlightbackground=C["borda"])
            f.winfo_children()[0].config(bg=C["quadro_normal"], fg=C["texto"])
        self.upd()

class TabItem(Tab):
    def __init__(self, p, cb):
        super().__init__(p, cb)
        g = tk.Frame(self, bg=C["fundo"])
        g.pack(expand=True)
        nc = 4
        nr = (len(R) + nc - 1) // nc
        for i, (n, v) in enumerate(R):
            c = self.mk_cell(g, n, v)
            c.grid(row=i % nr, column=i // nr, sticky="nsew", padx=D.get("celula_padding", 3), pady=D.get("celula_padding", 3))
        for col in range(nc):
            g.grid_columnconfigure(col, weight=1, uniform="c")
        for row in range(nr):
            g.grid_rowconfigure(row, weight=1, uniform="r")

    def upd(self):
        t = 0
        for v in self.s:
            t += v
        self.t = t
        self.cb(t)

    def chk(self, val):
        if not val.isdigit():
            messagebox.showwarning("Error", "Invalid decimal value.")
            return
        d = int(val)
        sel = [v for v in self.cs if (d & v) == v and v != 0]
        if not sel and d != 0:
            messagebox.showinfo("Info", "No flag matches.")
            return
        self.s.clear()
        for v, f in self.cs.items():
            l = f.winfo_children()[0]
            if (d & v) == v and v != 0:
                self.s.add(v)
                f.config(bg=C["quadro_selec"], highlightbackground=C["quadro_selec"])
                l.config(bg=C["quadro_selec"], fg=C["quadro_texto"])
            else:
                f.config(bg=C["quadro_normal"], highlightbackground=C["borda"])
                l.config(bg=C["quadro_normal"], fg=C["texto"])
        self.t = d
        self.cb(d)

class TabItemOP(Tab):
    def __init__(self, p, cb):
        super().__init__(p, cb)
        g = tk.Frame(self, bg=C["fundo"])
        g.pack(expand=True)
        nc = 4
        nr = (len(P) + nc - 1) // nc
        for i, (n, v) in enumerate(P):
            c = self.mk_cell(g, n, v)
            c.grid(row=i % nr, column=i // nr, sticky="nsew", padx=D.get("celula_padding", 3), pady=D.get("celula_padding", 3))
        for col in range(nc):
            g.grid_columnconfigure(col, weight=1, uniform="c")
        for row in range(nr):
            g.grid_rowconfigure(row, weight=1, uniform="r")

    def upd(self):
        t = 0
        for v in self.s:
            t += v
        self.t = t
        self.cb(t)

    def chk(self, val):
        if not val.isdigit():
            messagebox.showwarning("Error", "Invalid decimal value.")
            return
        d = int(val)
        sel = [v for v in self.cs if (d & v) == v and v != 0]
        if not sel and d != 0:
            messagebox.showinfo("Info", "No flag matches.")
            return
        self.s.clear()
        for v, f in self.cs.items():
            l = f.winfo_children()[0]
            if (d & v) == v and v != 0:
                self.s.add(v)
                f.config(bg=C["quadro_selec"], highlightbackground=C["quadro_selec"])
                l.config(bg=C["quadro_selec"], fg=C["quadro_texto"])
            else:
                f.config(bg=C["quadro_normal"], highlightbackground=C["borda"])
                l.config(bg=C["quadro_normal"], fg=C["texto"])
        self.t = d
        self.cb(d)

class TabClass(Tab):
    def __init__(self, p, cb):
        super().__init__(p, cb)
        g = tk.Frame(self, bg=C["fundo"])
        g.pack(expand=True)
        n = CLS[0][1]
        o = CLS[1:]
        nc = 1 + len(o)
        mr = max(len(x[1]) for x in o)
        tr = mr
        for r in range(tr):
            if r < len(n):
                nm, hid = n[r]
                c = self.mk_cell(g, nm, hid, b=True)
                c.grid(row=r, column=0, sticky="nsew", padx=D.get("celula_padding", 3), pady=D.get("celula_padding", 3))
            else:
                c = self.mk_null(g)
                c.grid(row=r, column=0, sticky="nsew", padx=D.get("celula_padding", 3), pady=D.get("celula_padding", 3))
        for col, (_, cls) in enumerate(o, start=1):
            for r in range(tr):
                if r < len(cls):
                    nm, hid = cls[r]
                    c = self.mk_cell(g, nm, hid)
                    c.grid(row=r, column=col, sticky="nsew", padx=D.get("celula_padding", 3), pady=D.get("celula_padding", 3))
        for col in range(nc):
            g.grid_columnconfigure(col, weight=1, uniform="c")
        for row in range(tr):
            g.grid_rowconfigure(row, weight=1, uniform="r")

    def upd(self):
        t = 0
        for h in self.s:
            t |= h2i(h)
        self.t = t
        self.cb(t)

    def chk(self, val):
        if val.lower().startswith("0x"):
            val = val[2:]
        if not is_hex(val):
            messagebox.showwarning("Error", "Invalid hexadecimal value.")
            return
        d = int(val, 16)
        sel = [h for h in self.cs if (d & h2i(h)) == h2i(h) and h2i(h) != 0]
        if not sel and d != 0:
            messagebox.showinfo("Info", "No flag matches.")
            return
        self.s.clear()
        for h, f in self.cs.items():
            l = f.winfo_children()[0]
            if (d & h2i(h)) == h2i(h) and h2i(h) != 0:
                self.s.add(h)
                f.config(bg=C["quadro_selec"], highlightbackground=C["quadro_selec"])
                l.config(bg=C["quadro_selec"], fg=C["quadro_texto"])
            else:
                f.config(bg=C["quadro_normal"], highlightbackground=C["borda"])
                l.config(bg=C["quadro_normal"], fg=C["texto"])
        self.t = d
        self.cb(d)

class TabEnch(Tab):
    def __init__(self, p, cb):
        super().__init__(p, cb)
        g = tk.Frame(self, bg=C["fundo"])
        g.pack(expand=True)
        nc = 4
        nr = (len(E) + nc - 1) // nc
        for i, (n, v) in enumerate(E):
            c = self.mk_cell(g, n, v)
            c.grid(row=i % nr, column=i // nr, sticky="nsew", padx=D.get("celula_padding", 3), pady=D.get("celula_padding", 3))
        for col in range(nc):
            g.grid_columnconfigure(col, weight=1, uniform="c")
        for row in range(nr):
            g.grid_rowconfigure(row, weight=1, uniform="r")

    def upd(self):
        t = 0
        for v in self.s:
            t += v
        self.t = t
        self.cb(t)

    def chk(self, val):
        if not val.isdigit():
            messagebox.showwarning("Error", "Invalid decimal value.")
            return
        d = int(val)
        sel = [v for v in self.cs if (d & v) == v and v != 0]
        if not sel and d != 0:
            messagebox.showinfo("Info", "No flag matches.")
            return
        self.s.clear()
        for v, f in self.cs.items():
            l = f.winfo_children()[0]
            if (d & v) == v and v != 0:
                self.s.add(v)
                f.config(bg=C["quadro_selec"], highlightbackground=C["quadro_selec"])
                l.config(bg=C["quadro_selec"], fg=C["quadro_texto"])
            else:
                f.config(bg=C["quadro_normal"], highlightbackground=C["borda"])
                l.config(bg=C["quadro_normal"], fg=C["texto"])
        self.t = d
        self.cb(d)

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Flags Calculator")
        self.geometry(f"{D.get('janela_largura', 720)}x{D.get('janela_altura', 550)}")
        self.resizable(False, False)
        self.configure(bg=C["fundo"])
        self.cur = "itens"
        self.mk_toolbar()
        self.cnt = tk.Frame(self, bg=C["fundo"])
        self.cnt.pack(fill="both", expand=True)
        self.tabs = {
            "itens": TabItem(self.cnt, self.upd_res),
            "ItemPlus": TabItemOP(self.cnt, self.upd_res),
            "classes": TabClass(self.cnt, self.upd_res),
            "enchants": TabEnch(self.cnt, self.upd_res)
        }
        self.mk_statusbar()
        self.tabs["itens"].pack(fill="both", expand=True)
        self.sw_tab("itens")

    def mk_toolbar(self):
        tb = tk.Frame(self, bg=C["header"], height=D.get("toolbar_altura", 42))
        tb.pack(side=tk.TOP, fill="x")
        tb.pack_propagate(False)
        c = tk.Frame(tb, bg=C["header"])
        c.pack(expand=True, padx=D.get("toolbar_padx", 8), pady=D.get("toolbar_pady", 6))
        tk.Label(c, font=(F[0], 9, "bold"), fg=C["destaque"], bg=C["header"]).pack(side=tk.LEFT, padx=(0, D.get("label_padx", 6)))
        self.btns = {}
        for txt, key in [("Item", "itens"), ("ItemPlus", "ItemPlus"), ("Class", "classes"), ("Enchant", "enchants")]:
            btn = tk.Button(c, text=txt, command=lambda k=key: self.sw_tab(k), font=(F[0], 9, "bold"),
                            bg=C["botao"], fg=C["botao_txt"], activebackground=C["botao_ativo"], activeforeground=C["botao_ativo_txt"],
                            relief="flat", bd=0, width=D.get("botao_largura", 80)//7, pady=D.get("botao_pady", 6), cursor="hand2")
            btn.pack(side=tk.LEFT, padx=D.get("botao_padx", 2))
            self.btns[key] = btn

    def mk_statusbar(self):
        sb = tk.Frame(self, bg=C["header"], height=D.get("statusbar_altura", 42))
        sb.pack(side=tk.BOTTOM, fill="x")
        sb.pack_propagate(False)
        l = tk.Frame(sb, bg=C["header"])
        l.pack(side=tk.LEFT, fill="y", padx=D.get("statusbar_padx", 8), pady=D.get("statusbar_pady", 6))
        self.mk_btn(l, "Check").pack(side=tk.LEFT, padx=D.get("botao_padx", 2))
        self.ent = tk.Entry(
            l, font=(F[0], 9), justify="center", width=D.get("entry_largura", 18),
            bg=C["card"], fg=C["texto"], insertbackground=C["destaque"], relief="flat", bd=1
        )
        self.ent.pack(side=tk.LEFT, ipady=D.get("botao_pady", 6))
        self.mk_btn(l, "Copy").pack(side=tk.LEFT, padx=D.get("botao_padx", 2))
        r = tk.Frame(sb, bg=C["header"])
        r.pack(side=tk.RIGHT, fill="y", padx=D.get("statusbar_padx", 8), pady=D.get("statusbar_pady", 6))
        self.mk_btn(r, "Mark").pack(side=tk.LEFT, padx=(0, D.get("botao_padx", 2)))
        self.mk_btn(r, "Clear").pack(side=tk.LEFT, padx=(0, D.get("botao_padx", 2)))

    def mk_btn(self, p, txt):
        cmd = {"Mark": self.mark, "Clear": self.clr, "Check": self.chk, "Copy": self.cpy}[txt]
        return tk.Button(p, text=txt, command=cmd, font=(F[0], 9, "bold"),
                         bg=C["botao"], fg=C["botao_txt"], activebackground=C["botao_ativo"], activeforeground=C["botao_ativo_txt"],
                         relief="flat", bd=0, width=D.get("botao_largura", 80)//7, pady=D.get("botao_pady", 6), cursor="hand2")

    def upd_res(self, tot):
        self.ent.delete(0, tk.END)
        if tot != 0:
            self.ent.insert(0, f"{tot}" if self.cur in ["itens", "ItemPlus", "enchants"] else i2h(tot))

    def chk(self):
        self.tabs[self.cur].chk(self.ent.get().strip())

    def cpy(self):
        v = (str(self.tabs[self.cur].t) if self.cur in ["itens", "ItemPlus", "enchants"] else i2h(self.tabs[self.cur].t))
        self.clipboard_clear()
        self.clipboard_append(v)
        messagebox.showinfo("Success", f"Value {v} copied!")

    def mark(self):
        self.tabs[self.cur].mark_all()

    def clr(self):
        self.tabs[self.cur].clear_all()

    def sw_tab(self, k):
        for key, tab in self.tabs.items():
            tab.pack_forget()
        self.tabs[k].pack(fill="both", expand=True)
        self.cur = k
        for key, btn in self.btns.items():
            if key == k:
                btn.config(bg=C["botao_ativo"], fg=C["botao_ativo_txt"])
            else:
                btn.config(bg=C["botao"], fg=C["botao_txt"])
        self.upd_res(self.tabs[k].t)

if __name__ == "__main__":
    app = App()
    app.mainloop()
