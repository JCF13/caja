from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import NoTransition, Screen, ScreenManager
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
import string
import random

from sqlalchemy.sql.expression import desc

from db import Article, Department, Family, Iva, User, create_db, session


class FamilyScreen(Screen):
    def create_layout(self):
        layout = GridLayout(rows=2, padding=20, spacing=20)

        top_layout = GridLayout(cols=7, height=50, spacing=20, size_hint_x=None)
        top_layout.bind(minimum_width=top_layout.setter('width'))
        
        fam_select = Button(text="Modificar", size_hint_x=None, width=200, background_color="brown", \
            on_press=lambda a: self.select_family(a, fam_name, fam_desc, save_btn, fam_code, box_delete))
        fam_select.id = 0
        top_layout.add_widget(fam_select)
        top_layout.add_widget(Button(size_hint_x=None, width=200, background_color="brown"))
        top_layout.add_widget(Button(size_hint_x=None, width=200, background_color="brown"))
        top_layout.add_widget(Button(size_hint_x=None, width=200, background_color="brown"))
        top_layout.add_widget(Button(size_hint_x=None, width=200, background_color="brown"))
        top_layout.add_widget(Button(size_hint_x=None, width=200, background_color="brown"))
        top_layout.add_widget(Button(text="MENÚ PRINCIPAL", size_hint_x=None, width=200, background_color="brown", \
            on_press=lambda a: self.go_menu()))

        bottom_layout = GridLayout(cols=1, rows=5, spacing=40, row_force_default=True, row_default_height=40)

        box_code = BoxLayout(orientation="horizontal")
        box_code.add_widget(Label(text="Código:", size_hint=(.1, 1), text_size=box_code.size, \
            halign="left", valign="middle"))
        fam_code = TextInput(hint_text="Vacío para crear una nueva familia")
        box_code.add_widget(fam_code)

        box_name = BoxLayout(orientation="horizontal")
        box_name.add_widget(Label(text="Nombre: *", size_hint=(.1, 1), text_size=box_name.size, \
            halign="left", valign="middle"))
        fam_name = TextInput(hint_text="Nombre")
        box_name.add_widget(fam_name)

        box_desc = BoxLayout(orientation="horizontal")
        box_desc.add_widget(Label(text="Descripción:", size_hint=(.1, 1), text_size=box_desc.size, \
            halign="left", valign="middle"))
        fam_desc = TextInput(hint_text="Descripción")
        box_desc.add_widget(fam_desc)

        box_save = BoxLayout()
        save_btn = Button(text="GUARDAR", size_hint=(.6, 1), background_color="green")
        save_btn.bind(on_press=lambda a: self.modify(fam_select.id, fam_name.text, fam_desc.text, fam_code.text))
        box_save.add_widget(save_btn)

        box_delete = BoxLayout()
        
        bottom_layout.add_widget(box_code)
        bottom_layout.add_widget(box_name)
        bottom_layout.add_widget(box_desc)
        bottom_layout.add_widget(box_save)
        bottom_layout.add_widget(box_delete)

        top_scroll = ScrollView(size_hint=(1, .1))
        top_scroll.add_widget(top_layout)

        layout.add_widget(top_scroll)
        layout.add_widget(bottom_layout)

        self.add_widget(layout)
        
        
    def select_family(self, select, name, description, save_btn, code, box_delete):
        if select.text == "Modificar":
            families = session.query(Family).all()

            content_popup = BoxLayout(orientation="vertical", size_hint_y=None)
            content_popup.bind(minimum_height=content_popup.setter('height'))

            fam_count = 0
            for fam in families:
                btn = Button(text=fam.name, height=50, size_hint_y=None, background_color="blue")
                btn.id = fam.id
                btn.bind(on_press=lambda a: self.change_family(a, select, popup, name, description, \
                    save_btn, code, box_delete))
                content_popup.add_widget(btn)
                fam_count += 1

            scroll_content = ScrollView(size_hint=(1, 1))
            scroll_content.add_widget(content_popup)

            if fam_count > 0:
                popup = Popup(title="Seleccionar familia", content=scroll_content, \
                    size_hint=(None, None), size=(600, 600))
                popup.open()
            else:
                popup = Popup(title="AVISO", content=Label(text="No hay familias"), \
                    size_hint=(None, None), size=(400, 100))
                popup.open()
        else:
            select.text = "Modificar"
            select.id = 0
            name.text = ""
            code.text = ""
            description.text = ""
            box_delete.clear_widgets()


    def change_family(self, button, select, popup, name, description, save_btn, code, box_delete):
        family = session.query(Family).filter_by(id=button.id).first()
        select.id = button.id
        select.text = button.text

        name.text = family.name
        description.text = family.description
        code.text = family.code

        box_delete.add_widget(Button(text="Eliminar familia {}".format(family.name), size_hint=(.3, 1), \
            background_color="red", on_press=lambda a: self.popup_delete(family.id)))
        
        popup.dismiss()


    def popup_delete(self, id):
        if id > 0:
            family = session.query(Family).filter_by(id=id).first()
            
            content = BoxLayout(orientation="vertical")
            content.add_widget(Label(text="Se eliminará la familia {}".format(family.name), \
                height=50, size_hint_y=None))
            content.add_widget(Button(text="Confirmar", on_press=lambda a: self.delete(id, popup), \
                height=50, size_hint_y=None, background_color="red"))

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
            content.add_widget(dismiss_btn)

            scroll_content = ScrollView(size_hint=(1, .8))
            scroll_content.add_widget(content_popup)
            content.add_widget(scroll_content)

            popup = Popup(title="AVISO", content=content, size_hint=(None, None), size=(600, 800))
            dismiss_btn.bind(on_press=popup.dismiss)
            popup.open()
        else:
            popup = Popup(title="ERROR", content=Label(text="Selecciona una familia"), size_hint=(None, None), \
                size=(400, 100))
            popup.open()


    def dismiss_modify(self, id, name, description, code, popup):
        popup.dismiss()

        return self.modify(id, name, description, code)
    
    
    def modify(self, id, name, description, code):
        if code is None:
            code = ''.join(random.SystemRandom().choice(string.digits) for _ in range(4))
            
            while session.query(Family).filter_by(code=code).first():
                code = ''.join(random.SystemRandom().choice(string.digits) for _ in range(4))
            
            family = session.query(Family).filter_by(id=id).first()
            family.name = name
            family.description = description
            family.code = code
            session.commit()

            popup = Popup(title="AVISO", content=Label(text="Se ha modificado la familia correctamente"), \
                size_hint=(None, None), size=(400, 100))
            popup.open()

            self.manager.current = "Options Screen"
        
        elif name != '':
            if code != '':
                exists_family = session.query(Family).filter_by(id=id).first()

                if exists_family:
                    same_family = session.query(Family).filter_by(code=code).first()

                    if same_family:
                        if same_family.name == exists_family.name:
                            family = session.query(Family).filter_by(id=id).first()
                            family.name = name
                            family.description = description
                            session.commit()

                            popup = Popup(title="AVISO", content=Label(text="Se ha modificado la familia correctamente"), \
                                size_hint=(None, None), size=(400, 100))
                            popup.open()

                            self.manager.current = "Options Screen"
                        else:
                            popup = Popup(title="ERROR", content=Label(text="El código ya está en uso"), \
                                size_hint=(None, None), size=(400, 100))
                            popup.open()
                    else:
                        family = session.query(Family).filter_by(id=id).first()
                        family.name = name
                        family.description = description
                        family.code = code
                        session.commit()

                        popup = Popup(title="AVISO", content=Label(text="Se ha modificado la familia correctamente"), \
                            size_hint=(None, None), size=(400, 100))
                        popup.open()

                        self.manager.current = "Options Screen"

                else:
                    popup = Popup(title="ERROR", content=Label(text="La familia no existe"), \
                        size_hint=(None, None), size=(400, 100))
                    popup.open()
            else:
                if id > 0:
                    content_popup = BoxLayout(orientation="vertical")
                    content_popup.add_widget(Label(text="Se modificará la familia con un código nuevo"))
                    content_popup.add_widget(Button(text="Confirmar", size_hint=(1, .5), \
                        on_press=lambda a: self.dismiss_modify(id, name, description, None, popup)))
                    
                    popup = Popup(title="AVISO", content=content_popup, size_hint=(None, None), size=(400, 200))
                    popup.open()
                else:
                    self.save(name, description)
        else:
            popup = Popup(title="ERROR", content=Label(text="Introduce un nombre válido"), \
                size_hint=(None, None), size=(400, 100))
            popup.open()
  

    def save(self, name, description):
        if name != '':
            code = ''.join(random.SystemRandom().choice(string.digits) for _ in range(4))
            
            while session.query(Family).filter_by(code=code).first():
                code = ''.join(random.SystemRandom().choice(string.digits) for _ in range(4))
            
            new_family = Family(name=name, description=description, code=code)
            session.add(new_family)
            session.commit()

            popup = Popup(title="AVISO", content=Label(text="Se ha añadido la familia correctamente"), \
                size_hint=(None, None), size=(400, 100))
            popup.open()

            self.manager.current = "Options Screen"

        else:
            popup = Popup(title="ERROR", content=Label(text="Introduce un nombre válido"), \
                size_hint=(None, None), size=(400, 200))
            popup.open()

    
    def delete(self, id, popup):
        family = session.query(Family).filter_by(id=id).first()
        session.delete(family)
        session.commit()

        popup.dismiss()

        second_popup = Popup(title="AVISO", content=Label(text="Se ha eliminado la familia correctamente"), \
            size_hint=(None, None), size=(400, 100))
        second_popup.open()
        
        self.manager.current = 'Options Screen'


    def go_menu(self):
        self.manager.current = "Options Screen"

    
    def __init__(self, **kw):
        super(FamilyScreen, self).__init__(**kw)

        self.create_layout()


class DepartmentScreen(Screen):
    def create_layout(self):
        layout = GridLayout(rows=2, padding=20, spacing=20)

        top_layout = GridLayout(cols=7, height=50, spacing=20, size_hint_x=None)
        top_layout.bind(minimum_width=top_layout.setter('width'))
        
        fam_select = Button(text="Modificar", size_hint_x=None, width=200, background_color="brown", \
            on_press=lambda a: self.select_family(a, dpt_name, dpt_desc, save_btn, dpt_code, box_delete))
        fam_select.id = 0
        top_layout.add_widget(fam_select)
        top_layout.add_widget(Button(size_hint_x=None, width=200, background_color="brown"))
        top_layout.add_widget(Button(size_hint_x=None, width=200, background_color="brown"))
        top_layout.add_widget(Button(size_hint_x=None, width=200, background_color="brown"))
        top_layout.add_widget(Button(size_hint_x=None, width=200, background_color="brown"))
        top_layout.add_widget(Button(size_hint_x=None, width=200, background_color="brown"))
        top_layout.add_widget(Button(text="MENÚ PRINCIPAL", size_hint_x=None, width=200, background_color="brown", \
            on_press=lambda a: self.go_menu()))

        bottom_layout = GridLayout(cols=1, rows=6, spacing=40, row_force_default=True, row_default_height=40)

        box_code = BoxLayout(orientation="horizontal")
        box_code.add_widget(Label(text="Código:", size_hint=(.1, 1), text_size=box_code.size, \
            halign="left", valign="middle"))
        dpt_code = TextInput(hint_text="Vacío para crear un nuevo departamento")
        box_code.add_widget(dpt_code)

        box_name = BoxLayout(orientation="horizontal")
        box_name.add_widget(Label(text="Nombre: *", size_hint=(.1, 1), text_size=box_name.size, \
            halign="left", valign="middle"))
        dpt_name = TextInput(hint_text="Nombre")
        box_name.add_widget(dpt_name)

        box_desc = BoxLayout(orientation="horizontal")
        box_desc.add_widget(Label(text="Descripción:", size_hint=(.1, 1), text_size=box_desc.size, \
            halign="left", valign="middle"))
        dpt_desc = TextInput(hint_text="Descripción")
        box_desc.add_widget(dpt_desc)

        box_family = BoxLayout(orientation="horizontal")
        box_family.add_widget(Label(text="Familia:", size_hint=(.1, 1), text_size=box_family.size, \
            halign="left", valign="middle"))
        family_select = Button(text="Seleccionar familia", background_color="blue", \
            on_press=lambda a: self.select_family(a))
        box_family.add_widget(family_select)


        box_save = BoxLayout()
        save_btn = Button(text="GUARDAR", size_hint=(.6, 1), background_color="green")
        save_btn.bind(on_press=lambda a: self.modify(fam_select.id, dpt_name.text, dpt_desc.text, dpt_code.text))
        box_save.add_widget(save_btn)

        box_delete = BoxLayout()
        
        bottom_layout.add_widget(box_code)
        bottom_layout.add_widget(box_name)
        bottom_layout.add_widget(box_desc)
        bottom_layout.add_widget(box_family)
        bottom_layout.add_widget(box_save)
        bottom_layout.add_widget(box_delete)

        top_scroll = ScrollView(size_hint=(1, .1))
        top_scroll.add_widget(top_layout)

        layout.add_widget(top_scroll)
        layout.add_widget(bottom_layout)

        self.add_widget(layout)


    def select_family(self, select):
        families = session.query(Family).all()

        content_popup = BoxLayout(orientation="vertical", size_hint_y=None)
        content_popup.bind(minimum_height=content_popup.setter('height'))

        for fam in families:
            btn = Button(text=fam.name, height=50, size_hint_y=None, background_color="blue")
            btn.id = fam.id
            btn.bind(on_press=lambda a: self.change_family(a, select, popup))
            content_popup.add_widget(btn)

        scroll_content = ScrollView(size_hint=(1, 1))
        scroll_content.add_widget(content_popup)

        popup = Popup(title="Seleccionar familia", content=scroll_content, \
            size_hint=(None, None), size=(400, 300))
        popup.open()


    def change_family(self, button, select, popup):
        select.text = button.text
        select.id = button.id
        popup.dismiss()


    def create_family(self):
        content_popup = BoxLayout(orientation="vertical")
        content_popup.add_widget(Label(text="Nombre:", size_hint=(1, .2)))
        fam_name = TextInput(hint_text="Nombre", size_hint=(1, .1))
        content_popup.add_widget(fam_name)
        content_popup.add_widget(Label(text="Descripción:", size_hint=(1, .2)))
        fam_desc = TextInput(hint_text="Descripción", size_hint=(1, .2))
        content_popup.add_widget(fam_desc)
        content_popup.add_widget(Button(text="Guardar", size_hint=(1, .1), \
            on_press=lambda a: self.save_family(fam_name.text, fam_desc.text, popup), \
                background_color="green"))
        content_popup.add_widget(Button(text="Cancelar", size_hint=(1, .1), \
            on_press=lambda a: popup.dismiss(), background_color="red"))

        popup = Popup(title="Nueva familia", content=content_popup, size_hint=(None, None), \
            size=(400, 500))
        popup.open()


    def go_menu(self):
        self.manager.current = "Options Screen"


    def __init__(self, **kw):
        super(DepartmentScreen, self).__init__(**kw)

        self.create_layout()


class NewDepartmentScreen(Screen):
    def create_layout(self):
        layout = GridLayout(cols=2)

        left_layout = FloatLayout()

        left_layout.add_widget(Label(text="Nombre:", size_hint=(.3, .1), pos_hint={'top':.9}))
        department_name = TextInput(hint_text="Nombre", size_hint=(.5, .1), pos_hint={'top':.8, 'right':.55})
        left_layout.add_widget(department_name)

        left_layout.add_widget(Label(text="Descripción:", size_hint=(.3, .1), pos_hint={'top':.7}))
        department_desc = TextInput(hint_text="Descripción", size_hint=(.7, .2), pos_hint={'top':.6, 'right':.75})
        left_layout.add_widget(department_desc)

        left_layout.add_widget(Label(text="Tipo de IVA:", size_hint=(.2, .1), pos_hint={'top':.9, 'right':.9}))

        iva_button = Button(text="Seleccionar IVA", size_hint=(.4, .1), pos_hint={'top':.8, 'right':1}, \
            background_color="pink", on_press=lambda a: self.select_iva(iva_button))
        iva_button.id = -1
        left_layout.add_widget(iva_button)

        left_layout.add_widget(Label(text="Familia:", size_hint=(.2, .1), pos_hint={'top':.4}))
        
        family_button = Button(text="Seleccionar familia", size_hint=(.4, .1), pos_hint={'top':.3, 'right':.45}, \
            background_color="blue", on_press=lambda a: self.select_family(a))
        family_button.id = 0
        
        left_layout.add_widget(family_button)
        
        left_layout.add_widget(Button(text="Nueva", size_hint=(.2, .1), pos_hint={'top':.3, 'right':.7}, \
            background_color="blue", on_press=lambda a: self.create_family()))

        left_layout.add_widget(Button(text="AÑADIR", size_hint=(.3, .1), pos_hint={'top':.15, 'right':.4}, \
            on_press=lambda a: self.save(department_name.text, department_desc.text, \
                family_button.id, iva_button.id), background_color="green"))
        
        right_layout = FloatLayout()

        right_layout.add_widget(Label(text="NUEVO DEPARTAMENTO", size_hint=(.2, .1), pos_hint={'top':1, 'right':.5}))
        
        right_layout.add_widget(Button(text="MENÚ", size_hint=(.3, .1), pos_hint={'top':1, 'right':1}, \
            background_color="brown", on_press=lambda a: self.go_menu()))
        
        layout.add_widget(left_layout)
        layout.add_widget(right_layout)
        self.add_widget(layout)
    

    def select_family(self, select):
        families = session.query(Family).all()

        content_popup = BoxLayout(orientation="vertical", size_hint_y=None)
        content_popup.bind(minimum_height=content_popup.setter('height'))

        for fam in families:
            btn = Button(text=fam.name, height=50, size_hint_y=None, background_color="blue")
            btn.id = fam.id
            btn.bind(on_press=lambda a: self.change_family(a, select, popup))
            content_popup.add_widget(btn)

        scroll_content = ScrollView(size_hint=(1, 1))
        scroll_content.add_widget(content_popup)

        popup = Popup(title="Seleccionar familia", content=scroll_content, \
            size_hint=(None, None), size=(400, 300))
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
                btn = Button(text=str(type.type) + "%", height=50, \
                    size_hint_y=None, background_color="pink")
                btn.id = type.id
                btn.bind(on_press=lambda a: self.change_iva(a, select, popup))
                content_popup.add_widget(btn)

        scroll_content = ScrollView(size_hint=(1, 1))
        scroll_content.add_widget(content_popup)

        popup = Popup(title="Seleccionar IVA", content=scroll_content, \
            size_hint=(None, None), size=(400, 300))
        popup.open()


    def change_iva(self, button, select, popup):
        select.id = button.id
        select.text = button.text

        popup.dismiss()


    def create_family(self):
        content_popup = BoxLayout(orientation="vertical")
        content_popup.add_widget(Label(text="Nombre:", size_hint=(1, .2)))
        fam_name = TextInput(hint_text="Nombre", size_hint=(1, .1))
        content_popup.add_widget(fam_name)
        content_popup.add_widget(Label(text="Descripción:", size_hint=(1, .2)))
        fam_desc = TextInput(hint_text="Descripción", size_hint=(1, .2))
        content_popup.add_widget(fam_desc)
        content_popup.add_widget(Button(text="Guardar", size_hint=(1, .1), \
            on_press=lambda a: self.save_family(fam_name.text, fam_desc.text, popup), \
                background_color="green"))
        content_popup.add_widget(Button(text="Cancelar", size_hint=(1, .1), \
            on_press=lambda a: popup.dismiss(), background_color="red"))

        popup = Popup(title="Nueva familia", content=content_popup, size_hint=(None, None), \
            size=(400, 500))
        popup.open()

    
    def save_family(self, name, description, popup):
        if name != '':
            family = Family(name=name, description=description)
            session.add(family)
            session.commit()

            popup.dismiss()
        else:
            second_popup = Popup(title="ERROR", content=Label(text="Introduce un nombre válido"), \
                size_hint=(None, None), size=(400, 100))
            second_popup.open()


    def save(self, name, description, family_id, iva_id):
        if name != '':
            if family_id > 0:
                if iva_id >= 0:
                    department = Department(name=name, description=description, family_id=family_id, iva_type=iva_id)
                    session.add(department)
                    session.commit()

                    popup = Popup(title="AVISO", content=Label(text="Se ha añadido el departamento correctamente"), \
                        size_hint=(None, None), size=(400, 100))
                    popup.open()

                    self.manager.current = 'Options Screen'
                else:
                    popup = Popup(title="ERROR", content=Label(text="Selecciona un tipo de IVA"), \
                        size_hint=(None, None), size=(400, 100))
                    popup.open()
            else:
                popup = Popup(title="ERROR", content=Label(text="Selecciona una familia"), \
                    size_hint=(None, None), size=(400, 100))
                popup.open()
        else:
            popup = Popup(title="ERROR", content=Label(text="Introduce un nombre válido"), \
                size_hint=(None, None), size=(400, 100))
            popup.open()


    def go_menu(self):
        self.manager.current = "Options Screen"
    
    
    def __init__(self, **kw):
        super(NewDepartmentScreen, self).__init__(**kw)

        self.create_layout()


class ModifyDepartmentScreen(Screen):
    def create_layout(self):
        layout = GridLayout(cols=2)

        left_layout = FloatLayout()
        right_layout = FloatLayout(size_hint=(.5, 1))

        
        right_layout.add_widget(Label(text="MODIFICAR DEPARTAMENTO", size_hint=(.2, .1), \
            pos_hint={'top':1, 'right':.2}))
        
        right_layout.add_widget(Button(text="MENÚ", size_hint=(.5, .1), background_color="brown", \
            on_press=lambda a: self.go_menu(), pos_hint={'top':1, 'right':1}))

        right_layout.add_widget(Label(text="Selecciona Departamento:", size_hint=(.2, .1), \
            pos_hint={'top':.8, 'right':.6}))

        right_layout.add_widget(Button(text="Seleccionar departamento", size_hint=(.8, .1), \
            background_color="orange", on_press=lambda a: \
                self.select_department(a, left_layout), pos_hint={'top':.7, 'right':.9}))
        
        layout.add_widget(left_layout)
        layout.add_widget(right_layout)

        self.add_widget(layout)
    

    def select_department(self, select, layout):
        departments = session.query(Department).all()

        content_popup = BoxLayout(orientation="vertical", size_hint_y=None)
        content_popup.bind(minimum_height=content_popup.setter('height'))

        dpt_count = 0
        for dpt in departments:
            btn = Button(text=dpt.name, height=50, size_hint_y=None, background_color="orange")
            btn.id = dpt.id
            btn.bind(on_press=lambda a: self.change_department(a, select, popup, layout))
            content_popup.add_widget(btn)
            dpt_count += 1

        scroll_content = ScrollView(size_hint=(1, 1))
        scroll_content.add_widget(content_popup)

        if dpt_count > 0:
            popup = Popup(title="Seleccionar departamento", content=scroll_content, \
                size_hint=(None, None), size=(400, 300))
            popup.open()
        else:
            popup = Popup(title="AVISO", content=Label(text="No hay departamentos"), \
                size_hint=(None, None), size=(400, 100))
            popup.open()


    def change_department(self, button, select, popup, layout):
        select.text = button.text
        select.id = button.id
        popup.dismiss()

        layout.clear_widgets()
        department = session.query(Department).filter_by(id=button.id).first()

        layout.add_widget(Label(text="Editar nombre", size_hint=(.3, .1), pos_hint={'top':.9}))
        dpt_name = TextInput(text=department.name, size_hint=(.4, .1), pos_hint={'top':.8, 'right':.45})
        layout.add_widget(dpt_name)

        layout.add_widget(Label(text="Editar descripción:", size_hint=(.35, .1), pos_hint={'top':.7}))
        dpt_desc = None
        if department.description is None:
            dpt_desc = TextInput(text='', size_hint=(.4, .2), pos_hint={'top':.6})
        else:
            dpt_desc = TextInput(text=department.description, size_hint=(.4, .2), pos_hint={'top':.6, 'right':.45})
        layout.add_widget(dpt_desc)

        layout.add_widget(Label(text="Editar tipo de IVA:", size_hint=(.2, .1), pos_hint={'top':.9, 'right':.8}))
        iva_button = Button(text=str(department.iva.type) + "%", size_hint=(.3, .1), pos_hint={'top':.8, 'right':.8}, \
            background_color="pink", on_press=lambda a: self.select_iva(iva_button))
        iva_button.id = department.iva.id
        layout.add_widget(iva_button)

        layout.add_widget(Label(text="Cambiar de familia:", size_hint=(.3, .1), pos_hint={'top':.4}))
        family_button = Button(text=department.family.name, size_hint=(.3, .1), pos_hint={'top':.3, 'right':.35}, \
            background_color="blue", on_press=lambda a: self.select_family(a))
        family_button.id = department.family.id
        
        layout.add_widget(family_button)
        
        layout.add_widget(Button(text="Nueva", size_hint=(.2, .1), pos_hint={'top':.3, 'right':.6}, \
            background_color="blue", on_press=lambda a: self.create_family()))

        layout.add_widget(Button(text="Guardar cambios", size_hint=(.3, .1), pos_hint={'top':.15, 'right':.4}, \
            background_color="green", on_press=lambda a: \
                self.modify(department.id, dpt_name.text, dpt_desc.text, family_button.id, iva_button.id)))


    def select_family(self, select):
        families = session.query(Family).all()

        content_popup = BoxLayout(orientation="vertical", size_hint_y=None)
        content_popup.bind(minimum_height=content_popup.setter('height'))

        for fam in families:
            btn = Button(text=fam.name, height=50, size_hint_y=None, background_color="blue")
            btn.id = fam.id
            btn.bind(on_press=lambda a: self.change_family(a, select, popup))
            content_popup.add_widget(btn)

        scroll_content = ScrollView(size_hint=(1, 1))
        scroll_content.add_widget(content_popup)

        popup = Popup(title="Seleccionar familia", content=scroll_content, \
            size_hint=(None, None), size=(400, 300))
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
                btn = Button(text=str(type.type) + "%", height=50, size_hint_y=None, \
                    background_color="pink")
                btn.id = type.id
                btn.bind(on_press=lambda a: self.change_iva(a, select, popup))
                content_popup.add_widget(btn)

        scroll_content = ScrollView(size_hint=(1, 1))
        scroll_content.add_widget(content_popup)

        popup = Popup(title="Seleccionar IVA", content=scroll_content, \
            size_hint=(None, None), size=(400, 300))
        popup.open()


    def change_iva(self, button, select, popup):
        select.id = button.id
        select.text = button.text

        popup.dismiss()


    def create_family(self):
        content_popup = BoxLayout(orientation="vertical")
        content_popup.add_widget(Label(text="Nombre:", size_hint=(1, .2)))
        fam_name = TextInput(hint_text="Nombre", size_hint=(1, .1))
        content_popup.add_widget(fam_name)
        content_popup.add_widget(Label(text="Descripción:", size_hint=(1, .2)))
        fam_desc = TextInput(hint_text="Descripción", size_hint=(1, .2))
        content_popup.add_widget(fam_desc)
        content_popup.add_widget(Button(text="Guardar", size_hint=(1, .1), \
            on_press=lambda a: self.save_family(fam_name.text, fam_desc.text, popup), \
                background_color="green"))
        content_popup.add_widget(Button(text="Cancelar", size_hint=(1, .1), \
            background_color="red", on_press=lambda a: popup.dismiss()))

        popup = Popup(title="Nueva familia", content=content_popup, size_hint=(None, None), \
            size=(400, 500))
        popup.open()


    def save_family(self, name, description, popup):
        if name != '':
            family = Family(name=name, description=description)
            session.add(family)
            session.commit()

            popup.dismiss()
        else:
            second_popup = Popup(title="ERROR", content=Label(text="Introduce un nombre válido"), \
                size_hint=(None, None), size=(400, 100))
            second_popup.open()


    def modify(self, id, name, description, family_id, iva_id):
        department = session.query(Department).filter_by(id=id).first()

        if name != '':
            department.name = name
            department.description = description
            department.family_id = family_id
            department.iva_type = iva_id
            session.commit()

            popup = Popup(title="AVISO", content=Label(text="Se ha modificado el departamento correctamente"), \
                size_hint=(None, None), size=(400, 100))
            popup.open()

            self.manager.current = 'Options Screen'
        else:
            popup = Popup(title="ERROR", content=Label(text="Introduce un nombre válido"), \
                size_hint=(None, None), size=(400, 100))
            popup.open()


    def go_menu(self):
        self.manager.current = "Options Screen"


    def __init__(self, **kw):
        super(ModifyDepartmentScreen, self).__init__(**kw)

        self.create_layout()


class DeleteDepartmentScreen(Screen):
    def create_layout(self):
        layout = GridLayout(cols=2)

        left_layout = FloatLayout()
        right_layout = FloatLayout()

        right_layout.add_widget(Label(text="ELIMINAR DEPARTAMENTO", size_hint=(.2, .1), \
            pos_hint={'top':1, 'right':.5}))

        right_layout.add_widget(Label(text="Selecciona departamento:", size_hint=(.4, .1), \
            pos_hint={'top':.8, 'right':.9}))
        department_button = Button(text="Seleccionar departamento", size_hint=(.5, .1), \
            pos_hint={'top':.7, 'right':.9}, background_color="orange", \
                on_press=lambda a: self.select_department())

        right_layout.add_widget(department_button)

        right_layout.add_widget(Button(text="MENÚ", size_hint=(.3, .1), pos_hint={'top':1, 'right':1}, \
            background_color="brown", on_press=lambda a: self.go_menu()))
        
        layout.add_widget(left_layout)
        layout.add_widget(right_layout)

        self.add_widget(layout)
    

    def select_department(self):
        departments = session.query(Department).all()

        content_popup = BoxLayout(orientation="vertical", size_hint_y=None)
        content_popup.bind(minimum_height=content_popup.setter('height'))

        dpt_count = 0
        for dpt in departments:
            if len(dpt.articles) == 0:
                btn = Button(text=dpt.name, height=50, size_hint_y=None, background_color="orange")
                btn.id = dpt.id
                btn.bind(on_press=lambda a: self.popup_delete(a.id, popup))
                content_popup.add_widget(btn)
                dpt_count += 1

        scroll_content = ScrollView(size_hint=(1, 1))
        scroll_content.add_widget(content_popup)

        if dpt_count > 0:
            popup = Popup(title="Seleccionar departamento", content=scroll_content, \
                size_hint=(None, None), size=(400, 300))
            popup.open()
        else:
            popup = Popup(title="AVISO", content=Label(text="No hay departamentos disponibles"), \
                size_hint=(None, None), size=(400, 100))
            popup.open()


    def change_department(self, button, select, popup, layout):
        department = session.query(Department).filter_by(id=button.id).first()
        select.id = button.id
        select.text = button.text

        delete_btn = Button(text="Eliminar departamento {}".format(department.name), \
            size_hint=(.8, .1), pos=(150, 200), background_color="red")
        delete_btn.bind(on_press=lambda a: self.popup_delete(department.id))

        layout.add_widget(delete_btn)

        popup.dismiss()


    def popup_delete(self, id, popup):
        popup.dismiss()

        department = session.query(Department).filter_by(id=id).first()

        content = BoxLayout(orientation="vertical")
        content.add_widget(Label(text="Se eliminará el departamento {}".format(department.name), \
            size_hint_y=None, height=50))
        content.add_widget(Button(text="Confirmar", on_press=lambda a: self.delete(id, second_popup), \
            height=50, size_hint_y=None, background_color="red"))
        dismiss_btn = Button(text="Cancelar", height=50, size_hint_y=None, background_color="orange")
        content.add_widget(dismiss_btn)

        content_popup = BoxLayout(orientation="vertical", size_hint_y=None)
        content_popup.bind(minimum_height=content_popup.setter('height'))

        content_popup.add_widget(Label(text="Nombre: {}".format(department.name), size_hint_y=None, height=50))
        
        if department.description == None or department.description == '':
            content_popup.add_widget(Label(text="Descripción: Sin descripción", size_hint_y=None, height=50))
        else:
            content_popup.add_widget(Label(text="Descripción: {}".format(department.description), \
                size_hint_y=None, height=50))

        content_popup.add_widget(Label(text="Tipo de IVA: {}".format(str(department.iva.type) + "%"), \
            size_hint_y=None, height=50))

        content_popup.add_widget(Label(text="Familia: {}".format(department.family.name), \
            size_hint_y=None, height=50))

        scroll_content = ScrollView(size_hint=(1, 1))
        scroll_content.add_widget(content_popup)

        content.add_widget(scroll_content)

        second_popup = Popup(title="AVISO", content=content, size_hint=(None, None), size=(400, 600))
        dismiss_btn.bind(on_press=second_popup.dismiss)
        second_popup.open()

    
    def delete(self, id, popup):
        department = session.query(Department).filter_by(id=id).first()
        session.delete(department)
        session.commit()

        popup.dismiss()

        second_popup = Popup(title="AVISO", content=Label(text="Se ha eliminado el departamento correctamente"), \
            size_hint=(None, None), size=(400, 100))
        second_popup.open()

        self.manager.current = 'Options Screen'


    def go_menu(self):
        self.manager.current = "Options Screen"
    
    
    def __init__(self, **kw):
        super(DeleteDepartmentScreen, self).__init__(**kw)

        self.create_layout()


class NewArticleScreen(Screen):
    def create_layout(self):
        layout = GridLayout(cols=2)

        left_layout = FloatLayout()
        right_layout = FloatLayout()

        right_layout.add_widget(Label(text="NUEVO ARTÍCULO", size_hint=(.2, .1), pos_hint={'top':1, 'right':.6}))
        
        right_layout.add_widget(Button(text="MENÚ", size_hint=(.3, .1), background_color="brown", \
            on_press=lambda a: self.go_menu(), pos_hint={'top':1, 'right':1}))

        left_layout.add_widget(Label(text="Nombre:", size_hint=(.3, .1), pos_hint={'top':.9}))
        
        art_name = TextInput(hint_text="Nombre", size_hint=(.5, .1), pos_hint={'top':.8, 'right':.6})
        left_layout.add_widget(art_name)

        left_layout.add_widget(Label(text="Descripción:", size_hint=(.3, .1), pos_hint={'top':.7, 'right':.35}))

        art_desc = TextInput(hint_text="Descripción", size_hint=(.5, .2), pos_hint={'top':.6, 'right':.6})
        left_layout.add_widget(art_desc)

        left_layout.add_widget(Label(text="Precio:", size_hint=(.3, .1), pos_hint={'top':.9, 'right':.9}))

        art_price = TextInput(hint_text="Precio:", size_hint=(.3, .1), pos_hint={'top':.8, 'right':1})
        left_layout.add_widget(art_price)

        left_layout.add_widget(Label(text="IVA:", size_hint=(.3, .1), pos_hint={'top':.7, 'right':.9}))

        iva_select = Button(text="Selecciona IVA", size_hint=(.4, .1), pos_hint={'top':.6, 'right':1.05}, \
            background_color="pink", on_press=lambda a: self.select_iva(a))
        iva_select.id = 0
        left_layout.add_widget(iva_select)

        left_layout.add_widget(Label(text="Selecciona familia:", size_hint=(.3, .1), \
            pos_hint={'top':.9, 'right':1.5}))
        
        family_button = Button(text="Seleccionar familia", size_hint=(.6, .1), pos_hint={'top':.8, 'right':1.7}, \
            background_color="blue", on_press=lambda a: self.select_family(a, department_button))
        family_button.id = 0
        left_layout.add_widget(family_button)

        left_layout.add_widget(Button(text="Nueva", size_hint=(.2, .1), pos_hint={'top':.8, 'right':1.95}, \
            background_color="blue", on_press=lambda a: self.create_family()))

        left_layout.add_widget(Label(text="Selecciona departamento:", size_hint=(.3, .1), \
            pos_hint={'top':.7, 'right':1.5}))

        department_button = Button(text="Seleccionar departamento", size_hint=(.6, .1), \
            pos_hint={'top':.6, 'right':1.7}, background_color="orange", \
                on_press=lambda a: self.select_department(a, family_button.id))
        department_button.id = 0
        left_layout.add_widget(department_button)

        left_layout.add_widget(Button(text="Nuevo", size_hint=(.2, .1), pos_hint={'top':.6, 'right':1.95}, \
            background_color="orange", on_press=lambda a: self.create_department()))
        
        left_layout.add_widget(Button(text="AÑADIR", size_hint=(.3, .1), pos_hint={'top':.4, 'right':1.6}, \
            background_color="green", on_press=lambda a: \
                self.save(art_name.text, art_desc.text, art_price.text, iva_select.id, department_button.id)))

        layout.add_widget(left_layout)
        layout.add_widget(right_layout)

        self.add_widget(layout) 


    def select_family(self, select, dpt_btn):
        families = session.query(Family).all()

        content_popup = BoxLayout(orientation="vertical", size_hint_y=None)
        content_popup.bind(minimum_height=content_popup.setter('height'))

        for fam in families:
            btn = Button(text=fam.name, height=50, size_hint_y=None, background_color="blue")
            btn.id = fam.id
            btn.bind(on_press=lambda a: self.change_family(a, select, popup, dpt_btn))
            content_popup.add_widget(btn)

        scroll_content = ScrollView(size_hint=(1, 1))
        scroll_content.add_widget(content_popup)

        popup = Popup(title="Seleccionar familia", content=scroll_content, \
            size_hint=(None, None), size=(400, 300))
        popup.open()


    def change_family(self, button, select, popup, dpt_btn):
        select.id = button.id
        select.text = button.text

        if not dpt_btn is None:
            dpt_btn.text = "Seleccionar departamento"
            dpt_btn.id = 0

        popup.dismiss()


    def select_department(self, select, family_id):
        if family_id == 0:
            popup = Popup(title="Error", content=Label(text="Selecciona una familia"), \
                size_hint=(None, None), size=(400, 100))
            popup.open()
        else:
            departments = session.query(Department).filter_by(family_id=family_id).all()
            content = None

            if len(departments) > 0:
                content_popup = BoxLayout(orientation="vertical", size_hint_y=None)
                content_popup.bind(minimum_height=content_popup.setter('height'))

                for dpt in departments:
                    btn = Button(text=dpt.name, height=50, size_hint_y=None, background_color="orange")
                    btn.id = dpt.id
                    btn.bind(on_press=lambda a: self.change_department(a, select, popup))
                    content_popup.add_widget(btn)

                content = ScrollView(size_hint=(1, 1))
                content.add_widget(content_popup)

                
            else:
                content = Label(text="Esta familia no contiene departamentos")
                
            popup = Popup(title="Seleccionar departamento", content=content, \
                size_hint=(None, None), size=(400, 300))
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
            btn = Button(text=str(type.type) + "%", height=50, size_hint_y=None, background_color="pink")
            if type.type == -1:
                btn.text = "IVA del departamento"
            btn.id = type.id
            btn.bind(on_press=lambda a: self.change_iva(a, select, popup))
            content_popup.add_widget(btn)

        scroll_content = ScrollView(size_hint=(1, 1))
        scroll_content.add_widget(content_popup)

        popup = Popup(title="Seleccionar IVA", content=scroll_content, \
            size_hint=(None, None), size=(400, 300))
        popup.open()


    def change_iva(self, button, select, popup):
        select.id = button.id
        select.text = button.text

        popup.dismiss()


    def create_family(self):
        content_popup = BoxLayout(orientation="vertical")
        content_popup.add_widget(Label(text="Nombre:", size_hint=(1, .2)))
        fam_name = TextInput(hint_text="Nombre", size_hint=(1, .1))
        content_popup.add_widget(fam_name)
        content_popup.add_widget(Label(text="Descripción:", size_hint=(1, .2)))
        fam_desc = TextInput(hint_text="Descripción", size_hint=(1, .2))
        content_popup.add_widget(fam_desc)
        content_popup.add_widget(Button(text="Guardar", size_hint=(1, .1), \
            on_press=lambda a: self.save_family(fam_name.text, fam_desc.text, popup), \
                background_color="green"))
        content_popup.add_widget(Button(text="Cancelar", size_hint=(1, .1), \
            background_color="red", on_press=lambda a: popup.dismiss()))

        popup = Popup(title="Nueva familia", content=content_popup, size_hint=(None, None), size=(400, 500))
        popup.open()


    def save_family(self, name, description, popup):
        if name != '':
            family = Family(name=name, description=description)
            session.add(family)
            session.commit()

            popup.dismiss()
        else:
            second_popup = Popup(title="ERROR", content=Label(text="Introduce un nombre válido"), \
                size_hint=(None, None), size=(400, 100))
            second_popup.open()


    def create_department(self):
        content_popup = BoxLayout(orientation="vertical")
        content_popup.add_widget(Label(text="Nombre:", size_hint=(1, .2)))
        dpt_name = TextInput(hint_text="Nombre", size_hint=(1, .1))
        content_popup.add_widget(dpt_name)
        content_popup.add_widget(Label(text="Descripción:", size_hint=(1, .2)))
        dpt_desc = TextInput(hint_text="Descripción", size_hint=(1, .2))
        content_popup.add_widget(dpt_desc)
        content_popup.add_widget(Label(text="Familia:", size_hint=(1, .1)))

        fam_select = Button(text="Seleccionar familia", size_hint=(1, .1), \
            on_press=lambda a: self.select_family(fam_select, None), \
                background_color="blue")
        content_popup.add_widget(fam_select)

        content_popup.add_widget(Button(text="GUARDAR", size_hint=(1, .1), \
            on_press=lambda a: self.save_department(dpt_name.text, dpt_desc.text, fam_select.text, popup), \
                background_color="green"))
        content_popup.add_widget(Button(text="Cancelar", size_hint=(1, .1), \
            background_color="red", on_press=lambda a: popup.dismiss()))

        popup = Popup(title="Nuevo departamento", content=content_popup, size_hint=(None, None), size=(400, 500))
        popup.open()

    
    def save_department(self, name, description, family_name, popup):
        if name != '':
            if family_name != 'Seleccionar familia':
                family = session.query(Family).filter_by(name=family_name).first()
                department = Department(name=name, description=description, family_id=family.id)
                session.add(department)
                session.commit()

                popup.dismiss()
            else:
                second_popup = Popup(title="ERROR", content=Label(text="Selecciona una familia"), \
                    size_hint=(None, None), size=(400, 100))
                second_popup.open()
        else:
            second_popup = Popup(title="ERROR", content=Label(text="Introduce un nombre válido"), \
                    size_hint=(None, None), size=(400, 100))
            second_popup.open()


    def save(self, name, description, price, iva_id, dpt_id):
        if name != '':
            try:
                if float(price) >= 0:
                    if iva_id > 0:
                        if dpt_id > 0:
                            article = Article(name=name, description=description, \
                                price=float(price), iva_type=iva_id, department_id=dpt_id)
                            session.add(article)
                            session.commit()

                            popup = Popup(title="AVISO", content=Label(text="Se ha añadido el artículo correctamente"), \
                                size_hint=(None, None), size=(400, 100))
                            popup.open()

                            self.manager.current = 'Options Screen'
                        else:
                            popup = Popup(title="ERROR", content=Label(text="Selecciona un departamento"), \
                                size_hint=(None, None), size=(400, 100))
                            popup.open()
                    else:
                        popup = Popup(title="ERROR", content=Label(text="Selecciona un tipo de IVA"), \
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


    def go_menu(self):
        self.manager.current = "Options Screen"

    
    def __init__(self, **kw):
        super(NewArticleScreen, self).__init__(**kw)

        self.create_layout()


class ModifyArticleScreen(Screen):
    def create_layout(self):
        layout = GridLayout(cols=2)

        left_layout = FloatLayout()
        right_layout = FloatLayout(size_hint=(.5, 1))

        right_layout.add_widget(Label(text="MODIFICAR ARTÍCULO", size_hint=(.2, .1), pos_hint={'top':1, 'right':.3}))
        
        right_layout.add_widget(Button(text="MENÚ", size_hint=(.5, .1), background_color="brown", \
            on_press=lambda a: self.go_menu(), pos_hint={'top':1, 'right':1}))

        right_layout.add_widget(Label(text="Artículo:", size_hint=(.2, .1), pos_hint={'top':.4, 'right':.5}))

        right_layout.add_widget(Button(text="Seleccionar artículo", size_hint=(.8, .1), \
            background_color="pink", on_press=lambda a: \
                self.select_article(a, left_layout), pos_hint={'top':.3, 'right':.8}))
        
        layout.add_widget(left_layout)
        layout.add_widget(right_layout)

        self.add_widget(layout)


    def select_article(self, select, layout):
        articles = session.query(Article).all()

        content_popup = BoxLayout(orientation="vertical", size_hint_y=None)
        content_popup.bind(minimum_height=content_popup.setter('height'))

        art_count = 0
        for art in articles:
            btn = Button(text=art.name, height=50, size_hint_y=None, background_color="pink")
            btn.id = art.id
            btn.bind(on_press=lambda a: self.change_article(a, select, popup, layout))
            content_popup.add_widget(btn)
            art_count += 1

        scroll_content = ScrollView(size_hint=(1, 1))
        scroll_content.add_widget(content_popup)

        if art_count > 0:
            popup = Popup(title="Seleccionar artículo", content=scroll_content, \
                size_hint=(None, None), size=(400, 300))
            popup.open()
        else:
            popup = Popup(title="AVISO", content=Label(text="No hay artículos"), \
                size_hint=(None, None), size=(400, 100))
            popup.open()


    def change_article(self, button, select, popup, layout):
        select.text = button.text
        select.id = button.id
        popup.dismiss()

        layout.clear_widgets()
        
        article = session.query(Article).filter_by(id=button.id).first()

        layout.add_widget(Label(text="Editar nombre:", size_hint=(.3, .1), pos_hint={'top':.9}))
        
        art_name = TextInput(text=article.name, size_hint=(.4, .1), pos_hint={'top':.8, 'right':.45})
        layout.add_widget(art_name)

        layout.add_widget(Label(text="Editar descripción:", size_hint=(.3, .1), pos_hint={'top':.7}))

        art_desc = TextInput(text=article.description, size_hint=(.4, .2), pos_hint={'top':.6, 'right':.45})
        layout.add_widget(art_desc)

        layout.add_widget(Label(text="Editar precio:", size_hint=(.3, .1), pos_hint={'top':.4}))

        art_price = TextInput(text=str(article.price), size_hint=(.3, .1), pos_hint={'top':.3, 'right':.35})
        layout.add_widget(art_price)

        layout.add_widget(Label(text="Editar IVA:", size_hint=(.3, .1), pos_hint={'top':.4, 'right':.7}))

        iva_select = Button(text=str(article.iva.type) + "%", size_hint=(.4, .1), pos_hint={'top':.3, 'right':.8}, \
            background_color="pink", on_press=lambda a: self.select_iva(a))
        if article.iva.type == -1:
            iva_select.text = "IVA del departamento - " + str(article.department.iva.type) + "%"
        iva_select.id = article.iva.id
        layout.add_widget(iva_select)

        layout.add_widget(Label(text="Editar familia:", size_hint=(.3, .1), pos_hint={'top':.9, 'right':.9}))
        
        family_button = Button(text=article.department.family.name, size_hint=(.4, .1), \
            pos_hint={'top':.8, 'right':1}, background_color="blue", \
                on_press=lambda a: self.select_family(a, department_button))
        family_button.id = article.department.family.id
        layout.add_widget(family_button)

        layout.add_widget(Button(text="Nueva", size_hint=(.2, .1), pos_hint={'top':.8, 'right':1.25}, \
            background_color="blue", on_press=lambda a: self.create_family()))

        layout.add_widget(Label(text="Editar departamento:", size_hint=(.3, .1), pos_hint={'top':.7, 'right':.9}))

        department_button = Button(text=article.department.name, size_hint=(.4, .1), pos_hint={'top':.6, 'right':1}, \
            background_color="orange", on_press=lambda a: self.select_department(a, family_button.id))
        department_button.id = article.department.id
        layout.add_widget(department_button)

        layout.add_widget(Button(text="Nuevo", size_hint=(.2, .1), pos_hint={'top':.6, 'right':1.25}, \
            background_color="orange", on_press=lambda a: self.create_department()))
        
        layout.add_widget(Button(text="Guardar cambios", size_hint=(.3, .1), pos_hint={'top':.15, 'right':1.35}, \
            background_color="green", on_press=lambda a: \
            self.modify(article.id, art_name.text, art_desc.text, \
                art_price.text, iva_select.id, department_button.id)))


    def select_family(self, select, dpt_btn):
        families = session.query(Family).all()

        content_popup = BoxLayout(orientation="vertical", size_hint_y=None)
        content_popup.bind(minimum_height=content_popup.setter('height'))

        for fam in families:
            btn = Button(text=fam.name, height=50, size_hint_y=None, background_color="blue")
            btn.id = fam.id
            btn.bind(on_press=lambda a: self.change_family(a, select, popup, dpt_btn))
            content_popup.add_widget(btn)

        scroll_content = ScrollView(size_hint=(1, 1))
        scroll_content.add_widget(content_popup)

        popup = Popup(title="Seleccionar familia", content=scroll_content, \
            size_hint=(None, None), size=(400, 300))
        popup.open()


    def change_family(self, button, select, popup, dpt_btn):
        select.id = button.id
        select.text = button.text

        if not dpt_btn is None:
            dpt_btn.text = "Seleccionar departamento"
            dpt_btn.id = 0

        popup.dismiss()


    def select_department(self, select, family_id):
        if family_id == 0:
            popup = Popup(title="Error", content=Label(text="Selecciona una familia"), \
                size_hint=(None, None), size=(400, 100))
            popup.open()
        else:
            departments = session.query(Department).filter_by(family_id=family_id).all()
            content = None

            if len(departments) > 0:
                content_popup = BoxLayout(orientation="vertical", size_hint_y=None)
                content_popup.bind(minimum_height=content_popup.setter('height'))

                for dpt in departments:
                    btn = Button(text=dpt.name, height=50, size_hint_y=None, background_color="orange")
                    btn.id = dpt.id
                    btn.bind(on_press=lambda a: self.change_department(a, select, popup))
                    content_popup.add_widget(btn)

                content = ScrollView(size_hint=(1, 1))
                content.add_widget(content_popup)

                
            else:
                content = Label(text="Esta familia no contiene departamentos")
                
            popup = Popup(title="Seleccionar departamento", content=content, \
                size_hint=(None, None), size=(400, 300))
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
            btn = Button(text=str(type.type) + "%", height=50, size_hint_y=None, background_color="pink")
            if type.type == -1:
                btn.text = "IVA del departamento"
            btn.id = type.id
            btn.bind(on_press=lambda a: self.change_iva(a, select, popup))
            content_popup.add_widget(btn)

        scroll_content = ScrollView(size_hint=(1, 1))
        scroll_content.add_widget(content_popup)

        popup = Popup(title="Seleccionar IVA", content=scroll_content, \
            size_hint=(None, None), size=(400, 300))
        popup.open()


    def change_iva(self, button, select, popup):
        select.id = button.id
        select.text = button.text

        popup.dismiss()


    def create_family(self):
        content_popup = BoxLayout(orientation="vertical")
        content_popup.add_widget(Label(text="Nombre:", size_hint=(1, .2)))
        fam_name = TextInput(hint_text="Nombre", size_hint=(1, .1))
        content_popup.add_widget(fam_name)
        content_popup.add_widget(Label(text="Descripción:", size_hint=(1, .2)))
        fam_desc = TextInput(hint_text="Descripción", size_hint=(1, .2))
        content_popup.add_widget(fam_desc)
        content_popup.add_widget(Button(text="Guardar", size_hint=(1, .1), \
            on_press=lambda a: self.save_family(fam_name.text, fam_desc.text, popup), \
                background_color="green"))
        content_popup.add_widget(Button(text="Cancelar", size_hint=(1, .1), \
            background_color="red", on_press=lambda a: popup.dismiss()))

        popup = Popup(title="Nueva familia", content=content_popup, size_hint=(None, None), size=(400, 500))
        popup.open()


    def save_family(self, name, description, popup):
        if name != '':
            family = Family(name=name, description=description)
            session.add(family)
            session.commit()

            popup.dismiss()
        else:
            second_popup = Popup(title="ERROR", content=Label(text="Introduce un nombre válido"), \
                size_hint=(None, None), size=(400, 100))
            second_popup.open()


    def create_department(self):
        content_popup = BoxLayout(orientation="vertical")
        content_popup.add_widget(Label(text="Nombre:", size_hint=(1, .2)))
        dpt_name = TextInput(hint_text="Nombre", size_hint=(1, .1))
        content_popup.add_widget(dpt_name)
        content_popup.add_widget(Label(text="Descripción:", size_hint=(1, .2)))
        dpt_desc = TextInput(hint_text="Descripción", size_hint=(1, .2))
        content_popup.add_widget(dpt_desc)
        content_popup.add_widget(Label(text="Familia:", size_hint=(1, .1)))

        fam_select = Button(text="Seleccionar familia", size_hint=(1, .1), \
            on_press=lambda a: self.select_family(fam_select, None), background_color="blue")
        content_popup.add_widget(fam_select)

        content_popup.add_widget(Button(text="GUARDAR", size_hint=(1, .1), \
            on_press=lambda a: self.save_department(dpt_name.text, dpt_desc.text, fam_select.text, popup), \
                background_color="green"))
        content_popup.add_widget(Button(text="Cancelar", size_hint=(1, .1), \
            background_color="red", on_press=lambda a: popup.dismiss()))

        popup = Popup(title="Nuevo departamento", content=content_popup, size_hint=(None, None), size=(400, 500))
        popup.open()


    def save_department(self, name, description, family_name, popup):
        if name != '':
            if family_name != 'Seleccionar familia':
                family = session.query(Family).filter_by(name=family_name).first()
                department = Department(name=name, description=description, family_id=family.id)
                session.add(department)
                session.commit()

                popup.dismiss()
            else:
                second_popup = Popup(title="ERROR", content=Label(text="Selecciona una familia"), \
                    size_hint=(None, None), size=(400, 100))
                second_popup.open()
        else:
            second_popup = Popup(title="ERROR", content=Label(text="Introduce un nombre válido"), \
                size_hint=(None, None), size=(400, 100))
            second_popup.open()


    def modify(self, id, name, description, price, iva_id, dpt_id):
        if name != '':
            try:
                if float(price) >= 0:
                    if iva_id > 0:
                        if dpt_id > 0:
                            article = session.query(Article).filter_by(id=id).first()
                            article.name = name
                            article.description = description
                            article.price = price
                            article.iva_type = iva_id
                            article.department_id = dpt_id
                            session.commit()

                            popup = Popup(title="AVISO", content=Label(text="Se ha modificado el artículo correctamente"), \
                                size_hint=(None, None), size=(400, 100))
                            popup.open()

                            self.manager.current = 'Options Screen'
                        else:
                            popup = Popup(title="ERROR", content=Label(text="Selecciona un departamento"), \
                                size_hint=(None, None), size=(400, 100))
                            popup.open()
                    else:
                        popup = Popup(title="ERROR", content=Label(text="Selecciona un tipo de IVA"), \
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

    
    def go_menu(self):
        self.manager.current = "Options Screen"
    
    
    def __init__(self, **kw):
        super(ModifyArticleScreen, self).__init__(**kw)

        self.create_layout()


class DeleteArticleScreen(Screen):
    def create_layout(self):
        layout = GridLayout(cols=2)

        left_layout = FloatLayout()
        right_layout = FloatLayout()

        right_layout.add_widget(Label(text="ELIMINAR ARTÍCULO", size_hint=(.2, .1), \
            pos_hint={'top':1, 'right':.6}))

        right_layout.add_widget(Label(text="Selecciona artículo:", size_hint=(.4, .1), \
            pos_hint={'top':.5, 'right':.8}))
        article_button = Button(text="Seleccionar artículo", size_hint=(.5, .1), \
            pos_hint={'top':.4, 'right':.8}, background_color="pink", \
                on_press=lambda a: self.select_article())

        right_layout.add_widget(article_button)

        right_layout.add_widget(Button(text="MENÚ", size_hint=(.3, .1), pos_hint={'top':1, 'right':1}, \
            background_color="brown", on_press=lambda a: self.go_menu()))
        
        layout.add_widget(left_layout)
        layout.add_widget(right_layout)

        self.add_widget(layout)


    def select_article(self):
        articles = session.query(Article).all()

        content_popup = BoxLayout(orientation="vertical", size_hint_y=None)
        content_popup.bind(minimum_height=content_popup.setter('height'))

        if len(articles) > 0:
            for art in articles:
                btn = Button(text=art.name, height=50, size_hint_y=None, background_color="pink")
                btn.id = art.id
                btn.bind(on_press=lambda a: self.popup_delete(a.id, popup))
                content_popup.add_widget(btn)

            scroll_content = ScrollView(size_hint=(1, 1))
            scroll_content.add_widget(content_popup)

            popup = Popup(title="Seleccionar artículo", content=scroll_content, \
                size_hint=(None, None), size=(400, 300))
            popup.open()
        else:
            popup = Popup(title="AVISO", content=Label(text="No hay artículos"), \
                size_hint=(None, None), size=(400, 100))
            popup.open()


    def change_article(self, button, select, popup, layout):
        article = session.query(Article).filter_by(id=button.id).first()
        select.id = button.id
        select.text = button.text

        delete_btn = Button(text="Eliminar artículo {}".format(article.name), \
            size_hint=(.8, .1), pos=(150, 200), background_color="red")
        delete_btn.bind(on_press=lambda a: self.popup_delete(article.id))

        layout.add_widget(delete_btn)

        popup.dismiss()


    def popup_delete(self, id, popup):
        popup.dismiss()

        article = session.query(Article).filter_by(id=id).first()

        content = BoxLayout(orientation="vertical")
        content.add_widget(Label(text="Se eliminará el artículo {}".format(article.name), \
            size_hint_y=None, height=50))
        content.add_widget(Button(text="Confirmar", on_press=lambda a: self.delete(id, second_popup), \
            height=50, size_hint_y=None, background_color="red"))
        dismiss_btn = Button(text="Cancelar", height=50, size_hint_y=None, background_color="orange")
        content.add_widget(dismiss_btn)

        content_popup = BoxLayout(orientation="vertical", size_hint_y=None)
        content_popup.bind(minimum_height=content_popup.setter('height'))

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

        second_popup = Popup(title="AVISO", content=content, size_hint=(None, None), size=(400, 600))
        dismiss_btn.bind(on_press=second_popup.dismiss)
        second_popup.open()


    def delete(self, id, popup):
        article = session.query(Article).filter_by(id=id).first()
        session.delete(article)
        session.commit()

        popup.dismiss()

        second_popup = Popup(title="AVISO", content=Label(text="Se ha eliminado el artículo correctamente"), \
            size_hint=(None, None), size=(400, 100))
        second_popup.open()

        self.manager.current = 'Options Screen'


    def go_menu(self):
        self.manager.current = "Options Screen"


    def __init__(self, **kw):
        super(DeleteArticleScreen, self).__init__(**kw)

        self.create_layout()


class OptionsScreen(Screen):
    options = ["fam", "dpt", "art"]


    def create_layout(self):
        main_layout = BoxLayout(orientation="vertical", spacing=10)

        first_layout = BoxLayout(orientation="horizontal", spacing=10, size_hint_x=None)
        first_layout.bind(minimum_width=first_layout.setter('width'))

        mid_layout = BoxLayout(orientation="horizontal", spacing=10, size_hint=(1, .1))

        last_layout = FloatLayout()

        first_layout.add_widget(Button(text="FAMILIAS", background_color="blue", size_hint_x=None, \
            width=200, on_press=lambda a: self.change_first_opt(0, mid_layout, last_layout)))
        first_layout.add_widget(Button(text="DEPARTAMENTOS", background_color="orange", size_hint_x=None, \
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


    def change_first_opt(self, opt, layout, second_layout):
        layout.clear_widgets()
        
        if opt >= 0:
            option = self.options[opt]
            
            if option == 'fam':
                if self.family.name in self.manager.screen_names:
                    self.manager.remove_widget(self.family)
                    self.family = FamilyScreen(name="Family Screen")
                    self.manager.add_widget(self.family)
                else:
                    self.manager.add_widget(self.family)

                self.manager.current = "Family Screen"
            elif option == 'dpt':
                if self.department.name in self.manager.screen_names:
                    self.manager.remove_widget(self.department)
                    self.department = DepartmentScreen(name="Department Screen")
                    self.manager.add_widget(self.department)
                else:
                    self.manager.add_widget(self.department)
                
                self.manager.current = "Department Screen"
            else:
                layout.add_widget(Button(text="NUEVO", background_color="pink", \
                    on_press=lambda a: self.change_last_opt('add-art', second_layout)))
                layout.add_widget(Button(text="MODIFICAR", background_color="pink", \
                    on_press=lambda a: self.change_last_opt('mod-art', second_layout)))
                layout.add_widget(Button(text="ELIMINAR", background_color="pink", \
                    on_press=lambda a: self.change_last_opt('del-art', second_layout)))
        else:
            self.manager.current = "Main Screen"

    
    def change_last_opt(self, opt, layout):
        layout.clear_widgets()

        if opt == 'add-dpt':
            if self.new_department.name in self.manager.screen_names:
                self.manager.remove_widget(self.new_department)
                self.new_department = NewDepartmentScreen(name="New Department Screen")
                self.manager.add_widget(self.new_department)
            else:
                self.manager.add_widget(self.new_department)
            
            self.manager.current = "New Department Screen"
        elif opt == 'add-art':
            if self.new_article.name in self.manager.screen_names:
                self.manager.remove_widget(self.new_article)
                self.new_article = NewArticleScreen(name="New Article Screen")
                self.manager.add_widget(self.new_article)
            else:
                self.manager.add_widget(self.new_article)

            self.manager.current = "New Article Screen"
        elif opt == 'mod-dpt':
            if self.mod_department.name in self.manager.screen_names:
                self.manager.remove_widget(self.mod_department)
                self.mod_department = ModifyDepartmentScreen(name="Modify Department Screen")
                self.manager.add_widget(self.mod_department)
            else:
                self.manager.add_widget(self.mod_department)
            
            self.manager.current = "Modify Department Screen"
        elif opt == 'mod-art':
            if self.mod_article.name in self.manager.screen_names:
                self.manager.remove_widget(self.mod_article)
                self.mod_article = ModifyArticleScreen(name="Modify Article Screen")
                self.manager.add_widget(self.mod_article)
            else:
                self.manager.add_widget(self.mod_article)
            
            self.manager.current = "Modify Article Screen"
        elif opt == 'del-dpt':
            if self.del_department.name in self.manager.screen_names:
                self.manager.remove_widget(self.del_department)
                self.del_department = DeleteDepartmentScreen(name="Delete Department Screen")
                self.manager.add_widget(self.del_department)
            else:
                self.manager.add_widget(self.del_department)
            
            self.manager.current = "Delete Department Screen"
        else:
            if self.del_article.name in self.manager.screen_names:
                self.manager.remove_widget(self.del_article)
                self.del_article = DeleteArticleScreen(name="Delete Article Screen")
                self.manager.add_widget(self.del_article)
            else:
                self.manager.add_widget(self.del_article)

            self.manager.current = "Delete Article Screen"

    
    def __init__(self, **kw):
        super(OptionsScreen, self).__init__(**kw)
        
        self.family = FamilyScreen(name="Family Screen")
        
        self.department = DepartmentScreen(name="Department Screen")

        self.new_department = NewDepartmentScreen(name="New Department Screen")
        self.new_article = NewArticleScreen(name="New Article Screen")
        
        self.mod_department = ModifyDepartmentScreen(name="Modify Department Screen")
        self.mod_article = ModifyArticleScreen(name="Modify Article Screen")

        self.del_department = DeleteDepartmentScreen(name="Delete Department Screen")
        self.del_article = DeleteArticleScreen(name="Delete Article Screen")
        
        self.create_layout()


class MainScreen(Screen):
    departments = session.query(Department).all()
    selection = []


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
        opt_btn.bind(on_press=lambda a: self.go_menu())
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

        self.add_widget(main_layout)


    def add_on_press_departments(self, btn, department_id, layout, layout_to):
        btn.bind(on_press=lambda a: self.change_dpt(department_id, layout, layout_to))
    
    
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
    

    def add_on_press_article(self, btn, layout, article_id):
        btn.bind(on_press=lambda a: self.add_selection(layout, article_id))


    def add_selection(self, layout, article_id):
        article = session.query(Article).filter_by(id=article_id).first()
        self.selection.append(article)

        layout.clear_widgets()

        for i in self.selection:
            layout.add_widget(Label(text=i.name + " - " + str(i.price) + "€"))


    def go_menu(self):
        self.manager.current = "Options Screen"


    def __init__(self, **kw):
        super(MainScreen, self).__init__(**kw)

        self.departments = session.query(Department).all()
        self.create_layout()


class LoginScreen(Screen):
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
        
        password = TextInput(hint_text="Contraseña", password=True, size_hint=(.6, .05), \
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

        buttons = ["7", "8", "9", "4", "5", "6", "1", "2", "3", "0"]
        
        for btn in buttons:
            right_layout1.add_widget(Button(text=btn, \
                on_press=lambda a: self.add_number(a.text, txt, username, password)))

        right_layout1.add_widget(Button(text="Cancelar", background_color="red", \
            on_press=lambda a: self.delete_number(txt, username, password)))

        right_layout1.add_widget(Button(text="Confirmar", background_color="green", \
            on_press=lambda a: self.confirm_user(txt, username, password)))

        right_layout.add_widget(right_layout1)
        layout.add_widget(left_layout)
        layout.add_widget(right_layout)

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
                popup = Popup(title="Error", \
                    content=Label(text="Usuario incorrecto"),
                    size_hint=(None, None), size=(400, 200))
                popup.open()
        else:
            if user.password == password.text:
                opcion.text = "Usuario correcto"
                password.disabled = True

                self.manager.current = "Main Screen"
            else:
                popup = Popup(title="Error", \
                    content=Label(text="Contraseña incorrecta"),
                    size_hint=(None, None), size=(400, 200))
                popup.open()


    def __init__(self, **kw):
        super(LoginScreen, self).__init__(**kw)

        self.create_layout()


class GridScreen(Screen):
    def go_menu(self):
        self.manager.current = 'Options Screen'


    def create_layout(self):
        layout = GridLayout(rows=2, padding=20, spacing=20)

        top_layout = FloatLayout(size_hint_y=None, height=50)
        top_layout.add_widget(Label(text="NUEVA FAMILIA", size_hint=(.2, 1), pos_hint={'top':1, 'right':.8}))
        top_layout.add_widget(Button(text="MENÚ PRINCIPAL", size_hint=(.2, 1), pos_hint={'top':1, 'right':1}, \
            background_color="brown", on_press=lambda a: self.go_menu()))
        
        bottom_layout = GridLayout(cols=1, rows=3, spacing=40, row_force_default=True, row_default_height=40)
        
        box_name = BoxLayout(orientation="horizontal")
        box_name.add_widget(Label(text="Nombre: *", size_hint=(.1, 1), text_size=box_name.size, halign="left", valign="middle"))
        name = TextInput(hint_text="Nombre")
        box_name.add_widget(name)

        box_desc = BoxLayout(orientation="horizontal")
        box_desc.add_widget(Label(text="Descripción:", size_hint=(.1, 1), text_size=box_desc.size, halign="left", valign="middle"))
        desc = TextInput(hint_text="Descripción")
        box_desc.add_widget(desc)

        box_btn = BoxLayout()
        box_btn.add_widget(Button(text="AÑADIR", size_hint=(.6, 1), background_color="green"))

        
        
        bottom_layout.add_widget(box_name)
        bottom_layout.add_widget(box_desc)
        bottom_layout.add_widget(box_btn)
        
        layout.add_widget(top_layout)
        layout.add_widget(bottom_layout)

        self.add_widget(layout)


    def __init__(self, **kw):
        super(GridScreen, self).__init__(**kw)

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
