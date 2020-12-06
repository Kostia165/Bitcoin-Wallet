import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from ctypes import windll
from bit import PrivateKeyTestnet
from bit import Key
from bit import SUPPORTED_CURRENCIES
import requests
import datetime
import clipboard as cb
import threading
import concurrent.futures

LARGEFONT =("Verdana", 14) 

class tkinterApp(tk.Tk): 

    # __init__ function for class tkinterApp  
    def __init__(self, *args, **kwargs):  
          
        # __init__ function for class Tk 
        tk.Tk.__init__(self, *args, **kwargs)
        
        # create config dictionary for all windows
        self.config = {'state': 0};
        
        # configuring main window of app
        # self.configure(background='white')
        self.geometry('900x400')
        self.minsize(900, 400)
        self.maxsize(900, 400)
        self.title('Bitcoin Wallet');
        windll.shcore.SetProcessDpiAwareness(1)
          
        # creating a container 
        self.container = tk.Frame(self)   
        self.container.pack(side = "top", fill = "both", expand = True)  
   
        self.container.grid_rowconfigure(0, weight = 1) 
        self.container.grid_columnconfigure(0, weight = 1) 
   
        # starting page
        self.frame = StartPage(self.container, self)
        self.frame.grid(row = 0, column = 0, rowspan = 3, columnspan = 3, sticky ="nsew")
   
    # to display the current frame passed as 
    # parameter 
    def async_show_frame(self, page, button_text, def_text, button):
        x = threading.Thread(target = self.show_frame, args = (page, button_text, def_text, button))
        x.start()
    
    def show_frame(self, page, button_text, def_text, button):
        try:
            button_text.set('Loading...')
            button['state'] = tk.DISABLED
            self.frame = page(self.container, self)
            self.frame.grid(row = 0, column = 0, rowspan = 3, columnspan = 3, sticky ="nsew")
            #frame.tkraise()
        except BaseException:
            button_text.set(def_text)
            button['state'] = tk.NORMAL
            messagebox.showerror(title = 'Error', message = 'Maybe, you don\'t have internet connection or use wrong key')

# first window frame startpage 
class StartPage(tk.Frame): 
    def __init__(self, parent, controller):  
        tk.Frame.__init__(self, parent)
        
        self.controller = controller
        self.configure(background='white')
        self.istestnet = IntVar()
        self.istestnet.set(1)
        
        self.textCreateButton = tk.StringVar()
        self.textOpenButton = tk.StringVar()
        self.textCreateButton.set('Create')
        self.textOpenButton.set('Open')
          
        startTitle = tk.Label(self, text="What do you want to do with wallet?", bg="white", fg="black", font = LARGEFONT)
        startTitle.grid(row = 0, column = 0, columnspan = 2)
        isTestnetCheckBox = tk.Checkbutton(self, text = 'Testnet', 
                                variable = self.istestnet, 
                                onvalue = 1, 
                                offvalue = 0,
                                bg = 'white',
                                padx = 15, 
                                pady = 10, 
                                font = LARGEFONT)
        isTestnetCheckBox.grid(row = 0, column = 2, sticky = W)
        self.createButton = tk.Button(self, textvariable = self.textCreateButton,
                                fg='white',
                                bg='#8c9fbd',
                                activeforeground='white',
                                activebackground='#b8c2d1',  
                                bd=10,
                                borderwidth=2,
                                relief=FLAT,
                                overrelief=RAISED,
                                font=LARGEFONT,
                                command = self.mainPage)
        self.createButton.grid(row = 1, column = 0, columnspan = 3, padx=10, pady=10, sticky = "nsew")
        self.openButton = tk.Button(self, textvariable = self.textOpenButton,
                                fg='white',
                                bg='#8c9fbd',
                                activeforeground='white',
                                activebackground='#b8c2d1',  
                                bd=10,
                                borderwidth=2,
                                relief=FLAT,
                                overrelief=RAISED,
                                font=LARGEFONT,
                                command = self.enterKeyPage)
        self.openButton.grid(row = 2, column = 0, columnspan = 3, padx=10, pady=10, sticky = "nsew")
        
        for x in range(3):
            Grid.columnconfigure(self, x, weight = 1)

        for y in range(3):
            Grid.rowconfigure(self, y, weight = 1)
    
    def mainPage(self):
        self.controller.config.update({'istestnet' : self.istestnet.get()});
        self.controller.async_show_frame(MainPage, self.textCreateButton, 'Create', self.createButton)
    
    def enterKeyPage(self):
        self.controller.config.update({'istestnet' : self.istestnet.get()});
        self.controller.async_show_frame(EnterKey, self.textOpenButton, 'Open', self.openButton)

# window for entering private key
class EnterKey(tk.Frame): 
      
    def __init__(self, parent, controller): 
          
        tk.Frame.__init__(self, parent)
        
        self.configure(background='white')
        
        self.textOpenButton2 = tk.StringVar()
        self.textOpenButton2.set('Open')
        
        keyTitle = tk.Label(self, text="Enter your private key", bg="white", fg="black", font = LARGEFONT)
        keyTitle.pack()
        self.keyInput = tk.Entry(self, bg='#ebf3ff', font = LARGEFONT)
        self.keyInput.pack(expand=1, padx=10, pady=10)
        self.enterButton = tk.Button(self, textvariable = self.textOpenButton2,
                                fg='white',
                                bg='#8c9fbd',
                                activeforeground='white',
                                activebackground='#b8c2d1',
                                borderwidth=2,
                                relief=FLAT,
                                overrelief=RAISED,
                                font=LARGEFONT,
                                command = lambda : self.transferKey(controller))
        self.enterButton.pack(expand=1, padx=10, pady=10)
        
    def transferKey(self, controller):
        controller.config['private_key'] = self.keyInput.get()
        controller.async_show_frame(MainPage, self.textOpenButton2, 'Open', self.enterButton)

# window for working with wallet
class MainPage(tk.Frame):  
    def __init__(self, parent, controller): 
        tk.Frame.__init__(self, parent)
        
        self.parent = parent
        self.configure(background='white')
        self.currency = 'btc'
        self.trans_url = "https://blockstream.info/testnet/api/tx/"
        
        addressLabel = tk.Label(self, text = "Address: dfsu3fdu434", bg = "white", fg = "black", font = LARGEFONT)
        addressLabel.grid(row = 0, column = 0, columnspan = 2, sticky = W, padx = 10, pady = 10, ipadx = 5, ipady = 5)
        self.coinLabel = tk.Label(self, text = "Coins: 1 btc", bg = "white", fg = "black", font = LARGEFONT)
        self.coinLabel.grid(row = 1, column = 0, columnspan = 2, sticky = W, padx = 10, pady = 10, ipadx = 5, ipady = 5)
        self.sendAddressInput = tk.Entry(self, bg='#ebf3ff', font = LARGEFONT)
        self.sendAddressInput.grid(row = 2, column = 0, sticky = W+E, padx = 10, pady = 10, ipadx = 5, ipady = 5)
        self.sendCoinsInput = tk.Entry(self, bg='#ebf3ff', font = LARGEFONT)
        self.sendCoinsInput.grid(row = 3, column = 0, sticky = W, padx = 10, pady = 10, ipadx = 5, ipady = 5)
        sendButton = tk.Button(self, text = 'Send',
                                fg = 'white',
                                bg = '#8c9fbd',
                                activeforeground = 'white',
                                activebackground = '#b8c2d1',
                                borderwidth = 2,
                                relief = FLAT,
                                overrelief = RAISED,
                                font = LARGEFONT,
                                command = lambda : self.asyncSendCoins())
        sendButton.grid(row = 4, column = 0, sticky = W, padx = 10, pady = 10, ipadx = 5, ipady = 5)
        copyButton = tk.Button(self, text = 'Copy PrivKey to Clipboard',
                                fg = 'white',
                                bg = '#de9ec0',
                                activeforeground = 'white',
                                activebackground = '#de9ec0',
                                borderwidth = 2,
                                relief = FLAT,
                                overrelief = RAISED,
                                font = LARGEFONT,
                                command = lambda : self.copyKey())
        copyButton.grid(row = 4, column = 1, sticky = W, padx = 10, pady = 10, ipadx = 5, ipady = 5)
        self.changeCurrencyInput = tk.Entry(self, bg='#ebf3ff', font = LARGEFONT)
        self.changeCurrencyInput.grid(row = 5, column = 0, sticky = W, padx = 10, pady = 10, ipadx = 5, ipady = 5)
        changeCurrencyButton = tk.Button(self, text = 'Change currency',
                                fg = 'white',
                                bg = '#8c9fbd',
                                activeforeground = 'white',
                                activebackground = '#b8c2d1',
                                borderwidth = 2,
                                relief = FLAT,
                                overrelief = RAISED,
                                font = LARGEFONT,
                                command = lambda : self.asyncChangeCurrency())
        changeCurrencyButton.grid(row = 5, column = 1, padx = 10, pady = 10, ipadx = 5, ipady = 5)
        
        self.transactions = Listbox(self)
        self.transactions.grid(row = 0, column = 2, rowspan = 3, columnspan = 4, sticky = 'nsew')
        self.transactions.bind('<<ListboxSelect>>', self.asynconselect)
        self.transactionsVar = StringVar()
        self.transactionsVar.set(150 * " ")
        self.transactionsLabel = tk.Message(self, textvariable = self.transactionsVar, bg = "white", fg = "black", width = 300)
        self.transactionsLabel.grid(row = 3, column = 2, rowspan = 3, sticky = W+E, columnspan = 4, padx = 10, pady = 10, ipadx = 5, ipady = 5)
        
        self.parent.after(3000, self.asyncUpdateInterface)
        
        if (controller.config.get('istestnet') == 1):
            self.trans_url = "https://blockstream.info/testnet/api/tx/"
            if (controller.config.get('private_key') != None):
                self.key = PrivateKeyTestnet(controller.config.get('private_key'))
            else:
                self.key = PrivateKeyTestnet()
        else:
            self.trans_url = "https://blockstream.info/api/tx/"
            if (controller.config.get('private_key') != None):
                self.key = Key(controller.config.get('private_key'))
            else:
                self.key = Key()
        
        addressLabel.config(text = "Address: " + self.key.address)
        self.coinLabel.config(text = "Coins: " + self.key.get_balance(self.currency) + " " + self.currency)
            
        transactions_list = self.key.get_transactions()
        for trans in transactions_list:
            print(trans)
            self.transactions.insert(END, trans)
        print(self.trans_url)
        for x in range(6):
            Grid.columnconfigure(self, x, weight=1)

        for y in range(5):
            Grid.rowconfigure(self, y, weight=1)
    
    def asyncChangeCurrency(self):
        x = threading.Thread(target = self.changeCurrency)
        x.start()
        
    def changeCurrency(self):
        cur_values = dict(SUPPORTED_CURRENCIES).keys()
        us_input = self.changeCurrencyInput.get()
        self.changeCurrencyInput.delete(0, 'end')
        if (us_input in cur_values):
            self.currency = us_input
            coins = self.key.get_balance(self.currency)
            self.coinLabel.config(text = "Coins: " + coins + " " + self.currency)
    
    def asynconselect(self,evt):
        x = threading.Thread(target = self.onselect, args = (evt,))
        x.start()
    
    def onselect(self, evt):
        # Note here that Tkinter passes an event object to onselect()
        w = evt.widget
        index = 0
        try:
            index = int(w.curselection()[0])
        except IndexError:
            print('Unselected item in list of transactions')
            return
        value = w.get(index)
        cb.copy(value)
        print('You selected item %d: "%s"' % (index, value))
        try:
            response = requests.get(self.trans_url + value)
            print(response.json())
            json_resp = response.json()
            in_address = json_resp['vin'][0]['prevout']['scriptpubkey_address']
            out_address = json_resp['vout'][0]['scriptpubkey_address']
            fee = json_resp['fee']
            money = json_resp['vout'][0]['value']
            block_time = json_resp['status']['block_time']
            block_time = datetime.datetime.fromtimestamp(block_time).strftime('%Y-%m-%d %H:%M:%S')
            self.transactionsVar.set("Transaction: " + str(value) +
                            "\nFrom: " + str(in_address) + 
                            "\nTo: " + str(out_address) +
                            "\nValue: " + str(money) + " satoshi" +
                            "\nFee: " + str(fee) + " satoshi" + 
                            "\nTime: " + block_time)
        except BaseException:
            messagebox.showerror(title = 'Error', message = 'Maybe problems with connection or you don\'t have transactions')
    
    def asyncSendCoins(self):
        x = threading.Thread(target = self.sendCoins)
        x.start()
    
    def sendCoins(self):
        us_address = self.sendAddressInput.get()
        us_coins = self.sendCoinsInput.get()
        self.sendAddressInput.delete(0, 'end')
        self.sendCoinsInput.delete(0, 'end')
        try:
            if (us_address == '' or us_coins == ''):
                return
            us_coins = float(us_coins)
        except ValueError:
            print('invalid transformation')
            return
        
        try:
            # Send coins and update labels
            outputs = [
                (us_address, us_coins, self.currency)
            ]
            print(self.key.send(outputs))
            self.updateInterface()
            messagebox.showinfo(title = 'Transacation', message = 'Successed')
        except BaseException:
            messagebox.showerror(title = 'Error', message = 'Maybe, you don\'t have internet connection or use wrong key or you don\'t have enough money')
            
    def asyncUpdateInterface(self):
        x = threading.Thread(target = self.cycleUpdateInterface, daemon = True)
        x.start()
    
    def cycleUpdateInterface(self):
        self.updateInterface()
        self.parent.after(3000, self.asyncUpdateInterface)
            
    def updateInterface(self):
        self.coinLabel.config(text = "Coins: " + self.key.get_balance(self.currency) + " " + self.currency)
        new_transactions = self.key.get_transactions()
        trans_values = self.transactions.get(0, 'end')
        for trans in new_transactions:
            if trans not in trans_values:
                self.transactions.insert(0, trans)

    def copyKey(self):
        cb.copy(self.key.to_wif())
        
# Driver Code 
app = tkinterApp() 
app.mainloop() 
