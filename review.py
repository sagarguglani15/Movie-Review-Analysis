import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import *
from collections import defaultdict
from tkinter import messagebox
from textblob import TextBlob
from googlesearch import search
from nltk.tokenize import sent_tokenize
import pandas as pd
from bs4 import BeautifulSoup
import urllib.request

root=Tk()
root.geometry('1400x700')
root.title('Movie Review Analysis')

reviews=defaultdict(list)
class Review(Canvas):
    def __init__(self, **kw):
        super().__init__(width=1400, height=700, highlightthickness=0, background='black', **kw)

        self.heading='Welcome to Movie Review System'
        self.create_text(700, 50, text='', fill='cyan', font='Abc 20 bold italic', tag='head')
        self.head_move()
        self.get_movie()

    def head_move(self):
        s=self.itemcget(self.find_withtag('head'),'text')
        ns=len(s)
        c=self.itemcget(self.find_withtag('head'),'fill')

        if s=='Welcome to Movie Review System':
            s=''
        else:
            s=self.heading[:ns+2]

        if c=='cyan':
            c='light green'
        else:
            c='cyan'
        self.itemconfigure(self.find_withtag('head'), fill=c)
        self.itemconfigure(self.find_withtag('head'), text=s)

        self.after(400,self.head_move)

    def get_movie(self):
        self.create_text(300, 100, text='Please Enter Movie Name :', fill='white', font='abc 15 underline')
        self.e1 = Entry(root, bd=1, fg='midnight blue', bg='white', font='abc 15 bold')
        self.e1.focus_set()
        self.create_window(600, 100, window=self.e1, tag='movie_entry')

        self.bind_all('<Key>', self.on_enter_press)

    def on_enter_press(self, e):
        entered = e.keysym
        if (entered == 'Return' or entered == 'KP_Enter'):
            if (self.e1.get() == '' or self.e1.get() == ' '):
                messagebox.showerror('Error','Please Enter a valid movie name !!', default='ok')
                return
            else:
                self.delete(self.find_withtag('btrpr'), self.find_withtag('bttpr'), self.find_withtag('btrnr'), self.find_withtag('bttnr'))
                self.start_review(self.e1.get())

    @staticmethod
    def showp(self):
        pr = Tk()
        pr.title('Positive Reviews')
        frame = Frame(pr)
        scroll = Scrollbar(frame)
        scroll.pack(side=RIGHT, fill=Y)

        scroll2=Scrollbar(frame, orient=HORIZONTAL)
        scroll2.pack(side=BOTTOM, fill=X)

        listbox = Listbox(frame, yscrollcommand=scroll.set, xscrollcommand=scroll2.set)
        j = 1
        l=reviews['Positive']
        for i in l:
            try:
                listbox.insert(END, str(j) + '. ' + str(i))
                listbox.insert(END, ' ')
                j += 1
            except:
                pass
        listbox.pack(padx=10, pady=10, fill=BOTH, expand=True)
        scroll.config(command=listbox.yview)
        scroll2.config(command=listbox.xview)
        frame.pack(fill=BOTH, expand=True)
        pr.geometry('500x500')
        pr.mainloop()

    @staticmethod
    def shown(self):
        pr = Tk()
        pr.title('Negative Reviews')
        frame = Frame(pr)
        scroll = Scrollbar(frame)
        scroll.pack(side=RIGHT, fill=Y)

        scroll2 = Scrollbar(frame, orient=HORIZONTAL)
        scroll2.pack(side=BOTTOM, fill=X)

        listbox = Listbox(frame, yscrollcommand=scroll.set,  xscrollcommand=scroll2.set)
        j = 1
        l = reviews['Negative']
        for i in l:
            try:
                listbox.insert(END, str(j) + '. ' + str(i))
                listbox.insert(END, ' ')
                j += 1
            except:
                pass
        listbox.pack(padx=10, pady=10, fill=BOTH, expand=True)
        scroll.config(command=listbox.yview)
        scroll2.config(command=listbox.xview)
        frame.pack(fill=BOTH, expand=True)
        pr.geometry('500x500')
        pr.mainloop()


    def start_review(self, movie):

        query = movie + ' user review'
        for j in search(query, tld="co.in", num=1, stop=1, pause=2):
            link = j
        print(link)


        response = urllib.request.urlopen(link)
        html = response.read()
        soup = BeautifulSoup(html, "html.parser")
        text = soup.get_text(strip=False)


        sent = sent_tokenize(text)
        data = []
        for i in range(1, len(sent) - 7):
            if 'found this helpful.' in sent[i]:
                continue
            if 'Was this review helpful?' in sent[i]:
                continue
            if 'Sign in to vote.' in sent[i]:
                continue
            if 'Permalink' in sent[i]:
                continue
            data.append(sent[i])

        def subjective(s):
            p = TextBlob(s).sentiment.subjectivity
            return p

        def polar(s):
            p = TextBlob(s).sentiment.polarity
            if p < 0:
                return ('Negative', p)
            elif p == 0:
                return ('Neutral', p)
            else:
                return ('Positive', p)

        self.df = pd.DataFrame({'review': data})


        polarity = []
        subjectivity = []
        polar_values = []
        reviews.clear()
        for i in data:
            response = polar(i)
            polarity.append(response[0])
            reviews[response[0]].append(i)
            polar_values.append(response[1])
            subjectivity.append(subjective(i))

        self.df['polarity'] = polarity
        self.df['polar_values'] = polar_values
        self.df['subjective_values'] = subjectivity


        nc = self.df[self.df['polarity'] == 'Negative'].shape[0]
        np = self.df[self.df['polarity'] == 'Positive'].shape[0]
        nn = self.df[self.df['polarity'] == 'Neutral'].shape[0]

        plt.style.use('fivethirtyeight')

        figure_bar=plt.Figure(figsize=(4, 4))
        a_bar=figure_bar.add_subplot(111)
        a_bar.pie([np, nc, nn], labels=['Positive', 'Negative', 'Neutral'], explode=[0,0.1,0.1],
                  shadow=True, autopct='%1.1f%%')

        figure_scatter=plt.Figure(figsize=(4, 4))
        a_scatter=figure_scatter.add_subplot(111)
        for i in range(0, self.df.shape[0]):
            a_scatter.scatter(self.df['polar_values'][i], self.df['subjective_values'][i], color='Blue')
        figure_scatter.suptitle('Scatter Graph')

        chart_bar=FigureCanvasTkAgg(figure_bar,root)
        chart_scatter=FigureCanvasTkAgg(figure_scatter,root)

        chart_bar.get_tk_widget().place(x=30, y=200)
        chart_scatter.get_tk_widget().place(x=500, y=200)

        self.create_text(475, 400, text='Subjectivity', fill='white', angle=90, tag='subjectivity', font='Abc 15 bold')
        self.create_text(650, 630, text='Polarity', fill='white', tag='polarity', font='Abc 15 bold')
        l=[1,2,3,4,5]
        self.create_rectangle(950, 220, 1200, 250, fill="yellow", outline="red", tag='btrpr')
        self.create_text(1060, 235, text="Positive Reviews", fill='green', font='Abc 15 bold', tag='bttpr')
        self.tag_bind(self.find_withtag('btrpr'), "<Button-1>", self.showp)
        self.tag_bind(self.find_withtag('bttpr'), "<Button-1>", self.showp)

        self.create_rectangle(950, 420, 1200, 450, fill="yellow", outline="red", tag='btrnr')
        self.create_text(1060, 435, text="Negative Reviews", fill='green', font='Abc 15 bold', tag='bttnr')
        self.tag_bind(self.find_withtag('btrnr'), "<Button-1>", self.shown)
        self.tag_bind(self.find_withtag('bttnr'), "<Button-1>", self.shown)


obj=Review()
obj.pack()
root.mainloop()