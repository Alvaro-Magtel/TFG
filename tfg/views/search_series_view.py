import flet as ft

from tfg.components.top_app_bar import top_app_bar
from tfg.utils.helpers import update_controls


def search_series_view(page: ft.Page):
    from tfg.data.series_list import get_full_series_list

    full_series_list = get_full_series_list()
    selected_series = []
    search_bar_ref = ft.Ref[ft.SearchBar]()

    checkbox_map = {}

    # Generar los checkboxes y añadirlos al mapa
    for series in full_series_list:
        cb = ft.Container(
            padding=ft.padding.symmetric(vertical=10),
            width=500,  # Ajusta el tamaño según tu layout
            content=ft.Checkbox(
                label=series,
                label_style=ft.TextStyle(size=20),
                on_change=lambda e, s=series: (
                    selected_series.append(s) if e.control.value else selected_series.remove(s)
                ),
            ),
        )

        checkbox_map[series] = cb

    def handle_search_change(e):
        update_controls(e.data, full_series_list, checkbox_map, search_bar_ref)

    def handle_search_tap(e):
        search_bar_ref.current.open_view()
        update_controls("", full_series_list, checkbox_map, search_bar_ref)

    def go_to_recommendations(e):
        page.selected_series = selected_series
        page.go("/recommendations")

    def go_back(e):
        page.go("/")

    return ft.Column(
        [
            top_app_bar(page),
            ft.Text("Select your favorite series", size=24, weight="bold"),
            ft.ElevatedButton("Back", icon=ft.Icons.ARROW_BACK, on_click=go_back),
            ft.SearchBar(
                ref=search_bar_ref,
                bar_hint_text="Search series...",
                view_hint_text="Select from the list below...",
                on_tap=handle_search_tap,
                on_change=handle_search_change,
                controls=list(checkbox_map.values()),  # Usar los valores del diccionario
            ),
            ft.ElevatedButton("Get Recommendations", on_click=go_to_recommendations),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )
