import sqlite3
import csv
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.list import MDList, TwoLineAvatarListItem, IconLeftWidget
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.dialog import MDDialog
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel

class LoginScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = MDBoxLayout(orientation='vertical', padding="40dp", spacing="20dp")
        layout.add_widget(MDLabel(text="CONTROL DE FLOTA", halign="center", font_style="H4"))
        
        self.user = MDTextField(hint_text="Usuario")
        self.password = MDTextField(hint_text="Contraseña", password=True)
        layout.add_widget(self.user)
        layout.add_widget(self.password)
        
        layout.add_widget(MDRaisedButton(text="ENTRAR", pos_hint={"center_x": .5}, on_release=self.verificar))
        self.add_widget(layout)

    def verificar(self, *args):
        if self.user.text == "admin" and self.password.text == "1234":
            self.manager.current = "principal"
        else:
            MDDialog(title="Error", text="Clave incorrecta").open()

class ControlFlotaApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Blue"
        self.conexion = sqlite3.connect("flota_v7.db")
        self.cursor = self.conexion.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS moviles 
            (chapa TEXT PRIMARY KEY, chofer TEXT, km REAL, u_mante REAL, u_dife REAL)''')
        self.conexion.commit()

        self.sm = MDScreenManager()
        self.sm.add_widget(LoginScreen(name="login"))
        
        # Pantalla Principal
        main_screen = MDScreen(name="principal")
        layout = MDBoxLayout(orientation='vertical', padding="10dp")
        
        self.buscador = MDTextField(hint_text="Buscar Chapa...")
        self.buscador.bind(text=self.cargar_datos)
        layout.add_widget(self.buscador)
        
        self.scroll = MDScrollView()
        self.lista = MDList()
        self.scroll.add_widget(self.lista)
        layout.add_widget(self.scroll)
        
        btns = MDBoxLayout(size_hint_y=None, height="60dp", spacing="10dp")
        btns.add_widget(MDRaisedButton(text="+ NUEVO", on_release=self.dialogo_alta))
        btns.add_widget(MDRaisedButton(text="EXCEL", on_release=self.exportar))
        layout.add_widget(btns)
        
        main_screen.add_widget(layout)
        self.sm.add_widget(main_screen)
        
        self.cargar_datos()
        return self.sm

    def cargar_datos(self, *args):
        self.lista.clear_widgets()
        busqueda = self.buscador.text
        self.cursor.execute("SELECT * FROM moviles WHERE chapa LIKE ?", ('%' + busqueda + '%',))
        
        for r in self.cursor.fetchall():
            chapa, chofer, km, u_mante, u_dife = r
            f_mante = 5000 - (km - u_mante)
            f_dife = 20000 - (km - u_dife)
            
            # Alertas
            alerta = ""
            vencido = False
            if f_mante <= 0: 
                alerta += "!! MANT "
                vencido = True
            if f_dife <= 0: 
                alerta += "!! DIFE "
                vencido = True
            
            color = (1, 0, 0, 1) if vencido else (0, 0.5, 1, 1)
            
            item = TwoLineAvatarListItem(
                text=f"{chapa} {alerta}",
                secondary_text=f"KM: {km} | Mante: {int(f_mante)} | Dife: {int(f_dife)}",
                on_release=lambda x, c=chapa: self.gestionar(c)
            )
            icon = IconLeftWidget(icon="car-info", theme_text_color="Custom", text_color=color)
            item.add_widget(icon)
            self.lista.add_widget(item)

    def dialogo_alta(self, *args):
        box = MDBoxLayout(orientation="vertical", size_hint_y=None, height="180dp")
        self.c_in = MDTextField(hint_text="Chapa")
        self.h_in = MDTextField(hint_text="Chofer")
        self.k_in = MDTextField(hint_text="KM Actual", input_filter="float")
        box.add_widget(self.c_in); box.add_widget(self.h_in); box.add_widget(self.k_in)
        
        self.dia = MDDialog(title="Nueva Unidad", type="custom", content_cls=box,
                            buttons=[MDFlatButton(text="SALIR", on_release=lambda x: self.dia.dismiss()),
                                     MDRaisedButton(text="GRABAR", on_release=self.grabar)])
        self.dia.open()

    def grabar(self, *args):
        try:
            k = float(self.k_in.text)
            self.cursor.execute("INSERT INTO moviles VALUES (?,?,?,?,?)", (self.c_in.text, self.h_in.text, k, k, k))
            self.conexion.commit(); self.cargar_datos(); self.dia.dismiss()
        except: pass

    def gestionar(self, chapa):
        self.sel = chapa
        box = MDBoxLayout(orientation="vertical", size_hint_y=None, height="150dp")
        self.km_up = MDTextField(hint_text="Actualizar KM", input_filter="float")
        self.ch_up = MDTextField(hint_text="Nuevo Chofer")
        box.add_widget(self.km_up); box.add_widget(self.ch_up)
        
        self.dia = MDDialog(title=f"Móvil {chapa}", type="custom", content_cls=box,
                            buttons=[
                                MDRaisedButton(text="OK", on_release=self.update),
                                MDRaisedButton(text="R. 5K", on_release=lambda x: self.reset_serv("mante")),
                                MDRaisedButton(text="R. 20K", on_release=lambda x: self.reset_serv("dife"))
                            ])
        self.dia.open()

    def update(self, *args):
        if self.km_up.text: self.cursor.execute("UPDATE moviles SET km=? WHERE chapa=?", (float(self.km_up.text), self.sel))
        if self.ch_up.text: self.cursor.execute("UPDATE moviles SET chofer=? WHERE chapa=?", (self.ch_up.text, self.sel))
        self.conexion.commit(); self.cargar_datos(); self.dia.dismiss()

    def reset_serv(self, tipo):
        self.cursor.execute("SELECT km FROM moviles WHERE chapa=?", (self.sel,))
        k = self.cursor.fetchone()[0]
        col = "u_mante" if tipo == "mante" else "u_dife"
        self.cursor.execute(f"UPDATE moviles SET {col}=? WHERE chapa=?", (k, self.sel))
        self.conexion.commit(); self.cargar_datos(); self.dia.dismiss()

    def exportar(self, *args):
        with open("Reporte.csv", "w", newline="") as f:
            w = csv.writer(f); self.cursor.execute("SELECT * FROM moviles")
            w.writerows(self.cursor.fetchall())
        MDDialog(title="Excel", text="Reporte.csv creado").open()

if __name__ == "__main__":
    ControlFlotaApp().run()
