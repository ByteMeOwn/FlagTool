import configparser, tkinter as tk
from tkinter import messagebox

def carregar_cores():
    ini = configparser.ConfigParser()
    ini.read("color.ini", encoding="utf-8")
    c = dict(ini["colors"])
    return {
        "fundo": c["fundo"],"header": c["header"],"card": c["card"],"destaque": c["destaque"],"texto": c["texto"],"botao": c["botao"],"botao_txt": c["botao_txt"],"botao_ativo": c["botao_ativo"],"botao_ativo_txt": c["botao_ativo_txt"],"quadro_selec": c["quadro_selec"],"quadro_normal": c["quadro_normal"],"quadro_texto": c["quadro_texto"],"quadro_null": c.get("quadro_null", "#1a1a1a")
    }

def carregar_fonte():
    ini = configparser.ConfigParser()
    try:
        ini.read("font.ini", encoding="utf-8")
        nome = ini.get("font", "nome", fallback="Arial")
        tamanho = ini.getint("font", "tamanho", fallback=9)
        return (nome, tamanho)
    except:
        return ("Arial", 9)

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
FONTE = carregar_fonte()
restricoes, enchants, classes_por_categoria = carregar_flags()
HEADER_FOOTER_HEIGHT = 40

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
            f=tk.Frame(inner,bg=CORES["quadro_normal"],bd=1,relief="solid",width=140,height=36,cursor="hand2")
            col,row=i//nl,i%nl; f.grid(row=row,column=col,sticky="nsew",padx=3,pady=3); f.pack_propagate(False)
            l=tk.Label(f,text=n,font=FONTE,fg=CORES["texto"],bg=CORES["quadro_normal"]); l.pack(expand=True,fill=tk.BOTH)
            f.bind("<Button-1>",lambda e,v=v:self.toggle_selection(v)); l.bind("<Button-1>",lambda e,v=v:self.toggle_selection(v)); self.cf[v]=f
        for col in range(nc): inner.grid_columnconfigure(col,weight=1,uniform="cols")
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
        novato_cat=classes_por_categoria[0][1]; outras=classes_por_categoria[1:]; cc=1+len(outras); mr=max(len(cat[1]) for cat in outras); tr=mr
        for row in range(tr):
            if row < len(novato_cat):
                hid,nome=novato_cat[row];f=tk.Frame(inner,bg=CORES["quadro_normal"],bd=1,relief="solid",width=140,height=36,cursor="hand2")
                f.grid(row=row,column=0,sticky="nsew",padx=3,pady=3);f.pack_propagate(False)
                l=tk.Label(f,text=nome,font=(FONTE[0],FONTE[1],"bold"),fg=CORES["texto"],bg=CORES["quadro_normal"]);l.pack(expand=True,fill=tk.BOTH)
                f.bind("<Button-1>",lambda e,h=hid:self.toggle_selection(h));l.bind("<Button-1>",lambda e,h=hid:self.toggle_selection(h));self.cf[hid]=f
            else:
                f=tk.Frame(inner,bg=CORES["quadro_null"],bd=1,relief="flat",width=140,height=36)
                f.grid(row=row,column=0,sticky="nsew",padx=3,pady=3);f.pack_propagate(False)
        for col,(_,cls) in enumerate(outras,start=1):
            for row in range(tr):
                if row<len(cls):
                    hid,nome=cls[row];f=tk.Frame(inner,bg=CORES["quadro_normal"],bd=1,relief="solid",width=140,height=36,cursor="hand2")
                    f.grid(row=row,column=col,sticky="nsew",padx=3,pady=3);f.pack_propagate(False)
                    l=tk.Label(f,text=nome,font=FONTE,fg=CORES["texto"],bg=CORES["quadro_normal"]);l.pack(expand=True,fill=tk.BOTH)
                    f.bind("<Button-1>",lambda e,h=hid:self.toggle_selection(h));l.bind("<Button-1>",lambda e,h=hid:self.toggle_selection(h));self.cf[hid]=f
        for col in range(cc): inner.grid_columnconfigure(col,weight=1,uniform="cols")
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
            f=tk.Frame(inner,bg=CORES["quadro_normal"],bd=1,relief="solid",width=140,height=36,cursor="hand2")
            col,row=i//nl,i%nl;f.grid(row=row,column=col,sticky="nsew",padx=3,pady=3);f.pack_propagate(False)
            l=tk.Label(f,text=n,font=FONTE,fg=CORES["texto"],bg=CORES["quadro_normal"]);l.pack(expand=True,fill=tk.BOTH)
            f.bind("<Button-1>",lambda e,v=v:self.toggle_selection(v));l.bind("<Button-1>",lambda e,v=v:self.toggle_selection(v));self.cf[v]=f
        for col in range(nc): inner.grid_columnconfigure(col,weight=1,uniform="cols")
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
        self.geometry("680x490");self.resizable(False,False)
        self.configure(bg=CORES["fundo"])
        self.current_tab = "itens"
        self.grid_rowconfigure(1, weight=1);self.grid_columnconfigure(0, weight=1)
        header = tk.Frame(self, bg=CORES["header"], height=HEADER_FOOTER_HEIGHT);header.grid(row=0,column=0,sticky="ew");header.grid_propagate(False)
        botao_estilo={"font":(FONTE[0],10,"bold"),"bg":CORES["botao"],"fg":CORES["botao_txt"],"relief":"flat","width":10,"height":1,"activebackground":CORES["botao_ativo"],"activeforeground":CORES["botao_ativo_txt"],"bd":0}
        self.btn_itens=tk.Button(header,text="Item",command=self.show_itens,cursor="hand2",**botao_estilo);self.btn_itens.pack(side=tk.LEFT,fill="y",padx=2)
        self.btn_classes=tk.Button(header,text="Classe",command=self.show_classes,cursor="hand2",**botao_estilo);self.btn_classes.pack(side=tk.LEFT,fill="y",padx=2)
        self.btn_enchants=tk.Button(header,text="Enchant",command=self.show_enchants,cursor="hand2",**botao_estilo);self.btn_enchants.pack(side=tk.LEFT,fill="y",padx=2)
        self.container=tk.Frame(self,bg=CORES["fundo"]);self.container.grid(row=1,column=0,sticky="nsew")
        self.footer=tk.Frame(self,bg=CORES["header"],height=HEADER_FOOTER_HEIGHT);self.footer.grid(row=2,column=0,sticky="ew");self.footer.grid_propagate(False);self.create_footer()
        self.aba_itens=AbaItens(self.container,self.update_footer,self.remove_input_focus)
        self.aba_classes=AbaClasses(self.container,self.update_footer,self.remove_input_focus)
        self.aba_enchants=AbaEnchants(self.container,self.update_footer,self.remove_input_focus)
        self.aba_itens.pack(fill="both",expand=True);self.aba_classes.pack_forget();self.aba_enchants.pack_forget()
        self.update_btn_states("itens")
    def remove_input_focus(self):self.focus()
    def create_footer(self):
        top_footer=tk.Frame(self.footer,bg=CORES["header"],height=20);top_footer.pack(side=tk.TOP,fill="x")
        self.resultado_label=tk.Label(top_footer,text="Resultado - Decimal:",font=(FONTE[0],10,"bold"),fg=CORES["destaque"],bg=CORES["header"]);self.resultado_label.pack(side=tk.LEFT,padx=8)
        self.total_valor_label=tk.Label(top_footer,text="0",font=(FONTE[0],10,"bold"),fg=CORES["texto"],bg=CORES["header"]);self.total_valor_label.pack(side=tk.LEFT)
        bottom_footer=tk.Frame(self.footer,bg=CORES["header"]);bottom_footer.pack(side=tk.BOTTOM,fill="x",pady=2)
        self.input_valor=tk.Entry(bottom_footer,font=(FONTE[0],9),justify="center",width=15);self.input_valor.pack(side=tk.LEFT,padx=4,ipady=4)
        botao_estilo={"font":(FONTE[0],9,"bold"),"bg":CORES["botao"],"fg":CORES["botao_txt"],"relief":"flat","width":10,"activebackground":CORES["botao_ativo"],"activeforeground":CORES["botao_ativo_txt"]}
        self.checar_btn=tk.Button(bottom_footer,text="Checar",command=self.checar_hex,**botao_estilo);self.checar_btn.pack(side=tk.LEFT,padx=2)
        tk.Button(bottom_footer,text="Copiar",command=self.copiar_hex,**botao_estilo).pack(side=tk.LEFT,padx=2)
        tk.Button(bottom_footer,text="Marcar",command=self.marcar_tudo,**botao_estilo).pack(side=tk.LEFT,padx=2)
        tk.Button(bottom_footer,text="Limpar",command=self.limpar_selecoes,**botao_estilo).pack(side=tk.LEFT,padx=2)
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
        self.clipboard_clear();self.clipboard_append(valor);messagebox.showinfo("Copiado",f"Valor {valor} copiado!")
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
