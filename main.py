from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.screenmanager import Screen, ScreenManager, SlideTransition
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout


class LoginLayout(GridLayout):
    def add_number(self, num: str):
        if self.ids.instrucciones.text == "Usuario" or self.ids.instrucciones.text == "Usuario incorrecto":
            self.ids.codigo_usuario.text += num
        else:
            self.ids.contrasena_usuario.text += num

    def delete_number(self, opcion):
        if opcion == "Usuario":
            self.ids.codigo_usuario.text = self.ids.codigo_usuario.text[0:-1]
        else:
            self.ids.contrasena_usuario.text = self.ids.contrasena_usuario.text[0:-1]

    def confirm_user(self, opcion):
        instruccion = self.ids.instrucciones.text
        codigo = ''

        if opcion == "Usuario":
            if instruccion == "Usuario" or instruccion == "Usuario incorrecto":
                codigo = self.ids.codigo_usuario.text
                if codigo == "1234":
                    self.ids.instrucciones.text = "Contraseña"
                    self.ids.codigo_usuario.disabled = True
                else:
                    self.ids.instrucciones.text = "Usuario incorrecto"
        else:
            codigo = self.ids.contrasena_usuario.text
            if codigo == "1234":
                self.ids.instrucciones.text = "Usuario correcto"
                self.ids.contrasena_usuario.disabled = True
            else:
                self.ids.instrucciones.text = "Contraseña incorrecta"


class MainLayout(GridLayout):
    pass


class LoginScreen(Screen):
    def add_number(self, num: str):
        if self.ids.instrucciones.text == "Usuario" or self.ids.instrucciones.text == "Usuario incorrecto":
            self.ids.codigo_usuario.text += num
        else:
            self.ids.contrasena_usuario.text += num

    def delete_number(self, opcion):
        if opcion == "Usuario":
            self.ids.codigo_usuario.text = self.ids.codigo_usuario.text[0:-1]
        else:
            self.ids.contrasena_usuario.text = self.ids.contrasena_usuario.text[0:-1]

    def confirm_user(self, opcion):
        instruccion = self.ids.instrucciones.text
        codigo = ''

        if opcion == "Usuario":
            if instruccion == "Usuario" or instruccion == "Usuario incorrecto":
                codigo = self.ids.codigo_usuario.text
                if codigo == "1234":
                    self.ids.instrucciones.text = "Contraseña"
                    self.ids.codigo_usuario.disabled = True
                else:
                    self.ids.instrucciones.text = "Usuario incorrecto"
        else:
            codigo = self.ids.contrasena_usuario.text
            if codigo == "1234":
                self.ids.instrucciones.text = "Usuario correcto"
                self.ids.contrasena_usuario.disabled = True
                self.manager.transition = SlideTransition(direction="left")
                self.manager.current = self.manager.next()
            else:
                self.ids.instrucciones.text = "Contraseña incorrecta"

    def __init__(self, **kw):
        super(LoginScreen, self).__init__(**kw)
        layout = LoginLayout()
        
        self.add_widget(layout)


class MainScreen(Screen):
    def __init__(self, **kw):
        super(MainScreen, self).__init__(**kw)
        layout = MainLayout()

        self.add_widget(layout)


class MainApp(App):
    def build(self):
        root = ScreenManager()

        root.add_widget(LoginScreen())
        root.add_widget(MainScreen())

        return root


if __name__ == '__main__':
    MainApp().run()

