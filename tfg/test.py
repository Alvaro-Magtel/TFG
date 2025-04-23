import threading

import flet as ft
import flet_map as fmap
import requests


def main(page: ft.Page):
    marker_layer_ref = ft.Ref[fmap.MarkerLayer]()
    location_text = ft.Text("Click on the map or search to find a location")
    search_timer = None  # Temporizador para el debounce

    def perform_search(location: str):
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

                marker_layer_ref.current.markers = [
                    fmap.Marker(
                        content=ft.Icon(
                            ft.Icons.LOCATION_ON,
                            color=ft.CupertinoColors.DESTRUCTIVE_RED,
                        ),
                        coordinates=coordinates,
                    )
                ]

                page.controls[-1].center_on(coordinates, zoom=12)
                location_text.value = f"Found: {data[0].get('display_name', 'Unknown')}"
            else:
                location_text.value = "Location not found."

        except Exception as ex:
            location_text.value = f"Error: {ex}"

        page.update()

    def search_location(e):
        nonlocal search_timer

        location = e.control.value

        if search_timer:
            search_timer.cancel()

        # Espera 0.6 segundos después de la última tecla antes de buscar
        search_timer = threading.Timer(0.6, lambda: perform_search(location))
        search_timer.start()

    def handle_map_click(e: fmap.MapTapEvent):
        coordinates = e.coordinates
        lat, lon = coordinates.latitude, coordinates.longitude

        marker_layer_ref.current.markers = [
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
            location_name = data.get("display_name", "Unknown location")
            location_text.value = f"Clicked location: {location_name}"
        except Exception as ex:
            location_text.value = f"Reverse geocoding error: {ex}"

        page.update()

    page.add(
        ft.Text("Search or click to identify a place on the map."),
        ft.TextField(label="Search for a place", on_change=search_location),
        location_text,
        fmap.Map(
            expand=True,
            initial_center=fmap.MapLatitudeLongitude(15, 10),
            initial_zoom=4.2,
            layers=[
                fmap.TileLayer(url_template="https://tile.openstreetmap.org/{z}/{x}/{y}.png"),
                fmap.MarkerLayer(ref=marker_layer_ref, markers=[]),
            ],
            on_tap=handle_map_click,
        ),
    )


ft.app(main)
