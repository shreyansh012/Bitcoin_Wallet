from bitcoinlib.wallets import Wallet, wallet_delete
from kivy.app import App
from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.widget import Widget
from kivy.lang import Builder
from kivy.core.clipboard import Clipboard
from kivy.uix.textinput import TextInput
from kivy.uix.image import AsyncImage
from kivy.clock import Clock
from bitcoinlib.mnemonic import Mnemonic
import requests


w = Wallet("Wallet1")
# w.update_balance()
# def check_if_wallet_exists():
#     try:
#         w = Wallet("Wallet1")
#     except:
#         return False
#
#
# def createWallet():
#     passphrase = Mnemonic().generate()
#     print(passphrase)
#     w = Wallet.create("Wallet1", keys=passphrase, network='testnet')


class MainScreen(Screen):
    pass


# function to fetch the total balance in the Wallet
def get_balance():
    return w.balance()


# returns currency BTC to USD rate using a public API key
def fetch_usd_price_bitcoin():
    url = 'https://api.coindesk.com/v1/bpi/currentprice.json'
    req = requests.request("GET", url=url)
    response = req.json()
    price = response["bpi"]["USD"]["rate_float"]
    return price


class HomeScreen(Screen):
    btc = get_balance() / 100000000
    btc_balance = StringProperty("{:.08f} BTC".format(btc))
    btc_usd = StringProperty("$ {:.02f}".format(fetch_usd_price_bitcoin() * float(btc)))

    def refresh_balance(self):
        w.utxos_update()
        w.utxos_update()
        self.btc_balance = ("{:.08f} BTC".format(get_balance() / 100000000))
        self.btc_usd = str("$ {:.02f}".format(fetch_usd_price_bitcoin() * float(self.btc)))


class ReceiveScreen(Screen):
    def show_copied_to_clipboard(self):
        text = Label(text='Copied to clipboard')

    def get_address(self):
        add = w.addresslist()[0]
        return add


class SendScreen(Screen):
    def __init__(self, **kwargs):
        super(SendScreen, self).__init__(**kwargs)

        # create a GridLayout with two columns
        box = BoxLayout(spacing=20)
        back_button = (Button(text='Back',
                              size_hint=(0.05, 0.05)
                              )
                       )
        back_button.bind(on_release=self.back_button_pressed)
        box.add_widget(back_button)

        grid = GridLayout(cols=2, spacing=20)
        grid.add_widget(Label(
            text='',
            size_hint=(0.5, 0.2),
            height=30
        )
        )
        grid.add_widget(Label(
            text='',
            size_hint=(0.5, 0.2),
            height=30
        )
        )

        # add first label and text input to the GridLayout
        grid.add_widget(Label(text='Enter Amount:',
                              size_hint=(0.6, 0.1),
                              height=30
                              )
                        )
        self.amount_input = TextInput(multiline=False,
                                      size_hint=(0.6, 0.1),
                                      height=30)
        grid.add_widget(self.amount_input)

        # add second label and text input to the GridLayout
        grid.add_widget(Label(text='Enter Address:',
                              size_hint=(0.3, 0.1),
                              height=30
                              )
                        )
        self.address_input = TextInput(multiline=False,
                                       size_hint=(0.3, 0.1),
                                       height=30
                                       )
        grid.add_widget(self.address_input)
        grid.add_widget(Label(text='', size_hint=(0.5, 0.2), height=30))
        grid.add_widget(Label(text='', size_hint=(0.5, 0.2), height=30))

        # add a button to the GridLayout
        box.add_widget(Label(size_hint=(0.15, 0.1), height=3))

        submit_button = Button(text='Submit', size_hint=(0.1, 0.1), height=30)
        submit_button.bind(on_press=self.submit_data)
        box.add_widget(submit_button)

        grid.add_widget(Label(text='', size_hint=(0.5, 0.2), height=30))
        grid.add_widget(Label(text='', size_hint=(0.5, 0.1), height=30))
        box.add_widget(Label(size_hint=(0.2, 0.1), height=3))

        # add the GridLayout to the screen
        self.add_widget(grid)
        self.add_widget(box)

    def submit_data(self, instance):
        amount = self.amount_input.text
        address = self.address_input.text
        # send bitcoin with the data given by the user
        print(f'Amount: {amount}, Address: {address}')
        send_amount = float(amount) * 100000000
        w.utxos_update()
        tx = w.transaction_create([(address, send_amount)])
        tx.sign()
        tx.send()
        send_amount_label = Label(
            text=f'                      Amount: {amount} BTC ----> Sent to Address: {address}\n\n\n\n\n',
            size_hint=(0.6, 0.1),
            height=30
        )
        self.add_widget(send_amount_label)
        Clock.schedule_once(lambda dt: self.hide_label(send_amount_label), 10)

    def back_button_pressed(self, button):
        self.manager.current = 'second'
        self.manager.transition.direction = "right"

    def hide_label(self, label):
        label.text = ''


class WindowManager(ScreenManager):
    pass


kv = Builder.load_file('BtcWallet.kv')


class BtcWallet(App):
    def copy_to_clipboard(self):
        Clipboard.copy(w.addresslist()[0])  # the text which needs to be copied when we press copy to clipboard

    def build(self):
        return kv


if __name__ == '__main__':
    BtcWallet().run()
