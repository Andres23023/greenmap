import flet as ft
from flet.map import Map, MarkerLayer, CircleLayer, MapConfiguration, MapLatitudeLongitude, MapInteractiveFlag
from database import localitation, firebase_db

class Mapa(ft.Container):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.expand = True
        self.allowed_bounds = {"north": 18.630, "south": 17.015, "west": -94.718, "east": -90.500}
        self.initial_center = MapLatitudeLongitude(17.989, -92.933)
        self.marker_layer_ref = ft.Ref[MarkerLayer]()
        self.circle_layer_ref = ft.Ref[CircleLayer]()
        self.locations = []
        self.create_map()

    def create_map(self):
        """Inicializa el mapa."""
        self.map_instance = Map(
            expand=True,
            configuration=MapConfiguration(
                initial_center=self.initial_center,
                initial_zoom=9,
                interaction_configuration=ft.map.MapInteractionConfiguration(flags=MapInteractiveFlag.ALL),
                on_event=self.handle_move
            ),
            layers=[
                ft.map.TileLayer(
                    url_template="https://tile.openstreetmap.org/{z}/{x}/{y}.png",
                    on_image_error=lambda e: print("TileLayer Error"),
                ),
                MarkerLayer(ref=self.marker_layer_ref, markers=[]),
                CircleLayer(ref=self.circle_layer_ref, circles=[])
            ]
        )
        self.content = self.map_instance
        

    def check_bounds(self, lat, lng):
        return self.allowed_bounds["south"] <= lat <= self.allowed_bounds["north"] and self.allowed_bounds["west"] <= lng <= self.allowed_bounds["east"]

    def handle_move(self, e):
        lat_lng = e.center
        if not self.check_bounds(lat_lng.latitude, lat_lng.longitude):
            print(f"Fuera de límites: {lat_lng.latitude}, {lat_lng.longitude}")
            self.create_map()
            self.load_markers()
            self.update()

    def load_markers(self):
        """Carga los marcadores desde Firebase."""
        locations = firebase_db.get('/localizaciones', None)
        if locations:
            for key, value in locations.items():
                marker = ft.map.Marker(
                    content=ft.Icon(ft.icons.LOCATION_ON, color=ft.cupertino_colors.DESTRUCTIVE_RED),
                    coordinates=MapLatitudeLongitude(value['latitud'], value['longitud'])
                )
                marker.key = key
                self.marker_layer_ref.current.markers.append(marker)
            self.update()

    def add_marker(self, coordinates: MapLatitudeLongitude, tipo: str, descripcion: str):
        """Agrega un marcador al mapa y guarda la localización en la base de datos."""
        marker = ft.map.Marker(
            content=ft.Icon(ft.icons.LOCATION_ON, color=ft.cupertino_colors.DESTRUCTIVE_RED),
            coordinates=coordinates
        )
        self.marker_layer_ref.current.markers.append(marker)
        new_location = localitation(coordinates.latitude, coordinates.longitude, descripcion, tipo)
        new_location.save()
        self.update()

    def get_locations(self):
        """Obtiene las ubicaciones desde Firebase."""
        locations = firebase_db.get('/localizaciones', None)
        if locations:
            return [
                {
                    'latitud': loc.get('latitud', 0),
                    'longitud': loc.get('longitud', 0),
                    'tipo': loc.get('tipo', 'Desconocido'),
                    'descripcion': loc.get('descripcion', 'Sin descripción')
                } for loc in locations.values()
            ]
        return []

    def update_marker(self, coordinates: MapLatitudeLongitude, tipo: str, descripcion: str):
        """Actualiza un marcador en el mapa y también actualiza la base de datos con la nueva información."""
        marker_found = None
        for marker in self.marker_layer_ref.current.markers:
            if marker.coordinates.latitude == coordinates.latitude and marker.coordinates.longitude == coordinates.longitude:
                marker_found = marker
                break
        if marker_found:
            marker_found.content = ft.Icon(ft.icons.LOCATION_ON, color=ft.cupertino_colors.DESTRUCTIVE_RED)
            locations = firebase_db.get('/localizaciones', None)
            if locations:
                for key, value in locations.items():
                    if value['latitud'] == coordinates.latitude and value['longitud'] == coordinates.longitude:
                        print(f"Actualizando marcador {key} en Firebase.")
                        firebase_db.put('/localizaciones', key, {
                            'latitud': coordinates.latitude,
                            'longitud': coordinates.longitude,
                            'tipo': tipo,
                            'descripcion': descripcion
                        })
                        break
            self.update()
        else:
            print(f"No se encontró un marcador en {coordinates.latitude}, {coordinates.longitude}")

    def ubicacion(self, lat, lng, zoom=12):
        """Recarga el mapa y centra en la ubicación especificada con el zoom deseado."""
        # Creamos nuevamente el mapa para forzar el centrado y el zoom
        self.map_instance = Map(
            expand=True,
            configuration=MapConfiguration(
                initial_center=MapLatitudeLongitude(lat, lng),
                initial_zoom=zoom,
                interaction_configuration=ft.map.MapInteractionConfiguration(flags=MapInteractiveFlag.ALL),
                on_event=self.handle_move
            ),
            layers=[
                ft.map.TileLayer(
                    url_template="https://tile.openstreetmap.org/{z}/{x}/{y}.png",
                    on_image_error=lambda e: print("TileLayer Error"),
                ),
                MarkerLayer(ref=self.marker_layer_ref, markers=self.marker_layer_ref.current.markers),
                CircleLayer(ref=self.circle_layer_ref, circles=[])
            ]
        )
        self.content = self.map_instance  # Actualiza el contenido del contenedor con el nuevo mapa
        self.update()  # Refresca el mapa para aplicar los cambios

