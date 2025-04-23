from flet import Page
from utils.theme import setup_theme
from views.recommendations_view import recommendations_view
from views.search_series_view import search_series_view
from views.user_form_view import user_form_view


def main(page: Page):
    # Configurar el tamaño mínimo de la ventana
    page.window.min_width = 600
    page.window.min_height = 700

    setup_theme(page)
    configure_routes(page)
    page.go("/")


def configure_routes(page: Page):
    page.on_route_change = lambda route: handle_route_change(page, route)
    page.on_view_pop = lambda view: handle_view_pop(page)


def handle_route_change(page: Page, route):
    page.views.clear()
    if route.route == "/":
        page.views.append(user_form_view(page))
    elif route.route == "/search_series":
        page.views.append(search_series_view(page))
    elif route.route == "/recommendations":
        page.views.append(recommendations_view(getattr(page, "selected_series", []), page))
    page.update()


def handle_view_pop(page: Page):
    page.views.pop()
    if len(page.views) == 0:
        page.go("/")


if __name__ == "__main__":
    from flet import app

    app(target=main)
