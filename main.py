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
        
        fam_select = Button(text="MODIFICAR", size_hint_x=None, width=200, background_color="brown", \
            on_press=lambda a: self.select_family(a, fam_name, fam_desc, fam_code, box_delete))
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
        
        
    def select_family(self, select, name, description, code, box_delete):
        if select.text != "VOLVER":
            families = session.query(Family).all()

            content_popup = BoxLayout(orientation="vertical", size_hint_y=None)
            content_popup.bind(minimum_height=content_popup.setter('height'))

            fam_count = 0
            for fam in families:
                btn = Button(text=fam.name, height=50, size_hint_y=None, background_color="blue")
                btn.id = fam.id
                btn.bind(on_press=lambda a: self.change_family(a, select, popup, name, description, \
                    code, box_delete))
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
            select.text = "MODIFICAR"
            select.id = 0
            name.text = ""
            code.text = ""
            description.text = ""
            box_delete.clear_widgets()


    def change_family(self, button, select, popup, name, description, code, box_delete):
        family = session.query(Family).filter_by(id=button.id).first()
        select.id = button.id
        select.text = "VOLVER"

        name.text = family.name
        description.text = family.description
        code.text = family.code

        if len(family.departments) == 0:
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
        
        dpt_select = Button(text="MODIFICAR", size_hint_x=None, width=200, background_color="brown", \
            on_press=lambda a: self.select_department(a, dpt_name, dpt_desc, dpt_code, \
                box_delete, family_select, iva_select))
        dpt_select.id = 0
        top_layout.add_widget(dpt_select)
        top_layout.add_widget(Button(size_hint_x=None, width=200, background_color="brown"))
        top_layout.add_widget(Button(size_hint_x=None, width=200, background_color="brown"))
        top_layout.add_widget(Button(size_hint_x=None, width=200, background_color="brown"))
        top_layout.add_widget(Button(size_hint_x=None, width=200, background_color="brown"))
        top_layout.add_widget(Button(size_hint_x=None, width=200, background_color="brown"))
        top_layout.add_widget(Button(text="MENÚ PRINCIPAL", size_hint_x=None, width=200, background_color="brown", \
            on_press=lambda a: self.go_menu()))

        bottom_layout = GridLayout(cols=1, rows=7, spacing=40, row_force_default=True, row_default_height=40)

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
            on_press=lambda a: self.select_family(a), size_hint=(.9, 1))
        family_select.id = 0
        box_family.add_widget(family_select)
        box_family.add_widget(Button(text="+", size_hint=(.1, 1), background_color="blue", \
            on_press=lambda a: self.create_family()))
        

        box_iva = BoxLayout(orientation="horizontal")
        box_iva.add_widget(Label(text="Tipo de IVA:", size_hint=(.1, 1), text_size=box_iva.size, \
            halign="left", valign="middle"))
        iva_select = Button(text="Seleccionar IVA", background_color="pink", \
            on_press=lambda a: self.select_iva(a))
        iva_select.id = 0
        box_iva.add_widget(iva_select)

        box_save = BoxLayout()
        save_btn = Button(text="GUARDAR", size_hint=(.6, 1), background_color="green")
        save_btn.bind(on_press=lambda a: self.modify(dpt_select.id, dpt_name.text, dpt_desc.text, dpt_code.text, \
            family_select.id, iva_select.id))
        box_save.add_widget(save_btn)

        box_delete = BoxLayout()
        
        bottom_layout.add_widget(box_code)
        bottom_layout.add_widget(box_name)
        bottom_layout.add_widget(box_desc)
        bottom_layout.add_widget(box_family)
        bottom_layout.add_widget(box_iva)
        bottom_layout.add_widget(box_save)
        bottom_layout.add_widget(box_delete)

        top_scroll = ScrollView(size_hint=(1, .1))
        top_scroll.add_widget(top_layout)

        layout.add_widget(top_scroll)
        layout.add_widget(bottom_layout)

        self.add_widget(layout)

    
    def select_department(self, select, name, description, code, box_delete, fam_select, iva_select):
        if select.text != "VOLVER":
            departments = session.query(Department).all()

            content_popup = BoxLayout(orientation="vertical", size_hint_y=None)
            content_popup.bind(minimum_height=content_popup.setter('height'))

            dpt_count = 0
            for dpt in departments:
                btn = Button(text=dpt.name, height=50, size_hint_y=None, background_color="orange")
                btn.id = dpt.id
                btn.bind(on_press=lambda a: self.change_department(a, select, popup, name, description, \
                    code, box_delete, fam_select, iva_select))
                content_popup.add_widget(btn)
                dpt_count += 1

            scroll_content = ScrollView(size_hint=(1, 1))
            scroll_content.add_widget(content_popup)

            if dpt_count > 0:
                popup = Popup(title="Seleccionar departamento", content=scroll_content, \
                    size_hint=(None, None), size=(600, 600))
                popup.open()
            else:
                popup = Popup(title="AVISO", content=Label(text="No hay departamentos"), \
                    size_hint=(None, None), size=(400, 100))
                popup.open()
        else:
            select.text = "MODIFICAR"
            select.id = 0
            name.text = ""
            code.text = ""
            description.text = ""
            fam_select.text = "Seleccionar familia"
            fam_select.id = 0
            iva_select.text = "Seleccionar IVA"
            iva_select.id = 0
            box_delete.clear_widgets()


    def change_department(self, button, select, popup, name, description, code, box_delete, fam_select, iva_select):
        department = session.query(Department).filter_by(id=button.id).first()
        select.id = button.id
        select.text = "VOLVER"

        name.text = department.name
        description.text = department.description
        code.text = department.code
        fam_select.text = department.family.name
        fam_select.id = department.family.id
        iva_select.text = str(department.iva.type) + "%"
        iva_select.id = department.iva.id

        if len(department.articles) == 0:
            box_delete.add_widget(Button(text="Eliminar departamento {}".format(department.name), size_hint=(.3, 1), \
                background_color="red", on_press=lambda a: self.popup_delete(department.id)))
        
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


    def save_family(self, name, description, popup):
        if name != '':
            code = ''.join(random.SystemRandom().choice(string.digits) for _ in range(4))
                    
            while session.query(Family).filter_by(code=code).first():
                code = ''.join(random.SystemRandom().choice(string.digits) for _ in range(4))
            
            family = Family(name=name, description=description, code=code)
            session.add(family)
            session.commit()

            popup.dismiss()
        else:
            second_popup = Popup(title="ERROR", content=Label(text="Introduce un nombre válido"), \
                size_hint=(None, None), size=(400, 100))
            second_popup.open()


    def popup_delete(self, id):
        if id > 0:
            department = session.query(Department).filter_by(id=id).first()
            
            content = BoxLayout(orientation="vertical")
            content.add_widget(Label(text="Se eliminará el departamento {}".format(department.name), \
                height=50, size_hint_y=None))
            content.add_widget(Button(text="Confirmar", on_press=lambda a: self.delete(id, popup), \
                height=50, size_hint_y=None, background_color="red"))

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


    def dismiss_modify(self, id, name, description, family_id, iva_id, code, popup):
        popup.dismiss()

        return self.modify(id, name, description, code, family_id, iva_id)


    def modify(self, id, name, description, code, family_id, iva_id):
        if code is None:
            code = ''.join(random.SystemRandom().choice(string.digits) for _ in range(4))
            
            while session.query(Family).filter_by(code=code).first():
                code = ''.join(random.SystemRandom().choice(string.digits) for _ in range(4))
            
            department = session.query(Department).filter_by(id=id).first()
            department.name = name
            department.description = description
            department.code = code
            department.family_id = family_id
            department.iva_type = iva_id
            session.commit()

            popup = Popup(title="AVISO", content=Label(text="Se ha modificado el departamento correctamente"), \
                size_hint=(None, None), size=(400, 100))
            popup.open()

            self.manager.current = "Options Screen"
        
        elif name != '':
            if code != '':
                exists_department = session.query(Department).filter_by(id=id).first()

                if exists_department:
                    same_department = session.query(Department).filter_by(code=code).first()

                    if same_department:
                        if same_department.name == exists_department.name:
                            department = session.query(Department).filter_by(id=id).first()
                            department.name = name
                            department.description = description
                            department.family_id = family_id
                            department.iva_type = iva_id
                            session.commit()

                            popup = Popup(title="AVISO", content=Label(text="Se ha modificado el departamento correctamente"), \
                                size_hint=(None, None), size=(400, 100))
                            popup.open()

                            self.manager.current = "Options Screen"
                        else:
                            popup = Popup(title="ERROR", content=Label(text="El código ya está en uso"), \
                                size_hint=(None, None), size=(400, 100))
                            popup.open()
                    else:
                        department = session.query(Department).filter_by(id=id).first()
                        department.name = name
                        department.description = description
                        department.code = code
                        department.family_id = family_id
                        department.iva_type = iva_id
                        session.commit()

                        popup = Popup(title="AVISO", content=Label(text="Se ha modificado el departamento correctamente"), \
                            size_hint=(None, None), size=(400, 100))
                        popup.open()

                        self.manager.current = "Options Screen"

                else:
                    popup = Popup(title="ERROR", content=Label(text="El departamento no existe"), \
                        size_hint=(None, None), size=(400, 100))
                    popup.open()
            else:
                if id > 0:
                    content_popup = BoxLayout(orientation="vertical")
                    content_popup.add_widget(Label(text="Se modificará el departamento con un código nuevo"))
                    content_popup.add_widget(Button(text="Confirmar", size_hint=(1, .5), \
                        on_press=lambda a: self.dismiss_modify(id, name, description, family_id, iva_id, None, popup)))
                    
                    popup = Popup(title="AVISO", content=content_popup, size_hint=(None, None), size=(400, 200))
                    popup.open()
                else:
                    self.save(name, description, family_id, iva_id)
        else:
            popup = Popup(title="ERROR", content=Label(text="Introduce un nombre válido"), \
                size_hint=(None, None), size=(400, 100))
            popup.open()


    def save(self, name, description, family_id, iva_id):
        if name != '':
            if family_id > 0:
                if iva_id > 0:
                    code = ''.join(random.SystemRandom().choice(string.digits) for _ in range(4))
                    
                    while session.query(Family).filter_by(code=code).first():
                        code = ''.join(random.SystemRandom().choice(string.digits) for _ in range(4))
                    
                    new_department = Department(name=name, description=description, code=code, \
                        family_id=family_id, iva_type=iva_id)
                    session.add(new_department)
                    session.commit()

                    popup = Popup(title="AVISO", content=Label(text="Se ha añadido el departamento correctamente"), \
                        size_hint=(None, None), size=(400, 100))
                    popup.open()

                    self.manager.current = "Options Screen"
                else:
                    popup = Popup(title="ERROR", content=Label(text="Selecciona un tipo de IVA"), \
                        size_hint=(None, None), size=(400, 200))
                    popup.open()
            else:
                popup = Popup(title="ERROR", content=Label(text="Selecciona una familia"), \
                    size_hint=(None, None), size=(400, 200))
                popup.open()
        else:
            popup = Popup(title="ERROR", content=Label(text="Introduce un nombre válido"), \
                size_hint=(None, None), size=(400, 200))
            popup.open()


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
        super(DepartmentScreen, self).__init__(**kw)

        self.create_layout()


class ArticleScreen(Screen):
    def create_layout(self):
        layout = GridLayout(rows=2, padding=20, spacing=20)

        top_layout = GridLayout(cols=7, height=50, spacing=20, size_hint_x=None)
        top_layout.bind(minimum_width=top_layout.setter('width'))
        
        art_select = Button(text="MODIFICAR", size_hint_x=None, width=200, background_color="brown", \
            on_press=lambda a: self.select_article(a, art_name, art_desc, art_price, art_code, box_delete, \
                family_select, iva_select, department_select))
        art_select.id = 0
        top_layout.add_widget(art_select)
        top_layout.add_widget(Button(size_hint_x=None, width=200, background_color="brown"))
        top_layout.add_widget(Button(size_hint_x=None, width=200, background_color="brown"))
        top_layout.add_widget(Button(size_hint_x=None, width=200, background_color="brown"))
        top_layout.add_widget(Button(size_hint_x=None, width=200, background_color="brown"))
        top_layout.add_widget(Button(size_hint_x=None, width=200, background_color="brown"))
        top_layout.add_widget(Button(text="MENÚ PRINCIPAL", size_hint_x=None, width=200, background_color="brown", \
            on_press=lambda a: self.go_menu()))

        bottom_layout = GridLayout(cols=1, rows=9, spacing=40, row_force_default=True, row_default_height=40)

        box_code = BoxLayout(orientation="horizontal")
        box_code.add_widget(Label(text="Código:", size_hint=(.1, 1), text_size=box_code.size, \
            halign="left", valign="middle"))
        art_code = TextInput(hint_text="Vacío para crear un nuevo artículo")
        box_code.add_widget(art_code)

        box_name = BoxLayout(orientation="horizontal")
        box_name.add_widget(Label(text="Nombre: *", size_hint=(.1, 1), text_size=box_name.size, \
            halign="left", valign="middle"))
        art_name = TextInput(hint_text="Nombre")
        box_name.add_widget(art_name)

        box_desc = BoxLayout(orientation="horizontal")
        box_desc.add_widget(Label(text="Descripción:", size_hint=(.1, 1), text_size=box_desc.size, \
            halign="left", valign="middle"))
        art_desc = TextInput(hint_text="Descripción")
        box_desc.add_widget(art_desc)

        box_price = BoxLayout(orientation="horizontal")
        box_price.add_widget(Label(text="Precio:", size_hint=(.1, 1), text_size=box_price.size, \
            halign="left", valign="middle"))
        art_price = TextInput(hint_text="Precio")
        box_price.add_widget(art_price)

        box_family = BoxLayout(orientation="horizontal")
        box_family.add_widget(Label(text="Familia:", size_hint=(.1, 1), text_size=box_family.size, \
            halign="left", valign="middle"))
        family_select = Button(text="Seleccionar familia", background_color="blue", \
            on_press=lambda a: self.select_family(a, department_select), size_hint=(.9, 1))
        family_select.id = 0
        box_family.add_widget(family_select)
        box_family.add_widget(Button(text="+", size_hint=(.1, 1), background_color="blue", \
            on_press=lambda a: self.create_family()))

        box_department = BoxLayout(orientation="horizontal")
        box_department.add_widget(Label(text="Departamento:", size_hint=(.1, 1), text_size=box_department.size, \
            halign="left", valign="middle"))
        department_select = Button(text="Seleccionar departamento", background_color="orange", \
            on_press=lambda a: self.select_department(a, family_select.id), size_hint=(.9, 1))
        department_select.id = 0
        box_department.add_widget(department_select)
        box_department.add_widget(Button(text="+", size_hint=(.1, 1), background_color="orange", \
            on_press=lambda a: self.create_department()))
        
        box_iva = BoxLayout(orientation="horizontal")
        box_iva.add_widget(Label(text="Tipo de IVA:", size_hint=(.1, 1), text_size=box_iva.size, \
            halign="left", valign="middle"))
        iva_select = Button(text="Seleccionar IVA", background_color="pink", \
            on_press=lambda a: self.select_iva(a))
        iva_select.id = 0
        box_iva.add_widget(iva_select)

        box_save = BoxLayout()
        save_btn = Button(text="GUARDAR", size_hint=(.6, 1), background_color="green")
        save_btn.bind(on_press=lambda a: self.modify(art_select.id, art_name.text, art_desc.text, art_code.text, \
            iva_select.id, art_price.text, department_select.id))
        box_save.add_widget(save_btn)

        box_delete = BoxLayout()
        
        bottom_layout.add_widget(box_code)
        bottom_layout.add_widget(box_name)
        bottom_layout.add_widget(box_desc)
        bottom_layout.add_widget(box_price)
        bottom_layout.add_widget(box_family)
        bottom_layout.add_widget(box_department)
        bottom_layout.add_widget(box_iva)
        bottom_layout.add_widget(box_save)
        bottom_layout.add_widget(box_delete)

        top_scroll = ScrollView(size_hint=(1, .1))
        top_scroll.add_widget(top_layout)

        layout.add_widget(top_scroll)
        layout.add_widget(bottom_layout)

        self.add_widget(layout)
    

    def select_article(self, select, name, description, price, code, box_delete, \
        fam_select, iva_select, dpt_select):
        
        if select.text != "VOLVER":
            articles = session.query(Article).all()

            content_popup = BoxLayout(orientation="vertical", size_hint_y=None)
            content_popup.bind(minimum_height=content_popup.setter('height'))

            art_count = 0
            for art in articles:
                btn = Button(text=art.name, height=50, size_hint_y=None, background_color="pink")
                btn.id = art.id
                btn.bind(on_press=lambda a: self.change_article(a, select, popup, name, description, \
                    code, box_delete, fam_select, iva_select, price, dpt_select))
                content_popup.add_widget(btn)
                art_count += 1

            scroll_content = ScrollView(size_hint=(1, 1))
            scroll_content.add_widget(content_popup)

            if art_count > 0:
                popup = Popup(title="Seleccionar artículo", content=scroll_content, \
                    size_hint=(None, None), size=(600, 600))
                popup.open()
            else:
                popup = Popup(title="AVISO", content=Label(text="No hay artículos"), \
                    size_hint=(None, None), size=(400, 100))
                popup.open()
        else:
            select.text = "MODIFICAR"
            select.id = 0
            name.text = ""
            code.text = ""
            description.text = ""
            price.text = ""
            fam_select.text = "Seleccionar familia"
            fam_select.id = 0
            dpt_select.text = "Seleccionar departamento"
            dpt_select.id = 0
            iva_select.text = "Seleccionar IVA"
            iva_select.id = 0
            box_delete.clear_widgets()


    def change_article(self, button, select, popup, name, description, code, box_delete, \
        fam_select, iva_select, price, dpt_select):
        
        article = session.query(Article).filter_by(id=button.id).first()
        select.id = button.id
        select.text = "VOLVER"

        name.text = article.name
        description.text = article.description
        code.text = article.code
        price.text = str(article.price)
        fam_select.text = article.department.family.name
        fam_select.id = article.department.family.id
        dpt_select.text = article.department.name
        dpt_select.id = article.department.id

        if article.iva_type == 5:
            iva_select.text = "IVA del departamento: {}%".format(article.department.iva.type)
        else:
            iva_select.text = str(article.iva.type) + "%"
        iva_select.id = article.iva.id

        box_delete.add_widget(Button(text="Eliminar artículo {}".format(article.name), size_hint=(.3, 1), \
            background_color="red", on_press=lambda a: self.popup_delete(article.id)))
        
        popup.dismiss()

    
    def select_family(self, select, dpt_btn):
        families = session.query(Family).all()

        if not dpt_btn is None:
            dpt_btn.text = "Seleccionar departamento"
            dpt_btn.id = 0

        content_popup = BoxLayout(orientation="vertical", size_hint_y=None)
        content_popup.bind(minimum_height=content_popup.setter('height'))

        fam_count = 0
        for fam in families:
            btn = Button(text=fam.name, height=50, size_hint_y=None, background_color="blue")
            btn.id = fam.id
            btn.bind(on_press=lambda a: self.change_family(a, select, popup))
            content_popup.add_widget(btn)
            fam_count += 1

        scroll_content = ScrollView(size_hint=(1, 1))
        scroll_content.add_widget(content_popup)

        if fam_count > 0:
            popup = Popup(title="Seleccionar familia", content=scroll_content, \
                size_hint=(None, None), size=(400, 300))
            popup.open()
        else:
            popup = Popup(title="Seleccionar familia", content=Label(text="No hay familias"), \
                size_hint=(None, None), size=(400, 100))
            popup.open()


    def change_family(self, button, select, popup):
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
                btn = Button(text=dpt.name, height=50, size_hint_y=None, background_color="orange")
                btn.id = dpt.id
                btn.bind(on_press=lambda a: self.change_department(a, select, popup))
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
        else:
            popup = Popup(title="ERROR", content=Label(text="Selecciona una familia"), \
                size_hint=(None, None), size=(400, 100))
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
            btn = Button(text=str(type.type) + "%", height=50, \
                size_hint_y=None, background_color="pink")
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
            on_press=lambda a: popup.dismiss(), background_color="red"))

        popup = Popup(title="Nueva familia", content=content_popup, size_hint=(None, None), \
            size=(400, 500))
        popup.open()


    def save_family(self, name, description, popup):
        if name != '':
            code = ''.join(random.SystemRandom().choice(string.digits) for _ in range(4))
                    
            while session.query(Family).filter_by(code=code).first():
                code = ''.join(random.SystemRandom().choice(string.digits) for _ in range(4))
            
            family = Family(name=name, description=description, code=code)
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

        content_popup.add_widget(Label(text="Tipo de IVA:", size_hint=(1, .2)))
        iva_select = Button(text="Seleccionar familia", size_hint=(1, .1), \
            on_press=lambda a: self.select_iva(a), background_color="pink")
        iva_select.id = 0
        content_popup.add_widget(iva_select)

        content_popup.add_widget(Label(text="Familia:", size_hint=(1, .1)))
        fam_select = Button(text="Seleccionar familia", size_hint=(1, .1), \
            on_press=lambda a: self.select_family(fam_select, None), \
                background_color="blue")
        fam_select.id = 0
        content_popup.add_widget(fam_select)

        content_popup.add_widget(Button(text="GUARDAR", size_hint=(1, .1), \
            on_press=lambda a: self.save_department(dpt_name.text, dpt_desc.text, \
                fam_select.id, iva_select.id, popup), background_color="green"))
        content_popup.add_widget(Button(text="Cancelar", size_hint=(1, .1), \
            background_color="red", on_press=lambda a: popup.dismiss()))

        popup = Popup(title="Nuevo departamento", content=content_popup, size_hint=(None, None), size=(400, 500))
        popup.open()


    def save_department(self, name, description, family_id, iva_id, popup):
        if name != '':
            if family_id > 0:
                if iva_id > 0:
                    code = ''.join(random.SystemRandom().choice(string.digits) for _ in range(4))
                            
                    while session.query(Family).filter_by(code=code).first():
                        code = ''.join(random.SystemRandom().choice(string.digits) for _ in range(4))
                    
                    department = Department(name=name, description=description, \
                        code=code, family_id=family_id, iva_type=iva_id)
                    session.add(department)
                    session.commit()

                    popup.dismiss()
                else:
                    second_popup = Popup(title="ERROR", content=Label(text="Selecciona un tipo de IVA"), \
                        size_hint=(None, None), size=(400, 100))
                    second_popup.open()
            else:
                second_popup = Popup(title="ERROR", content=Label(text="Selecciona una familia"), \
                    size_hint=(None, None), size=(400, 100))
                second_popup.open()
        else:
            second_popup = Popup(title="ERROR", content=Label(text="Introduce un nombre válido"), \
                size_hint=(None, None), size=(400, 100))
            second_popup.open()


    def popup_delete(self, id):
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


    def dismiss_modify(self, id, name, description, price, department_id, iva_id, code, popup):
        popup.dismiss()

        return self.modify(id, name, description, code, iva_id, price, department_id)


    def modify(self, id, name, description, code, iva_id, price, department_id):
        if code is None:
            code = ''.join(random.SystemRandom().choice(string.digits) for _ in range(4))
            
            while session.query(Family).filter_by(code=code).first():
                code = ''.join(random.SystemRandom().choice(string.digits) for _ in range(4))
            
            article = session.query(Article).filter_by(id=id).first()
            article.name = name
            article.description = description
            article.code = code
            article.price = price
            article.department_id = department_id
            article.iva_type = iva_id
            session.commit()

            popup = Popup(title="AVISO", content=Label(text="Se ha modificado el artículo correctamente"), \
                size_hint=(None, None), size=(400, 100))
            popup.open()

            self.manager.current = "Options Screen"
        
        elif name != '':
            if code != '':
                exists_article = session.query(Article).filter_by(id=id).first()

                if exists_article:
                    same_article = session.query(Article).filter_by(code=code).first()

                    if same_article:
                        if same_article.name == exists_article.name:
                            article = session.query(Article).filter_by(id=id).first()
                            article.name = name
                            article.price = price
                            article.department_id = department_id
                            article.description = description
                            article.iva_type = iva_id
                            session.commit()

                            popup = Popup(title="AVISO", content=Label(text="Se ha modificado el artículo correctamente"), \
                                size_hint=(None, None), size=(400, 100))
                            popup.open()

                            self.manager.current = "Options Screen"
                        else:
                            popup = Popup(title="ERROR", content=Label(text="El código ya está en uso"), \
                                size_hint=(None, None), size=(400, 100))
                            popup.open()
                    else:
                        article = session.query(Article).filter_by(id=id).first()
                        article.name = name
                        article.description = description
                        article.code = code
                        article.price = price
                        article.department_id = department_id
                        article.iva_type = iva_id
                        session.commit()

                        popup = Popup(title="AVISO", content=Label(text="Se ha modificado el artículo correctamente"), \
                            size_hint=(None, None), size=(400, 100))
                        popup.open()

                        self.manager.current = "Options Screen"

                else:
                    popup = Popup(title="ERROR", content=Label(text="El artículo no existe"), \
                        size_hint=(None, None), size=(400, 100))
                    popup.open()
            else:
                if id > 0:
                    content_popup = BoxLayout(orientation="vertical")
                    content_popup.add_widget(Label(text="Se modificará el artículo con un código nuevo"))
                    content_popup.add_widget(Button(text="Confirmar", size_hint=(1, .5), \
                        on_press=lambda a: self.dismiss_modify(id, name, description, \
                            price, department_id, iva_id, None, popup)))
                    
                    popup = Popup(title="AVISO", content=content_popup, size_hint=(None, None), size=(400, 200))
                    popup.open()
                else:
                    self.save(name, description, price, department_id, iva_id)
        else:
            popup = Popup(title="ERROR", content=Label(text="Introduce un nombre válido"), \
                size_hint=(None, None), size=(400, 100))
            popup.open()


    def save(self, name, description, price, dpt_id, iva_id):
        if name != '':
            try:
                if float(price) >= 0:
                    if iva_id > 0:
                        if dpt_id > 0:
                            code = ''.join(random.SystemRandom().choice(string.digits) for _ in range(4))
            
                            while session.query(Family).filter_by(code=code).first():
                                code = ''.join(random.SystemRandom().choice(string.digits) for _ in range(4))

                            article = Article(name=name, description=description, \
                                price=float(price), iva_type=iva_id, department_id=dpt_id, code=code)
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
        super(ArticleScreen, self).__init__(**kw)

        self.create_layout()


class OptionsScreen(Screen):
    def create_layout(self):
        layout = GridLayout(rows=2)
        
        top_layout = BoxLayout(size_hint=(1, .1))
        top_layout.add_widget(Button(text="MENÚ PRINCIPAL", background_color="brown"))

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
    
    
    def __init__(self, **kw):
        super(OptionsScreen, self).__init__(**kw)
        
        self.family = FamilyScreen(name="Family Screen")
        self.department = DepartmentScreen(name="Department Screen")
        self.article = ArticleScreen(name="Article Screen")

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
    def create_families_layout(self, layout, reset, save, delete):
        layout.clear_widgets()
        reset.clear_widgets()
        save.clear_widgets()
        delete.clear_widgets()

        families_layout = GridLayout(cols=3, spacing=10, size_hint_y=None)
        families_layout.bind(minimum_height=families_layout.setter('height'))

        families_layout.add_widget(BoxLayout(size_hint=(.1, 1)))

        buttons_layout = GridLayout(cols=4, size_hint_y=None, spacing=10)
        buttons_layout.bind(minimum_height=buttons_layout.setter('height'))

        families = session.query(Family).all()

        for fam in families:
            fam_btn = Button(text=fam.name, size_hint_y=None, height=100, background_color="blue", \
                on_press=lambda a: self.get_family(a.id, layout, reset, save, delete))
            fam_btn.id = fam.id
            buttons_layout.add_widget(fam_btn)

        families_layout.add_widget(buttons_layout)

        families_layout.add_widget(BoxLayout(size_hint=(.1, 1)))
        
        scroll_bottom = ScrollView(size_hint=(1, .9))
        scroll_bottom.add_widget(families_layout)

        layout.add_widget(scroll_bottom)

    
    def on_text(self, save):
        print('The widget')


    def get_family(self, id, layout, reset, save, delete):
        family = session.query(Family).filter_by(id=id).first()
        
        layout.clear_widgets()

        reset.add_widget(Button(text="VOLVER", background_color="pink", \
            on_press=lambda a: self.create_families_layout(layout, reset, save, delete)))
        save.add_widget(Button(text="GUARDAR", background_color="green", \
            on_press=lambda a: self.modify(id, fam_code.text, fam_name.text, fam_desc.text, layout, reset, save, delete)))
        
        if len(family.departments) == 0: 
            delete.add_widget(Button(text="ELIMINAR", background_color="red"))

        bottom_layout = GridLayout(cols=3, rows=1, spacing=40, row_force_default=True, row_default_height=40)

        box_code = BoxLayout(orientation="horizontal")
        box_code.add_widget(Label(text="Código:", size_hint=(.05, 1), text_size=box_code.size, \
            halign="left", valign="middle"))
        fam_code = TextInput(text=family.code, size_hint=(.05, 1))
        box_code.add_widget(fam_code)

        box_name = BoxLayout(orientation="horizontal")
        box_name.add_widget(Label(text="Nombre: *", size_hint=(.05, 1), text_size=box_name.size, \
            halign="left", valign="middle"))
        fam_name = TextInput(text=family.name, size_hint=(.1, 1))
        #fam_name.bind(text=lambda a: self.on_text(save))
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


    def modify(self, id, code, name, description, layout, reset, save, delete):
        family = session.query(Family).filter_by(id=id).first()
        family.code = code
        family.name = name
        family.description = description

        self.create_families_layout(layout, reset, save, delete)
        reset.clear_widgets()
        save.clear_widgets()
        delete.clear_widgets()

        session.commit()

    
    def go_menu(self):
        self.manager.current = 'Options Screen'


    def create_layout(self):
        layout = GridLayout(rows=2, padding=10, spacing=20)

        top_layout = GridLayout(cols=5, spacing=20, size_hint=(1, .1))

        box_reset = BoxLayout()
        box_save = BoxLayout()
        box_delete = BoxLayout()

        top_layout.add_widget(Button(text="MENÚ", background_color="brown", \
            on_press=lambda a: self.go_menu()))
        top_layout.add_widget(Button(text="NUEVO", background_color="brown"))
        top_layout.add_widget(box_reset)
        top_layout.add_widget(box_save)
        top_layout.add_widget(box_delete)

        bottom_layout = GridLayout(cols=1)
        self.create_families_layout(bottom_layout, box_reset, box_save, box_delete)
    
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
        
        root.add_widget(GridScreen())
        #.add_widget(LoginScreen(name="Login Screen"))
        #root.add_widget(MainScreen(name="Main Screen"))
        #root.add_widget(OptionsScreen(name="Options Screen"))

        return root
        
    
    def __init__(self, **kwargs):
        super(MainApp, self).__init__(**kwargs)


if __name__ == '__main__':
    create_db()
    
    MainApp().run()
