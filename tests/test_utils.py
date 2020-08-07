from itbrowz.utils import deep_flatten, get_elem_link_attr


def test_get_elem_link_attr__no_link_attr__empty_string(mocker):
    elem = mocker.Mock()
    render_info = mocker.Mock()
    link_attr = "foo"

    elem_link_attr = get_elem_link_attr(elem, render_info, link_attr)

    assert elem_link_attr == ""


def test_deep_flatten__deeply_nested_lists__no_nesting_in_result(mocker):
    nested_list = [[1, 2, [3, 4, [5, 6]], [7, 8], 9], 10]

    flattened_list = deep_flatten(nested_list)

    assert flattened_list == range(1, 10)
