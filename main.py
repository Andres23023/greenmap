# main.py
import flet as ft
from flet.map import MapLatitudeLongitude
from map import Mapa
from database import firebase_db

def main(page: ft.Page):
    def clear_fields():
        """Limpia los campos de entrada del formulario."""
        latitud_field.value = ""
        longitud_field.value = ""
        tipo_dropdown.value = None  # Selección vacía en el dropdown
        descripcion_field.value = ""
        page.update()  # Actualiza la página para reflejar los cambios

    # def switch_page():
    #     page.controls.clear()
    #     BIOWATT.main(page)
    #     page.update()

    def populate_fields(lat, lng, tipo, desc):
        """Rellena los campos de entrada con los datos del marcador seleccionado y centra el mapa."""
        latitud_field.value, longitud_field.value = str(lat), str(lng)
        tipo_dropdown.value, descripcion_field.value = tipo, desc
        mapa.ubicacion(lat, lng, zoom=12)  # Llama al método en `map.py` para centrar el mapa
        page.update()


    def show_snackbar(message):
        """Muestra un mensaje temporal en la pantalla."""
        snackbar = ft.SnackBar(ft.Text(message))
        page.add(snackbar)
        snackbar.open = True
        page.update()

    def validate_coordinates():
        """Valida que las coordenadas sean números y estén completas."""
        try:
            lat, lng = float(latitud_field.value), float(longitud_field.value)
            return lat, lng
        except ValueError:
            show_snackbar("Las coordenadas deben ser números válidos.")
            return None, None

    # Configurar la ventana
    page.title, page.window.width, page.window.height = "Bioenergías en Tabasco", 1200, 800
    page.theme_mode = "light"
    
    mapa = Mapa(page)

    # Campos de entrada
    latitud_field = ft.TextField(label="Latitud", read_only=True)
    longitud_field = ft.TextField(label="Longitud", read_only=True)
    tipo_dropdown = ft.Dropdown(label="Tipo", options=[
        ft.dropdown.Option("Bagazo de caña de azúcar"),
        ft.dropdown.Option("Plátano"),
        ft.dropdown.Option("Cacao"),
        ft.dropdown.Option("Palma de aceite")
    ])
    descripcion_field = ft.TextField(label="Descripción")

    # Tabla para mostrar los marcadores
    markers_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Latitud")),
            ft.DataColumn(ft.Text("Longitud")),
            ft.DataColumn(ft.Text("Tipo")),
            ft.DataColumn(ft.Text("Descripción")),
            ft.DataColumn(ft.Text("Acciones")),
        ],
        rows=[]
    )

    def handle_map_click(e):
        if e.name == "tap":
            latitud_field.value, longitud_field.value = str(e.coordinates.latitude), str(e.coordinates.longitude)

    mapa.map_instance.configuration.on_tap = handle_map_click

    def add_marker():
        """Función para agregar un marcador al mapa."""
        lat, lng = validate_coordinates()
        if lat is not None and lng is not None:
            mapa.add_marker(
                MapLatitudeLongitude(lat, lng),
                tipo=tipo_dropdown.value,
                descripcion=descripcion_field.value
            )
            load_markers_table()
            clear_fields()
        else:
            dlg=ft.AlertDialog(
                title=ft.Text("Por favor, completa la latitud y longitud", color="red"), bgcolor="white",
                actions=[ft.ElevatedButton("Cerrar", bgcolor="red", on_click=lambda e: page.close(dlg))],
                modal=True
            )
        

    def update_marker():
        """Función para actualizar un marcador existente en el mapa."""
        lat, lng = validate_coordinates()  # Validamos las coordenadas
        if lat is not None and lng is not None:
            if tipo_dropdown.value and descripcion_field.value:  # Validar que los campos no estén vacíos
                mapa.update_marker(
                    MapLatitudeLongitude(lat, lng),
                    tipo=tipo_dropdown.value,
                    descripcion=descripcion_field.value
                )
                load_markers_table()
                show_snackbar("Marcador actualizado correctamente.")
            else:
                dlg=ft.AlertDialog(
                    title=ft.Text("Por favor, completa todos los campos antes de actualizar el marcador.", color="red"), bgcolor="white",
                    actions=[ft.ElevatedButton("Cerrar", bgcolor="red", on_click=lambda e: page.close(dlg))],
                    modal=True
                )
        else:
            dlg=ft.AlertDialog(
                title=ft.Text("Coordenadas inválidas. Por favor, revisa los campos de latitud y longitud.", color="red"), bgcolor="white",
                actions=[ft.ElevatedButton("Cerrar", bgcolor="red", on_click=lambda e: page.close(dlg))],
                modal=True
            )
        clear_fields()

    def load_markers_table():
        """Carga los marcadores en la tabla desde la clase Mapa."""
        locations = mapa.get_locations()
        markers_table.rows = [
            ft.DataRow(cells=[
                ft.DataCell(ft.Text(str(loc['latitud']))),
                ft.DataCell(ft.Text(str(loc['longitud']))),
                ft.DataCell(ft.Text(loc['tipo'])),
                ft.DataCell(ft.Text(loc['descripcion'])),
                ft.DataCell(
                    ft.Row(controls=[
                        ft.IconButton(
                            icon=ft.icons.VISIBILITY,
                            on_click=lambda e, loc=loc: populate_fields(loc['latitud'], loc['longitud'], loc['tipo'], loc['descripcion'])
                        ),
                        ft.IconButton(
                            icon=ft.icons.CLOSE,
                            on_click=lambda e, loc=loc: delete_marker(loc)  # Función para eliminar el marcador
                        )
                    ])
                )
            ]) for loc in locations
        ]
        page.update()

    def delete_marker(loc):
        """Elimina un marcador de Firebase y actualiza la tabla."""
        locations = firebase_db.get('/localizaciones', None)
        if locations:
            for key, value in locations.items():
                if value['latitud'] == loc['latitud'] and value['longitud'] == loc['longitud']:
                    # Eliminar el marcador de Firebase
                    firebase_db.delete('/localizaciones', key)
                    show_snackbar(f"Marcador en {loc['latitud']}, {loc['longitud']} eliminado.")
                    load_markers_table()
                    mapa.create_map()
                    mapa.load_markers()
                    clear_fields()
                    break

    
        
        
    # Agregar controles a la página
    page.add(
        ft.Column(
            expand=True,
            controls=[
                ft.Row(
                    expand=True,
                    controls=[
                        ft.Column(
                            width=320,
                            controls=[
                                ft.Text("AGREGAR / ACTUALIZAR"),
                                tipo_dropdown, latitud_field, longitud_field, descripcion_field,
                                ft.Column(
                                    controls=[
                                        ft.ElevatedButton("Agregar", on_click=lambda e: add_marker(),width=200,color="white",bgcolor="green"),
                                        ft.ElevatedButton("Actualizar", on_click=lambda e: update_marker(),width=200,color="white",bgcolor="blue"),
                                        ft.ElevatedButton("Cerrar", on_click=lambda e: page.window.close(),width=200,color="white",bgcolor="red")
                                        # ft.IconButton(icon=ft.icons.CALCULATE,on_click=lambda e:(
                                        #     page.controls.clear(),
                                        #     calculadora.calc(page),
                                        #     page.update()
                                        #     ),width=200)
                                    ]
                                )
                            ],
                            horizontal_alignment="center"
                        ),
                        ft.Container(
                            expand=True, content=mapa
                        )
                    ]
                ),
                ft.Container(
                    expand=False,
                    content=markers_table,
                    bgcolor=ft.colors.LIGHT_BLUE_50,
                    alignment=ft.alignment.center
                )
            ]
        )
    )

    # Cargar marcadores
    mapa.load_markers()
    load_markers_table()

# ft.app(target=main)

ft.app(target=main, view=ft.AppView.WEB_BROWSER)
