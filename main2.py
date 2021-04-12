from kivy.uix.floatlayout import FloatLayout
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.uix.screenmanager import Screen, ScreenManager, SlideTransition
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from sqlalchemy.sql.expression import text
from db import User, Department, Article, create_db, session

class OptionsScreen(Screen):
    options = ["fam", "dpt", "art"]


    def save_dpt(self, name):
        if name != '':
            department = Department(name=name)
            session.add(department)
            session.commit()

            popup_content = BoxLayout(orientation="vertical")
            popup_content.add_widget(Label(text="Es necesario reiniciar para ver los cambios"))
            popup_content.add_widget(Button(text="Reiniciar ahora", on_press=\
                lambda a: self.reload_app()))

            popup = Popup(title="AVISO", content=popup_content, size_hint=(None, None),\
                size=(400, 200))
            popup.open()
        else:
            popup = Popup(title="ERROR", content=Label(text="Introduce un nombre válido"), \
                size_hint=(None, None), size=(400, 100))
            popup.open()


    def save_cnt(self, name, price, department_id):
        if len(name) > 0 and float(price) > 0 and len(price) > 0:
            article = Article(name=name, price=price, department_id=department_id)
            session.add(article)
            session.commit()

            popup = Popup(title="AVISO", content=Label(text="Contenido añadido correctamente"), \
                size_hint=(None, None), size=(400, 200))
            popup.open()

            self.manager.transition = SlideTransition(direction="down")
            self.manager.current = "Main Screen"
        else:
            popup = Popup(title="ERROR", content=Label(text="Introduce datos válidos"), \
                size_hint=(None, None), size=(400, 100))
            popup.open()


    def mod_dpt(self, name, new_name):
        if name != '':
            department = session.query(Department).filter_by(name=name).first()
            department.name = new_name
            session.add(department)
            session.commit()

            popup_content = BoxLayout(orientation="vertical")
            popup_content.add_widget(Label(text="Es necesario reiniciar para ver los cambios"))
            popup_content.add_widget(Button(text="Reiniciar ahora", on_press=\
                lambda a: self.reload_app()))

            popup = Popup(title="AVISO", content=popup_content, size_hint=(None, None),\
                size=(400, 200))
            popup.open()
        else:
            popup = Popup(title="ERROR", content=Label(text="Introduce un nombre válido"), \
                size_hint=(None, None), size=(400, 100))
            popup.open()


    def mod_cnt(self, name, new_name, price, new_price, department_id):
        pass


    def del_dpt(self, name):
        if name != "DEPARTAMENTOS":
            department = session.query(Department).filter_by(name=name).first()
            session.delete(department)
            session.commit()

            popup_content = BoxLayout(orientation="vertical")
            popup_content.add_widget(Label(text="Es necesario reiniciar para ver los cambios"))
            popup_content.add_widget(Button(text="Reiniciar ahora", on_press=\
                lambda a: self.reload_app()))

            popup = Popup(title="AVISO", content=popup_content, size_hint=(None, None),\
                size=(400, 200))
            popup.open()
        else:
            popup = Popup(title="ERROR", content=Label(text="Selecciona un departamento"), size_hint=(None, None), \
                size=(400, 100))
            popup.open()


    def del_cnt(self, name, dpt_name):
        if name != dpt_name:
            article = session.query(Article).filter_by(name=name).first()
            session.delete(article)
            session.commit()

            popup = Popup(title="AVISO", content=Label(text="Contenido eliminado correctamente"), \
            size_hint=(None, None), size=(400, 200))
            popup.open()

            self.manager.transition = SlideTransition(direction="down")
            self.manager.current = "Main Screen"
        else:
            popup = Popup(title="ERROR", content=Label(text="Selecciona un contenido"), \
                size_hint=(None, None), size=(400, 100))
            popup.open()


    def add_on_release_dpt(self, btn, dropdown, name):
        btn.bind(on_release=lambda btn: dropdown.select(name))


    def on_release_cnt_del(self, dropdown, name, layout, dpt):
        layout.clear_widgets()

        department = session.query(Department).filter_by(name=name).first()

        dropdown = DropDown()
            
        for i in department.articles:
            btn = Button(text=i.name, size_hint_y=None, height=44, background_color="pink")
            self.add_on_release_dpt(btn, dropdown, i.name)
            dropdown.add_widget(btn)

        select_btn = Button(text='CONTENIDO', size_hint=(.7, .08), pos=(140, 350), \
            background_color="pink")
        select_btn.bind(on_release=dropdown.open)

        dropdown.bind(on_select=lambda instance, x: setattr(select_btn, 'text', x))
            
        layout.add_widget(Label(text="Contenido", size_hint=(.7, .06), pos=(0, 400)))
        layout.add_widget(select_btn)
        layout.add_widget(Button(text="ELIMINAR", size_hint=(.7, .06), \
            on_press=lambda a:self.del_cnt(select_btn.text, dpt), \
                background_color="red"))

        return dropdown.select(name)


    def on_release_cnt_add(self, dropdown, name, layout, department_id):
        layout.clear_widgets()

        layout.add_widget(Label(text="Nombre del contenido"))
        
        article_name = TextInput(hint_text="Nombre")
        layout.add_widget(article_name)

        article_price = TextInput(hint_text="0")
        layout.add_widget(article_price)

        layout.add_widget(Button(text="AÑADIR CONTENIDO", background_color="green", \
            on_press=lambda a: self.save_cnt(article_name.text, article_price.text, department_id)))
        
        return dropdown.select(name)


    def on_release_cnt_mod(self, dropdown, name, layout, department_id):
        layout.clear_widgets()

        layout.add_widget(Label(text="Nuevo nombre del departamento"))

        dpt_name = TextInput(hint_text="Nombre")
        layout.add_widget(dpt_name)

        layout.add_widget(Button(text="GUARDAR CAMBIOS", background_color="green", \
            on_press=lambda a: self.mod_dpt(name, dpt_name.text)))
        
        return dropdown.select(name)


    def add_on_release_cnt_del(self, btn, dropdown, name, layout):
        btn.bind(on_release=lambda a:self.on_release_cnt_del(dropdown, name, layout, btn.text))


    def add_on_release_cnt_add(self, btn, dropdown, name, layout):
        department = session.query(Department).filter_by(name=btn.text).first()
        btn.bind(on_release=lambda a:self.on_release_cnt_add(dropdown, name, layout, department.id))
        
    
    def add_on_release_cnt_mod(self, btn, dropdown, name, layout):
        department = session.query(Department).filter_by(name=btn.text).first()
        btn.bind(on_release=lambda a: self.on_release_cnt_mod(dropdown, name, layout, department.id))


    def change_first_opt(self, opt, layout, second_layout):
        """ if opt >= 0:
            option = self.options[opt]
            
            layout.clear_widgets()
            if option == "add-dpt":
                dpt_label = Label(text="Departamento", size_hint=(1, .06), pos=(-250, 400))
                dpt_name = TextInput(hint_text="Nuevo departamento", size_hint=(.7, .06), pos=(100, 350))
                save_btn = Button(text="GUARDAR DEPARTAMENTO", on_press=lambda a: self.save_dpt(dpt_name.text), \
                    size_hint=(.3, .07), pos=(420, 300), background_color="green")

                layout.add_widget(dpt_label)
                layout.add_widget(dpt_name)
                layout.add_widget(save_btn)
            elif option == "add-cnt":
                content_layout = BoxLayout(orientation="vertical", size_hint=(None, None), \
                    size=(560,200), pos=(140,100))

                departments = session.query(Department).all()
                dropdown = DropDown()
                
                for i in departments:
                    btn = Button(text=i.name, size_hint_y=None, height=44, background_color="pink")
                    self.add_on_release_cnt_add(btn, dropdown, i.name, content_layout)
                    dropdown.add_widget(btn)

                select_btn = Button(text='DEPARTAMENTOS', size_hint=(.7, .08), pos=(140, 350), \
                    background_color="pink")
                select_btn.bind(on_release=dropdown.open)

                dropdown.bind(on_select=lambda instance, x: setattr(select_btn, 'text', x))
                
                layout.add_widget(Label(text="Departamentos disponibles", size_hint=(.7, .06), pos=(0, 400)))
                layout.add_widget(select_btn)
                layout.add_widget(content_layout)
            elif option == "del-dpt":
                departments = session.query(Department).all()
                dropdown = DropDown()
                
                for i in departments:
                    btn = Button(text=i.name, size_hint_y=None, height=44, background_color="pink")
                    self.add_on_release_dpt(btn, dropdown, i.name)
                    dropdown.add_widget(btn)

                select_btn = Button(text='DEPARTAMENTOS', size_hint=(.7, .08), pos=(140, 350), \
                    background_color="pink")
                select_btn.bind(on_release=dropdown.open)

                dropdown.bind(on_select=lambda instance, x: setattr(select_btn, 'text', x))
                
                layout.add_widget(Label(text="Departamentos disponibles", size_hint=(.7, .06), pos=(0, 400)))
                layout.add_widget(Button(text="ELIMINAR", background_color="red", size_hint=(.2, .08), pos=(140, 300), \
                    on_press=lambda a: self.del_dpt(select_btn.text)))
                layout.add_widget(select_btn)
            elif option == 'del-cnt':
                content_layout = BoxLayout(orientation="vertical", size_hint=(None, None), \
                    size=(560,200), pos=(140,100))

                departments = session.query(Department).all()
                dropdown = DropDown()
                
                for i in departments:
                    btn = Button(text=i.name, size_hint_y=None, height=44, background_color="pink")
                    self.add_on_release_cnt_del(btn, dropdown, i.name, content_layout)
                    dropdown.add_widget(btn)

                select_btn = Button(text='DEPARTAMENTOS', size_hint=(.7, .08), pos=(140, 350), \
                    background_color="pink")
                select_btn.bind(on_release=dropdown.open)

                dropdown.bind(on_select=lambda instance, x: setattr(select_btn, 'text', x))
                
                layout.add_widget(Label(text="Departamentos disponibles", size_hint=(.7, .06), pos=(0, 400)))
                layout.add_widget(select_btn)
                layout.add_widget(content_layout)
            elif option == 'mod-dpt':
                content_layout = BoxLayout(orientation="vertical", size_hint=(None, None), \
                    size=(560, 200), pos=(140, 100))

                departments = session.query(Department).all()
                dropdown = DropDown()

                for i in departments:
                    btn = Button(text=i.name, size_hint_y=None, height=44, background_color="pink")
                    self.add_on_release_cnt_mod(btn, dropdown, i.name, content_layout)
                    dropdown.add_widget(btn)

                select_btn = Button(text='DEPARTAMENTOS', size_hint=(.7, .08), pos=(140, 350), \
                    background_color="pink")
                select_btn.bind(on_release=dropdown.open)

                dropdown.bind(on_select=lambda instance, x: setattr(select_btn, 'text', x))

                layout.add_widget(Label(text='Departamentos disponibles', size_hint=(.7, .06), pos=(0, 400)))
                layout.add_widget(select_btn)
                layout.add_widget(content_layout)
            else:
                pass
        else:
            self.manager.transition = SlideTransition(direction="up")
            self.manager.current = "Main Screen" """
        layout.clear_widgets()
        
        if opt >= 0:
            option = self.options[opt]
            
            if option == 'fam':
                layout.add_widget(Button(text="NUEVA", background_color="blue", \
                    on_press=lambda a: self.change_last_opt('add-fam', second_layout)))
                layout.add_widget(Button(text="MODIFICAR", background_color="blue", \
                    on_press=lambda a: self.change_last_opt('mod-fam', second_layout)))
                layout.add_widget(Button(text="ELIMINAR", background_color="blue", \
                    on_press=lambda a: self.change_last_opt('del-fam', second_layout)))
            elif option == 'dpt':
                layout.add_widget(Button(text="NUEVO", background_color="green", \
                    on_press=lambda a: self.change_last_opt('add-dpt', second_layout)))
                layout.add_widget(Button(text="MODIFICAR", background_color="green", \
                    on_press=lambda a: self.change_last_opt('mod-dpt', second_layout)))
                layout.add_widget(Button(text="ELIMINAR", background_color="green", \
                    on_press=lambda a: self.change_last_opt('del-dpt', second_layout)))
            else:
                layout.add_widget(Button(text="NUEVO", background_color="pink", \
                    on_press=lambda a: self.change_last_opt('add-art', second_layout)))
                layout.add_widget(Button(text="MODIFICAR", background_color="pink", \
                    on_press=lambda a: self.change_last_opt('mod-art', second_layout)))
                layout.add_widget(Button(text="ELIMINAR", background_color="pink", \
                    on_press=lambda a: self.change_last_opt('del-art', second_layout)))
        else:
            self.manager.transition = SlideTransition(direction="up")
            self.manager.current = "Main Screen"

    
    def change_last_opt(self, opt, layout):
        layout.clear_widgets()

        if opt == 'add-fam':
            layout.add_widget(Label(text="Nombre de la familia:", size_hint=(1, .2)))
            layout.add_widget(TextInput(hint_text="Bebida", size_hint=(1, .2)))
            layout.add_widget(Button(text="AÑADIR", size_hint=(1, .2)))
        elif opt == 'add-dpt':
            layout.add_widget(Label(text="Nombre del departamento:", size_hint=(1, .2)))
            layout.add_widget(TextInput(hint_text="Refresco", size_hint=(1, .2)))
            layout.add_widget(Button(text="AÑADIR", size_hint=(1, .2)))
        elif opt == 'add-art':
            layout.add_widget(Label(text="Nombre del artículo:", size_hint=(1, .2)))
            layout.add_widget(TextInput(hint_text="Coca Cola", size_hint=(1, .2)))
            layout.add_widget(Button(text="AÑADIR", size_hint=(1, .2)))
        elif opt == 'mod-fam':
            layout.add_widget(Button(text="mod-fam"))
        elif opt == 'mod-dpt':
            layout.add_widget(Button(text="mod-dpt"))
        elif opt == 'mod-art':
            layout.add_widget(Button(text="mod-art"))
        elif opt == 'del-fam':
            layout.add_widget(Button(text="del-fam"))
        elif opt == 'del-dpt':
            layout.add_widget(Button(text="del-dpt"))
        else:
            layout.add_widget(Button(text="del-art"))


    def create_layout(self):
        main_layout = BoxLayout(orientation="vertical", spacing=10)

        first_layout = BoxLayout(orientation="horizontal", spacing=10, size_hint_x=None)
        first_layout.bind(minimum_width=first_layout.setter('width'))

        mid_layout = BoxLayout(orientation="horizontal", spacing=10, size_hint=(1, .1))

        last_layout = GridLayout(cols=2)
        
        first_layout.add_widget(Button(text="FAMILIAS", background_color="blue", size_hint_x=None, \
            width=200, on_press=lambda a: self.change_first_opt(0, mid_layout, last_layout)))
        first_layout.add_widget(Button(text="DEPARTAMENTOS", background_color="green", size_hint_x=None, \
            width=200, on_press=lambda a: self.change_first_opt(1, mid_layout, last_layout)))
        first_layout.add_widget(Button(text="ARTÍCULOS", background_color="pink", size_hint_x=None, \
            width=200, on_press=lambda a: self.change_first_opt(2, mid_layout, last_layout)))
        first_layout.add_widget(Button(text="MENÚ PRINCIPAL", background_color="red", size_hint_x=None, \
            width=200, on_press=lambda a: self.change_first_opt(-1, mid_layout, last_layout)))

        #first_layout.add_widget(Button(text="Añadir departamento", background_color="pink", \
        #    on_press=lambda a: self.change_opt(0, last_layout), size_hint_x=None, width=200))
        #first_layout.add_widget(Button(text=" Añadir contenido a\n   un departamento", background_color="pink", \
        #    on_press=lambda a: self.change_opt(1, last_layout), size_hint_x=None, width=200))
        #first_layout.add_widget(Button(text="Eliminar departamento", background_color="red", \
        #    on_press=lambda a: self.change_opt(2, last_layout), size_hint_x=None, width=200))
        #first_layout.add_widget(Button(text="Eliminar contenido de\n    un departamento", background_color="red", \
        #    on_press=lambda a: self.change_opt(3, last_layout), size_hint_x=None, width=200))
        #first_layout.add_widget(Button(text="Modificar departamento", background_color="pink", \
        #    on_press=lambda a: self.change_opt(4, last_layout), size_hint_x=None, width=200))
        #first_layout.add_widget(Button(text="Modificar contenido de\n    un departamento", background_color="pink", \
        #    on_press=lambda a: self.change_opt(5, last_layout), size_hint_x=None, width=200))
        #first_layout.add_widget(Button(text="Menú principal", background_color="pink", \
        #    on_press=lambda a: self.change_opt(-1, last_layout), size_hint_x=None, width=200))

        scroll_options = ScrollView(size_hint=(1, .1))
        scroll_options.add_widget(first_layout)

        main_layout.add_widget(scroll_options)
        main_layout.add_widget(mid_layout)
        main_layout.add_widget(last_layout)
        self.add_widget(main_layout)

    
    def __init__(self, **kw):
        super(OptionsScreen, self).__init__(**kw)

        self.create_layout()


class MainScreen(Screen):
    departments = session.query(Department).all()
    selection = []


    def change_dpt(self, department_id, layout, layout_to):
        layout.clear_widgets()

        article = session.query(Article).filter_by(department_id=department_id).all()

        if len(article) > 0:
            for i in range(len(article)):
                btn = Button(text=article[i].name, size_hint_y=None, height=40, \
                    size_hint_x=None, width=100, background_color="pink")
                self.add_on_press_article(btn, layout_to, article[i].id)
                layout.add_widget(btn)
        else:
            layout.add_widget(Label(text="No hay contenido"))


    def add_on_press_departments(self, btn, department_id, layout, layout_to):
        btn.bind(on_press=lambda a: self.change_dpt(department_id, layout, layout_to))


    def add_on_press_article(self, btn, layout, article_id):
        btn.bind(on_press=lambda a: self.add_selection(layout, article_id))


    def add_selection(self, layout, article_id):
        article = session.query(Article).filter_by(id=article_id).first()
        self.selection.append(article)

        layout.clear_widgets()

        for i in self.selection:
            layout.add_widget(Label(text=i.name + " - " + str(i.price) + "€"))


    def create_layout(self):
        main_layout = GridLayout(cols=2)

        left_layout = BoxLayout(orientation="vertical")
        
        right_layout = BoxLayout(orientation="vertical", spacing=10)

        department_layout = GridLayout(cols=2, spacing=10, size_hint_y=None)
        department_layout.bind(minimum_height=department_layout.setter('height'))
        
        content_layout = GridLayout(cols=4, spacing=10, size_hint_y=None)
        content_layout.bind(minimum_height=content_layout.setter('height'))
        
        for i in range(len(self.departments)):
            btn = Button(text=self.departments[i].name, size_hint_y=None, height=40, background_color="blue")
            self.add_on_press_departments(btn, self.departments[i].id, content_layout, left_layout)
            department_layout.add_widget(btn)

        scroll_departament = ScrollView(size_hint=(1, .2))
        scroll_departament.add_widget(department_layout)

        scroll_content = ScrollView(size_hint=(1, .6))
        scroll_content.add_widget(content_layout)

        options_layout = BoxLayout(orientation="horizontal")
        opt_btn = Button(text="OPCIONES", size_hint=(None, None), \
            height=40, width=200, background_color="brown")
        opt_btn.bind(on_press=lambda a: self.change_screen())
        exit_btn = Button(text="SALIR", size_hint=(None, None), \
            height=40, width=200, background_color="brown", \
                on_press=lambda a: App.get_running_app().stop())
        options_layout.add_widget(opt_btn)
        options_layout.add_widget(exit_btn)

        right_layout.add_widget(scroll_departament)
        right_layout.add_widget(scroll_content)
        right_layout.add_widget(options_layout)

        main_layout.add_widget(left_layout)
        main_layout.add_widget(right_layout)

        return main_layout


    def change_screen(self):
        self.manager.transition = SlideTransition(direction="down")
        self.manager.current = "Options Screen"


    def __init__(self, **kw):
        super(MainScreen, self).__init__(**kw)

        layout = self.create_layout()

        self.departments = session.query(Department).all()
        
        self.add_widget(layout)


class LoginScreen(Screen):
    def add_number(self, num: str, txt, username, password):
        if txt.text == "Usuario" or txt.text == "Usuario incorrecto":
            username.text += num
        else:
            password.text += num


    def delete_number(self, opcion, username, password):
        if opcion.text == "Usuario" or opcion.text == "Usuario incorrecto":
            username.text = username.text[0:-1]
        else:
            password.text = password.text[0:-1]


    def confirm_user(self, opcion, user_name, password):
        user = session.query(User).filter_by(username=user_name.text).first()

        if opcion.text == "Usuario" or opcion.text == "Usuario incorrecto":
            if not user is None:
                opcion.text = "Contraseña"
                user_name.disabled = True
            else:
                popup = Popup(title="Error", \
                    content=Label(text="Usuario incorrecto"),
                    size_hint=(None, None), size=(400, 200))
                popup.open()
        else:
            if user.password == password.text:
                opcion.text = "Usuario correcto"
                password.disabled = True
                self.manager.transition = SlideTransition(direction="left")
                self.manager.current = "Main Screen"
            else:
                popup = Popup(title="Error", \
                    content=Label(text="Contraseña incorrecta"),
                    size_hint=(None, None), size=(400, 200))
                popup.open()

    
    def create_layout(self):
        layout = GridLayout()
        layout.cols = 2

        left_layout = FloatLayout()

        txt = TextInput(disabled=True, text="Usuario", size_hint=(.6, .05), \
            pos=(70, 550))
        txt.id = "instrucciones"
        
        username = TextInput(hint_text="Código usuario", size_hint=(.6, .05), \
            pos=(70, 400))
        username.id = "codigo_usuario"
        
        password = TextInput(hint_text="Contraseña", size_hint=(.6, .05), \
            pos=(70, 200))
        password.id = "contrasena_usuario"
        
        left_layout.add_widget(txt)
        left_layout.add_widget(Label(text="Código usuario", size_hint=(.2, .2), \
            pos=(70, 400)))
        left_layout.add_widget(username)
        left_layout.add_widget(Label(text="Contraseña", size_hint=(.2, .2), \
            pos=(70, 200)))
        left_layout.add_widget(password)

        right_layout = BoxLayout(orientation="vertical")
        right_layout.add_widget(GridLayout(cols=1))
        right_layout1 = GridLayout()
        right_layout1.cols = 3

        right_layout1.add_widget(Button(text="7", \
            on_press=lambda a: self.add_number("7", txt, username, password)))
        right_layout1.add_widget(Button(text="8", \
            on_press=lambda a: self.add_number("8", txt, username, password)))
        right_layout1.add_widget(Button(text="9", \
            on_press=lambda a: self.add_number("9", txt, username, password)))
        right_layout1.add_widget(Button(text="4", \
            on_press=lambda a: self.add_number("4", txt, username, password)))
        right_layout1.add_widget(Button(text="5", \
            on_press=lambda a: self.add_number("5", txt, username, password)))
        right_layout1.add_widget(Button(text="6", \
            on_press=lambda a: self.add_number("6", txt, username, password)))
        right_layout1.add_widget(Button(text="1", \
            on_press=lambda a: self.add_number("1", txt, username, password)))
        right_layout1.add_widget(Button(text="2", \
            on_press=lambda a: self.add_number("2", txt, username, password)))
        right_layout1.add_widget(Button(text="3", \
            on_press=lambda a: self.add_number("3", txt, username, password)))
        right_layout1.add_widget(Button(text="Cancelar", background_color="red", \
            on_press=lambda a: self.delete_number(txt, username, password)))
        right_layout1.add_widget(Button(text="0", \
            on_press=lambda a: self.add_number("0", txt, username, password)))
        right_layout1.add_widget(Button(text="Confirmar", background_color="green", \
            on_press=lambda a: self.confirm_user(txt, username, password)))

        right_layout.add_widget(right_layout1)
        layout.add_widget(left_layout)
        layout.add_widget(right_layout)

        return layout


    def __init__(self, **kw):
        super(LoginScreen, self).__init__(**kw)

        layout = self.create_layout()

        self.add_widget(layout)


class Main2App(App):
    def build(self):
        root = ScreenManager()

        root.add_widget(LoginScreen(name="Login Screen"))
        root.add_widget(MainScreen(name="Main Screen"))
        root.add_widget(OptionsScreen(name="Options Screen"))
        
        return root


if __name__ == '__main__':
    create_db()
    
    Main2App().run()
