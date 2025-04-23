import flet as ft


def create_checkbox_map(full_series_list, selected_series):
    checkbox_map = {}

    def checkbox_change(e, series):
        if e.control.value:
            if series not in selected_series:
                selected_series.append(series)
        else:
            if series in selected_series:
                selected_series.remove(series)

    for series in full_series_list:
        checkbox_map[series] = ft.Checkbox(
            label=series,
            value=False,
            on_change=lambda e, s=series: checkbox_change(e, s),
        )
    return checkbox_map
