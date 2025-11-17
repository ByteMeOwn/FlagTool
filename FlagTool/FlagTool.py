import configparser, tkinter as tk
from tkinter import messagebox

def carregar_cores():
    ini = configparser.ConfigParser()
    ini.read("color.ini", encoding="utf-8")
    c = dict(ini["colors"])
    return {
        "fundo": c["fundo"],
        "header": c["header"],
        "card": c["card"],
        "destaque": c["destaque"],
        "texto": c["texto"],
        "botao": c["botao"],
        "botao_txt": c["botao_txt"],
        "botao_ativo": c["botao_ativo"],
        "botao_ativo_txt": c["botao_ativo_txt"],
        "quadro_selec": c["quadro_selec"],
        "quadro_normal": c["quadro_normal"],
        "quadro_texto": c["quadro_texto"],
        "copyright_bg": c["copyright_bg"],
    }

def carregar_flags():
    ini = configparser.ConfigParser()
    ini.read("flags.ini", encoding="utf-8")
    restricoes = [(k, int(v,0)) for k, v in ini["item"].items()]
    enchants = [(k, int(v,0)) for k, v in ini["enchant"].items()]
    classes_categorias = []
    for sec in ini.sections():
        if sec.startswith("classe_"):
            cat = sec.split("_",1)[1]
            pares = [(k,ini[sec][k]) for k in ini[sec]]
            classes_categorias.append((cat, pares))
    return restricoes, enchants, classes_categorias

CORES = carregar_cores()
restricoes, enchants, classes_por_categoria = carregar_flags()
FONTE = ("Tahoma", 10)
HEADER_FOOTER_HEIGHT = 48

def hexstr_to_int(hexstr): return int(hexstr,16)
def int_to_hexstr(val): return f"{val:X}"
def is_hexadecimal(valor):
    if valor.lower().startswith("0x"): valor=valor[2:]
    return all(c in "0123456789abcdefABCDEF" for c in valor) and valor != ""

class AbaItens(tk.Frame):
    def __init__(self, master, cb, rf): super().__init__(master,bg=CORES["fundo"]); self.selected=set(); self.cf={}; self.total=0; self.cb=cb; self.rf=rf; self.build()
    def build(self):
        inner = tk.Frame(self, bg=CORES["fundo"]); inner.pack(expand=True)
        lista = restricoes; nc=4; nl=(len(lista)+nc-1)//nc
        for i,(n,v) in enumerate(lista):
            f=tk.Frame(inner,bg=CORES["quadro_normal"],bd=2,relief="ridge",width=160,height=44,cursor="hand2")
            col,row=i//nl,i%nl; f.grid(row=row,column=col,sticky="nsew",padx=5,pady=5); f.pack_propagate(False)
            l=tk.Label(f,text=n,font=("Tahoma",11),fg=CORES["texto"],bg=CORES["quadro_normal"]); l.pack(expand=True,fill=tk.BOTH)
            f.bind("<Button-1>",lambda e,v=v:self.toggle_selection(v)); l.bind("<Button-1>",lambda e,v=v:self.toggle_selection(v)); self.cf[v]=f
        for col in range(nc): inner.grid_columnconfigure(col,weight=1)
    def toggle_selection(self,v):
        f,l=self.cf[v],self.cf[v].winfo_children()[0]
        if v in self.selected:self.selected.remove(v);f.config(bg=CORES["quadro_normal"]);l.config(bg=CORES["quadro_normal"],fg=CORES["texto"])
        else:self.selected.add(v);f.config(bg=CORES["quadro_selec"]);l.config(bg=CORES["quadro_selec"],fg=CORES["quadro_texto"])
        self.update_total();self.rf()
    def update_total(self):
        self.total=sum(self.selected);self.cb(self.total)
    def checar_decimal(self,valor):
        if not valor.isdigit():messagebox.showwarning("Valor inválido","Digite um valor decimal válido.");return
        decimal=int(valor)
        sel=[v for v in self.cf if (decimal&v)==v and v!=0]
        if not sel and decimal!=0:messagebox.showinfo("Nenhuma Flag","Nenhuma flag corresponde.");return
        self.selected.clear()
        for v,f in self.cf.items():
            l=f.winfo_children()[0]
            if(decimal&v)==v and v!=0:self.selected.add(v);f.config(bg=CORES["quadro_selec"]);l.config(bg=CORES["quadro_selec"],fg=CORES["quadro_texto"])
            else:f.config(bg=CORES["quadro_normal"]);l.config(bg=CORES["quadro_normal"],fg=CORES["texto"])
        self.total=decimal;self.cb(decimal)
    def marcar_tudo(self):self.selected=set(self.cf.keys());[f.config(bg=CORES["quadro_selec"])or f.winfo_children()[0].config(bg=CORES["quadro_selec"],fg=CORES["quadro_texto"]) for f in self.cf.values()];self.update_total();self.rf()
    def limpar_selecoes(self):self.selected.clear();self.total=0;[f.config(bg=CORES["quadro_normal"])or f.winfo_children()[0].config(bg=CORES["quadro_normal"],fg=CORES["texto"]) for f in self.cf.values()];self.update_total();self.rf()

class AbaClasses(tk.Frame):
    def __init__(self, master, cb, rf): super().__init__(master, bg=CORES["fundo"]); self.selected=set(); self.cf={}; self.total=0; self.cb=cb; self.rf=rf; self.build()
    def build(self):
        inner = tk.Frame(self, bg=CORES["fundo"]); inner.pack(expand=True)
        novato_cat=classes_por_categoria[0][1]; outras=classes_por_categoria[1:]; cc=1+len(outras); mr=max(len(cat[1]) for cat in outras); tr=max(mr,len(novato_cat))
        for row in range(tr):
            if row < len(novato_cat):
                hid,nome=novato_cat[row];f=tk.Frame(inner,bg=CORES["quadro_normal"],bd=2,relief="ridge",width=160,height=44,cursor="hand2")
                f.grid(row=row,column=0,sticky="nsew",padx=5,pady=5);f.pack_propagate(False)
                l=tk.Label(f,text=nome,font=("Tahoma",11,"bold"),fg=CORES["texto"],bg=CORES["quadro_normal"]);l.pack(expand=True,fill=tk.BOTH)
                f.bind("<Button-1>",lambda e,h=hid:self.toggle_selection(h));l.bind("<Button-1>",lambda e,h=hid:self.toggle_selection(h));self.cf[hid]=f
        for col,(_,cls) in enumerate(outras,start=1):
            for row in range(tr):
                if row<len(cls):
                    hid,nome=cls[row];f=tk.Frame(inner,bg=CORES["quadro_normal"],bd=2,relief="ridge",width=160,height=44,cursor="hand2")
                    f.grid(row=row,column=col,sticky="nsew",padx=5,pady=5);f.pack_propagate(False)
                    l=tk.Label(f,text=nome,font=("Tahoma",11),fg=CORES["texto"],bg=CORES["quadro_normal"]);l.pack(expand=True,fill=tk.BOTH)
                    f.bind("<Button-1>",lambda e,h=hid:self.toggle_selection(h));l.bind("<Button-1>",lambda e,h=hid:self.toggle_selection(h));self.cf[hid]=f
        for col in range(cc): inner.grid_columnconfigure(col,weight=1)
    def toggle_selection(self,hid):
        f,l=self.cf[hid],self.cf[hid].winfo_children()[0]
        if hid in self.selected:self.selected.remove(hid);f.config(bg=CORES["quadro_normal"]);l.config(bg=CORES["quadro_normal"],fg=CORES["texto"])
        else:self.selected.add(hid);f.config(bg=CORES["quadro_selec"]);l.config(bg=CORES["quadro_selec"],fg=CORES["quadro_texto"])
        self.update_total();self.rf()
    def update_total(self):
        t=0;[t:=t|hexstr_to_int(hid) for hid in self.selected];self.total=t;self.cb(t)
    def checar_hex(self,valor):
        if valor.lower().startswith("0x"):valor=valor[2:]
        if not is_hexadecimal(valor):messagebox.showwarning("Valor inválido","Digite um valor hexadecimal.");return
        decimal=int(valor,16)
        sel=[hid for hid in self.cf if(decimal&hexstr_to_int(hid))==hexstr_to_int(hid)and hexstr_to_int(hid)!=0]
        if not sel and decimal!=0:messagebox.showinfo("Nenhuma Flag","Nenhuma flag corresponde.");return
        self.selected.clear()
        for hid,f in self.cf.items():
            l=f.winfo_children()[0]
            if(decimal&hexstr_to_int(hid))==hexstr_to_int(hid)and hexstr_to_int(hid)!=0:
                self.selected.add(hid);f.config(bg=CORES["quadro_selec"]);l.config(bg=CORES["quadro_selec"],fg=CORES["quadro_texto"])
            else:f.config(bg=CORES["quadro_normal"]);l.config(bg=CORES["quadro_normal"],fg=CORES["texto"])
        self.total=decimal;self.cb(decimal)
    def marcar_tudo(self):self.selected=set(self.cf.keys());[f.config(bg=CORES["quadro_selec"])or f.winfo_children()[0].config(bg=CORES["quadro_selec"],fg=CORES["quadro_texto"]) for f in self.cf.values()];self.update_total();self.rf()
    def limpar_selecoes(self):self.selected.clear();self.total=0;[f.config(bg=CORES["quadro_normal"])or f.winfo_children()[0].config(bg=CORES["quadro_normal"],fg=CORES["texto"]) for f in self.cf.values()];self.update_total();self.rf()

class AbaEnchants(tk.Frame):
    def __init__(self, master, cb, rf): super().__init__(master, bg=CORES["fundo"]); self.selected=set(); self.cf={}; self.total=0; self.cb=cb; self.rf=rf; self.build()
    def build(self):
        inner = tk.Frame(self, bg=CORES["fundo"]);inner.pack(expand=True)
        lista = enchants; nc=4; nl=(len(lista)+nc-1)//nc
        for i,(n,v) in enumerate(lista):
            f=tk.Frame(inner,bg=CORES["quadro_normal"],bd=2,relief="ridge",width=160,height=44,cursor="hand2")
            col,row=i//nl,i%nl;f.grid(row=row,column=col,sticky="nsew",padx=5,pady=5);f.pack_propagate(False)
            l=tk.Label(f,text=n,font=("Tahoma",11),fg=CORES["texto"],bg=CORES["quadro_normal"]);l.pack(expand=True,fill=tk.BOTH)
            f.bind("<Button-1>",lambda e,v=v:self.toggle_selection(v));l.bind("<Button-1>",lambda e,v=v:self.toggle_selection(v));self.cf[v]=f
        for col in range(nc): inner.grid_columnconfigure(col,weight=1)
    def toggle_selection(self,v):
        f,l=self.cf[v],self.cf[v].winfo_children()[0]
        if v in self.selected:self.selected.remove(v);f.config(bg=CORES["quadro_normal"]);l.config(bg=CORES["quadro_normal"],fg=CORES["texto"])
        else:self.selected.add(v);f.config(bg=CORES["quadro_selec"]);l.config(bg=CORES["quadro_selec"],fg=CORES["quadro_texto"])
        self.update_total();self.rf()
    def update_total(self):
        self.total=sum(self.selected);self.cb(self.total)
    def checar_decimal(self,valor):
        if not valor.isdigit():messagebox.showwarning("Valor inválido","Digite um valor decimal válido.");return
        decimal=int(valor)
        sel=[v for v in self.cf if (decimal&v)==v and v!=0]
        if not sel and decimal!=0:messagebox.showinfo("Nenhuma Flag","Nenhuma flag corresponde.");return
        self.selected.clear()
        for v,f in self.cf.items():
            l=f.winfo_children()[0]
            if(decimal&v)==v and v!=0:self.selected.add(v);f.config(bg=CORES["quadro_selec"]);l.config(bg=CORES["quadro_selec"],fg=CORES["quadro_texto"])
            else:f.config(bg=CORES["quadro_normal"]);l.config(bg=CORES["quadro_normal"],fg=CORES["texto"])
        self.total=decimal;self.cb(decimal)
    def marcar_tudo(self):self.selected=set(self.cf.keys());[f.config(bg=CORES["quadro_selec"])or f.winfo_children()[0].config(bg=CORES["quadro_selec"],fg=CORES["quadro_texto"]) for f in self.cf.values()];self.update_total();self.rf()
    def limpar_selecoes(self):self.selected.clear();self.total=0;[f.config(bg=CORES["quadro_normal"])or f.winfo_children()[0].config(bg=CORES["quadro_normal"],fg=CORES["texto"]) for f in self.cf.values()];self.update_total();self.rf()

class CalculadoraRestricoesApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Calculadora de Flags - Mestick & Eternity")
        self.geometry("1280x720");self.minsize(1280,720)
        self.configure(bg=CORES["fundo"])
        self.current_tab = "itens"
        self.grid_rowconfigure(1, weight=1);self.grid_columnconfigure(0, weight=1)
        header = tk.Frame(self, bg=CORES["header"], height=HEADER_FOOTER_HEIGHT);header.grid(row=0,column=0,sticky="ew");header.grid_propagate(False)
        botao_estilo={
            "font":("Tahoma",11,"bold"),"bg":CORES["botao"],"fg":CORES["botao_txt"],
            "relief":"flat","width":12,"height":2,
            "activebackground":CORES["botao_ativo"],"activeforeground":CORES["botao_ativo_txt"],"bd":0,
        }
        self.btn_itens=tk.Button(header,text="Item",command=self.show_itens,cursor="hand2",**botao_estilo);self.btn_itens.pack(side=tk.LEFT,fill="y")
        self.btn_classes=tk.Button(header,text="Classe",command=self.show_classes,cursor="hand2",**botao_estilo);self.btn_classes.pack(side=tk.LEFT,fill="y")
        self.btn_enchants=tk.Button(header,text="Enchant",command=self.show_enchants,cursor="hand2",**botao_estilo);self.btn_enchants.pack(side=tk.LEFT,fill="y")
        self.container=tk.Frame(self,bg=CORES["fundo"]);self.container.grid(row=1,column=0,sticky="nsew")
        self.footer=tk.Frame(self,bg=CORES["header"],height=HEADER_FOOTER_HEIGHT);self.footer.grid(row=2,column=0,sticky="ew");self.footer.grid_propagate(False);self.create_footer()
        copyright_frame=tk.Frame(self,bg=CORES["copyright_bg"],height=32);copyright_frame.grid(row=3,column=0,sticky="ew");copyright_frame.grid_propagate(False)
        copyright_label=tk.Label(copyright_frame,text="© 2025 [DEV]Mestick & Equipe Eternity. Todos os direitos reservados.",
            font=("Tahoma",9),fg=CORES["texto"],bg=CORES["copyright_bg"]);copyright_label.pack(expand=True)
        self.aba_itens=AbaItens(self.container,self.update_footer,self.remove_input_focus)
        self.aba_classes=AbaClasses(self.container,self.update_footer,self.remove_input_focus)
        self.aba_enchants=AbaEnchants(self.container,self.update_footer,self.remove_input_focus)
        self.aba_itens.pack(fill="both",expand=True);self.aba_classes.pack_forget();self.aba_enchants.pack_forget()
        self.update_btn_states("itens")
    def remove_input_focus(self):self.focus()
    def create_footer(self):
        left_footer=tk.Frame(self.footer,bg=CORES["header"]);left_footer.pack(side=tk.LEFT,fill="both",expand=True,padx=20)
        self.resultado_label=tk.Label(left_footer,text="Resultado - Decimal:",font=("Tahoma",14,"bold"),
            fg=CORES["destaque"],bg=CORES["header"]);self.resultado_label.pack(side=tk.LEFT,padx=(0,10))
        self.total_valor_label=tk.Label(left_footer,text="0",font=("Tahoma",13,"bold"),
            fg=CORES["texto"],bg=CORES["header"]);self.total_valor_label.pack(side=tk.LEFT,padx=(0,20))
        right_footer=tk.Frame(self.footer,bg=CORES["header"]);right_footer.pack(side=tk.RIGHT,padx=20)
        self.input_valor=tk.Entry(right_footer,font=("Tahoma",11),justify="center",width=28);self.input_valor.pack(side=tk.LEFT,padx=(0,6),ipady=10)
        botao_estilo = {
            "font":("Tahoma",11,"bold"),"bg":CORES["botao"],"fg":CORES["botao_txt"],
            "relief":"flat","width":12,"height":2,
            "activebackground":CORES["botao_ativo"],"activeforeground":CORES["botao_ativo_txt"]
        }
        self.checar_btn=tk.Button(right_footer,text="Checar",command=self.checar_hex,**botao_estilo);self.checar_btn.pack(side=tk.LEFT,padx=3)
        tk.Button(right_footer,text="Copiar",command=self.copiar_hex,**botao_estilo).pack(side=tk.LEFT,padx=3)
        tk.Button(right_footer,text="Marcar tudo",command=self.marcar_tudo,**botao_estilo).pack(side=tk.LEFT,padx=3)
        tk.Button(right_footer,text="Desmarcar tudo",command=self.limpar_selecoes,**botao_estilo).pack(side=tk.LEFT,padx=3)
    def update_footer(self,total):
        if self.current_tab in ["itens","enchants"]:self.resultado_label.config(text="Resultado - Decimal:");self.total_valor_label.config(text=f"{total}")
        else:self.resultado_label.config(text="Resultado - Hexadecimal:");self.total_valor_label.config(text=f"{int_to_hexstr(total)}")
        self.input_valor.delete(0,tk.END)
        if total!=0:
            if self.current_tab in ["itens","enchants"]:self.input_valor.insert(0,f"{total}")
            else:self.input_valor.insert(0,int_to_hexstr(total))
    def checar_hex(self):
        valor=self.input_valor.get().strip()
        if self.current_tab=="itens":self.aba_itens.checar_decimal(valor)
        elif self.current_tab=="classes":self.aba_classes.checar_hex(valor)
        elif self.current_tab=="enchants":self.aba_enchants.checar_decimal(valor)
    def copiar_hex(self):
        if self.current_tab=="itens":valor=str(self.aba_itens.total)
        elif self.current_tab=="classes":valor=int_to_hexstr(self.aba_classes.total)
        elif self.current_tab=="enchants":valor=str(self.aba_enchants.total)
        self.clipboard_clear();self.clipboard_append(valor);messagebox.showinfo("Copiado",f"Valor {valor} copiado para a área de transferência!")
    def marcar_tudo(self):
        if self.current_tab=="itens":self.aba_itens.marcar_tudo()
        elif self.current_tab=="classes":self.aba_classes.marcar_tudo()
        elif self.current_tab=="enchants":self.aba_enchants.marcar_tudo()
    def limpar_selecoes(self):
        if self.current_tab=="itens":self.aba_itens.limpar_selecoes()
        elif self.current_tab=="classes":self.aba_classes.limpar_selecoes()
        elif self.current_tab=="enchants":self.aba_enchants.limpar_selecoes()
    def show_itens(self):
        self.aba_classes.pack_forget();self.aba_enchants.pack_forget()
        self.aba_itens.pack(fill="both",expand=True);self.update_btn_states("itens")
        self.current_tab="itens";self.update_footer(self.aba_itens.total)
    def show_classes(self):
        self.aba_itens.pack_forget();self.aba_enchants.pack_forget()
        self.aba_classes.pack(fill="both",expand=True);self.update_btn_states("classes")
        self.current_tab="classes";self.update_footer(self.aba_classes.total)
    def show_enchants(self):
        self.aba_itens.pack_forget();self.aba_classes.pack_forget()
        self.aba_enchants.pack(fill="both",expand=True);self.update_btn_states("enchants")
        self.current_tab="enchants";self.update_footer(self.aba_enchants.total)
    def update_btn_states(self,ativo):
        if ativo=="itens":self.btn_itens.config(bg=CORES["botao"],fg=CORES["botao_txt"]);self.btn_classes.config(bg=CORES["card"],fg=CORES["destaque"]);self.btn_enchants.config(bg=CORES["card"],fg=CORES["destaque"])
        elif ativo=="classes":self.btn_classes.config(bg=CORES["botao"],fg=CORES["botao_txt"]);self.btn_itens.config(bg=CORES["card"],fg=CORES["destaque"]);self.btn_enchants.config(bg=CORES["card"],fg=CORES["destaque"])
        elif ativo=="enchants":self.btn_enchants.config(bg=CORES["botao"],fg=CORES["botao_txt"]);self.btn_itens.config(bg=CORES["card"],fg=CORES["destaque"]);self.btn_classes.config(bg=CORES["card"],fg=CORES["destaque"])

if __name__ == "__main__":
    app=CalculadoraRestricoesApp();app.mainloop()
