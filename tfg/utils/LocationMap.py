import threading
from typing import Callable, Optional

import flet as ft
import flet_map as fmap
import requests
from flet.core.ref import Ref


class LocationMap(ft.Column):
    """
    A custom map control that allows searching and marking locations using Flet Map and Nominatim API.
    Includes a close button that emits a callback when clicked.
    """

    def __init__(
        self,
        ref: Optional[Ref] = None,
        location_text: Optional[str] = "Click on the map or search to find a location",
        initial_lat: float = 15,
        initial_lon: float = 10,
        initial_zoom: float = 4.2,
        search_debounce_time: float = 0.6,
        on_location_select: Optional[Callable[[float, float], None]] = None,
        on_close: Optional[Callable[[], None]] = None,
        **kwargs,
    ):
        super().__init__(ref=ref, **kwargs)

        self.location_text = location_text
        self.marker_layer_ref = ft.Ref[fmap.MarkerLayer]()
        self.search_timer = None
        self.initial_lat = initial_lat
        self.initial_lon = initial_lon
        self.initial_zoom = initial_zoom
        self.search_debounce_time = search_debounce_time
        self.on_location_select = on_location_select
        self.on_close = on_close
        self.location_name = "Ubicación desconocida"
        self.location_display = ft.Text(self.location_text)
        self.search_field = ft.TextField(label="Search for a place", on_change=self.search_location)
        self.map_control = fmap.Map(
            expand=True,
            initial_center=fmap.MapLatitudeLongitude(self.initial_lat, self.initial_lon),
            initial_zoom=self.initial_zoom,
            layers=[
                fmap.TileLayer(url_template="https://tile.openstreetmap.org/{z}/{x}/{y}.png"),
                fmap.MarkerLayer(ref=self.marker_layer_ref, markers=[]),
            ],
            on_tap=self.handle_map_click,
        )
        # Ahora lo envolvemos en un Container
        map_container = ft.Container(
            content=self.map_control,
            height=300,  # Altura definida para que se vea bien
            expand=True,
        )

        # Finalmente, usamos el contenedor en lugar del map_control directamente
        self.controls = [
            ft.Text("Buscar o haz clic en el mapa para identificar un lugar."),
            self.search_field,
            self.location_display,
            map_container,
        ]

    def perform_search(self, location: str):
        url = "https://nominatim.openstreetmap.org/search"
        params = {"q": location, "format": "json", "limit": 1}

        try:
            response = requests.get(
                url,
                params=params,
                headers={"User-Agent": "flet-app"},
                timeout=5,
            )
            data = response.json()

            if data:
                lat = float(data[0]["lat"])
                lon = float(data[0]["lon"])
                coordinates = fmap.MapLatitudeLongitude(lat, lon)

                self.marker_layer_ref.current.markers = [
                    fmap.Marker(
                        content=ft.Icon(
                            ft.Icons.LOCATION_ON,
                            color=ft.CupertinoColors.DESTRUCTIVE_RED,
                        ),
                        coordinates=coordinates,
                    )
                ]

                self.map_control.center_on(coordinates, zoom=12)
                self.location_display.value = f"Encontrado: {data[0].get('display_name', 'Desconocido')}"
                self.location_name = data[0].get("display_name", "Desconocido")
            else:
                self.location_display.value = "Ubicación no encontrada."

        except Exception as ex:
            self.location_display.value = f"Error: {ex}"

        if self.on_location_select:
            self.on_location_select()

        self.update()

    def search_location(self, e):
        if self.search_timer:
            self.search_timer.cancel()

        location = e.control.value
        self.search_timer = threading.Timer(self.search_debounce_time, lambda: self.perform_search(location))
        self.search_timer.start()

    def handle_map_click(self, e: fmap.MapTapEvent):
        coordinates = e.coordinates
        lat, lon = coordinates.latitude, coordinates.longitude

        self.marker_layer_ref.current.markers = [
            fmap.Marker(
                content=ft.Icon(
                    ft.Icons.LOCATION_ON,
                    color=ft.CupertinoColors.DESTRUCTIVE_RED,
                ),
                coordinates=coordinates,
            )
        ]

        url = "https://nominatim.openstreetmap.org/reverse"
        params = {"lat": lat, "lon": lon, "format": "json"}

        try:
            response = requests.get(
                url,
                params=params,
                headers={"User-Agent": "flet-app"},
                timeout=5,
            )
            data = response.json()
            self.location_name = data.get("display_name", "Ubicación desconocida")
            self.location_display.value = f"Ubicación seleccionada: {self.location_name}"
        except Exception as ex:
            self.location_display.value = f"Error de geocodificación inversa: {ex}"

        if self.on_location_select:
            self.on_location_select()

        self.update()

    def close(self, e):
        if self.on_close:
            self.on_close()
