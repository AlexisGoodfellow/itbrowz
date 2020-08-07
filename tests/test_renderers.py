from termcolor import colored

from itbrowz.renderers import render_horizontal_line

SOME_TOTAL_TERMINAL_WIDTH = 82


def test_render_horizontal_line__fills_all_columns(mocker):
    render_info = mocker.Mock(
        div_depth=0,
        list_depth=0,
        available_terminal_width=lambda: SOME_TOTAL_TERMINAL_WIDTH,
    )

    line = render_horizontal_line(render_info)

    assert line == colored("-" * SOME_TOTAL_TERMINAL_WIDTH, "cyan", attrs=[])
