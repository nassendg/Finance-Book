# |
# |  DANIYAL NASSEN - Copyright 2021 / All rights reserved.
# |  Finance Book - v.1.4.2
# |

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import sqlite3
import sys
import webbrowser
import requests


class Main(tk.Frame):
    def __init__(self, root):
        super().__init__(root)
        self.init_main()
        self.db = db
        self.view_records()

    def init_main(self):

        filemenu = tk.Menu(mainmenu, tearoff=0)
        filemenu.add_command(label="Добавить", command=self.open_dialog)
        filemenu.add_command(label="Изменить", command=self.open_update_dialog)
        filemenu.add_command(label="Удалить", command=self.delete_records)
        filemenu.add_separator()
        filemenu.add_command(label="Поиск", command=self.open_search_dialog)
        filemenu.add_command(label="Обновить", command=self.view_records)
        filemenu.add_separator()
        filemenu.add_command(label="Выйти", command=self.exit)
        
        allmenu = tk.Menu(mainmenu, tearoff=0)
        allmenu.add_command(label="Настройки", command=self.open_settings)

        helpmenu = tk.Menu(mainmenu, tearoff=0)
        helpmenu.add_command(label="Помощь", command=self.open_help_dialog)
        helpmenu.add_command(label="Донат", command=self.open_donate_dialog)
        helpmenu.add_separator()
        helpmenu.add_command(label="О программе", command=self.open_about_dialog)
        helpmenu.add_command(label="О создателе", command=self.open_author_dialog)
         
        mainmenu.add_cascade(label="Файл", menu=filemenu)
        mainmenu.add_cascade(label="Справка", menu=helpmenu)
        mainmenu.add_cascade(label="Общие", menu=allmenu)


        toolbar = tk.Frame(bg='#DDDDDD', bd=2)
        toolbar.pack(side=tk.TOP, fill=tk.X)


        self.add_img = tk.PhotoImage(file='images/add.png')
        btn_open_dialog = tk.Button(toolbar, text='Добавить', command=self.open_dialog, bg='#DDDDDD', bd=0,
                                    compound=tk.TOP, image=self.add_img)
        btn_open_dialog.pack(side=tk.LEFT)

        self.delete_img = tk.PhotoImage(file='images/delete.png')
        btn_delete = tk.Button(toolbar, text='Удалить', bg='#DDDDDD', bd=0, image=self.delete_img,
                               compound=tk.TOP, command=self.delete_records)
        btn_delete.pack(side=tk.LEFT)

        self.update_img = tk.PhotoImage(file='images/update.png')
        btn_edit_dialog = tk.Button(toolbar, text='Изменить', bg='#DDDDDD', bd=0, image=self.update_img,
                                    compound=tk.TOP, command=self.open_update_dialog)
        btn_edit_dialog.pack(side=tk.LEFT)

        self.refresh_img = tk.PhotoImage(file='images/refresh.png')
        btn_refresh = tk.Button(toolbar, text='Обновить', bg='#DDDDDD', bd=0, image=self.refresh_img,
                                compound=tk.TOP, command=self.view_records)
        btn_refresh.pack(side=tk.RIGHT)

        self.search_img = tk.PhotoImage(file='images/search.png')
        btn_search = tk.Button(toolbar, text='Поиск', bg='#DDDDDD', bd=0, image=self.search_img, compound=tk.TOP, command=self.open_search_dialog)
        btn_search.pack(side=tk.RIGHT)

        
        self.tree = ttk.Treeview(self, columns=('ID', 'description', 'category', 'costs', 'total'), height=15, show='headings')

        self.tree.column('ID', width=30, anchor=tk.CENTER)
        self.tree.column('description', width=200, anchor=tk.CENTER)
        self.tree.column('category', width=165, anchor=tk.CENTER)
        self.tree.column('costs', width=150, anchor=tk.CENTER)
        self.tree.column('total', width=100, anchor=tk.CENTER)

        self.tree.heading('ID', text='ID', command=self.sort_records_by_id)
        self.tree.heading('description', text='Название', command=self.sort_records_by_description)
        self.tree.heading('category', text='Категория', command=self.sort_records_by_category)
        self.tree.heading('costs', text='Доход/Расход', command=self.sort_records_by_costs)
        self.tree.heading('total', text='Сумма', command=self.sort_records_by_total)

        self.tree.pack(side=tk.LEFT)

        self.scroll = tk.Scrollbar(self, orient = 'vertical', command = self.tree.yview)
        self.scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand = self.scroll.set)
   
    #Добавление данных в базу данных        
    def records(self, description, category, costs, total):
        self.db.insert_data(description, category, costs, total)
        self.view_records()

    #Редактирование\обновление данных записи
    def update_record(self, description, category, costs, total):
        self.db.c.execute('''UPDATE finance SET description=?, category=?, costs=?, total=? WHERE ID=?''',
                          (description, category, costs, total, self.tree.set(self.tree.selection()[0], '#1')))
        self.db.conn.commit()
        self.view_records()

    #Отображение содержимого базы данных
    def view_records(self):
        self.db.c.execute('''SELECT * FROM finance''')
        [self.tree.delete(i) for i in self.tree.get_children()]
        [self.tree.insert('', 'end', values=row) for row in self.db.c.fetchall()]

    #Удаление записей (с возможностью массового удаления)
    def delete_records(self):
        for selection_item in self.tree.selection():
            self.db.c.execute('''DELETE FROM finance WHERE id=?''', (self.tree.set(selection_item, '#1'),))
        self.db.conn.commit()
        self.view_records()

    #Поиск по наименованию (полю description)
    def search_records(self, description):
        description = ('%' + description + '%',)
        self.db.c.execute('''SELECT * FROM finance WHERE description LIKE ?''', description)
        [self.tree.delete(i) for i in self.tree.get_children()]
        [self.tree.insert('', 'end', values=row) for row in self.db.c.fetchall()]

    #Сортировка по полю ID
    def sort_records_by_id(self):
        self.db.c.execute('SELECT * FROM finance ORDER BY ID')
        [self.tree.delete(i) for i in self.tree.get_children()]
        [self.tree.insert('', 'end', values=row) for row in self.db.c.fetchall()]

    #Сортировка по полю decription
    def sort_records_by_description(self):
        self.db.c.execute('SELECT * FROM finance ORDER BY description')
        [self.tree.delete(i) for i in self.tree.get_children()]
        [self.tree.insert('', 'end', values=row) for row in self.db.c.fetchall()]

    #Сортировка по полю category
    def sort_records_by_category(self):
        self.db.c.execute('SELECT * FROM finance ORDER BY category')
        [self.tree.delete(i) for i in self.tree.get_children()]
        [self.tree.insert('', 'end', values=row) for row in self.db.c.fetchall()]

    #Сортировка по полю costs
    def sort_records_by_costs(self):
        self.db.c.execute('SELECT * FROM finance ORDER BY costs')
        [self.tree.delete(i) for i in self.tree.get_children()]
        [self.tree.insert('', 'end', values=row) for row in self.db.c.fetchall()]

    #Сортировка по полю total
    def sort_records_by_total(self):
        self.db.c.execute('SELECT * FROM finance ORDER BY total')
        [self.tree.delete(i) for i in self.tree.get_children()]
        [self.tree.insert('', 'end', values=row) for row in self.db.c.fetchall()]

    #Вызов окна добавления данных
    def open_dialog(self):
        Child()

    #Вызов окна редактирования данных
    def open_update_dialog(self):
        Update()

    #Вызов окна поиска по наименованию (полю description)
    def open_search_dialog(self):
        Search()

    def open_about_dialog(self):
        About()

    def open_author_dialog(self):
        Author()

    def open_help_dialog(self):
        Help()

    def open_donate_dialog(self):
        Donate()

    def open_settings(self):
        messagebox.showerror(title="Ошибка", message="Недостаточно полномочий для данного действия.")

    def exit(self):
        exit_dialogue = messagebox.askyesno(title="Подтверждение", message="Подтвердите действие. Выйти?")
        if exit_dialogue == True:
            sys.exit()

class Child(tk.Toplevel):
    def __init__(self):
        super().__init__(root)
        self.init_child()
        self.view = app

    def init_child(self):
        self.title('Добавить')
        self.geometry('355x180+400+300')
        self.iconbitmap("icons/icon.ico")
        self.resizable(False, False)

        label_description = tk.Label(self, text='Название:')
        label_description.place(x=15, y=15)
        label_category = tk.Label(self, text='Категория:')
        label_category.place(x=15, y=45)
        label_select = tk.Label(self, text='Доход/Расход:')
        label_select.place(x=15, y=75)
        label_sum = tk.Label(self, text='Сумма:')
        label_sum.place(x=15, y=105)

        self.entry_description = ttk.Entry(self)
        self.entry_description.place(x=135, y=15)

        self.combobox_category = ttk.Combobox(self, values=[u'Бизнес', u'Развлечения', u'Спорт', u'Здоровье', u'Образование', u'Продукты', u'Другое'])
        self.combobox_category.current(0)
        self.combobox_category.place(x=135, y=45)

        self.entry_money = ttk.Entry(self)
        self.entry_money.place(x=135, y=105)

        self.combobox = ttk.Combobox(self, values=[u'Доход', u'Расход'])
        self.combobox.current(0)
        self.combobox.place(x=135, y=75)

        btn_cancel = ttk.Button(self, text='Закрыть', command=self.destroy)
        btn_cancel.place(x=275, y=150)

        self.btn_ok = ttk.Button(self, text='Добавить')
        self.btn_ok.place(x=195, y=150)
        self.btn_ok.bind('<Button-1>', lambda event: self.view.records(self.entry_description.get(), self.combobox_category.get(), self.combobox.get(), self.entry_money.get()))

        self.grab_set()
        self.focus_set()
 

class Update(Child):
    def __init__(self):
        super().__init__()
        self.init_edit()
        self.view = app
        self.db = db
        #self.default_data() # Появляется баг где при изменеии элемента сумма меняется н надпись "Расход"

    def init_edit(self):
        self.title('Изменить')
        btn_edit = ttk.Button(self, text='Изменить')
        btn_edit.place(x=195, y=150)
        btn_edit.bind('<Button-1>', lambda event: self.view.update_record(self.entry_description.get(), self.combobox_category.get(), self.combobox.get(), self.entry_money.get()))

        self.btn_ok.destroy()

    def default_data(self):
        self.db.c.execute('''SELECT * FROM finance WHERE id=?''', (self.view.tree.set(self.view.tree.selection()[0], '#1'),))
        row = self.db.c.fetchone()
        self.entry_description.insert(0, row[1])
        if row[2] != 'Доход':
            self.combobox.current(1)
        self.entry_money.insert(0, row[3])


class Search(tk.Toplevel):
    def __init__(self):
        super().__init__()
        self.init_search()
        self.view = app

    def init_search(self):
        self.title('Поиск')
        self.geometry('300x100+400+300')
        self.iconbitmap("icons/icon.ico")
        self.resizable(False, False)

        label_search = tk.Label(self, text='Искать')
        label_search.place(x=50, y=20)

        self.entry_search = ttk.Entry(self)
        self.entry_search.place(x=105, y=20, width=150)

        btn_cancel = ttk.Button(self, text='Закрыть', command=self.destroy)
        btn_cancel.place(x=185, y=50)

        btn_search = ttk.Button(self, text='Найти')
        btn_search.place(x=105, y=50)
        btn_search.bind('<Button-1>', lambda event: self.view.search_records(self.entry_search.get()))
        btn_search.bind('<Button-1>', lambda event: self.destroy(), add='+')

        self.grab_set()
        self.focus_set()

class About(tk.Toplevel):
    def __init__(self):
        super().__init__()
        self.init_search()
        self.view = app

    def init_search(self):
        self.title('О программе')
        self.geometry('350x150+400+300')
        self.iconbitmap("icons/icon.ico")
        self.resizable(False, False)

        label_about = tk.Label(self, text='Finance Book', font="Calibri 20")
        label_about2 = tk.Label(self, text='v.1.4.2 - RELEASE\nBy NASSEN.DG', font="Calibri 12", justify="left")

        self.logo_about = tk.PhotoImage(file='icons/icon.png')
        logo_about_show = tk.Label(self, image=self.logo_about)
        logo_about_show.place(x=290, y=5)

        label_about3 = tk.Label(self, text='Copyright 2021')
        label_about.place(x=10, y=5)
        label_about2.place(x=10, y=40)
        label_about3.place(x=0, y=130)

        btn_cancel = ttk.Button(self, text='Закрыть', command=self.destroy)
        btn_cancel.place(x=270, y=120)

        self.grab_set()
        self.focus_set()

class Author(tk.Toplevel):
    def __init__(self):
        super().__init__()
        self.init_search()
        self.view = app

    def init_search(self):
        self.title('О создателе')
        self.geometry('350x150+400+300')
        self.iconbitmap("icons/icon.ico")
        self.resizable(False, False)

        label_about = tk.Label(self, text='Daniyal Nassen G.', font="Calibri 20")
        label_about2 = tk.Label(self, text='Создатель:', font="Calibri 12", justify="left")

        self.logo_author = tk.PhotoImage(file='images/author-photo.png')
        logo_author_show = tk.Label(self, image=self.logo_author)
        logo_author_show.place(x=240, y=5)

        label_about3 = tk.Label(self, text='Оснаватель, Программист Проекта')
        label_about.place(x=10, y=20)
        label_about2.place(x=10, y=5)
        label_about3.place(x=0, y=130)

        btn_cancel = ttk.Button(self, text='Закрыть', command=self.destroy)
        btn_cancel.place(x=270, y=120)

        self.grab_set()
        self.focus_set()

class Help(tk.Toplevel):
    def __init__(self):
        super().__init__()
        self.init_search()
        self.view = app

    def init_search(self):
        self.title('Помощь')
        self.geometry('450x150')
        self.iconbitmap("icons/icon.ico")
        self.resizable(False, False)

        label_help = tk.Label(self, text='Возникли проблемы?', font="Calibri 16")
        label_help2 = tk.Label(self, text='Напишите письмо на почту: nassen.d230@gmail.com\nЯ попробую помочь вам!', font="Calibri 13", justify="left")
        
        label_help.place(x=15, y=15)
        label_help2.place(x=15, y=45)

        btn_cancel = ttk.Button(self, text='Закрыть', command=self.destroy)
        btn_cancel.place(x=370, y=120)

        self.grab_set()
        self.focus_set()

class Donate(tk.Toplevel):
    def __init__(self):
        super().__init__()
        self.init_search()
        self.view = app

    def init_search(self):
        self.title('Пожертвование')
        self.geometry('400x150+400+300')
        self.iconbitmap("icons/icon.ico")
        self.resizable(False, False)

        label_help = tk.Label(self, text='В данный момент, это \nосуществить невозможно', font="Calibri 16", justify="left")
        label_help.place(x=15, y=15)

        btn_cancel = ttk.Button(self, text='Закрыть', command=self.destroy)
        btn_cancel.place(x=320, y=120)

        self.grab_set()
        self.focus_set()


class DB:
    def __init__(self):
        self.conn = sqlite3.connect('finance.db')
        self.c = self.conn.cursor()
        self.c.execute(
            '''CREATE TABLE IF NOT EXISTS finance (id integer primary key, description text, category text, costs text, total real)''')
        self.conn.commit()

    def insert_data(self, description, category, costs, total):
        self.c.execute('''INSERT INTO finance(description, category, costs, total) VALUES (?, ?, ?, ?)''',
                       (description, category, costs, total))
        self.conn.commit()


if __name__ == "__main__":
    quit()
else:
    root = tk.Tk()
    db = DB()
    mainmenu = tk.Menu(root)
    app = Main(root)
    app.pack()
    root.config(menu=mainmenu)
    root.title("Finance Book 1.4.2")
    root.geometry("665x450+300+200")
    root.iconbitmap("icons/icon.ico")
    root.resizable(False, False)

    # ОКНО С ЗАПРОСОМ ОБ УСТАНОВКЕ НОВОЙ ВЕРСИИ
    version_update_source = open('available_version.txt', 'r')
    version_update_content = version_update_source.read()
    version_update_source.close()

    if version_update_content == "True":
        accept_version_update = messagebox.askyesno(title="Доступно Обновление", message="Доступно новое обновление для Finance Book. Установить?")
        if accept_version_update == True:
            import main

    root.mainloop()
