from tkinter import *
from tkinter import ttk
import webbrowser
from matplotlib.pyplot import text

from improved_query import *

class Query_UI:
    def __init__(self) -> None:
        self.search_str = ""
        self.query = Improved_query()
        self.res = []
    

    def generate_ui(self):
        self.root = Tk()
        self.root.title("Tang's Customized Search Engine")
        self.root.geometry("2000x1000")
        # self.root.geometry("{}x{}".format(str(self.root.winfo_screenwidth()-100), 
		# 						str(self.root.winfo_screenheight()-100)))
        self.mid_wid = 200
        self.mid_hi = 200

        def update(data):
            self.res_list.delete(0, END)
            count = 1
            for item in data:
                self.res_list.insert(END, "#"+str(count)+" "+item)
                count += 1

        def update_score(data):
            self.res_list.delete(0, END)
            count = 1
            for item in data:
                self.res_list.insert(END, "#"+str(count)+" "+item[0]+", cosine scores: "+str(item[1]))
                # self.res_list.insert(END, "#"+str(count)+" "+item[0]+", cosine scores: "+str(item[1][1]))
                count += 1

        self.label =  Label(self.root, text="Customized Search Engine", font=("Helvetica", 15))
        # self.label.place(x=self.mid_wid, y=self.mid_hi, anchor=CENTER)
        self.label.pack(pady=10)

        self.entry = Entry(self.root, font=("Helvetica", 20), width=20)
        # self.entry.insert(0, "Type your search here")
        # self.entry.place(x=self.mid_wid, y=self.mid_hi+120, anchor=CENTER)
        self.entry.pack()

        def searchClick():
            self.search_str = self.entry.get()
            print(self.search_str)
            self.res, scores = self.query.start_query(self.search_str)
            if self.var.get() == 0:
                update(self.res)
            else:
                update_score(scores)

        def open_browser(event):
            weblink = self.res[self.res_list.index(ACTIVE)]
            chrome_path = 'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s'
            webbrowser.get(chrome_path).open_new(weblink)

        def show():
            pass


        search_button = Button(self.root, text="search", command=searchClick)
        search_button.pack()

        self.var = IntVar()
        check = Checkbutton(self.root, text="Show Scores", variable=self.var, command=show)
        check.pack()

        frame = Frame(self.root)
        h_scroll = Scrollbar(frame, orient=HORIZONTAL)

        self.label =  Label(self.root, text="Search Result:", font=("Helvetica", 20))
        # self.label.place(x=self.mid_wid, y=self.mid_hi, anchor=CENTER)
        self.label.pack()

        self.res_list = Listbox(frame, width=150, xscrollcommand=h_scroll, font=("Helvetica", 15), fg="blue")
        self.res_list.bind("<Double-Button-1>" , open_browser)

        h_scroll.config(command=self.res_list.xview)
        h_scroll.pack(side=BOTTOM, fill=X)
        frame.pack()
        self.res_list.pack(pady=20)



        self.root.mainloop()


if __name__ == "__main__":
    gui = Query_UI()
    gui.generate_ui()