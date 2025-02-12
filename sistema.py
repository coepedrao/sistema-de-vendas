import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk, filedialog
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

conn = sqlite3.connect("bar_vendas.db")
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS vendas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    produto TEXT NOT NULL,
    valor REAL NOT NULL,
    data TEXT NOT NULL
)
''')
conn.commit()

def formatar_data(event):
    
    texto = entrada_data.get().replace("/", "")  
    if len(texto) > 8:
        texto = texto[:8]  
    nova_data = ""
    for i, c in enumerate(texto):
        if i in [2, 4]:  
            nova_data += "/"
        nova_data += c
    entrada_data.delete(0, tk.END)
    entrada_data.insert(0, nova_data)

def formatar_data_busca(event):
    
    texto = entrada_data_busca.get().replace("/", "")
    if len(texto) > 8:
        texto = texto[:8]
    nova_data = ""
    for i, c in enumerate(texto):
        if i in [2, 4]:
            nova_data += "/"
        nova_data += c
    entrada_data_busca.delete(0, tk.END)
    entrada_data_busca.insert(0, nova_data)

def registrar_venda():
    try:
        produto = entrada_produto.get().strip()
        valor_str = entrada_valor.get().strip()
        data_br = entrada_data.get().strip()

        if not produto or not valor_str or not data_br:
            messagebox.showerror("Erro", "Preencha todos os campos!")
            return
        
        
        valor_str = valor_str.replace(".", "").replace(",", ".")
        valor = float(valor_str)
        
        
        data_sql = "/".join(reversed(data_br.split("/")))

        cursor.execute("INSERT INTO vendas (produto, valor, data) VALUES (?, ?, ?)", 
                       (produto, valor, data_sql))
        conn.commit()
        messagebox.showinfo("Sucesso", f"Venda registrada: {produto} - R$ {valor:.2f} em {data_br}")
        entrada_produto.delete(0, tk.END)
        entrada_valor.delete(0, tk.END)
        entrada_data.delete(0, tk.END)
        atualizar_tabela()
    except ValueError:
        messagebox.showerror("Erro", "Digite um valor numérico válido!")
    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um erro inesperado: {str(e)}")

def atualizar_tabela():
    for row in tabela.get_children():
        tabela.delete(row)
    try:
        cursor.execute("SELECT * FROM vendas ORDER BY id DESC")
        vendas = cursor.fetchall()
        for venda in vendas:
            data_formatada = "/".join(reversed(venda[3].split("/"))) 
            valor_formatado = f"{venda[2]:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            tabela.insert("", "end", values=(venda[0], venda[1], f"R$ {valor_formatado}", data_formatada))
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao carregar vendas: {str(e)}")

def buscar_por_data():
    try:
        data_busca = entrada_data_busca.get().strip()
        data_sql = "/".join(reversed(data_busca.split("/"))) 
        for row in tabela.get_children():
            tabela.delete(row)
        cursor.execute("SELECT * FROM vendas WHERE data = ? ORDER BY id DESC", (data_sql,))
        vendas = cursor.fetchall()
        for venda in vendas:
            data_formatada = "/".join(reversed(venda[3].split("/")))  
            valor_formatado = f"{venda[2]:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            tabela.insert("", "end", values=(venda[0], venda[1], f"R$ {valor_formatado}", data_formatada))
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao buscar vendas: {str(e)}")

def exportar_pdf():
    try:
        arquivo = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("Arquivo PDF", "*.pdf")])
        if not arquivo:
            return
        
        c = canvas.Canvas(arquivo, pagesize=letter)
        c.setFont("Helvetica", 12)
        
        c.drawString(200, 750, "Vendas Registradas")
        c.line(100, 745, 500, 745)
        
        c.drawString(100, 720, "ID")
        c.drawString(150, 720, "Produto")
        c.drawString(300, 720, "Valor")
        c.drawString(400, 720, "Data")
        
        cursor.execute("SELECT * FROM vendas ORDER BY id DESC")
        vendas = cursor.fetchall()
        
        y_position = 700
        for venda in vendas:
            data_formatada = "/".join(reversed(venda[3].split("/")))
            valor_formatado = f"{venda[2]:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            c.drawString(100, y_position, str(venda[0]))
            c.drawString(150, y_position, venda[1])
            c.drawString(300, y_position, f"R$ {valor_formatado}")
            c.drawString(400, y_position, data_formatada)
            y_position -= 20
            if y_position < 50:
                c.showPage()
                c.setFont("Helvetica", 12)
                y_position = 750
        
        c.save()
        messagebox.showinfo("Sucesso", "Dados exportados para PDF com sucesso!")
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao exportar PDF: {str(e)}")

janela = tk.Tk()
janela.title("Sistema de Vendas - Bar")
janela.geometry("600x500")

tk.Label(janela, text="Produto:").pack(pady=5)
entrada_produto = ttk.Entry(janela, width=40)
entrada_produto.pack()

tk.Label(janela, text="Valor:").pack(pady=5)
entrada_valor = ttk.Entry(janela, width=20)
entrada_valor.pack()

tk.Label(janela, text="Selecione a Data da Venda:").pack(pady=5)
entrada_data = ttk.Entry(janela, width=20)
entrada_data.pack()
entrada_data.bind("<KeyRelease>", formatar_data)

btn_registrar = ttk.Button(janela, text="Registrar Venda", command=registrar_venda)
btn_registrar.pack(pady=10)

tk.Label(janela, text="Buscar Vendas por Data:").pack(pady=5)
entrada_data_busca = ttk.Entry(janela, width=20)
entrada_data_busca.pack()
entrada_data_busca.bind("<KeyRelease>", formatar_data_busca)

btn_buscar = ttk.Button(janela, text="Buscar Vendas", command=buscar_por_data)
btn_buscar.pack(pady=10)

btn_exportar = ttk.Button(janela, text="Exportar PDF", command=exportar_pdf)
btn_exportar.pack(pady=10)

colunas = ("ID", "Produto", "Valor", "Data")
tabela = ttk.Treeview(janela, columns=colunas, show="headings")
tabela.heading("ID", text="ID")
tabela.heading("Produto", text="Produto")
tabela.heading("Valor", text="Valor")
tabela.heading("Data", text="Data")

tabela.pack(pady=10, fill=tk.BOTH, expand=True)

atualizar_tabela()
janela.mainloop()

conn.close()
