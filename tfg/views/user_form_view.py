import datetime

import flet as ft

from tfg.components.top_app_bar import top_app_bar
from tfg.utils.LocationMap import LocationMap


def user_form_view(page: ft.Page):
    user_name = ft.TextField(label="Name", width=300, value=getattr(page, "user_name", ""))

    language = ft.TextField(label="Language", width=300, value=getattr(page, "language", ""))
    birthday_value = getattr(page, "birthday", "Not selected")
    birthday_label = ft.Text(f"Birthday: {birthday_value}", size=16)

    def handle_date_change(e):
        selected_date = e.control.value.strftime("%Y-%m-%d")
        page.birthday = selected_date
        birthday_label.value = f"Birthday: {selected_date}"
        birthday_label.update()

    birthday_button = ft.ElevatedButton(
        "Pick Birthday",
        icon=ft.Icons.CALENDAR_MONTH,
        on_click=lambda e: page.open(
            ft.DatePicker(
                first_date=datetime.datetime(year=1900, month=1, day=1),
                last_date=datetime.datetime(year=2100, month=12, day=31),
                on_change=handle_date_change,
            )
        ),
    )

    submit_button = ft.ElevatedButton("Submit", on_click=lambda e: page.go("/search_series"))

    # Callback para manejar la selección de ubicación
    def handle_location_select():
        location.value = getattr(location_map, "location_name", "")
        page.update()

    location_map = LocationMap(
        location_text="Selecciona una ubicación en el mapa",
        initial_lat=15,
        initial_lon=10,
        initial_zoom=4.2,
        search_debounce_time=0.6,
        on_location_select=handle_location_select,
        visible=False,  # Comenzamos oculto
    )
    location = ft.TextField(
        label="Location",
        width=300,
        value=getattr(location_map, "location_name", ""),
    )
    toggle_map_button = ft.ElevatedButton(text="Seleccionar ubicación en el mapa")

    def toggle_map(e):
        location_map.visible = not location_map.visible
        toggle_map_button.text = "Ocultar mapa" if location_map.visible else "Seleccionar ubicación en el mapa"
        page.update()

    toggle_map_button.on_click = toggle_map

    return ft.Column(
        [
            top_app_bar(page),
            ft.Text("User Information Form", size=24, weight="bold"),
            user_name,
            location,
            birthday_label,
            birthday_button,
            language,
            toggle_map_button,
            location_map,
            submit_button,
        ],
        scroll=True,
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )
