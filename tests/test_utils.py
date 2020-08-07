from itbrowz.utils import deep_flatten, get_elem_link_attr


def test_get_elem_link_attr__no_link_attr__empty_string(mocker):
    elem = {}
    render_info = mocker.Mock()
    link_attr = "foo"

    elem_link_attr = get_elem_link_attr(elem, render_info, link_attr)

    assert elem_link_attr == ""


def test_deep_flatten__deeply_nested_lists__no_nesting_in_result(mocker):
    nested_list = [[0, 1, [2, 3, [4, 5]], [6, 7], 8], 9]

    flattened_list = deep_flatten(nested_list)

    assert flattened_list == [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]


def test_deep_flatten__none__empty_list(mocker):
    nested_list = None

    flattened_list = deep_flatten(nested_list)

    assert flattened_list == []
