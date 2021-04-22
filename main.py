import os

os.environ["KIVY_GL_BACKEND"] = "angle_sdl2"

import random
import string

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import NoTransition, Screen, ScreenManager
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput

from db import Article, Department, Family, Iva, User, create_db, session


class OptionsScreen(Screen):
    def create_layout(self):
        layout = GridLayout(rows=2)
        
        top_layout = BoxLayout(size_hint=(1, .1))
        top_layout.add_widget(Button(text="VOLVER", background_color="brown", \
            on_press=lambda a: self.go_main()))

        bottom_layout = GridLayout(rows=4, padding=10, spacing=10, size_hint_y=None)
        bottom_layout.bind(minimum_height=bottom_layout.setter('height'))

        bottom_layout.add_widget(Button(text="FAMILIAS", background_color="blue", size_hint_y=None, \
            height=200, on_press=lambda a: self.change_screen('families')))
        bottom_layout.add_widget(Button(text="DEPARTAMENTOS", background_color="orange", size_hint_y=None, \
            height=200, on_press=lambda a: self.change_screen('departments')))
        bottom_layout.add_widget(Button(text="ARTÍCULOS", background_color="pink", size_hint_y=None, \
            height=200, on_press=lambda a: self.change_screen('articles')))

        scroll_layout = ScrollView(size_hint=(1, 1))
        scroll_layout.add_widget(bottom_layout)

        layout.add_widget(top_layout)
        layout.add_widget(scroll_layout)
        
        self.add_widget(layout)


    def change_screen(self, screen):
        if screen == 'families':
            if self.family.name in self.manager.screen_names:
                self.manager.remove_widget(self.family)
                self.family = FamilyScreen(name="Family Screen")
                self.manager.add_widget(self.family)
            else:
                self.manager.add_widget(self.family)

            self.manager.current = "Family Screen"
        elif screen == 'departments':
            if self.department.name in self.manager.screen_names:
                self.manager.remove_widget(self.department)
                self.department = DepartmentScreen(name="Department Screen")
                self.manager.add_widget(self.department)
            else:
                self.manager.add_widget(self.department)
                
            self.manager.current = "Department Screen"
        else:
            if self.article.name in self.manager.screen_names:
                self.manager.remove_widget(self.article)
                self.article = ArticleScreen(name="Article Screen")
                self.manager.add_widget(self.article)
            else:
                self.manager.add_widget(self.article)
            
            self.manager.current = "Article Screen"
    

    def go_main(self):
        self.manager.current = "Main Screen"

    
    def __init__(self, **kw):
        super(OptionsScreen, self).__init__(**kw)
        
        self.family = FamilyScreen(name="Family Screen")
        self.department = DepartmentScreen(name="Department Screen")
        self.article = ArticleScreen(name="Article Screen")

        self.create_layout()


class MainScreen(Screen):
    def create_layout(self):
        layout = GridLayout(cols=2)
        left_layout = BoxLayout(orientation="vertical")
        right_layout = GridLayout(rows=4, spacing=10)

        box_families = GridLayout(cols=1, spacing=10, size_hint_y=None)
        box_families.bind(minimum_height=box_families.setter('height'))

        box_departments = GridLayout(cols=1, spacing=10, size_hint_y=None)
        box_departments.bind(minimum_height=box_departments.setter('height'))

        box_articles = GridLayout(cols=1, spacing=10, size_hint_y=None)
        box_articles.bind(minimum_height=box_articles.setter('height'))

        families = session.query(Family).all()
        for fam in families:
            btn = Button(text=fam.name, size_hint_y=None, height=70, background_color="blue")
            btn.bind(on_press=lambda a: self.change_family(a.id, box_departments, box_articles, left_layout))
            btn.id = fam.id
            box_families.add_widget(btn)

        scroll_families = ScrollView(size_hint=(1, .1))
        scroll_families.add_widget(box_families)

        scroll_departments = ScrollView(size_hint=(1, .2))
        scroll_departments.add_widget(box_departments)

        scroll_articles = ScrollView(size_hint=(1, .6))
        scroll_articles.add_widget(box_articles)

        box_menu = GridLayout(cols=2, spacing=10, size_hint=(1, .1))
        box_menu.add_widget(Button(text="MENÚ", background_color="brown", on_press=lambda a: self.go_menu()))
        box_menu.add_widget(Button(text="SALIR", background_color="brown", \
            on_press=lambda a: App.get_running_app().stop()))

        right_layout.add_widget(scroll_families)
        right_layout.add_widget(scroll_departments)
        right_layout.add_widget(scroll_articles)
        right_layout.add_widget(box_menu)

        layout.add_widget(left_layout)
        layout.add_widget(right_layout)

        self.add_widget(layout)
    
    
    def change_family(self, id, dpt_layout, art_layout, left_layout):
        dpt_layout.clear_widgets()
        art_layout.clear_widgets()
        
        departments = session.query(Department).filter_by(family_id=id).all()
        
        if len(departments) > 0:
            for dpt in departments:
                btn = Button(text=dpt.name, size_hint_y=None, height=70, background_color="orange")
                btn.bind(on_press=lambda a: self.change_department(a.id, art_layout, left_layout))
                btn.id = dpt.id
                dpt_layout.add_widget(btn)
        else:
            dpt_layout.add_widget(Label(text="No hay departamentos", size_hint_y=None, height=70))


    def change_department(self, id, art_layout, left_layout):
        art_layout.clear_widgets()

        articles = session.query(Article).filter_by(department_id=id).all()
        
        if len(articles) > 0:
            for art in articles:
                btn = Button(text=art.name, size_hint_y=None, height=70, background_color="pink")
                btn.bind(on_press=lambda a: self.add_selection(a.id, left_layout))
                btn.id = art.id
                art_layout.add_widget(btn)
        else:
            art_layout.add_widget(Label(text="No hay artículos", size_hint_y=None, height=70))
    
    
    def add_selection(self, id, layout):
        article = session.query(Article).filter_by(id=id).first()
        layout.add_widget(Label(text="{}: {}€".format(article.name, article.price)))


    def go_menu(self):
        self.manager.current = "Options Screen"


    def __init__(self, **kw):
        super(MainScreen, self).__init__(**kw)

        self.departments = session.query(Department).all()
        self.create_layout()


class LoginScreen(Screen):
    def create_layout(self):
        layout = GridLayout(cols=3)
        layout.add_widget(BoxLayout(size_hint=(.2, 1)))

        main_layout = BoxLayout(orientation="vertical", spacing=10, padding=10, size_hint=(.6, 1))
        
        top_layout = GridLayout(rows=5, size_hint=(1, .5))

        txt = TextInput(disabled=True, text="Usuario")
        txt.id = "instrucciones"
        top_layout.add_widget(txt)

        top_layout.add_widget(Label(text="Usuario", text_size=top_layout.size, \
            halign="left", valign="middle"))
        username = TextInput(hint_text="Código usuario")
        username.id = "codigo_usuario"
        top_layout.add_widget(username)
        
        top_layout.add_widget(Label(text="Contraseña", text_size=top_layout.size, \
            halign="left", valign="middle"))
        password = TextInput(hint_text="Contraseña", password=True)
        password.id = "contrasena_usuario"
        top_layout.add_widget(password)

        bottom_layout = GridLayout(cols=3)

        buttons = ["7", "8", "9", "4", "5", "6", "1", "2", "3", "0"]
        for btn in buttons:
            bottom_layout.add_widget(Button(text=btn, \
                on_press=lambda a: self.add_number(a.text, txt, username, password)))

        bottom_layout.add_widget(Button(text="Cancelar", background_color="red", \
            on_press=lambda a: self.delete_number(txt, username, password)))

        bottom_layout.add_widget(Button(text="Confirmar", background_color="green", \
            on_press=lambda a: self.confirm_user(txt, username, password)))

        main_layout.add_widget(top_layout)
        main_layout.add_widget(bottom_layout)

        layout.add_widget(main_layout)
        layout.add_widget(BoxLayout(size_hint=(.2, 1)))
        
        self.add_widget(layout)
    
    
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
                opcion.text = "Usuario incorrecto"
                popup = Popup(title="Error", \
                    content=Label(text="Usuario incorrecto"),
                    size_hint=(None, None), size=(400, 200))
                popup.open()
        else:
            if user.password == password.text:
                self.manager.current = "Main Screen"
            else:
                opcion.text = "Contraseña incorrecta"
                popup = Popup(title="Error", \
                    content=Label(text="Contraseña incorrecta"),
                    size_hint=(None, None), size=(400, 200))
                popup.open()


    def __init__(self, **kw):
        super(LoginScreen, self).__init__(**kw)

        self.create_layout()


class FamilyScreen(Screen):
    def create_layout(self):
        layout = GridLayout(rows=2, padding=10, spacing=20)

        top_layout = GridLayout(cols=5, spacing=20, size_hint_x=None)
        top_layout.bind(minimum_width=top_layout.setter('width'))

        box_reset = BoxLayout(size_hint_x=None, width=250)
        box_save = BoxLayout(size_hint_x=None, width=250)
        box_delete = BoxLayout(size_hint_x=None, width=250)
        box_new = BoxLayout(size_hint_x=None, width=250)

        top_layout.add_widget(Button(text="MENÚ", background_color="brown", \
            on_press=lambda a: self.go_menu(), size_hint_x=None, width=250))
        box_new.add_widget(Button(text="NUEVO", background_color="brown", \
            on_press=lambda a: self.get_new(bottom_layout, box_reset, box_save, box_delete, box_new)))
        top_layout.add_widget(box_new)
        top_layout.add_widget(box_reset)
        top_layout.add_widget(box_save)
        top_layout.add_widget(box_delete)

        bottom_layout = GridLayout(cols=1)
        self.create_families_layout(bottom_layout, box_reset, box_save, box_delete, box_new)
    
        top_scroll = ScrollView(size_hint=(1, .1))
        top_scroll.add_widget(top_layout)

        layout.add_widget(top_scroll)
        layout.add_widget(bottom_layout)

        self.add_widget(layout)
    

    def create_families_layout(self, layout, reset, save, delete, new):
        layout.clear_widgets()
        
        reset.clear_widgets()
        save.clear_widgets()
        delete.clear_widgets()
        new.clear_widgets()

        new.add_widget(Button(text="NUEVO", background_color="brown", \
            on_press=lambda a: self.get_new(layout, reset, save, delete, new)))

        families_layout = GridLayout(cols=3, spacing=10, size_hint_y=None)
        families_layout.bind(minimum_height=families_layout.setter('height'))

        families_layout.add_widget(BoxLayout(size_hint=(.1, 1)))

        buttons_layout = GridLayout(cols=1, size_hint_y=None, spacing=10)
        buttons_layout.bind(minimum_height=buttons_layout.setter('height'))

        families = session.query(Family).all()

        for fam in families:
            fam_btn = Button(text=fam.name, size_hint_y=None, height=100, background_color="blue", \
                on_press=lambda a: self.get_family(a.id, layout, reset, save, delete, new))
            fam_btn.id = fam.id
            buttons_layout.add_widget(fam_btn)

        families_layout.add_widget(buttons_layout)

        families_layout.add_widget(BoxLayout(size_hint=(.1, 1)))
        
        scroll_bottom = ScrollView(size_hint=(1, .9))
        scroll_bottom.add_widget(families_layout)

        layout.add_widget(scroll_bottom)


    def get_family(self, id, layout, reset, save, delete, new):
        family = session.query(Family).filter_by(id=id).first()
        
        layout.clear_widgets()
        new.clear_widgets()
        reset.clear_widgets()
        save.clear_widgets()
        delete.clear_widgets()

        reset.add_widget(Button(text="VOLVER", background_color="pink", \
            on_press=lambda a: self.create_families_layout(layout, reset, save, delete, new)))
        save.add_widget(Button(text="GUARDAR", background_color="green", \
            on_press=lambda a: self.modify(id, fam_code.text, fam_name.text, fam_desc.text, layout, reset, save, delete, new)))
        
        if len(family.departments) == 0: 
            delete.add_widget(Button(text="ELIMINAR", background_color="red", \
                on_press=lambda a: self.popup_delete(id, layout, reset, save, delete, new)))

        bottom_layout = GridLayout(cols=3, rows=1, spacing=40, row_force_default=True, row_default_height=40)

        box_code = BoxLayout(orientation="horizontal")
        box_code.add_widget(Label(text="Código:", size_hint=(.05, 1), text_size=box_code.size, \
            halign="left", valign="middle"))
        fam_code = TextInput(text=family.code, size_hint=(.05, 1))
        box_code.add_widget(fam_code)

        box_name = BoxLayout(orientation="horizontal")
        box_name.add_widget(Label(text="Nombre:", size_hint=(.05, 1), text_size=box_name.size, \
            halign="left", valign="middle"))
        fam_name = TextInput(text=family.name, size_hint=(.1, 1))
        box_name.add_widget(fam_name)

        box_desc = BoxLayout(orientation="horizontal")
        box_desc.add_widget(Label(text="Descripción:", size_hint=(.1, 1), text_size=box_desc.size, \
            halign="left", valign="middle"))
        fam_desc = TextInput(text=family.description, size_hint=(.4, 1))
        box_desc.add_widget(fam_desc)

        bottom_layout.add_widget(box_code)
        bottom_layout.add_widget(box_name)
        bottom_layout.add_widget(box_desc)

        layout.add_widget(bottom_layout)

    
    def get_new(self, layout, reset, save, delete, new):
        layout.clear_widgets()
        reset.clear_widgets()
        save.clear_widgets()
        delete.clear_widgets()
        new.clear_widgets()

        reset.add_widget(Button(text="VOLVER", background_color="pink", \
            on_press=lambda a: self.create_families_layout(layout, reset, save, delete, new)))
        save.add_widget(Button(text="GUARDAR", background_color="green", \
            on_press=lambda a: self.save(fam_name.text, fam_desc.text, fam_code.text, layout, reset, save, delete, new)))

        bottom_layout = GridLayout(cols=3, rows=1, spacing=40, row_force_default=True, row_default_height=40)

        box_code = BoxLayout(orientation="horizontal")
        box_code.add_widget(Label(text="Código:", size_hint=(.05, 1), text_size=box_code.size, \
            halign="left", valign="middle"))
        fam_code = TextInput(hint_text="Código", size_hint=(.05, 1))
        box_code.add_widget(fam_code)

        box_name = BoxLayout(orientation="horizontal")
        box_name.add_widget(Label(text="Nombre:", size_hint=(.05, 1), text_size=box_name.size, \
            halign="left", valign="middle"))
        fam_name = TextInput(hint_text="Nombre", size_hint=(.1, 1))
        box_name.add_widget(fam_name)

        box_desc = BoxLayout(orientation="horizontal")
        box_desc.add_widget(Label(text="Descripción:", size_hint=(.1, 1), text_size=box_desc.size, \
            halign="left", valign="middle"))
        fam_desc = TextInput(hint_text="Descripción", size_hint=(.4, 1))
        box_desc.add_widget(fam_desc)

        bottom_layout.add_widget(box_code)
        bottom_layout.add_widget(box_name)
        bottom_layout.add_widget(box_desc)

        layout.add_widget(bottom_layout)


    def popup_delete(self, id, layout, reset, save, delete, new):
        family = session.query(Family).filter_by(id=id).first()
            
        content = BoxLayout(orientation="vertical")
        content.add_widget(Label(text="Se eliminará la familia {}".format(family.name), \
            height=50, size_hint_y=None))
        

        content_popup = BoxLayout(orientation="vertical", size_hint_y=None)
        content_popup.bind(minimum_height=content_popup.setter('height'))

        content_popup.add_widget(Label(text="Código: {}".format(family.code), height=50, size_hint_y=None))

        content_popup.add_widget(Label(text="Nombre: {}".format(family.name), height=50, size_hint_y=None))
            
        if family.description == None or family.description == '':
            content_popup.add_widget(Label(text="Descripción: Sin descripción", height=50, size_hint_y=None))
        else:
            content_popup.add_widget(Label(text="Descripción: {}".format(family.description), \
                height=50, size_hint_y=None))
            
        dismiss_btn = Button(text="Cancelar", height=50, size_hint_y=None, background_color="orange")

        scroll_content = ScrollView(size_hint=(1, .8))
        scroll_content.add_widget(content_popup)
        content.add_widget(scroll_content)
        
        content.add_widget(Button(text="Confirmar", height=50, size_hint_y=None, background_color="red", \
            on_press=lambda a: self.delete(id, layout, reset, save, delete, new, popup)))
        content.add_widget(dismiss_btn)

        popup = Popup(title="AVISO", content=content, size_hint=(None, None), size=(600, 800))
        dismiss_btn.bind(on_press=popup.dismiss)
        popup.open()


    def delete(self, id, layout, reset, save, delete, new, popup):
        popup.dismiss()
        family = session.query(Family).filter_by(id=id).first()
        session.delete(family)

        self.create_families_layout(layout, reset, save, delete, new)
        
        session.commit()


    def modify(self, id, code, name, description, layout, reset, save, delete, new):
        code = code.replace(' ', '')
        
        if name != '':
            if code != '':
                if session.query(Department).filter_by(code=code).first() or \
                    session.query(Article).filter_by(code=code).first():
                    popup = Popup(title="ERROR", content=Label(text="El código ya está en uso"), \
                        size_hint=(None, None), size=(800, 200))
                    popup.open()
                else:
                    family = session.query(Family).filter_by(id=id).first()
                    
                    if family.code == code:
                        family.name = name
                        family.description = description

                        self.create_families_layout(layout, reset, save, delete, new)

                        session.commit()
                    else:
                        family_code = session.query(Family).filter_by(code=code).first()
                        
                        if family_code:
                            if family_code.id == family.id:
                                family.code = code
                                family.name = name
                                family.description = description

                                self.create_families_layout(layout, reset, save, delete, new)

                                session.commit()
                            else:
                                popup = Popup(title="ERROR", content=Label(text="El código ya está en uso"), \
                                    size_hint=(None, None), size=(400, 100))
                                popup.open()
                        else:
                            family.code = code
                            family.name = name
                            family.description = description

                            self.create_families_layout(layout, reset, save, delete, new)

                            session.commit()
            else:
                code = ''.join(random.SystemRandom().choice(string.digits) for _ in range(4))
            
                while session.query(Family).filter_by(code=code).first() or \
                    session.query(Department).filter_by(code=code).first() or \
                        session.query(Article).filter_by(code=code).first():
                    code = ''.join(random.SystemRandom().choice(string.digits) for _ in range(4))
                
                family = session.query(Family).filter_by(id=id).first()
                family.code = code
                family.name = name
                family.description = description

                self.create_families_layout(layout, reset, save, delete, new)

                session.commit()
        else:
            popup = Popup(title="ERROR", content=Label(text="Introduce un nombre válido"), \
                size_hint=(None, None), size=(800, 200))
            popup.open()


    def save(self, name, description, code, layout, reset, save, delete, new):
        code = code.replace(' ', '')
        
        if name != '':
            if code != '':
                if not session.query(Family).filter_by(code=code).first() and \
                    not session.query(Department).filter_by(code=code).first() and \
                        not session.query(Article).filter_by(code=code).first():
                    family = Family(name=name, description=description, code=code)
                    session.add(family)
                    session.commit()

                    self.create_families_layout(layout, reset, save, delete, new)
                else:
                    popup = Popup(title="ERROR", content=Label(text="El código ya está en uso"), \
                        size_hint=(None, None), size=(800, 200))
                    popup.open()
            else:
                code = ''.join(random.SystemRandom().choice(string.digits) for _ in range(4))
            
                while session.query(Family).filter_by(code=code).first() or \
                    session.query(Department).filter_by(code=code).first() or \
                        session.query(Article).filter_by(code=code).first():
                    code = ''.join(random.SystemRandom().choice(string.digits) for _ in range(4))
                
                family = Family(name=name, description=description, code=code)
                session.add(family)
                session.commit()

                self.create_families_layout(layout, reset, save, delete, new)
        else:
            popup = Popup(title="ERROR", content=Label(text="Introduce un nombre válido"), \
                size_hint=(None, None), size=(800, 200))
            popup.open()


    def go_menu(self):
        self.manager.current = 'Options Screen'


    def __init__(self, **kw):
        super(FamilyScreen, self).__init__(**kw)

        self.create_layout()


class DepartmentScreen(Screen):
    def create_layout(self):
        layout = GridLayout(rows=2, padding=10, spacing=20)

        top_layout = GridLayout(cols=5, spacing=20, size_hint_x=None)
        top_layout.bind(minimum_width=top_layout.setter('width'))

        box_reset = BoxLayout(size_hint_x=None, width=250)
        box_save = BoxLayout(size_hint_x=None, width=250)
        box_delete = BoxLayout(size_hint_x=None, width=250)
        box_new = BoxLayout(size_hint_x=None, width=250)

        top_layout.add_widget(Button(text="MENÚ", background_color="brown", \
            on_press=lambda a: self.go_menu(), size_hint_x=None, width=250))
        box_new.add_widget(Button(text="NUEVO", background_color="brown", \
            on_press=lambda a: self.get_new(bottom_layout, box_reset, box_save, box_delete, box_new)))
        top_layout.add_widget(box_new)
        top_layout.add_widget(box_reset)
        top_layout.add_widget(box_save)
        top_layout.add_widget(box_delete)

        bottom_layout = GridLayout(cols=1)
        self.create_departments_layout(bottom_layout, box_reset, box_save, box_delete, box_new)
    
        top_scroll = ScrollView(size_hint=(1, .1))
        top_scroll.add_widget(top_layout)

        layout.add_widget(top_scroll)
        layout.add_widget(bottom_layout)

        self.add_widget(layout)


    def create_departments_layout(self, layout, reset, save, delete, new):
        layout.clear_widgets()
        
        reset.clear_widgets()
        save.clear_widgets()
        delete.clear_widgets()
        new.clear_widgets()

        new.add_widget(Button(text="NUEVO", background_color="brown", \
            on_press=lambda a: self.get_new(layout, reset, save, delete, new)))

        departments_layout = GridLayout(cols=3, spacing=10, size_hint_y=None)
        departments_layout.bind(minimum_height=departments_layout.setter('height'))

        departments_layout.add_widget(BoxLayout(size_hint=(.1, 1)))

        buttons_layout = GridLayout(cols=1, size_hint_y=None, spacing=10)
        buttons_layout.bind(minimum_height=buttons_layout.setter('height'))

        departments = session.query(Department).all()

        for dpt in departments:
            dpt_btn = Button(text=dpt.name, size_hint_y=None, height=100, background_color="orange", \
                on_press=lambda a: self.get_department(a.id, layout, reset, save, delete, new))
            dpt_btn.id = dpt.id
            buttons_layout.add_widget(dpt_btn)

        departments_layout.add_widget(buttons_layout)

        departments_layout.add_widget(BoxLayout(size_hint=(.1, 1)))
        
        scroll_bottom = ScrollView(size_hint=(1, .9))
        scroll_bottom.add_widget(departments_layout)

        layout.add_widget(scroll_bottom)

    
    def get_department(self, id, layout, reset, save, delete, new):
        department = session.query(Department).filter_by(id=id).first()
        
        layout.clear_widgets()
        new.clear_widgets()
        reset.clear_widgets()
        save.clear_widgets()
        delete.clear_widgets()

        reset.add_widget(Button(text="VOLVER", background_color="pink", \
            on_press=lambda a: self.create_departments_layout(layout, reset, save, delete, new)))
        save.add_widget(Button(text="GUARDAR", background_color="green", \
            on_press=lambda a: self.modify(id, dpt_code.text, dpt_name.text, dpt_desc.text,  \
                fam_select.id, iva_select.id, layout, reset, save, delete, new)))
        
        if len(department.articles) == 0: 
            delete.add_widget(Button(text="ELIMINAR", background_color="red", \
                on_press=lambda a: self.popup_delete(id, layout, reset, save, delete, new)))

        bottom_layout = GridLayout(cols=3, rows=2, spacing=40, row_force_default=True, row_default_height=40)

        box_code = BoxLayout(orientation="horizontal")
        box_code.add_widget(Label(text="Código:", size_hint=(.1, 1), text_size=box_code.size, \
            halign="left", valign="middle"))
        dpt_code = TextInput(text=department.code, size_hint=(.2, 1))
        box_code.add_widget(dpt_code)

        box_name = BoxLayout(orientation="horizontal")
        box_name.add_widget(Label(text="Nombre:", size_hint=(.05, 1), text_size=box_name.size, \
            halign="left", valign="middle"))
        dpt_name = TextInput(text=department.name, size_hint=(.1, 1))
        box_name.add_widget(dpt_name)

        box_desc = BoxLayout(orientation="horizontal")
        box_desc.add_widget(Label(text="Descripción:", size_hint=(.1, 1), text_size=box_desc.size, \
            halign="left", valign="middle"))
        dpt_desc = TextInput(text=department.description, size_hint=(.4, 1))
        box_desc.add_widget(dpt_desc)

        box_fam = BoxLayout(orientation="horizontal")
        box_fam.add_widget(Label(text="Familia:", size_hint=(.1, 1), text_size=box_fam.size, \
            halign="left", valign="middle"))
        fam_select = Button(text=department.family.name, size_hint=(.15, 1), background_color="blue", \
            on_press=lambda a: self.select_family(a))
        fam_select.id = department.family.id
        box_fam.add_widget(fam_select)
        box_fam.add_widget(Button(text="+", background_color="blue", size_hint=(.05, 1), \
            on_press=lambda a: self.create_family()))

        box_iva = BoxLayout(orientation="horizontal")
        box_iva.add_widget(Label(text="Tipo IVA:", size_hint=(.1, 1), text_size=box_iva.size, \
            halign="left", valign="middle"))
        iva_select = Button(text=str(department.iva.type)+"%", size_hint=(.2, 1), background_color="pink", \
            on_press=lambda a: self.select_iva(a))
        iva_select.id = department.iva.id
        box_iva.add_widget(iva_select)

        bottom_layout.add_widget(box_code)
        bottom_layout.add_widget(box_name)
        bottom_layout.add_widget(box_desc)
        bottom_layout.add_widget(box_fam)
        bottom_layout.add_widget(box_iva)

        layout.add_widget(bottom_layout)


    def get_new(self, layout, reset, save, delete, new):
        layout.clear_widgets()
        new.clear_widgets()
        reset.clear_widgets()
        save.clear_widgets()
        delete.clear_widgets()

        reset.add_widget(Button(text="VOLVER", background_color="pink", \
            on_press=lambda a: self.create_departments_layout(layout, reset, save, delete, new)))
        save.add_widget(Button(text="GUARDAR", background_color="green", \
            on_press=lambda a: self.save(dpt_name.text, dpt_desc.text, dpt_code.text, fam_select.id, \
                iva_select.id, layout, reset, save, delete, new)))
        
        bottom_layout = GridLayout(cols=3, rows=2, spacing=40, row_force_default=True, row_default_height=40)

        box_code = BoxLayout(orientation="horizontal")
        box_code.add_widget(Label(text="Código:", size_hint=(.1, 1), text_size=box_code.size, \
            halign="left", valign="middle"))
        dpt_code = TextInput(hint_text="Código", size_hint=(.2, 1))
        box_code.add_widget(dpt_code)

        box_name = BoxLayout(orientation="horizontal")
        box_name.add_widget(Label(text="Nombre:", size_hint=(.05, 1), text_size=box_name.size, \
            halign="left", valign="middle"))
        dpt_name = TextInput(hint_text="Nombre", size_hint=(.1, 1))
        box_name.add_widget(dpt_name)

        box_desc = BoxLayout(orientation="horizontal")
        box_desc.add_widget(Label(text="Descripción:", size_hint=(.1, 1), text_size=box_desc.size, \
            halign="left", valign="middle"))
        dpt_desc = TextInput(hint_text="Descripción", size_hint=(.4, 1))
        box_desc.add_widget(dpt_desc)

        box_fam = BoxLayout(orientation="horizontal")
        box_fam.add_widget(Label(text="Familia:", size_hint=(.1, 1), text_size=box_fam.size, \
            halign="left", valign="middle"))
        fam_select = Button(text="Seleccionar familia", size_hint=(.15, 1), background_color="blue", \
            on_press=lambda a: self.select_family(a))
        fam_select.id = 0
        box_fam.add_widget(fam_select)
        box_fam.add_widget(Button(text="+", background_color="blue", size_hint=(.05, 1), \
            on_press=lambda a: self.create_family()))

        box_iva = BoxLayout(orientation="horizontal")
        box_iva.add_widget(Label(text="Tipo IVA:", size_hint=(.1, 1), text_size=box_iva.size, \
            halign="left", valign="middle"))
        iva_select = Button(text="Seleccionar tipo IVA", size_hint=(.2, 1), background_color="pink", \
            on_press=lambda a: self.select_iva(a))
        iva_select.id = 0
        box_iva.add_widget(iva_select)

        bottom_layout.add_widget(box_code)
        bottom_layout.add_widget(box_name)
        bottom_layout.add_widget(box_desc)
        bottom_layout.add_widget(box_fam)
        bottom_layout.add_widget(box_iva)

        layout.add_widget(bottom_layout)


    def select_family(self, select):
        families = session.query(Family).all()

        content_popup = BoxLayout(orientation="vertical", size_hint_y=None)
        content_popup.bind(minimum_height=content_popup.setter('height'))

        for fam in families:
            btn = Button(text=fam.name, height=70, size_hint_y=None, background_color="blue")
            btn.id = fam.id
            btn.bind(on_press=lambda a: self.change_family(a, select, popup))
            content_popup.add_widget(btn)

        scroll_content = ScrollView(size_hint=(1, 1))
        scroll_content.add_widget(content_popup)

        popup = Popup(title="Seleccionar familia", content=scroll_content, \
            size_hint=(None, None), size=(800, 600))
        popup.open()


    def change_family(self, button, select, popup):
        select.text = button.text
        select.id = button.id
        popup.dismiss()


    def select_iva(self, select):
        iva_types = session.query(Iva).all()

        content_popup = BoxLayout(orientation="vertical", size_hint_y=None)
        content_popup.bind(minimum_height=content_popup.setter('height'))

        for type in iva_types:
            if type.type >= 0:
                btn = Button(text=str(type.type) + "%", height=70, \
                    size_hint_y=None, background_color="pink")
                btn.id = type.id
                btn.bind(on_press=lambda a: self.change_iva(a, select, popup))
                content_popup.add_widget(btn)

        scroll_content = ScrollView(size_hint=(1, 1))
        scroll_content.add_widget(content_popup)

        popup = Popup(title="Seleccionar IVA", content=scroll_content, \
            size_hint=(None, None), size=(800, 400))
        popup.open()


    def change_iva(self, button, select, popup):
        select.id = button.id
        select.text = button.text

        popup.dismiss()


    def create_family(self):
        content_popup = BoxLayout(orientation="vertical", spacing=10)

        box_code = BoxLayout(orientation="horizontal", size_hint=(1, .05))
        box_code.add_widget(Label(text="Código:", size_hint=(.4, 1)))
        fam_code = TextInput(hint_text="Código")
        box_code.add_widget(fam_code)
        content_popup.add_widget(box_code)

        box_name = BoxLayout(orientation="horizontal", size_hint=(1, .05))
        box_name.add_widget(Label(text="Nombre:", size_hint=(.4, 1)))
        fam_name = TextInput(hint_text="Nombre")
        box_name.add_widget(fam_name)
        content_popup.add_widget(box_name)

        box_desc = BoxLayout(orientation="horizontal", size_hint=(1, .05))
        box_desc.add_widget(Label(text="Descripción:", size_hint=(.4, 1)))
        fam_desc = TextInput(hint_text="Descripción")
        box_desc.add_widget(fam_desc)
        content_popup.add_widget(box_desc)
        
        content_popup.add_widget(Button(text="Guardar", size_hint=(1, .05), \
            on_press=lambda a: self.save_family(fam_code.text, fam_name.text, fam_desc.text, popup), \
                background_color="green"))
        content_popup.add_widget(Button(text="Cancelar", size_hint=(1, .05), \
            on_press=lambda a: popup.dismiss(), background_color="red"))

        popup = Popup(title="Nueva familia", content=content_popup, size_hint=(None, None), \
            size=(800, 350))
        popup.open()


    def save_family(self, code, name, description, popup):
        code = code.replace(' ', '')
        
        if name != '':
            if code != '':
                if not session.query(Family).filter_by(code=code).first() and \
                    not session.query(Department).filter_by(code=code).first() and \
                        not session.query(Article).filter_by(code=code).first():
                    family = Family(name=name, description=description, code=code)
                    session.add(family)
                    session.commit()

                    popup.dismiss()
                else:
                    second_popup = Popup(title="ERROR", content=Label(text="El código ya está en uso"), \
                        size_hint=(None, None), size=(400, 200))
                    second_popup.open()
            else:
                code = ''.join(random.SystemRandom().choice(string.digits) for _ in range(4))
            
                while session.query(Family).filter_by(code=code).first() or \
                    session.query(Department).filter_by(code=code).first() or \
                        session.query(Article).filter_by(code=code).first():
                    code = ''.join(random.SystemRandom().choice(string.digits) for _ in range(4))
                
                family = Family(name=name, description=description, code=code)
                session.add(family)
                session.commit()

                popup.dismiss()
        else:
            second_popup = Popup(title="ERROR", content=Label(text="Introduce un nombre válido"), \
                size_hint=(None, None), size=(400, 200))
            second_popup.open()


    def popup_delete(self, id, layout, reset, save, delete, new):
        department = session.query(Department).filter_by(id=id).first()
            
        content = BoxLayout(orientation="vertical")
        content.add_widget(Label(text="Se eliminará el departamento {}".format(department.name), \
            height=50, size_hint_y=None))

        content_popup = BoxLayout(orientation="vertical", size_hint_y=None)
        content_popup.bind(minimum_height=content_popup.setter('height'))

        content_popup.add_widget(Label(text="Código: {}".format(department.code), height=50, size_hint_y=None))

        content_popup.add_widget(Label(text="Nombre: {}".format(department.name), height=50, size_hint_y=None))
            
        if department.description == None or department.description == '':
            content_popup.add_widget(Label(text="Descripción: Sin descripción", height=50, size_hint_y=None))
        else:
            content_popup.add_widget(Label(text="Descripción: {}".format(department.description), \
                height=50, size_hint_y=None))

        content_popup.add_widget(Label(text="Familia: {}".format(department.family.name), height=50, size_hint_y=None))

        content_popup.add_widget(Label(text="Tipo de IVA: {}%".format(department.iva.type), height=50, size_hint_y=None))
            
        dismiss_btn = Button(text="Cancelar", height=50, size_hint_y=None, background_color="orange")

        scroll_content = ScrollView(size_hint=(1, .8))
        scroll_content.add_widget(content_popup)
        content.add_widget(scroll_content)

        content.add_widget(Button(text="Confirmar", height=50, size_hint_y=None, background_color="red", \
            on_press=lambda a: self.delete(id, layout, reset, save, delete, new, popup)))
        content.add_widget(dismiss_btn)

        popup = Popup(title="AVISO", content=content, size_hint=(None, None), size=(600, 800))
        dismiss_btn.bind(on_press=popup.dismiss)
        popup.open()


    def delete(self, id, layout, reset, save, delete, new, popup):
        popup.dismiss()
        department = session.query(Department).filter_by(id=id).first()
        session.delete(department)

        self.create_departments_layout(layout, reset, save, delete, new)
        
        session.commit()


    def save(self, name, description, code, family_id, iva_id, layout, reset, save, delete, new):
        code = code.replace(' ', '')
        
        if name != '':
            if family_id > 0:
                if iva_id > 0:
                    if code != '':
                        if not session.query(Department).filter_by(code=code).first() and not \
                            session.query(Family).filter_by(code=code).first() and not \
                            session.query(Article).filter_by(code=code).first():
                            department = Department(name=name, description=description, code=code, \
                                family_id=family_id, iva_type=iva_id)
                            session.add(department)
                            session.commit()

                            self.create_departments_layout(layout, reset, save, delete, new)
                        else:
                            popup = Popup(title="ERROR", content=Label(text="El código ya está en uso"), \
                                size_hint=(None, None), size=(800, 200))
                            popup.open()
                    else:
                        code = ''.join(random.SystemRandom().choice(string.digits) for _ in range(4))
        
                        while session.query(Department).filter_by(code=code).first() or \
                            session.query(Family).filter_by(code=code).first() or \
                                session.query(Article).filter_by(code=code).first():
                            code = ''.join(random.SystemRandom().choice(string.digits) for _ in range(4))
                            
                        department = Department(name=name, description=description, code=code, \
                            family_id=family_id, iva_type=iva_id)
                        session.add(department)
                        session.commit()

                        self.create_departments_layout(layout, reset, save, delete, new)
                else:
                    popup = Popup(title="ERROR", content=Label(text="Selecciona un tipo de IVA"), \
                        size_hint=(None, None), size=(800, 200))
                    popup.open()
            else:
                popup = Popup(title="ERROR", content=Label(text="Selecciona una familia"), \
                    size_hint=(None, None), size=(800, 200))
                popup.open()
        else:
            popup = Popup(title="ERROR", content=Label(text="Introduce un nombre válido"), \
                size_hint=(None, None), size=(800, 200))
            popup.open()


    def modify(self, id, code, name, description, family_id, iva_id, layout, reset, save, delete, new):
        code = code.replace(' ', '')

        if name != '':
            if family_id > 0:
                if iva_id > 0:
                    department = session.query(Department).filter_by(id=id).first()
                    if code != '':
                        if department.code == code:
                            department.name = name
                            department.description = description
                            department.family_id = family_id
                            department.iva_type = iva_id

                            self.create_departments_layout(layout, reset, save, delete, new)

                            session.commit()
                        else:
                            if session.query(Family).filter_by(code=code).first() or \
                                session.query(Article).filter_by(code=code).first():
                                popup = Popup(title="ERROR", content=Label(text="El código ya está en uso"), \
                                    size_hint=(None, None), size=(800, 200))
                                popup.open()
                            else:
                                if session.query(Department).filter_by(code=code).first():
                                    popup = Popup(title="ERROR", content=Label(text="El código ya está en uso"), \
                                        size_hint=(None, None), size=(800, 200))
                                    popup.open()
                                else:
                                    department.code = code
                                    department.name = name
                                    department.description = description
                                    department.family_id = family_id
                                    department.iva_type = iva_id

                                    self.create_departments_layout(layout, reset, save, delete, new)

                                    session.commit()
                    else:
                        code = ''.join(random.SystemRandom().choice(string.digits) for _ in range(4))
        
                        while session.query(Department).filter_by(code=code).first() or \
                            session.query(Family).filter_by(code=code).first() or \
                                session.query(Article).filter_by(code=code).first():
                            code = ''.join(random.SystemRandom().choice(string.digits) for _ in range(4))

                        department.code = code
                        department.name = name
                        department.description = description
                        department.family_id = family_id
                        department.iva_type = iva_id

                        self.create_departments_layout(layout, reset, save, delete, new)

                        session.commit()
                else:
                    popup = Popup(title="ERROR", content=Label(text="Selecciona un tipo de IVA"), \
                        size_hint=(None, None), size=(800, 200))
                    popup.open()
            else:
                popup = Popup(title="ERROR", content=Label(text="Selecciona una familia"), \
                    size_hint=(None, None), size=(800, 200))
                popup.open()
        else:
            popup = Popup(title="ERROR", content=Label(text="Introduce un nombre válido"), \
                size_hint=(None, None), size=(800, 200))
            popup.open()


    def go_menu(self):
        self.manager.current = 'Options Screen'


    def __init__(self, **kw):
        super(DepartmentScreen, self).__init__(**kw)

        self.create_layout()


class ArticleScreen(Screen):
    def create_layout(self):
        layout = GridLayout(rows=2, padding=10, spacing=20)

        top_layout = GridLayout(cols=5, spacing=20, size_hint_x=None)
        top_layout.bind(minimum_width=top_layout.setter('width'))

        box_reset = BoxLayout(size_hint_x=None, width=250)
        box_save = BoxLayout(size_hint_x=None, width=250)
        box_delete = BoxLayout(size_hint_x=None, width=250)
        box_new = BoxLayout(size_hint_x=None, width=250)

        top_layout.add_widget(Button(text="MENÚ", background_color="brown", \
            on_press=lambda a: self.go_menu(), size_hint_x=None, width=250))
        box_new.add_widget(Button(text="NUEVO", background_color="brown", \
            on_press=lambda a: self.get_new(bottom_layout, box_reset, box_save, box_delete, box_new)))
        top_layout.add_widget(box_new)
        top_layout.add_widget(box_reset)
        top_layout.add_widget(box_save)
        top_layout.add_widget(box_delete)

        bottom_layout = GridLayout(cols=1)
        self.create_articles_layout(bottom_layout, box_reset, box_save, box_delete, box_new)
    
        top_scroll = ScrollView(size_hint=(1, .1))
        top_scroll.add_widget(top_layout)

        layout.add_widget(top_scroll)
        layout.add_widget(bottom_layout)

        self.add_widget(layout)
    

    def create_articles_layout(self, layout, reset, save, delete, new):
        layout.clear_widgets()
        
        reset.clear_widgets()
        save.clear_widgets()
        delete.clear_widgets()
        new.clear_widgets()

        new.add_widget(Button(text="NUEVO", background_color="brown", \
            on_press=lambda a: self.get_new(layout, reset, save, delete, new)))

        articles_layout = GridLayout(cols=3, spacing=10, size_hint_y=None)
        articles_layout.bind(minimum_height=articles_layout.setter('height'))

        articles_layout.add_widget(BoxLayout(size_hint=(.1, 1)))

        buttons_layout = GridLayout(cols=1, size_hint_y=None, spacing=10)
        buttons_layout.bind(minimum_height=buttons_layout.setter('height'))

        articles = session.query(Article).all()

        for art in articles:
            art_btn = Button(text=art.name, size_hint_y=None, height=100, background_color="pink", \
                on_press=lambda a: self.get_article(a.id, layout, reset, save, delete, new))
            art_btn.id = art.id
            buttons_layout.add_widget(art_btn)

        articles_layout.add_widget(buttons_layout)

        articles_layout.add_widget(BoxLayout(size_hint=(.1, 1)))
        
        scroll_bottom = ScrollView(size_hint=(1, .9))
        scroll_bottom.add_widget(articles_layout)

        layout.add_widget(scroll_bottom)
    

    def get_article(self, id, layout, reset, save, delete, new):
        article = session.query(Article).filter_by(id=id).first()
        
        layout.clear_widgets()
        new.clear_widgets()
        reset.clear_widgets()
        save.clear_widgets()
        delete.clear_widgets()

        reset.add_widget(Button(text="VOLVER", background_color="pink", \
            on_press=lambda a: self.create_articles_layout(layout, reset, save, delete, new)))
        save.add_widget(Button(text="GUARDAR", background_color="green", \
            on_press=lambda a: self.modify(id, art_code.text, art_name.text, art_desc.text, art_price.text, \
                dpt_select.id, iva_select.id, layout, reset, save, delete, new)))
        
        delete.add_widget(Button(text="ELIMINAR", background_color="red", \
            on_press=lambda a: self.popup_delete(id, layout, reset, save, delete, new)))

        bottom_layout = GridLayout(cols=3, rows=3, spacing=40, row_force_default=True, row_default_height=40)

        box_code = BoxLayout(orientation="horizontal")
        box_code.add_widget(Label(text="Código:", size_hint=(.1, 1), text_size=box_code.size, \
            halign="left", valign="middle"))
        art_code = TextInput(text=article.code, size_hint=(.2, 1))
        box_code.add_widget(art_code)

        box_name = BoxLayout(orientation="horizontal")
        box_name.add_widget(Label(text="Nombre:", size_hint=(.05, 1), text_size=box_name.size, \
            halign="left", valign="middle"))
        art_name = TextInput(text=article.name, size_hint=(.1, 1))
        box_name.add_widget(art_name)

        box_desc = BoxLayout(orientation="horizontal")
        box_desc.add_widget(Label(text="Descripción:", size_hint=(.1, 1), text_size=box_desc.size, \
            halign="left", valign="middle"))
        art_desc = TextInput(text=article.description, size_hint=(.4, 1))
        box_desc.add_widget(art_desc)

        box_fam = BoxLayout(orientation="horizontal")
        box_fam.add_widget(Label(text="Familia:", size_hint=(.1, 1), text_size=box_fam.size, \
            halign="left", valign="middle"))
        fam_select = Button(text=article.department.family.name, size_hint=(.15, 1), background_color="blue", \
            on_press=lambda a: self.select_family(a, dpt_select))
        fam_select.id = article.department.family.id
        box_fam.add_widget(fam_select)
        box_fam.add_widget(Button(text="+", background_color="blue", size_hint=(.05, 1), \
            on_press=lambda a: self.create_family()))

        box_iva = BoxLayout(orientation="horizontal")
        box_iva.add_widget(Label(text="Tipo IVA:", size_hint=(.1, 1), text_size=box_iva.size, \
            halign="left", valign="middle"))
        iva_select = Button(text="{}%".format(article.iva.type), size_hint=(.2, 1), background_color="pink", \
            on_press=lambda a: self.select_iva(a))
        if article.iva.type == -1:
            iva_select.text = "IVA del departamento: {}%".format(article.department.iva.type)
        iva_select.id = article.iva.id
        box_iva.add_widget(iva_select)

        box_price = BoxLayout(orientation="horizontal")
        box_price.add_widget(Label(text="Precio:", size_hint=(.05, 1), text_size=box_price.size, \
            halign="left", valign="middle"))
        art_price = TextInput(text=str(article.price), size_hint=(.2, 1))
        box_price.add_widget(art_price)

        box_dpt = BoxLayout(orientation="horizontal")
        box_dpt.add_widget(Label(text="Departamento:", size_hint=(.1, 1), text_size=box_dpt.size, \
            halign="left", valign="middle"))
        dpt_select = Button(text=article.department.name, size_hint=(.15, 1), background_color="orange", \
            on_press=lambda a: self.select_department(a, fam_select.id))
        dpt_select.id = article.department.id
        box_dpt.add_widget(dpt_select)
        box_dpt.add_widget(Button(text="+", background_color="orange", size_hint=(.05, 1), \
            on_press=lambda a: self.create_department()))


        bottom_layout.add_widget(box_code)
        bottom_layout.add_widget(box_name)
        bottom_layout.add_widget(box_desc)
        bottom_layout.add_widget(box_fam)
        bottom_layout.add_widget(box_iva)
        bottom_layout.add_widget(box_price)
        bottom_layout.add_widget(box_dpt)

        layout.add_widget(bottom_layout)


    def get_new(self, layout, reset, save, delete, new):
        layout.clear_widgets()
        new.clear_widgets()
        reset.clear_widgets()
        save.clear_widgets()
        delete.clear_widgets()

        reset.add_widget(Button(text="VOLVER", background_color="pink", \
            on_press=lambda a: self.create_articles_layout(layout, reset, save, delete, new)))
        save.add_widget(Button(text="GUARDAR", background_color="green", \
            on_press=lambda a: self.save(art_name.text, art_desc.text, art_price.text, art_code.text, dpt_select.id, \
                iva_select.id, layout, reset, save, delete, new)))
        
        bottom_layout = GridLayout(cols=3, rows=3, spacing=40, row_force_default=True, row_default_height=40)

        box_code = BoxLayout(orientation="horizontal")
        box_code.add_widget(Label(text="Código:", size_hint=(.1, 1), text_size=box_code.size, \
            halign="left", valign="middle"))
        art_code = TextInput(hint_text="Código", size_hint=(.2, 1))
        box_code.add_widget(art_code)

        box_name = BoxLayout(orientation="horizontal")
        box_name.add_widget(Label(text="Nombre:", size_hint=(.05, 1), text_size=box_name.size, \
            halign="left", valign="middle"))
        art_name = TextInput(hint_text="Nombre", size_hint=(.1, 1))
        box_name.add_widget(art_name)

        box_desc = BoxLayout(orientation="horizontal")
        box_desc.add_widget(Label(text="Descripción:", size_hint=(.1, 1), text_size=box_desc.size, \
            halign="left", valign="middle"))
        art_desc = TextInput(hint_text="Descripción", size_hint=(.4, 1))
        box_desc.add_widget(art_desc)

        box_fam = BoxLayout(orientation="horizontal")
        box_fam.add_widget(Label(text="Familia:", size_hint=(.1, 1), text_size=box_fam.size, \
            halign="left", valign="middle"))
        fam_select = Button(text="Seleccionar familia", size_hint=(.15, 1), background_color="blue", \
            on_press=lambda a: self.select_family(a, dpt_select))
        fam_select.id = 0
        box_fam.add_widget(fam_select)
        box_fam.add_widget(Button(text="+", background_color="blue", size_hint=(.05, 1), \
            on_press=lambda a: self.create_family()))

        box_iva = BoxLayout(orientation="horizontal")
        box_iva.add_widget(Label(text="Tipo IVA:", size_hint=(.1, 1), text_size=box_iva.size, \
            halign="left", valign="middle"))
        iva_select = Button(text="Seleccionar tipo IVA", size_hint=(.2, 1), background_color="pink", \
            on_press=lambda a: self.select_iva(a))
        iva_select.id = 0
        box_iva.add_widget(iva_select)

        box_price = BoxLayout(orientation="horizontal")
        box_price.add_widget(Label(text="Precio:", size_hint=(.05, 1), text_size=box_price.size, \
            halign="left", valign="middle"))
        art_price = TextInput(hint_text="Precio", size_hint=(.2, 1))
        box_price.add_widget(art_price)

        box_dpt = BoxLayout(orientation="horizontal")
        box_dpt.add_widget(Label(text="Departamento:", size_hint=(.1, 1), text_size=box_dpt.size, \
            halign="left", valign="middle"))
        dpt_select = Button(text="Seleccionar departamento", size_hint=(.15, 1), background_color="orange", \
            on_press=lambda a: self.select_department(a, fam_select.id))
        dpt_select.id = 0
        box_dpt.add_widget(dpt_select)
        box_dpt.add_widget(Button(text="+", background_color="orange", size_hint=(.05, 1), \
            on_press=lambda a: self.create_department()))

        bottom_layout.add_widget(box_code)
        bottom_layout.add_widget(box_name)
        bottom_layout.add_widget(box_desc)
        bottom_layout.add_widget(box_fam)
        bottom_layout.add_widget(box_iva)
        bottom_layout.add_widget(box_price)
        bottom_layout.add_widget(box_dpt)

        layout.add_widget(bottom_layout)


    def select_family(self, select, dpt_btn):
        families = session.query(Family).all()

        content_popup = BoxLayout(orientation="vertical", size_hint_y=None)
        content_popup.bind(minimum_height=content_popup.setter('height'))

        fam_count = 0
        for fam in families:
            btn = Button(text=fam.name, height=70, size_hint_y=None, background_color="blue")
            btn.id = fam.id
            btn.bind(on_press=lambda a: self.change_family(a, select, popup, dpt_btn))
            content_popup.add_widget(btn)
            fam_count += 1

        scroll_content = ScrollView(size_hint=(1, 1))
        scroll_content.add_widget(content_popup)

        if fam_count > 0:
            popup = Popup(title="Seleccionar familia", content=scroll_content, \
                size_hint=(None, None), size=(800, 400))
            popup.open()
        else:
            popup = Popup(title="Seleccionar familia", content=Label(text="No hay familias"), \
                size_hint=(None, None), size=(800, 200))
            popup.open()


    def change_family(self, button, select, popup, dpt_btn):
        if not dpt_btn is None:
            dpt_btn.text = "Seleccionar departamento"
            dpt_btn.id = 0
        
        select.text = button.text
        select.id = button.id
        popup.dismiss()


    def select_department(self, select, family_id):
        if family_id > 0:
            departments = session.query(Department).filter_by(family_id=family_id).all()

            content_popup = BoxLayout(orientation="vertical", size_hint_y=None)
            content_popup.bind(minimum_height=content_popup.setter('height'))

            dpt_count = 0
            for dpt in departments:
                btn = Button(text=dpt.name, height=70, size_hint_y=None, background_color="orange")
                btn.id = dpt.id
                btn.bind(on_press=lambda a: self.change_department(a, select, popup))
                content_popup.add_widget(btn)
                dpt_count += 1

            scroll_content = ScrollView(size_hint=(1, 1))
            scroll_content.add_widget(content_popup)

            if dpt_count > 0:
                popup = Popup(title="Seleccionar departamento", content=scroll_content, \
                    size_hint=(None, None), size=(800, 400))
                popup.open()
            else:
                popup = Popup(title="AVISO", content=Label(text="No hay departamentos"), \
                    size_hint=(None, None), size=(800, 200))
                popup.open()
        else:
            popup = Popup(title="ERROR", content=Label(text="Selecciona una familia"), \
                size_hint=(None, None), size=(800, 200))
            popup.open()


    def change_department(self, button, select, popup):
        select.text = button.text
        select.id = button.id
        popup.dismiss()


    def select_iva(self, select):
        iva_types = session.query(Iva).all()

        content_popup = BoxLayout(orientation="vertical", size_hint_y=None)
        content_popup.bind(minimum_height=content_popup.setter('height'))

        for type in iva_types:
            btn = Button(text=str(type.type) + "%", height=70, \
                size_hint_y=None, background_color="pink")
            if type.type == -1:
                btn.text = "IVA del departamento"
            btn.id = type.id
            btn.bind(on_press=lambda a: self.change_iva(a, select, popup))
            content_popup.add_widget(btn)

        scroll_content = ScrollView(size_hint=(1, 1))
        scroll_content.add_widget(content_popup)

        popup = Popup(title="Seleccionar IVA", content=scroll_content, \
            size_hint=(None, None), size=(800, 400))
        popup.open()


    def change_iva(self, button, select, popup):
        select.id = button.id
        select.text = button.text

        popup.dismiss()


    def create_family(self):
        content_popup = BoxLayout(orientation="vertical", spacing=10)

        box_code = BoxLayout(orientation="horizontal", size_hint=(1, .05))
        box_code.add_widget(Label(text="Código:", size_hint=(.4, 1)))
        fam_code = TextInput(hint_text="Código")
        box_code.add_widget(fam_code)
        content_popup.add_widget(box_code)

        box_name = BoxLayout(orientation="horizontal", size_hint=(1, .05))
        box_name.add_widget(Label(text="Nombre:", size_hint=(.4, 1)))
        fam_name = TextInput(hint_text="Nombre")
        box_name.add_widget(fam_name)
        content_popup.add_widget(box_name)

        box_desc = BoxLayout(orientation="horizontal", size_hint=(1, .05))
        box_desc.add_widget(Label(text="Descripción:", size_hint=(.4, 1)))
        fam_desc = TextInput(hint_text="Descripción")
        box_desc.add_widget(fam_desc)
        content_popup.add_widget(box_desc)
        
        content_popup.add_widget(Button(text="Guardar", size_hint=(1, .05), \
            on_press=lambda a: self.save_family(fam_code.text, fam_name.text, fam_desc.text, popup), \
                background_color="green"))
        content_popup.add_widget(Button(text="Cancelar", size_hint=(1, .05), \
            on_press=lambda a: popup.dismiss(), background_color="red"))

        popup = Popup(title="Nueva familia", content=content_popup, size_hint=(None, None), \
            size=(800, 350))
        popup.open()


    def save_family(self, code, name, description, popup):
        code = code.replace(' ', '')
        
        if name != '':
            if code != '':
                if not session.query(Family).filter_by(code=code).first() and \
                    not session.query(Department).filter_by(code=code).first() and \
                        not session.query(Article).filter_by(code=code).first():
                    family = Family(name=name, description=description, code=code)
                    session.add(family)
                    session.commit()

                    popup.dismiss()
                else:
                    second_popup = Popup(title="ERROR", content=Label(text="El código ya está en uso"), \
                        size_hint=(None, None), size=(400, 200))
                    second_popup.open()
            else:
                code = ''.join(random.SystemRandom().choice(string.digits) for _ in range(4))
            
                while session.query(Family).filter_by(code=code).first() or \
                    session.query(Department).filter_by(code=code).first() or \
                        session.query(Article).filter_by(code=code).first():
                    code = ''.join(random.SystemRandom().choice(string.digits) for _ in range(4))
                
                family = Family(name=name, description=description, code=code)
                session.add(family)
                session.commit()

                popup.dismiss()
        else:
            second_popup = Popup(title="ERROR", content=Label(text="Introduce un nombre válido"), \
                size_hint=(None, None), size=(400, 200))
            second_popup.open()


    def create_department(self):
        content_popup = BoxLayout(orientation="vertical", spacing=10)

        box_code = BoxLayout(orientation="horizontal", size_hint=(1, .05))
        box_code.add_widget(Label(text="Nombre:", size_hint=(.4, 1)))
        dpt_code = TextInput(hint_text="Código")
        box_code.add_widget(dpt_code)
        content_popup.add_widget(box_code)

        box_name = BoxLayout(orientation="horizontal", size_hint=(1, .05))
        box_name.add_widget(Label(text="Nombre:", size_hint=(.4, 1)))
        dpt_name = TextInput(hint_text="Nombre")
        box_name.add_widget(dpt_name)
        content_popup.add_widget(box_name)

        box_desc = BoxLayout(orientation="horizontal", size_hint=(1, .05))
        box_desc.add_widget(Label(text="Descripción:", size_hint=(.4, 1)))
        dpt_desc = TextInput(hint_text="Descripción")
        box_desc.add_widget(dpt_desc)
        content_popup.add_widget(box_desc)

        box_iva = BoxLayout(orientation="horizontal", size_hint=(1, .05))
        box_iva.add_widget(Label(text="Tipo IVA:", size_hint=(.4, 1)))
        iva_select = Button(text="Seleccionar IVA", on_press=lambda a: self.select_iva(a), \
            background_color="pink")
        iva_select.id = 0
        box_iva.add_widget(iva_select)
        content_popup.add_widget(box_iva)

        box_fam = BoxLayout(orientation="horizontal", size_hint=(1, .05))
        box_fam.add_widget(Label(text="Familia:", size_hint=(.4, 1)))
        fam_select = Button(text="Seleccionar familia", on_press=lambda a: self.select_family(a, None), \
            background_color="blue")
        fam_select.id = 0
        box_fam.add_widget(fam_select)
        content_popup.add_widget(box_fam)

        content_popup.add_widget(Button(text="GUARDAR", size_hint=(1, .05), \
            on_press=lambda a: self.save_department(dpt_code.text, dpt_name.text, dpt_desc.text, fam_select.id, \
                iva_select.id, popup), background_color="green"))

        content_popup.add_widget(Button(text="Cancelar", size_hint=(1, .05), background_color="red", \
            on_press=lambda a: popup.dismiss()))
        
        popup = Popup(title="Nuevo departamento", content=content_popup, size_hint=(None, None), size=(800, 500))
        popup.open()


    def save_department(self, code, name, description, family_id, iva_id, popup):
        code = code.replace(' ', '')
        
        if name != '':
            if family_id > 0:
                if iva_id > 0:
                    if code != '':
                        if not session.query(Department).filter_by(code=code).first() and not \
                            session.query(Family).filter_by(code=code).first() and not \
                            session.query(Article).filter_by(code=code).first():
                            department = Department(name=name, description=description, code=code, \
                                family_id=family_id, iva_type=iva_id)
                            session.add(department)
                            session.commit()

                            popup.dismiss()

                        else:
                            second_popup = Popup(title="ERROR", content=Label(text="El código ya está en uso"), \
                                size_hint=(None, None), size=(800, 200))
                            second_popup.open()
                    else:
                        code = ''.join(random.SystemRandom().choice(string.digits) for _ in range(4))
        
                        while session.query(Department).filter_by(code=code).first() or \
                            session.query(Family).filter_by(code=code).first() or \
                                session.query(Article).filter_by(code=code).first():
                            code = ''.join(random.SystemRandom().choice(string.digits) for _ in range(4))
                            
                        department = Department(name=name, description=description, code=code, \
                            family_id=family_id, iva_type=iva_id)
                        session.add(department)
                        session.commit()

                        popup.dismiss()

                else:
                    second_popup = Popup(title="ERROR", content=Label(text="Selecciona un tipo de IVA"), \
                        size_hint=(None, None), size=(800, 200))
                    second_popup.open()
            else:
                second_popup = Popup(title="ERROR", content=Label(text="Selecciona una familia"), \
                    size_hint=(None, None), size=(800, 200))
                second_popup.open()
        else:
            second_popup = Popup(title="ERROR", content=Label(text="Introduce un nombre válido"), \
                size_hint=(None, None), size=(800, 200))
            second_popup.open()


    def popup_delete(self, id, layout, reset, save, delete, new):
        article = session.query(Article).filter_by(id=id).first()

        content = BoxLayout(orientation="vertical")
        content.add_widget(Label(text="Se eliminará el artículo {}".format(article.name), \
            size_hint_y=None, height=50))

        content_popup = BoxLayout(orientation="vertical", size_hint_y=None)
        content_popup.bind(minimum_height=content_popup.setter('height'))

        content_popup.add_widget(Label(text="Código: {}".format(article.code), size_hint_y=None, height=50))

        content_popup.add_widget(Label(text="Nombre: {}".format(article.name), size_hint_y=None, height=50))
        
        if article.description == None or article.description == '':
            content_popup.add_widget(Label(text="Descripción: Sin descripción", size_hint_y=None, height=50))
        else:
            content_popup.add_widget(Label(text="Descripción: {}".format(article.description), \
                size_hint_y=None, height=50))

        content_popup.add_widget(Label(text="Precio: {}".format(article.price), \
            size_hint_y=None, height=50))
        
        if article.iva.type == -1:
            content_popup.add_widget(Label(text="Tipo de IVA: IVA del departamento: {}%"\
                .format(article.department.iva.type), size_hint_y=None, height=50))
        else:
            content_popup.add_widget(Label(text="Tipo de IVA: {}%".format(article.iva.type), \
                size_hint_y=None, height=50))

        content_popup.add_widget(Label(text="Departamento: {}".format(article.department.name), \
            size_hint_y=None, height=50))

        content_popup.add_widget(Label(text="Familia: {}".format(article.department.family.name), \
            size_hint_y=None, height=50))

        scroll_content = ScrollView(size_hint=(1, 1))
        scroll_content.add_widget(content_popup)

        content.add_widget(scroll_content)

        content.add_widget(Button(text="Confirmar", height=50, size_hint_y=None, background_color="red", \
            on_press=lambda a: self.delete(id, layout, reset, save, delete, new, popup)))
        dismiss_btn = Button(text="Cancelar", height=50, size_hint_y=None, background_color="orange")
        content.add_widget(dismiss_btn)

        popup = Popup(title="AVISO", content=content, size_hint=(None, None), size=(600, 800))
        dismiss_btn.bind(on_press=popup.dismiss)
        popup.open()


    def delete(self, id, layout, reset, save, delete, new, popup):
        popup.dismiss()
        article = session.query(Article).filter_by(id=id).first()
        session.delete(article)

        self.create_articles_layout(layout, reset, save, delete, new)
        
        session.commit()


    def save(self, name, description, price, code, department_id, iva_id, layout, reset, save, delete, new):
        code = code.replace(' ', '')

        if name != '':
            if code != '':
                if not session.query(Department).filter_by(code=code).first() and not \
                        session.query(Family).filter_by(code=code).first() and not \
                        session.query(Article).filter_by(code=code).first():
                    article = Article(name=name, description=description, price=price, code=code, \
                        department_id=department_id, iva_type=iva_id)
                    
                    session.add(article)
                    session.commit()

                    self.create_articles_layout(layout, reset, save, delete, new)
                else:
                    popup = Popup(title="ERROR", content=Label(text="El código ya está en uso"), \
                        size_hint=(None, None), size=(800, 200))
                    popup.open()
            else:
                code = ''.join(random.SystemRandom().choice(string.digits) for _ in range(4))
        
                while session.query(Department).filter_by(code=code).first() or \
                        session.query(Family).filter_by(code=code).first() or \
                        session.query(Article).filter_by(code=code).first():
                    code = ''.join(random.SystemRandom().choice(string.digits) for _ in range(4))
                            
                article = Article(name=name, description=description, price=price, code=code, \
                    department_id=department_id, iva_type=iva_id)
                    
                session.add(article)
                session.commit()

                self.create_articles_layout(layout, reset, save, delete, new)
        else:
            popup = Popup(title="ERROR", content=Label(text="Introduce un nombre válido"), \
                size_hint=(None, None), size=(400, 100))
            popup.open()


    def modify(self, id, code, name, description, price, department_id, iva_id, layout, reset, save, delete, new):
        code = code.replace(' ', '')

        if name != '':
            if department_id > 0:
                if iva_id > 0:
                    try:
                        if float(price) >= 0:
                            article = session.query(Article).filter_by(id=id).first()
                            if code != '':
                                if article.code == code:
                                    article.name = name
                                    article.description = description
                                    article.department_id = department_id
                                    article.iva_type = iva_id
                                    article.price = price

                                    self.create_articles_layout(layout, reset, save, delete, new)

                                    session.commit()
                                else:
                                    if session.query(Family).filter_by(code=code).first() or \
                                        session.query(Department).filter_by(code=code).first():
                                        popup = Popup(title="ERROR", content=Label(text="El código ya está en uso"), \
                                            size_hint=(None, None), size=(800, 200))
                                        popup.open()
                                    else:
                                        if session.query(Article).filter_by(code=code).first():
                                            popup = Popup(title="ERROR", content=Label(text="El código ya está en uso"), \
                                                size_hint=(None, None), size=(800, 200))
                                            popup.open()
                                        else:
                                            article.code = code
                                            article.name = name
                                            article.description = description
                                            article.department_id = department_id
                                            article.iva_type = iva_id
                                            article.price = price

                                            self.create_articles_layout(layout, reset, save, delete, new)

                                            session.commit()
                            else:
                                code = ''.join(random.SystemRandom().choice(string.digits) for _ in range(4))
                
                                while session.query(Department).filter_by(code=code).first() or \
                                    session.query(Family).filter_by(code=code).first() or \
                                        session.query(Article).filter_by(code=code).first():
                                    code = ''.join(random.SystemRandom().choice(string.digits) for _ in range(4))

                                article.code = code
                                article.name = name
                                article.description = description
                                article.department_id = department_id
                                article.iva_type = iva_id
                                article.price = price

                                self.create_articles_layout(layout, reset, save, delete, new)

                                session.commit()
                    except:
                        popup = Popup(title="ERROR", content=Label(text="Introduce un precio válido"), \
                            size_hint=(None, None), size=(800, 200))
                        popup.open()
                else:
                    popup = Popup(title="ERROR", content=Label(text="Selecciona un tipo de IVA"), \
                        size_hint=(None, None), size=(800, 200))
                    popup.open()
            else:
                popup = Popup(title="ERROR", content=Label(text="Selecciona un departamento"), \
                    size_hint=(None, None), size=(800, 200))
                popup.open()
        else:
            popup = Popup(title="ERROR", content=Label(text="Introduce un nombre válido"), \
                size_hint=(None, None), size=(800, 200))
            popup.open()


    def go_menu(self):
        self.manager.current = 'Options Screen'


    def __init__(self, **kw):
        super(ArticleScreen, self).__init__(**kw)

        self.create_layout()


class MainApp(App):
    def build(self):
        root = ScreenManager()
        root.transition = NoTransition()
        
        root.add_widget(LoginScreen(name="Login Screen"))
        root.add_widget(MainScreen(name="Main Screen"))
        root.add_widget(OptionsScreen(name="Options Screen"))

        return root
        
    
    def __init__(self, **kwargs):
        super(MainApp, self).__init__(**kwargs)


if __name__ == '__main__':
    create_db()
    
    MainApp().run()
