from functools import partial
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.properties import NumericProperty
from kivy.uix.dropdown import DropDown
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.modalview import ModalView
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import NoTransition, Screen, ScreenManager
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.clock import Clock


from db import Article, Department, Family, Iva, User, create_db, session


class NewFamilyScreen(Screen):
    def save(self, name, description):
        if name != '':
            new_family = Family(name=name, description=description)
            session.add(new_family)
            session.commit()

            popup = Popup(title="AVISO", content=Label(text="Se ha añadido la familia correctamente"), \
                size_hint=(None, None), size=(400, 100))
            popup.open()

            self.manager.transition = NoTransition()
            self.manager.current = "Options Screen"

        else:
            popup = Popup(title="ERROR", content=Label(text="Introduce un nombre válido"), \
                size_hint=(None, None), size=(400, 200))
            popup.open()
    
    
    def go_to_previous(self):
        self.manager.transition = NoTransition()
        self.manager.current = "Options Screen"


    def create_layout(self):
        layout = FloatLayout()
        
        layout.add_widget(Button(text="MENÚ", size_hint=(.1, .1), pos=(700, 525), \
            on_press=lambda a: self.go_to_previous(), background_color="brown"))
        
        layout.add_widget(Label(text="Nombre de la familia:", size_hint=(.5, .1), pos=(0, 450)))
        fam_name = TextInput(hint_text="Nombre", size_hint=(.5, .1), pos=(100, 400))
        layout.add_widget(fam_name)
            
        layout.add_widget(Label(text="Descripción:", size_hint=(.5, .1), pos=(0, 300)))
        fam_desc = TextInput(hint_text="Descripción de la familia", size_hint=(.5, .2), pos=(100, 175))
        layout.add_widget(fam_desc)
            
        layout.add_widget(Button(text="AÑADIR", size_hint=(.8, .1), pos=(100, 50), background_color="green", \
            on_press=lambda a: self.save(fam_name.text, fam_desc.text)))

        self.add_widget(layout)

    
    def __init__(self, **kw):
        super(NewFamilyScreen, self).__init__(**kw)

        self.create_layout()


class ModifyFamilyScreen(Screen):
    def reload_families(self):
        pass

    
    def modify(self, id, name, description):
        if name == '':
            popup = Popup(title="ERROR", content=Label(text="Introduce un nombre válido"), \
                size_hint=(None, None), size=(400, 200))
            popup.open()
        else:
            family = session.query(Family).filter_by(id=id).first()
            family.name = name
            family.description = description
            session.commit()
    

    def go_to_previous(self):
        self.manager.transition = NoTransition()
        self.manager.current = "Options Screen"


    def change_family(self, layout, id):
        layout.clear_widgets()

        family = session.query(Family).filter_by(id=id).first()

        layout.add_widget(Label(text="Editar nombre:", size_hint=(.5, .1), pos=(0, 500)))

        fam_name = TextInput(text=family.name, size_hint=(.5, .1), pos=(100, 450))
        layout.add_widget(fam_name)

        layout.add_widget(Label(text="Editar descripción:", size_hint=(.5, .1), pos=(0, 375)))

        fam_desc = TextInput(text=family.description, size_hint=(.5, .2), pos=(100, 250))
        layout.add_widget(fam_desc)

        btn_save = Button(text="GUARDAR", background_color="green", size_hint=(.3, .1), pos=(100, 100))
        btn_save.id = family.id
        btn_save.bind(on_press=lambda a: self.modify(a.id, fam_name.text, fam_desc.text))

        layout.add_widget(btn_save)
    

    def create_layout(self):
        layout = GridLayout(cols=2)

        left_layout = FloatLayout()
        right_layout = BoxLayout(orientation="vertical", size_hint=(.2, 1))

        families_layout = BoxLayout(orientation="vertical", size_hint_y=None)
        families_layout.bind(minimum_height=families_layout.setter('height'))

        families = session.query(Family).all()

        if len(families) > 0:
            for fam in families:
                btn = Button(text=fam.name, background_color="blue", height=50, size_hint_y=None)
                btn.id = fam.id
                btn.bind(on_press=lambda a: self.change_family(left_layout, a.id))
                families_layout.add_widget(btn)
        else:
            families_layout.add_widget(Button(text="No hay familias", background_color="red", \
                height=50, size_hint_y=None))

        scroll_families = ScrollView(size_hint=(1, .8))
        scroll_families.add_widget(families_layout)
        
        right_layout.add_widget(Button(text="MENÚ", size_hint=(1, .1), background_color="brown", \
            on_press=lambda a: self.go_to_previous()))

        right_layout.add_widget(Button(text="Recargar familias", size_hint=(1, .1), background_color="brown", \
            on_press=lambda a: self.reload_families()))
        
        right_layout.add_widget(scroll_families)
        layout.add_widget(left_layout)
        layout.add_widget(right_layout)

        self.add_widget(layout)

    
    def __init__(self, **kw):
        super(ModifyFamilyScreen, self).__init__(**kw)

        self.create_layout()


class DeleteFamilyScreen(Screen):
    def popup_delete(self, id):
        family = session.query(Family).filter_by(id=id).first()

        content_popup = None

        content_popup = BoxLayout(orientation="vertical")
        content_popup.add_widget(Label(text="Se eliminará la familia {}".format(family.name)))
        content_popup.add_widget(Button(text="Confirmar", on_press=lambda a: self.delete(id, popup)))
        dismiss_btn = Button(text="Cancelar")
        content_popup.add_widget(dismiss_btn)

        popup = Popup(title="AVISO", content=content_popup, size_hint=(None, None), size=(400, 200))
        dismiss_btn.bind(on_press=popup.dismiss)
        popup.open()
    
    
    def delete(self, id, popup):
        family = session.query(Family).filter_by(id=id).first()
        session.delete(family)
        session.commit()

        popup.dismiss()
    
    
    def change_to_delete(self, layout, id):
        family = session.query(Family).filter_by(id=id).first()

        delete_btn = Button(text="Eliminar familia {}".format(family.name), \
            size_hint=(.5, .1), pos=(100, 100), background_color="red")
        delete_btn.bind(on_press=lambda a: self.popup_delete(id))

        layout.add_widget(delete_btn)

    
    def go_to_previous(self):
        self.manager.transition = NoTransition()
        self.manager.current = "Options Screen"
    
    
    def create_layout(self):
        layout = GridLayout(cols=2)

        left_layout = FloatLayout()
        right_layout = BoxLayout(orientation="vertical", size_hint=(.2, 1))

        families_layout = BoxLayout(orientation="vertical", size_hint_y=None)
        families_layout.bind(minimum_height=families_layout.setter('height'))

        families = session.query(Family).all()

        for fam in families:
            btn = Button(text=fam.name, background_color="blue", height=50, size_hint_y=None)
            btn.id = fam.id
            btn.bind(on_press=lambda a: self.change_to_delete(left_layout, a.id))
            families_layout.add_widget(btn)

        scroll_families = ScrollView(size_hint=(1, .8))
        scroll_families.add_widget(families_layout)
        
        right_layout.add_widget(Button(text="MENÚ", size_hint=(1, .1), background_color="brown", \
            on_press=lambda a: self.go_to_previous()))
        
        right_layout.add_widget(scroll_families)
        layout.add_widget(left_layout)
        layout.add_widget(right_layout)

        self.add_widget(layout)


    def __init__(self, **kw):
        super(DeleteFamilyScreen, self).__init__(**kw)

        self.create_layout()
    

class NewDepartmentScreen(Screen):
    def save_family(self, name, description, popup):
        family = Family(name=name, description=description)
        session.add(family)
        session.commit()

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
            on_press=lambda a: self.save_family(fam_name.text, fam_desc.text, popup)))
        content_popup.add_widget(Button(text="Cancelar", size_hint=(1, .1), on_press=lambda a: popup.dismiss()))

        popup = Popup(title="Nueva familia", content=content_popup, size_hint=(None, None), \
            size=(400, 500))
        popup.open()


    def change_family(self, button, select, popup):
        select.text = button.text
        select.id = button.id
        popup.dismiss()


    def select_family(self, select):
        families = session.query(Family).all()

        content_popup = BoxLayout(orientation="vertical", size_hint_y=None)
        content_popup.bind(minimum_height=content_popup.setter('height'))

        for fam in families:
            btn = Button(text=fam.name, height=50, size_hint_y=None)
            btn.id = fam.id
            btn.bind(on_press=lambda a: self.change_family(a, select, popup))
            content_popup.add_widget(btn)

        scroll_content = ScrollView(size_hint=(1, 1))
        scroll_content.add_widget(content_popup)

        popup = Popup(title="Seleccionar familia", content=scroll_content, size_hint=(None, None), size=(400, 300))
        popup.open()


    def save(self, name, description, family_id):
        department = Department(name=name, description=description, family_id=family_id)
        session.add(department)
        session.commit()


    def go_to_previous(self):
        self.manager.transition = NoTransition()
        self.manager.current = "Options Screen"


    def create_layout(self):
        layout = GridLayout(cols=2)

        left_layout = FloatLayout()

        left_layout.add_widget(Label(text="NUEVO DEPARTAMENTO", size_hint=(.4, .1), pos=(0, 550)))
        
        left_layout.add_widget(Label(text="Nombre:", size_hint=(.2, .1), pos=(0, 475)))
        department_name = TextInput(hint_text="Nombre", size_hint=(.5, .1), pos=(25, 425))
        left_layout.add_widget(department_name)

        left_layout.add_widget(Label(text="Descripción:", size_hint=(.2, .1), pos=(10, 350)))
        department_desc = TextInput(hint_text="Descripción", size_hint=(.5, .2), pos=(25, 225))
        left_layout.add_widget(department_desc)

        left_layout.add_widget(Label(text="Familia:", size_hint=(.2, .1), pos=(0, 150)))
        
        family_button = Button(text="Seleccionar familia", size_hint=(.3, .1), pos=(25, 100), \
            background_color="blue", on_press=lambda a: self.select_family(a))
        left_layout.add_widget(family_button)
        
        left_layout.add_widget(Button(text="Nueva", size_hint=(.1, .1), pos=(225, 100), background_color="blue", \
            on_press=lambda a: self.create_family()))

        left_layout.add_widget(Button(text="AÑADIR", size_hint=(.3, .1), pos=(400, 50), \
            on_press=lambda a: self.save(department_name.text, department_desc.text, family_button.id), \
                background_color="green"))
        
        right_layout = BoxLayout(orientation="vertical", size_hint=(.3, 1))
        
        right_layout.add_widget(Button(text="MENÚ", size_hint=(1, 1), background_color="brown", \
            on_press=lambda a: self.go_to_previous()))
        
        layout.add_widget(left_layout)
        layout.add_widget(right_layout)
        self.add_widget(layout)
    
    
    def __init__(self, **kw):
        super(NewDepartmentScreen, self).__init__(**kw)

        self.create_layout()

# --------- MODIFICAR DEPARTAMENTO --------
class ModifyDepartmentScreen(Screen):
    def create_family(self):
        self.manager.transition = NoTransition()
        self.manager.current = "New Family Screen"


    def reload_families(self, layout, llayout, dpt_layout):
        layout.clear_widgets()

        families = session.query(Family).all()

        family_buttons = []
        for fam in families:
            btn = Button(text=fam.name, background_color="blue", height=50, size_hint_y=None)
            btn.id = fam.id
            btn.bind(on_press=lambda a: self.get_departments_by_family(llayout, a.id, dpt_layout))
            family_buttons.append(btn)
            layout.add_widget(btn)
    
    
    def modify(self, id, name, description, family_name):
        family = session.query(Family).filter_by(name=family_name).first()
        department = session.query(Department).filter_by(id=id).first()
        
        department.name = name
        department.description = description
        department.family_id = family.id
        session.commit()


    def change_department(self, layout, id):
        department = session.query(Department).filter_by(id=id).first()
        families = session.query(Family).all()
        
        layout.add_widget(Label(text="Editar nombre:", size_hint=(.5, .1), pos=(0, 550)))
        department_name = TextInput(text=department.name, size_hint=(.5, .1), pos=(100, 500))
        layout.add_widget(department_name)

        layout.add_widget(Label(text="Editar descripción:", size_hint=(.5, .1), pos=(0, 425)))
        department_desc = TextInput(text=department.description, size_hint=(.5, .2), pos=(100, 300))
        layout.add_widget(department_desc)

        dropdown = DropDown()
        for fam in families:
            btn = Button(text=fam.name, size_hint_y=None, height=40, background_color="blue")
            btn.id = fam.id
            btn.bind(on_release=lambda btn: dropdown.select(btn.text))
            dropdown.add_widget(btn)

        layout.add_widget(Label(text="Cambiar de familia:", size_hint=(.5, .1), pos=(0, 200)))
        family_select = Button(text=department.family.name, size_hint=(.5, .1), pos=(100, 150), background_color="blue")
        family_select.bind(on_release=dropdown.open)
        dropdown.bind(on_select=lambda instance, x: setattr(family_select, 'text', x))

        layout.add_widget(family_select)

        layout.add_widget(Button(text="GUARDAR", size_hint=(.3, .1), pos=(100, 50), \
            on_press=lambda a: self.modify(department.id, department_name.text, department_desc.text, family_select.text), \
                background_color="green"))

    
    def get_departments_by_family(self, llayout, family_id, rlayout):
        llayout.clear_widgets()
        rlayout.clear_widgets()

        family = session.query(Family).filter_by(id=family_id).first()
        departments = family.departments

        for dpt in departments:
            btn = Button(text=dpt.name, background_color="orange", height=50, size_hint_y=None)
            btn.id = dpt.id
            btn.bind(on_press=lambda a: self.change_department(llayout, a.id))
            rlayout.add_widget(btn)
        
    
    def go_to_previous(self):
        self.manager.transition = NoTransition()
        self.manager.current = "Options Screen"

    
    def create_layout(self):
        layout = GridLayout(cols=2)

        left_layout = FloatLayout()
        right_layout = FloatLayout(size_hint=(.5, 1))
        
        right_layout.add_widget(Button(text="MENÚ", size_hint=(.5, .1), background_color="brown", \
            on_press=lambda a: self.go_to_previous(), pos=(675, 540)))

        right_layout.add_widget(Button(text="Seleccionar departamento", size_hint=(.5, .1), background_color="orange", \
            on_press=lambda a: self.change_department()))
        
        layout.add_widget(left_layout)
        layout.add_widget(right_layout)

        self.add_widget(layout)


    def __init__(self, **kw):
        super(ModifyDepartmentScreen, self).__init__(**kw)

        self.create_layout()


class DeleteDepartmentScreen(Screen):
    def delete(self, id, popup):
        department = session.query(Department).filter_by(id=id).first()
        session.delete(department)
        session.commit()

        popup.dismiss()


    def popup_delete(self, id):
        department = session.query(Department).filter_by(id=id).first()

        content_popup = None

        content_popup = BoxLayout(orientation="vertical")
        content_popup.add_widget(Label(text="Se eliminará el departamento {}".format(department.name)))
        content_popup.add_widget(Button(text="Confirmar", on_press=lambda a: self.delete(id, popup)))
        dismiss_btn = Button(text="Cancelar")
        content_popup.add_widget(dismiss_btn)

        popup = Popup(title="AVISO", content=content_popup, size_hint=(None, None), size=(400, 200))
        dismiss_btn.bind(on_press=popup.dismiss)
        popup.open()


    def go_to_previous(self):
        self.manager.transition = NoTransition()
        self.manager.current = "Options Screen"


    def change_to_delete(self, layout, id):
        department = session.query(Department).filter_by(id=id).first()

        delete_btn = Button(text="Eliminar departamento {}".format(department.name), \
            size_hint=(.5, .1), pos=(100, 100), background_color="red")
        delete_btn.bind(on_press=lambda a: self.popup_delete(id))

        layout.add_widget(delete_btn)


    def get_departments_by_family(self, llayout, family_id, rlayout):
        llayout.clear_widgets()
        rlayout.clear_widgets()

        family = session.query(Family).filter_by(id=family_id).first()
        departments = family.departments

        for dpt in departments:
            btn = Button(text=dpt.name, background_color="orange", height=50, size_hint_y=None)
            btn.id = dpt.id
            btn.bind(on_press=lambda a: self.change_to_delete(llayout, a.id))
            rlayout.add_widget(btn)
    
    
    def create_layout(self):
        layout = GridLayout(cols=2)

        left_layout = FloatLayout()
        right_layout = BoxLayout(orientation="vertical", size_hint=(.5, 1))
        
        right_bottom_layout = BoxLayout(orientation="horizontal", size_hint=(1, 1))

        families_layout = BoxLayout(orientation="vertical", size_hint_y=None)
        families_layout.bind(minimum_height=families_layout.setter('height'))

        departments_layout = BoxLayout(orientation="vertical", size_hint_y=None)
        departments_layout.bind(minimum_height=departments_layout.setter('height'))

        families = session.query(Family).all()

        for fam in families:
            btn = Button(text=fam.name, background_color="blue", height=50, size_hint_y=None)
            btn.id = fam.id
            btn.bind(on_press=lambda a: self.get_departments_by_family(left_layout, a.id, departments_layout))
            families_layout.add_widget(btn)

        scroll_families = ScrollView(size_hint=(.5, 1))
        scroll_families.add_widget(families_layout)

        scroll_departments = ScrollView(size_hint=(.5, 1))
        scroll_departments.add_widget(departments_layout)
        
        right_layout.add_widget(Button(text="MENÚ", size_hint=(1, .1), background_color="brown", \
            on_press=lambda a: self.go_to_previous()))
        
        right_bottom_layout.add_widget(scroll_departments)
        right_bottom_layout.add_widget(scroll_families)
        layout.add_widget(left_layout)
        right_layout.add_widget(right_bottom_layout)
        layout.add_widget(right_layout)

        self.add_widget(layout)
    
    
    def __init__(self, **kw):
        super(DeleteDepartmentScreen, self).__init__(**kw)

        self.create_layout()


class NewArticleScreen(Screen):
    family_active = None
    

    def change_department(self, layout, id):
        department = session.query(Department).filter_by(id=id).first()
        families = session.query(Family).all()
        
        layout.add_widget(Label(text="Editar nombre:", size_hint=(.5, .1), pos=(0, 550)))
        department_name = TextInput(text=department.name, size_hint=(.5, .1), pos=(100, 500))
        layout.add_widget(department_name)

        layout.add_widget(Label(text="Editar descripción:", size_hint=(.5, .1), pos=(0, 425)))
        department_desc = TextInput(text=department.description, size_hint=(.5, .2), pos=(100, 300))
        layout.add_widget(department_desc)

        dropdown = DropDown()
        for fam in families:
            btn = Button(text=fam.name, size_hint_y=None, height=40, background_color="blue")
            btn.id = fam.id
            btn.bind(on_release=lambda btn: dropdown.select(btn.text))
            dropdown.add_widget(btn)

        layout.add_widget(Label(text="Cambiar de familia:", size_hint=(.5, .1), pos=(0, 200)))
        family_select = Button(text=department.family.name, size_hint=(.5, .1), pos=(100, 150), background_color="blue")
        family_select.bind(on_release=dropdown.open)
        dropdown.bind(on_select=lambda instance, x: setattr(family_select, 'text', x))

        layout.add_widget(family_select)

        layout.add_widget(Button(text="GUARDAR", size_hint=(.3, .1), pos=(100, 50), \
            on_press=lambda a: self.modify(department.id, department_name.text, department_desc.text, family_select.text), \
                background_color="green"))


    def get_departments_by_family(self, llayout, family_id, rlayout):
        llayout.clear_widgets()
        rlayout.clear_widgets()

        family = session.query(Family).filter_by(id=family_id).first()
        departments = family.departments

        for dpt in departments:
            btn = Button(text=dpt.name, background_color="orange", height=50, size_hint_y=None)
            btn.id = dpt.id
            btn.bind(on_press=lambda a: self.change_department(llayout, a.id))
            rlayout.add_widget(btn)


    def reload_families(self):
        pass


    def create_family(self):
        self.manager.transition = NoTransition()
        self.manager.current = "New Family Screen"


    def create_department(self):
        self.manager.transition = NoTransition()
        self.manager.current = "New Department Screen"


    def go_to_previous(self):
        self.manager.transition = NoTransition()
        self.manager.current = "Options Screen"


    def on_press_family(self, btn, buttons):
        for but in buttons:
            but.background_color = "blue"

        btn.background_color = "green"
        self.family_active = btn.id


    def create_layout(self):
        layout = GridLayout(cols=2)

        left_layout = FloatLayout()
        right_layout = BoxLayout(orientation="vertical", size_hint=(.5, 1))
        
        right_bottom_layout = BoxLayout(orientation="horizontal", size_hint=(1, 1))

        families_layout = BoxLayout(orientation="vertical", size_hint_y=None)
        families_layout.bind(minimum_height=families_layout.setter('height'))

        departments_layout = BoxLayout(orientation="vertical", size_hint_y=None)
        departments_layout.bind(minimum_height=departments_layout.setter('height'))

        families = session.query(Family).all()

        for fam in families:
            btn = Button(text=fam.name, background_color="blue", height=50, size_hint_y=None)
            btn.id = fam.id
            btn.bind(on_press=lambda a: self.get_departments_by_family(left_layout, a.id, departments_layout))
            families_layout.add_widget(btn)

        scroll_families = ScrollView(size_hint=(.5, 1))
        scroll_families.add_widget(families_layout)

        scroll_departments = ScrollView(size_hint=(.5, 1))
        scroll_departments.add_widget(departments_layout)
        
        right_layout.add_widget(Button(text="MENÚ", size_hint=(1, .1), background_color="brown", \
            on_press=lambda a: self.go_to_previous()))
        
        right_layout.add_widget(Button(text="Crear familia", size_hint=(1, .1), background_color="brown", \
            on_press=lambda a: self.create_family()))
        
        right_layout.add_widget(Button(text="Crear departamento", size_hint=(1, .1), background_color="brown", \
            on_press=lambda a: self.create_department()))

        right_layout.add_widget(Button(text="Recargar familias", size_hint=(1, .1), background_color="brown", \
            on_press=lambda a: self.reload_families()))
        
        right_bottom_layout.add_widget(scroll_departments)
        right_bottom_layout.add_widget(scroll_families)
        layout.add_widget(left_layout)
        right_layout.add_widget(right_bottom_layout)
        layout.add_widget(right_layout)

        self.add_widget(layout) 

    
    def __init__(self, **kw):
        super(NewArticleScreen, self).__init__(**kw)

        self.create_layout()


class OptionsScreen(Screen):
    options = ["fam", "dpt", "art"]


    def save_dpt(self, name, description, family_name):
        """ Guardar nuevo departamento """
        
        if name != '':
            if family_name != 'FAMILIA':
                family = session.query(Family).filter_by(name=family_name).first()

                new_dpt = Department(name=name, description=description, family_id=family.id)
                session.add(new_dpt)
                session.commit()

                popup = Popup(title="AVISO", content=Label(text="Se ha añadido el departamento correctamente"), \
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
            self.add_on_release(btn, dropdown, layout, 'select')
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

                            popup = Popup(title="AVISO", content=Label(text="Se ha añadido el artículo correctamente"), \
                                size_hint=(None, None), size=(400, 100))
                            popup.open()
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


    def popup_delete_department(self, name):
        """ Crear popup para confirmar eliminación de departamento """        
        
        content_popup = None
        dismiss_btn = Button(text="Cancelar")
        
        if name != 'DEPARTAMENTO':
            content_popup = BoxLayout(orientation="vertical")
            content_popup.add_widget(Label(text="Se eliminará el departamento {}".format(name)))
            content_popup.add_widget(Button(text="Confirmar", on_press=lambda a: self.delete_department(name, popup)))
            content_popup.add_widget(dismiss_btn)
        else:
            content_popup = Label(text="Selecciona un departamento")

        popup = Popup(title="AVISO", content=content_popup, size_hint=(None, None), size=(400, 200))
        dismiss_btn.bind(on_press=popup.dismiss)
        popup.open()

    
    def popup_delete_article(self, name):
        """ Crear popup para confirmar eliminación de artículo """
        
        content_popup = None
        dismiss_btn = Button(text="Cancelar")

        if name != 'ARTÍCULO':
            content_popup = BoxLayout(orientation="vertical")
            content_popup.add_widget(Label(text="Se eliminará el artículo {}".format(name)))
            content_popup.add_widget(Button(text="Confirmar", on_press=lambda a: self.delete_article(name, popup)))
            content_popup.add_widget(dismiss_btn)
        else:
            content_popup = Label(text="Selecciona un artículo")

        popup = Popup(title="AVISO", content=content_popup, size_hint=(None, None), size=(400, 200))
        dismiss_btn.bind(on_press=popup.dismiss)
        popup.open()


    def del_dpt_art_layout(self, name, layout, drop):
        family = session.query(Family).filter_by(name=name).first()
        
        departments = session.query(Department).filter_by(family_id=family.id).all()

        dropdown = DropDown()
        dpt_count = 0
        for dpt in departments:
            if len(dpt.articles) > 0:
                btn = Button(text=dpt.name, background_color="pink", height=40, size_hint_y=None)
                self.add_on_release(btn, dropdown, layout, 'del-art')
                dropdown.add_widget(btn)
                dpt_count += 1

        if dpt_count > 0:
            layout.add_widget(Label(text="Departamentos disponibles:", size_hint=(.4, .1), pos=(400, 400)))

            dpt_select = Button(text="DEPARTAMENTO", size_hint=(.4, .1), pos=(400, 350), background_color="pink")
            dpt_select.bind(on_release=dropdown.open)
            dropdown.bind(on_select=lambda instance, x: setattr(dpt_select, 'text', x))
            layout.add_widget(dpt_select)
        else:
            layout.add_widget(Label(text="No hay departamentos con artículos", size_hint=(.4, .1), pos=(400, 400)))
        
        return drop.select(name)


    def del_art_layout(self, name, layout, drop):
        department = session.query(Department).filter_by(name=name).first()
        articles = session.query(Article).filter_by(department_id=department.id).all()

        dropdown = DropDown()
        art_count = 0
        for art in articles:
            btn = Button(text=art.name, background_color="pink", height=40, size_hint_y=None)
            self.add_on_release(btn, dropdown, layout, 'select')
            dropdown.add_widget(btn)
            art_count += 1

        if art_count > 0:
            layout.add_widget(Label(text="Artículos disponibles:", size_hint=(.4, .1), pos=(50, 300)))

            art_select = Button(text="ARTÍCULO", size_hint=(.4, .1), pos=(50, 250), background_color="pink")
            art_select.bind(on_release=dropdown.open)
            dropdown.bind(on_select=lambda instance, x: setattr(art_select, 'text', x))
            layout.add_widget(art_select)

            layout.add_widget(Button(text="ELIMINAR", size_hint=(.2, .1), pos=(300, 100), \
                on_press=lambda a: self.popup_delete_article(art_select.text), background_color="red"))
        else:
            layout.add_widget(Label(text="No hay artículos", size_hint=(.4, .1), pos=(100, 300)))

        return drop.select(name)


    def delete_article(self, name, popup):
        """ Eliminar artículo """
        
        article = session.query(Article).filter_by(name=name).first()
        session.delete(article)
        session.commit()

        popup.dismiss()


    def del_dpt_layout(self, name, layout, drop):
        family = session.query(Family).filter_by(name=name).first()
        departments = session.query(Department).filter_by(family_id=family.id).all()
        dropdown = DropDown()

        dpt_count = 0
        for dpt in departments:
            if len(dpt.articles) == 0:
                btn = Button(text=dpt.name, background_color="green", height=40, size_hint_y=None)
                self.add_on_release(btn, dropdown, layout, 'select')
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


    def delete_department(self, name, popup):
        """ Eliminar departamento """
        
        department = session.query(Department).filter_by(name=name).first()
        session.delete(department)
        session.commit()

        popup.dismiss()


    def mod_dpt_layout(self, name, layout, drop):
        family = session.query(Family).filter_by(name=name).first()

        dropdown = DropDown()
        for dpt in family.departments:
            btn = Button(text=dpt.name, size_hint_y=None, height=40, background_color="green")
            self.add_on_release(btn, dropdown, layout, 'chg-dpt-mod')
            dropdown.add_widget(btn)

        layout.add_widget(Label(text="Seleccionar departamento:", size_hint=(.4, .1), pos=(400, 400)))
        dpt_select = Button(text="DEPARTAMENTO", size_hint=(.4, .1), pos=(400, 350), background_color="green")
        dpt_select.bind(on_release=dropdown.open)
        dropdown.bind(on_select=lambda instance, x: setattr(dpt_select, 'text', x))

        layout.add_widget(dpt_select)

        return drop.select(name)

    
    def change_dpt_layout(self, name, layout, dropdown):
        department = session.query(Department).filter_by(name=name).first()
        family = session.query(Family).filter_by(id=department.family_id).first()

        layout.add_widget(Label(text="Editar nombre:", size_hint=(.4, .1), pos=(50, 250)))
        dpt_name = TextInput(text=department.name, size_hint=(.5, .1), pos=(50, 200))
        layout.add_widget(dpt_name)

        layout.add_widget(Label(text="Editar descripción:", size_hint=(.4, .1), pos=(50, 150)))
        dpt_desc = TextInput(text=department.description, size_hint=(.5, .2), pos=(50, 50))
        layout.add_widget(dpt_desc)

        layout.add_widget(Label(text="Editar familia:", size_hint=(.4, .1), pos=(500, 250)))
            
        families = session.query(Family).all()
        dropdown = DropDown()
            
        for fam in families:
            btn = Button(text=fam.name, size_hint_y=None, height=40, background_color="green")
            self.add_on_release(btn, dropdown, layout, 'select')
            dropdown.add_widget(btn)

        families_label = Button(text=family.name, size_hint=(.3, .1), pos=(500, 200), background_color="green")
        families_label.bind(on_release=dropdown.open)
        dropdown.bind(on_select=lambda instance, x: setattr(families_label, 'text', x))

        layout.add_widget(families_label)

        layout.add_widget(Button(text="GUARDAR", size_hint=(.3, .1), pos=(500, 50), background_color="green", \
            on_press=lambda a: self.mod_dpt(department.id, dpt_name.text, dpt_desc.text, families_label.text)))


    def mod_dpt(self, id, name, description, family_name):
        family = session.query(Family).filter_by(name=family_name).first()

        department = session.query(Department).filter_by(id=id).first()
        department.name = name
        department.description = description
        department.family_id = family.id
        session.commit()


    def mod_dpt_art_layout(self, name, layout, drop):
        family = session.query(Family).filter_by(name=name).first()

        dropdown = DropDown()
        dpt_count = 0
        for dpt in family.departments:
            if len(dpt.articles) > 0:
                btn = Button(text=dpt.name, background_color="pink", height=40, size_hint_y=None)
                self.add_on_release(btn, dropdown, layout, 'art-mod')
                dropdown.add_widget(btn)
                dpt_count += 1

        if dpt_count > 0:
            layout.add_widget(Label(text="Selecciona un departamento:", size_hint=(.4, .1), pos=(400, 400)))
            dpt_select = Button(text="DEPARTAMENTO", size_hint=(.4, .1), pos=(400, 350), background_color="pink")
            dpt_select.bind(on_release=dropdown.open)
            dropdown.bind(on_select=lambda instance, x: setattr(dpt_select, 'text', x))

            layout.add_widget(dpt_select)
        else:
            layout.add_widget(Label(text="No hay departamentos con artículos", size_hint=(.4, .1), pos=(400, 400)))

        return drop.select(name)


    def mod_art_layout(self, name, layout, drop):
        department = session.query(Department).filter_by(name=name).first()

        dropdown = DropDown()
        for art in department.articles:
            btn = Button(text=art.name, height=40, size_hint_y=None, background_color="pink")
            self.add_on_release(btn, dropdown, layout, 'chg-art-mod')
            dropdown.add_widget(btn)

        layout.add_widget(Label(text="Selecciona un artículo:", size_hint=(.4, .1), pos=(50, 300)))
        art_select = Button(text="ARTÍCULO", size_hint=(.4, .1), pos=(50, 250), background_color="pink")
        art_select.bind(on_release=dropdown.open)
        dropdown.bind(on_select=lambda instance, x: setattr(art_select, 'text', x))

        layout.add_widget(art_select)

        return drop.select(name)


    def change_art_layout(self, name, layout, drop):
        article = session.query(Article).filter_by(name=name).first()
        iva_type = session.query(Iva).filter_by(id=article.iva_type).first()
        iva_types = session.query(Iva).all()
        departments = session.query(Department).all()
        
        layout.add_widget(Label(text="Editar nombre:", size_hint=(.4, .1), pos=(400, 300)))

        name_art = TextInput(text=article.name, size_hint=(.4, .1), pos=(400, 250))
        layout.add_widget(name_art)

        layout.add_widget(Label(text="Editar precio:", size_hint=(.3, .1), pos=(400, 200)))

        price_art = TextInput(text=str(article.price), size_hint=(.2, .1), pos=(400, 150))
        layout.add_widget(price_art)

        layout.add_widget(Label(text="Editar descripción:", size_hint=(.4, .1), pos=(50, 150)))

        desc_art = TextInput(text=article.description, size_hint=(.4, .2), pos=(50, 50))
        layout.add_widget(desc_art)

        dropdown_iva = DropDown()
        for type in iva_types:
            btn = Button(text=str(type.type)+'%', size_hint_y=None, height=40, background_color="pink")
            self.add_on_release(btn, dropdown_iva, layout, 'select')
            dropdown_iva.add_widget(btn)

        layout.add_widget(Label(text="Porcentaje de IVA:", size_hint=(.2, .1), pos=(400, 100)))
        iva_select = Button(text=str(iva_type.type)+'%', size_hint=(.2, .1), pos=(400, 50), background_color="pink")
        iva_select.bind(on_release=dropdown_iva.open)
        dropdown_iva.bind(on_select=lambda instance, x: setattr(iva_select, 'text', x))
        layout.add_widget(iva_select)

        dropdown_dpt = DropDown()
        for dpt in departments:
            btn = Button(text=dpt.name, size_hint_y=None, height=40, background_color="pink")
            self.add_on_release(btn, dropdown_dpt, layout, 'select')
            dropdown_dpt.add_widget(btn)

        layout.add_widget(Label(text="Editar departamento:", size_hint=(.2, .1), pos=(600, 200)))
        dpt_select = Button(text=article.department.name, size_hint=(.2, .1), pos=(600, 150), background_color="pink")
        dpt_select.bind(on_release=dropdown_dpt.open)
        dropdown_dpt.bind(on_select=lambda instance, x: setattr(dpt_select, 'text', x))
        layout.add_widget(dpt_select)

        layout.add_widget(Button(text="GUARDAR", size_hint=(.2, .1), pos=(600, 50), \
            on_press=lambda a: self.mod_art(article.id, name_art.text, desc_art.text, price_art.text, \
                iva_select.text, dpt_select.text), background_color="green"))
        

        return drop.select(name)

    
    def mod_art(self, id, name, description, price, iva, department_name):
        department = session.query(Department).filter_by(name=department_name).first()
        iva = int(iva.replace('%', ''))
        iva_type = session.query(Iva).filter_by(type=iva).first()
        article = session.query(Article).filter_by(id=id).first()
        article.name = name
        article.description = description
        article.price = float(price)
        article.department_id = department.id
        article.iva_type = iva_type.id

        session.commit()


    def add_on_release(self, btn, dropdown, layout, option):
        """ Añadir evento a un Dropdown """
        
        if option == 'select':
            btn.bind(on_release=lambda a: dropdown.select(btn.text))
        elif option == 'fam-art':
            btn.bind(on_release=lambda a: self.add_dpt_by_fam(btn.text, layout, dropdown))
        elif option == 'art':
            btn.bind(on_release=lambda a: self.new_article(btn.text, layout, dropdown))
        elif option == 'fam-dpt-del':
            btn.bind(on_release=lambda a: self.del_dpt_layout(btn.text, layout, dropdown))
        elif option == 'dpt-art-del':
            btn.bind(on_release=lambda a: self.del_dpt_art_layout(btn.text, layout, dropdown))
        elif option == 'del-art':
            btn.bind(on_release=lambda a: self.del_art_layout(btn.text, layout, dropdown))
        elif option == 'dpt-mod':
            btn.bind(on_release=lambda a: self.mod_dpt_layout(btn.text, layout, dropdown))
        elif option == 'chg-dpt-mod':
            btn.bind(on_release=lambda a: self.change_dpt_layout(btn.text, layout, dropdown))
        elif option == 'dpt-art-mod':
            btn.bind(on_release=lambda a: self.mod_dpt_art_layout(btn.text, layout, dropdown))
        elif option == 'art-mod':
            btn.bind(on_release=lambda a: self.mod_art_layout(btn.text, layout, dropdown))
        elif option == 'chg-art-mod':
            btn.bind(on_release=lambda a: self.change_art_layout(btn.text, layout, dropdown))

    
    def add_dpt_by_fam(self, fam_name, layout, drop):
        """ Añadir lista de departamentos """
        
        family = session.query(Family).filter_by(name=fam_name).first()

        departments = session.query(Department).filter_by(family_id=family.id).all()

        dropdown = DropDown()
        dpt_count = 0
        for dpt in departments:
            btn = Button(text=dpt.name, size_hint_y=None, height=40, background_color="pink")
            self.add_on_release(btn, dropdown, layout, 'art')
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
            self.manager.transition = NoTransition()
            self.manager.current = "Main Screen"

    
    def change_last_opt(self, opt, layout):
        """ Seleccionar operación """
        
        layout.clear_widgets()

        if opt == 'add-fam':
            if self.new_family.name in self.manager.screen_names:
                self.manager.remove_widget(self.new_family)
                self.new_family = NewFamilyScreen(name="New Family Screen")
                self.manager.add_widget(self.new_family)
            else:
                self.manager.add_widget(self.new_family)
            self.manager.transition = NoTransition()
            self.manager.current = "New Family Screen"
        elif opt == 'add-dpt':
            if self.new_department.name in self.manager.screen_names:
                self.manager.remove_widget(self.new_department)
                self.new_department = NewDepartmentScreen(name="New Department Screen")
                self.manager.add_widget(self.new_department)
            else:
                self.manager.add_widget(self.new_department)
            
            self.manager.transition = NoTransition()
            self.manager.current = "New Department Screen"
        elif opt == 'add-art':
            self.manager.transition = NoTransition()
            self.manager.current = "New Article Screen"
            #families = session.query(Family).all()
            
            #if len(families) > 0:
            #    dropdown = DropDown()
            #    for fam in families:
            #        btn = Button(text=fam.name, size_hint_y=None, height=40, background_color="pink")
            #        self.add_on_release(btn, dropdown, layout, 'fam-art')
            #        dropdown.add_widget(btn)

            #    layout.add_widget(Label(text="Seleccionar familia:", size_hint=(.5, .1), pos=(0, 400)))
            #    families_label = Button(text="FAMILIA", size_hint=(.4, .1), pos=(50, 350), background_color="pink")
            #    families_label.bind(on_release=dropdown.open)
            #    dropdown.bind(on_select=lambda instance, x: setattr(families_label, 'text', x))
                
            #    layout.add_widget(families_label)
            #else:
            #    layout.add_widget(Label(text="No hay familias creadas", size_hint=(.5, .1), pos=(0, 400)))
        elif opt == 'mod-fam':
            if self.mod_family.name in self.manager.screen_names:
                self.manager.remove_widget(self.mod_family)
                self.mod_family = ModifyFamilyScreen(name="Modify Family Screen")
                self.manager.add_widget(self.mod_family)
            else:
                self.manager.add_widget(self.mod_family)
            
            self.manager.transition = NoTransition()
            self.manager.current = "Modify Family Screen"
        elif opt == 'mod-dpt':
            if self.mod_department.name in self.manager.screen_names:
                self.manager.remove_widget(self.mod_department)
                self.mod_department = ModifyDepartmentScreen(name="Modify Department Screen")
                self.manager.add_widget(self.mod_department)
            else:
                self.manager.add_widget(self.mod_department)
            
            self.manager.transition = NoTransition()
            self.manager.current = "Modify Department Screen"
        elif opt == 'mod-art':
            families = session.query(Family).all()

            if len(families) > 0:
                fam_count = 0
                dropdown = DropDown()
                for fam in families:
                    if len(fam.departments) > 0:
                        btn = Button(text=fam.name, height=40, background_color="pink", size_hint_y=None)
                        self.add_on_release(btn, dropdown, layout, 'dpt-art-mod')
                        dropdown.add_widget(btn)
                        fam_count += 1

                if fam_count > 0:
                    layout.add_widget(Label(text="Selecciona familia:", size_hint=(.4, .1), pos=(50, 400)))
                    fam_select = Button(text="FAMILIA", size_hint=(.4, .1), pos=(50, 350), background_color="pink")
                    fam_select.bind(on_release=dropdown.open)
                    dropdown.bind(on_select=lambda instance, x: setattr(fam_select, 'text', x))

                    layout.add_widget(fam_select)
                else:
                    layout.add_widget(Label(text="No hay familias con departamentos", size_hint=(.5, .1), pos=(400, 400)))
            else:
                layout.add_widget(Label(text="No hay familias", size_hint=(.5, .1), pos=(100, 400)))
        elif opt == 'del-fam':
            if self.del_family.name in self.manager.screen_names:
                self.manager.remove_widget(self.del_family)
                self.del_family = DeleteFamilyScreen(name="Delete Family Screen")
                self.manager.add_widget(self.del_family)
            else:
                self.manager.add_widget(self.del_family)
            
            self.manager.transition = NoTransition()
            self.manager.current = "Delete Family Screen"
        elif opt == 'del-dpt':
            if self.del_department.name in self.manager.screen_names:
                self.manager.remove_widget(self.del_department)
                self.del_department = DeleteDepartmentScreen(name="Delete Department Screen")
                self.manager.add_widget(self.del_department)
            else:
                self.manager.add_widget(self.del_department)
            
            self.manager.transition = NoTransition()
            self.manager.current = "Delete Department Screen"
        else:
            families = session.query(Family).all()

            dropdown = DropDown()
            fam_count = 0
            for fam in families:
                if len(fam.departments) > 0:
                    btn = Button(text=fam.name, size_hint_y=None, height=40, background_color="pink")
                    self.add_on_release(btn, dropdown, layout, 'dpt-art-del')
                    dropdown.add_widget(btn)
                    fam_count += 1

            if fam_count > 0:
                layout.add_widget(Label(text="Familias disponibles:", size_hint=(.4, .1), pos=(50, 400)))
                fam_select = Button(text="FAMILIA", size_hint=(.4, .1), pos=(50, 350), background_color="pink")
                fam_select.bind(on_release=dropdown.open)
                dropdown.bind(on_select=lambda instance, x: setattr(fam_select, 'text', x))

                layout.add_widget(fam_select)
            else:
                layout.add_widget(Label(text="No hay familias con departamentos", size_hint=(.5, .1), pos=(0, 400)))
    

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
        
        self.new_family = NewFamilyScreen(name="New Family Screen")
        self.new_department = NewDepartmentScreen(name="New Department Screen")
        self.new_art = NewArticleScreen(name="New Article Screen")
        
        self.mod_family = ModifyFamilyScreen(name="Modify Family Screen")
        self.mod_department = ModifyDepartmentScreen(name="Modify Department Screen")

        self.del_family = DeleteFamilyScreen(name="Delete Family Screen")
        self.del_department = DeleteDepartmentScreen(name="Delete Department Screen")
        
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

        self.add_widget(main_layout)


    def change_screen(self):
        self.screen = OptionsScreen(name="Options Screen")
        self.manager.add_widget(self.screen)
        self.manager.transition = NoTransition()
        self.manager.current = "Options Screen"


    def __init__(self, **kw):
        super(MainScreen, self).__init__(**kw)

        self.departments = session.query(Department).all()
        self.create_layout()


class LoginScreen(Screen):
    def add_number(self, num: str, txt, username, password):
        #if touch.button == 'right':
        #    print('right')
        #elif touch.button == 'left':
        #    print('left')
        
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

                self.manager.add_widget(MainScreen(name="Main Screen"))
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

        buttons = ["7", "8", "9", "4", "5", "6", "1", "2", "3", "0"]
        actions = ["Confirmar", "Cancelar"]
        
        #right_layout.add_widget(Button(text="7", \
        #    on_touch_down=lambda instance, a: self.add_number(instance, a, "8", txt, username, password)))

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


    def __init__(self, **kw):
        super(LoginScreen, self).__init__(**kw)

        self.create_layout()


class LongpressButton(Button):
    __events__ = ('on_long_press', )

    long_press_time = NumericProperty(1)
    
    def on_state(self, instance, value):
        if value == 'down':
            lpt = self.long_press_time
            self._clockev = Clock.schedule_once(self._do_long_press, lpt)
        else:
            self._clockev.cancel()

    def _do_long_press(self, dt):
        self.dispatch('on_long_press')
        
    def on_long_press(self, *largs):
        pass

    #self.add_widget(LongpressButton(
    #        long_press_time=1,
    #        on_press=lambda w: setattr(w, 'text', 'short press!'),
    #        on_long_press=lambda w: setattr(w, 'text', 'long press!')))


class Main2App(App):
    def __init__(self, **kwargs):
        super(Main2App, self).__init__(**kwargs)


    def build(self):
        root = ScreenManager()
        root.transition = NoTransition()
        
        root.add_widget(ModifyDepartmentScreen(name="Modify Department Screen"))
        #root.add_widget(LoginScreen(name="Login Screen"))
        #root.add_widget(MainScreen(name="Main Screen"))
        #root.add_widget(OptionsScreen(name="Options Screen"))
        #root.add_widget(NewFamilyScreen(name="New Family Screen"))
        #root.add_widget(ModifyFamilyScreen(name="Modify Family Screen"))
        #root.add_widget(DeleteFamilyScreen(name="Delete Family Screen"))
        #root.add_widget(NewDepartmentScreen(name="New Department Screen"))
        #root.add_widget(ModifyDepartmentScreen(name="Modify Department Screen"))
        #root.add_widget(DeleteDepartmentScreen(name="Delete Department Screen"))
        #root.add_widget(NewArticleScreen(name="New Article Screen"))
        
        return root


if __name__ == '__main__':
    create_db()
    
    Main2App().run()