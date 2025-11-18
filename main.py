# ================================
# main.py – Blinkit style version
# ================================
import threading
import time
import os

from kivy.config import Config
Config.set('graphics', 'width', '400')
Config.set('graphics', 'height', '740')

from kivy.lang import Builder
from kivy.clock import Clock
from kivy.uix.screenmanager import Screen
from kivymd.app import MDApp
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivymd.toast import toast

import db, models
from firebase_client import FirebaseClient


class LoginScreen(Screen):
    pass

class CustomerHome(Screen):
    pass

class VendorHome(Screen):
    pass


class BlinkitMDApp(MDApp):
    dialog = None
    detail_dialog = None
    profile_dialog = None
    cart = []

    def build(self):
        db.init_db()
        self.firebase = FirebaseClient()
        self.user = None
        self.theme_cls.primary_palette = "Green"

        KV = open("ui.kv").read()
        return Builder.load_string(KV)

    # -------------------------
    # AUTHENTICATION
    # -------------------------
    def login(self, role, username, password):
        if not username or not password:
            self.show_msg("Enter username & password")
            return

        user = models.authenticate(username, password)
        if not user:
            self.show_msg("Invalid login")
            return

        if user["role"] != role:
            self.show_msg("Account role mismatch!")
            return

        self.user = user

        if role == "customer":
            self.root.current = "customer_home"
            Clock.schedule_once(lambda dt: self.load_products(), 0.2)
        else:
            self.root.current = "vendor_home"
            self.refresh_vendor_orders()
            threading.Thread(target=self.vendor_order_poller, daemon=True).start()

    def signup_user(self, role, username, password):
        if not username or not password:
            self.show_msg("Enter username & password")
            return

        uid = models.create_user(username, password, role, username)
        if uid:
            self.show_msg(f"Signup successful ({role})")
        else:
            self.show_msg("User exists or error")

    # -------------------------
    # PRODUCT LOADING
    # -------------------------
    def load_products(self, category=None, search=""):
        try:
            products = models.get_products(category)
            if search:
                s = search.lower()
                products = [p for p in products if s in p["title"].lower()]

            screen = self.root.get_screen("customer_home")
            grid = screen.ids.products_grid
            grid.clear_widgets()

            for p in products:
                card_kv = f'''
<ProductCard@MDCard>:
    product: {{}}
    title: "{p['title']}"
    price_text: "₹{p['price']}"
'''
                card = Builder.load_string(card_kv)
                card.product = p
                img = p.get("image_path") or "assets/sample_products/apple.jpg"
                if card.ids.get("p_img"):
                    card.ids.p_img.source = img
                grid.add_widget(card)

            self.update_category_chips()

        except Exception as e:
            print("LOAD ERROR:", e)
            self.show_msg("Error loading products")

    def filter_products(self, value):
        self.load_products(search=value)

    def update_category_chips(self):
        screen = self.root.get_screen("customer_home")
        cont = screen.ids.chips_container
        cont.clear_widgets()

        cats = set([p.get("category") or "All" for p in models.get_products()])
        if "All" not in cats:
            cats.add("All")

        from kivymd.uix.chip import MDChip

        for c in sorted(cats):
            chip = MDChip(
                text=c,
                on_release=lambda inst, cat=c: self.load_products(
                    None if cat == "All" else cat
                )
            )
            cont.add_widget(chip)

    # -------------------------
    # PRODUCT DETAIL
    # -------------------------
    def show_product_detail(self, product):
        txt = f"{product['title']}\n₹{product['price']}\n\n{product['description']}"
        if self.detail_dialog:
            self.detail_dialog.dismiss()
        self.detail_dialog = MDDialog(
            title=product["title"],
            text=txt,
            size_hint=(0.8, 0.6)
        )
        self.detail_dialog.open()

    # -------------------------
    # CART SYSTEM
    # -------------------------
    def add_to_cart(self, product):
        self.cart.append(product)
        self.show_msg("Added to cart")
        screen = self.root.get_screen("customer_home")
        screen.ids.topbar.title = f"Products ({len(self.cart)})"

    def open_cart(self):
        if not self.cart:
            self.show_msg("Cart empty")
            return

        txt = "\n".join([f"{p['title']} — ₹{p['price']}" for p in self.cart])
        total = sum([p["price"] for p in self.cart])

        self.detail_dialog = MDDialog(
            title="My Cart",
            text=f"{txt}\n\nTotal: ₹{total}",
            buttons=[MDFlatButton(text="Place Order", on_release=lambda x: self.place_orders())]
        )
        self.detail_dialog.open()

    def place_orders(self):
        if not self.user:
            self.show_msg("Login required")
            return

        groups = {}
        for p in self.cart:
            groups.setdefault(p["vendor_id"] or 0, []).append(p)

        for vid, items in groups.items():
            total = sum(p["price"] for p in items)
            models.place_order(self.user["id"], vid, items, total)

        self.cart = []
        self.show_msg("Order placed")

        if self.detail_dialog:
            self.detail_dialog.dismiss()

    # -------------------------
    # VENDOR SIDE
    # -------------------------
    def open_add_product(self):
        content = Builder.load_string('''
BoxLayout:
    orientation: "vertical"
    spacing: dp(8)
    MDTextField:
        id: t1
        hint_text: "Title"
    MDTextField:
        id: t2
        hint_text: "Price"
        input_filter: "float"
    MDTextField:
        id: t3
        hint_text: "Category"
    MDTextField:
        id: t4
        hint_text: "Description"
    MDFlatButton:
        text: "Save"
        on_release: app.save_product(t1.text, t2.text, t3.text, t4.text)
''')

        self.dialog = MDDialog(
            title="Add Product",
            type="custom",
            content_cls=content,
        )
        self.dialog.open()

    def save_product(self, title, price, category, desc):
        if not title or not price:
            self.show_msg("Missing fields")
            return

        models.add_product(self.user["id"], title, desc, float(price), category, "")
        self.show_msg("Product saved")
        self.dialog.dismiss()

    def refresh_vendor_orders(self):
        screen = self.root.get_screen("vendor_home")
        grid = screen.ids.vendor_orders
        grid.clear_widgets()

        orders = models.get_orders_for_vendor(self.user["id"])
        from kivymd.uix.list import OneLineListItem

        for o in orders:
            grid.add_widget(
                OneLineListItem(text=f"Order {o['id']}  ₹{o['total']}  {o['status']}")
            )

    def vendor_order_poller(self):
        while True:
            if self.user:
                self.refresh_vendor_orders()
            time.sleep(5)

    # -------------------------
    # PROFILE MENU
    # -------------------------
    def show_profile(self):
        self.profile_dialog = MDDialog(
            title="Profile / Role",
            text="Choose mode",
            buttons=[
                MDFlatButton(text="Customer", on_release=lambda x: self.switch_role("customer")),
                MDFlatButton(text="Vendor", on_release=lambda x: self.switch_role("vendor")),
                MDFlatButton(text="Close", on_release=lambda x: self.close_profile())
            ]
        )
        self.profile_dialog.open()

    def switch_role(self, role):
        if not self.user:
            self.show_msg("Login first")
        else:
            if self.user["role"] == role:
                if role == "customer":
                    self.root.current = "customer_home"
                    Clock.schedule_once(lambda dt: self.load_products(), 0.1)
                else:
                    self.root.current = "vendor_home"
                    self.refresh_vendor_orders()
            else:
                self.show_msg("This account is not " + role)
        self.close_profile()

    def close_profile(self):
        try:
            self.profile_dialog.dismiss()
        except:
            pass

    # -------------------------
    # UTIL
    # -------------------------
    def show_msg(self, t):
        print(t)
        try:
            toast(t)
        except:
            pass


if __name__ == "__main__":
    BlinkitMDApp().run()
