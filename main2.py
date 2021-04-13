from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen, ScreenManager, SlideTransition
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput

from db import Article, Department, Family, Iva, User, create_db, session


class OptionsScreen(Screen):
    options = ["fam", "dpt", "art"]


    def new_article(self, dpt_name, layout, drop):
        """ Crear layout para nuevo artículo """

        iva_types = session.query(Iva).all()
        
        layout.add_widget(Label(text="Nombre del artículo:", size_hint=(.5, .1), pos=(0, 300)))

        name_art = TextInput(hint_text="Nombre", size_hint=(.4, .1), pos=(50, 250))
        layout.add_widget(name_art)

        layout.add_widget(Label(text="Precio:", size_hint=(.5, .1), pos=(250, 300)))

        price_art = TextInput(hint_text="Precio", size_hint=(.2, .1), pos=(400, 250))
        layout.add_widget(price_art)

        layout.add_widget(Label(text="Descripción:", size_hint=(.5, .1), pos=(0, 200)))

        desc_art = TextInput(hint_text="Descripción", size_hint=(.5, .2), pos=(50, 100))
        layout.add_widget(desc_art)

        dropdown = DropDown()
        for type in iva_types:
            btn = Button(text=str(type.type)+'%', size_hint_y=None, height=40, background_color="pink")
            self.add_on_release(btn, dropdown, layout, 'iva')
            dropdown.add_widget(btn)

        layout.add_widget(Label(text="Porcentaje de IVA:", size_hint=(.4, .1), pos=(400, 200)))
        iva_select = Button(text="IVA", size_hint=(.2, .1), pos=(500, 150), background_color="pink")
        iva_select.bind(on_release=dropdown.open)
        dropdown.bind(on_select=lambda instance, x: setattr(iva_select, 'text', x))
        layout.add_widget(iva_select)

        layout.add_widget(Button(text="AÑADIR", size_hint=(.2, .1), pos=(500, 100), \
            on_press=lambda a: self.save_art(name_art.text, desc_art.text, price_art.text, iva_select.text, dpt_name), \
                background_color="green"))
        
        return drop.select(dpt_name)


    def delete_family(self, name, popup):
        """ Eliminar familia """

        family = session.query(Family).filter_by(name=name).first()
        session.delete(family)
        session.commit()

        popup.dismiss()


    def popup_delete_family(self, name):
        """ Crear popup para confirmar eliminación de familia """
        
        content_popup = BoxLayout(orientation="vertical")
        content_popup.add_widget(Label(text="Se eliminará la familia {}".format(name)))
        content_popup.add_widget(Button(text="Confirmar", on_press=lambda a: self.delete_family(name, popup)))
        dismiss_btn = Button(text="Cancelar")
        content_popup.add_widget(dismiss_btn)

        popup = Popup(title="AVISO", content=content_popup, size_hint=(None, None), size=(400, 200))
        dismiss_btn.bind(on_press=popup.dismiss)

        popup.open()


    def popup_delete_department(self, name):
        """ Crear popup para confirmar eliminación de departamento """        
        
        content_popup = BoxLayout(orientation="vertical")
        content_popup.add_widget(Label(text="Se eliminará el departamento {}".format(name)))
        content_popup.add_widget(Button(text="Confirmar", on_press=lambda a: self.delete_department(name, popup)))
        dismiss_btn = Button(text="Cancelar")
        content_popup.add_widget(dismiss_btn)

        popup = Popup(title="AVISO", content=content_popup, size_hint=(None, None), size=(400, 200))
        dismiss_btn.bind(on_press=popup.dismiss)

        popup.open()


    def delete_department(self, name, popup):
        """ Eliminar departamento """
        
        department = session.query(Department).filter_by(name=name).first()
        session.delete(department)
        session.commit()

        popup.dismiss()


    def del_fam_layout(self, name, layout, dropdown):
        if name != 'FAMILIA':
            layout.add_widget(Button(text="ELIMINAR", background_color="red", size_hint=(.5, .1), pos=(100, 200), \
                on_press=lambda a: self.popup_delete_family(name)))

        return dropdown.select(name)


    def del_dpt_layout(self, name, layout, drop):
        family = session.query(Family).filter_by(name=name).first()
        departments = session.query(Department).filter_by(family_id=family.id).all()
        dropdown = DropDown()

        dpt_count = 0
        for dpt in departments:
            if len(dpt.articles) == 0:
                btn = Button(text=dpt.name, background_color="green", height=40, size_hint_y=None)
                self.add_on_release(btn, dropdown, layout, 'fam')
                dropdown.add_widget(btn)
                dpt_count += 1

        if dpt_count > 0:
            layout.add_widget(Label(text="Departamentos disponibles:", size_hint=(.4, .1), pos=(100, 300)))
                
            dpt_select = Button(text="DEPARTAMENTO", size_hint=(.4, .1), pos=(100, 250), background_color="green")
            dpt_select.bind(on_release=dropdown.open)
            dropdown.bind(on_select=lambda instance, x: setattr(dpt_select, 'text', x))
            layout.add_widget(dpt_select)

            layout.add_widget(Button(text="ELIMINAR", background_color="red", size_hint=(.4, .1), pos=(100, 200), \
                on_press=lambda a: self.popup_delete_department(dpt_select.text)))
        else:
            layout.add_widget(Label(text="Hay departamentos pero contienen artículos", size_hint=(.4, .1), pos=(100, 300)))

        return drop.select(name)


    def add_on_release(self, btn, dropdown, layout, option):
        if option == 'fam':
            btn.bind(on_release=lambda a: dropdown.select(btn.text))
        elif option == 'dpt':
            btn.bind(on_release=lambda a: self.add_dpt_by_fam(btn.text, layout, dropdown, None))
        elif option == 'fam-art':
            btn.bind(on_release=lambda a: self.add_dpt_by_fam(btn.text, layout, dropdown, 'dpt-art'))
        elif option == 'art':
            btn.bind(on_release=lambda a: self.new_article(btn.text, layout, dropdown))
        elif option == 'iva':
            btn.bind(on_release=lambda a: dropdown.select(btn.text))
        elif option == 'fam-del':
            btn.bind(on_release=lambda a: self.del_fam_layout(btn.text, layout, dropdown))
        elif option == 'fam-dpt-del':
            btn.bind(on_release=lambda a: self.del_dpt_layout(btn.text, layout, dropdown))

    
    def add_dpt_by_fam(self, fam_name, layout, drop, option):
        """ Añadir lista de departamentos """
        
        family = session.query(Family).filter_by(name=fam_name).first()

        departments = session.query(Department).filter_by(family_id=family.id).all()

        dropdown = DropDown()
        dpt_count = 0
        for dpt in departments:
            btn = Button(text=dpt.name, size_hint_y=None, height=40, background_color="pink")
            
            if option == 'dpt-art':
                self.add_on_release(btn, dropdown, layout, 'art')
            else:
                self.add_on_release(btn, dropdown, layout, 'fam')
            dropdown.add_widget(btn)
            dpt_count += 1

        if dpt_count > 0:
            layout.add_widget(Label(text="Seleccionar departamento:", size_hint=(.5, .1), pos=(400, 400)))
            dpt_label = Button(text="DEPARTAMENTO", size_hint=(.4, .1), pos=(400, 350), background_color="pink")
            dpt_label.bind(on_release=dropdown.open)
            dropdown.bind(on_select=lambda instance, x: setattr(dpt_label, 'text', x))

            layout.add_widget(dpt_label)
        else:
            layout.add_widget(Label(text="No hay departamentos disponibles", size_hint=(.5, .1), pos=(400, 400)))

        return drop.select(fam_name)

    
    def save_fam(self, name, description):
        """ Guardar nueva familia """

        if name != '':
            new_family = Family(name=name, description=description)
            session.add(new_family)
            session.commit()
        else:
            popup = Popup(title="ERROR", content=Label(text="Introduce un nombre válido"), \
                size_hint=(None, None), size=(400, 200))
            popup.open()
        

    def save_dpt(self, name, description, family_name):
        """ Guardar nuevo departamento """
        
        family = session.query(Family).filter_by(name=family_name).first()

        if name != '':
            if family_name != 'FAMILIA':
                new_dpt = Department(name=name, description=description, family_id=family.id)
                session.add(new_dpt)
                session.commit()
            else:
                popup = Popup(title="ERROR", content=Label(text="Selecciona una familia"), \
                    size_hint=(None, None), size=(400, 100))
        else:
            popup = Popup(title="ERROR", content=Label(text="Introduce un nombre válido"), \
                size_hint=(None, None), size=(400, 100))
            popup.open()

    
    def save_art(self, name, description, price, iva_type, dpt_name):
        """ Guardar nuevo artículo """
        
        if name != '':
            try:
                price = float(price)
                
                if price != '' and float(price) > 0:
                    if iva_type != 'IVA':
                        if dpt_name != 'DEPARTAMENTO':
                            iva_type = iva_type.replace('%', '')
                            iva = session.query(Iva).filter_by(type=iva_type).first()
                            department = session.query(Department).filter_by(name=dpt_name).first()

                            new_article = Article(name=name, description=description, price=price, \
                                department_id=department.id, iva_type=iva.type)
                            session.add(new_article)
                            session.commit()
                        else:
                            popup = Popup(title="ERROR", content=Label(text="Selecciona un departamento"), \
                                size_hint=(None, None), size=(400, 100))
                            popup.open()
                    else:
                        popup = Popup(title="ERROR", content=Label(text="Selecciona un porcentaje de IVA"), \
                            size_hint=(None, None), size=(400, 100))
                        popup.open()
                else:
                    popup = Popup(title="ERROR", content=Label(text="Introduce un precio válido"), \
                        size_hint=(None, None), size=(400, 100))
                    popup.open()
            except:
                popup = Popup(title="ERROR", content=Label(text="Introduce un precio válido"), \
                    size_hint=(None, None), size=(400, 100))
                popup.open()  
        else:
            popup = Popup(title="ERROR", content=Label(text="Introduce un nombre válido"), \
                size_hint=(None, None), size=(400, 100))
            popup.open()
        

    def change_first_opt(self, opt, layout, second_layout):
        """ Seleccionar opción con la que operar """

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
            layout.add_widget(Label(text="Nombre de la familia:", size_hint=(.8, .1), pos=(-175, 400)))
            fam_name = TextInput(hint_text="Nombre", size_hint=(.8, .1), pos=(100, 350))
            layout.add_widget(fam_name)
            
            layout.add_widget(Label(text="Descripción:", size_hint=(.8, .1), pos=(-175, 225)))
            fam_desc = TextInput(hint_text="Descripción de la familia", size_hint=(.8, .2), pos=(100, 125))
            layout.add_widget(fam_desc)
            
            layout.add_widget(Button(text="AÑADIR", size_hint=(.8, .1), pos=(100, 50), background_color="green", \
                on_press=lambda a: self.save_fam(fam_name.text, fam_desc.text)))
        elif opt == 'add-dpt':
            layout.add_widget(Label(text="Nombre del departamento:", size_hint=(.8, .1), pos=(-150, 400)))
            dpt_name = TextInput(hint_text="Nombre", size_hint=(.8, .1), pos=(100, 350))
            layout.add_widget(dpt_name)

            layout.add_widget(Label(text="Descripción:", size_hint=(.8, .1), pos=(-175, 300)))
            dpt_desc = TextInput(hint_text="Descripción del departamento", size_hint=(.8, .2), pos=(100, 200))
            layout.add_widget(dpt_desc)

            layout.add_widget(Label(text="Añadir a la familia:", size_hint=(.8, .1), pos=(-175, 150)))
            
            families = session.query(Family).all()
            dropdown = DropDown()
            
            for fam in families:
                btn = Button(text=fam.name, size_hint_y=None, height=40, background_color="green")
                self.add_on_release(btn, dropdown, layout, 'fam')
                dropdown.add_widget(btn)

            families_label = Button(text="FAMILIA", size_hint=(.8, .1), pos=(100, 100), background_color="green")
            families_label.bind(on_release=dropdown.open)
            dropdown.bind(on_select=lambda instance, x: setattr(families_label, 'text', x))

            layout.add_widget(families_label)

            layout.add_widget(Button(text="AÑADIR", size_hint=(.8, .1), pos=(100, 50), background_color="green", \
                on_press=lambda a: self.save_dpt(dpt_name.text, dpt_desc.text, families_label.text)))
        elif opt == 'add-art':
            families = session.query(Family).all()
            
            dropdown = DropDown()
            for fam in families:
                btn = Button(text=fam.name, size_hint_y=None, height=40, background_color="pink")
                self.add_on_release(btn, dropdown, layout, 'fam-art')
                dropdown.add_widget(btn)

            layout.add_widget(Label(text="Seleccionar familia:", size_hint=(.5, .1), pos=(0, 400)))
            families_label = Button(text="FAMILIA", size_hint=(.4, .1), pos=(50, 350), background_color="pink")
            families_label.bind(on_release=dropdown.open)
            dropdown.bind(on_select=lambda instance, x: setattr(families_label, 'text', x))
            
            layout.add_widget(families_label)
        elif opt == 'mod-fam':
            layout.add_widget(Button(text="mod-fam"))
        elif opt == 'mod-dpt':
            layout.add_widget(Button(text="mod-dpt"))
        elif opt == 'mod-art':
            layout.add_widget(Button(text="mod-art"))
        elif opt == 'del-fam':
            families = session.query(Family).all()

            layout.add_widget(Label(text="Una familia no puede ser eliminada si contiene departamentos", \
                size_hint=(.5, .1), pos=(100, 450)))

            if len(families) > 0:
                
                dropdown = DropDown()
                fam_count = 0
                for fam in families:
                    if len(fam.departments) == 0:
                        btn = Button(text=fam.name, size_hint_y=None, height=40, background_color="blue")
                        self.add_on_release(btn, dropdown, layout, 'fam-del')
                        dropdown.add_widget(btn)
                        fam_count += 1

                if fam_count > 0:
                    layout.add_widget(Label(text="Familias disponibles:", size_hint=(.5, .1), pos=(100, 400)))
                    fam_select = Button(text="FAMILIA", size_hint=(.5, .1), pos=(100, 350), background_color="blue")
                    fam_select.bind(on_release=dropdown.open)
                    dropdown.bind(on_select=lambda instance, x: setattr(fam_select, 'text', x))
                
                    layout.add_widget(fam_select)
                else:
                    layout.add_widget(Label(text="Hay familias pero contienen departamentos", size_hint=(.5, .1), pos=(100, 400)))
            else:
                layout.add_widget(Label(text="No hay familias", size_hint=(.5, .1), pos=(100, 400)))
        elif opt == 'del-dpt':
            families = session.query(Family).all()
            
            layout.add_widget(Label(text="Un departamento no puede ser eliminado si contiene artículos", \
                size_hint=(.5, .1), pos=(50, 450)))

            dropdown = DropDown()
            for fam in families:
                if len(fam.departments) > 0:
                    btn = Button(text=fam.name, size_hint_y=None, height=40, background_color="green")
                    self.add_on_release(btn, dropdown, layout, 'fam-dpt-del')
                    dropdown.add_widget(btn)

            layout.add_widget(Label(text="Familias disponibles:", size_hint=(.5, .1), pos=(0, 400)))
            fam_select = Button(text="FAMILIA", size_hint=(.5, .1), pos=(50, 350), background_color="green")
            fam_select.bind(on_release=dropdown.open)
            dropdown.bind(on_select=lambda instance, x: setattr(fam_select, 'text', x))
            
            layout.add_widget(fam_select)
        else:
            layout.add_widget(Button(text="del-art"))


    def create_layout(self):
        main_layout = BoxLayout(orientation="vertical", spacing=10)

        first_layout = BoxLayout(orientation="horizontal", spacing=10, size_hint_x=None)
        first_layout.bind(minimum_width=first_layout.setter('width'))

        mid_layout = BoxLayout(orientation="horizontal", spacing=10, size_hint=(1, .1))

        last_layout = FloatLayout()
        
        first_layout.add_widget(Button(text="FAMILIAS", background_color="blue", size_hint_x=None, \
            width=200, on_press=lambda a: self.change_first_opt(0, mid_layout, last_layout)))
        first_layout.add_widget(Button(text="DEPARTAMENTOS", background_color="green", size_hint_x=None, \
            width=200, on_press=lambda a: self.change_first_opt(1, mid_layout, last_layout)))
        first_layout.add_widget(Button(text="ARTÍCULOS", background_color="pink", size_hint_x=None, \
            width=200, on_press=lambda a: self.change_first_opt(2, mid_layout, last_layout)))
        first_layout.add_widget(Button(text="MENÚ PRINCIPAL", background_color="red", size_hint_x=None, \
            width=200, on_press=lambda a: self.change_first_opt(-1, mid_layout, last_layout)))

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
