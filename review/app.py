"""RE-view prompt_toolkit app."""
# Function create_task would be preferred, but this aims to be compatible with
# python 3.6
# from asyncio import Future, ensure_future

import re

from prompt_toolkit import HTML
from prompt_toolkit.application import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import FormattedTextControl, HSplit, Layout, Window

lorem = (
    """Lorem ipsum dolor sit amet, consectetur adipiscing elit. Etiam ut sodales felis. Vestibulum eu tortor eget erat eleifend auctor mattis quis ligula. Curabitur sed felis lectus. Morbi ac est condimentum, tempus ante eget, euismod eros. Phasellus ultricies in nibh non malesuada. Aenean ut placerat justo. Nullam facilisis sapien viverra, posuere dolor sit amet, consectetur turpis. Quisque placerat rhoncus nisi laoreet dapibus. Suspendisse vestibulum fermentum dui, a molestie nunc posuere eu. In ex dolor, malesuada a diam id, viverra sodales justo. Nullam nibh nulla, blandit eu tristique posuere, sodales nec odio. Ut tempus, orci a gravida laoreet, eros velit placerat nisl, vitae venenatis est ipsum sed purus. Integer vestibulum est eget ultrices tempor. Mauris dictum mauris sed nisi sodales, et venenatis tortor malesuada. Pellentesque placerat vehicula tincidunt."""  # noqa: E501
    """\nAliquam erat volutpat. Etiam maximus aliquet lacus at euismod. Suspendisse consequat mattis pulvinar. Quisque aliquet sagittis ligula eget viverra. Curabitur viverra sodales nisi, quis tempus turpis dapibus at. Donec aliquam sit amet ipsum sit amet rhoncus. Sed aliquam massa eu elementum cursus. Mauris sapien magna, dapibus vitae risus sit amet, congue placerat orci. Donec vulputate augue ut erat faucibus, at convallis arcu auctor. Duis porttitor quam sit amet ipsum luctus, in suscipit ante hendrerit. Morbi molestie aliquet dapibus."""  # noqa: E501
)


def _highlight(m):
    return f'<b bg="white" fg="black">{m.group(0)}</b>'


def _split_line(m):
    return m.group(0).strip() + "\n"


wrapped_lorem = re.sub(r"(.{80}\s*)", _split_line, lorem)
highlighted_lorem = re.sub(r"(i[^i]*?t)", _highlight, wrapped_lorem)
sample_text_field = FormattedTextControl(text=HTML(highlighted_lorem), show_cursor=False)
stf_container = Window(content=sample_text_field)
# regex_field =
root_container = HSplit([stf_container])
layout = Layout(root_container, focused_element=stf_container)
# layout = Layout(root_container, focused_element=regex_field)
bindings = KeyBindings()


@bindings.add("q", eager=True)
def _(event):
    event.app.exit()


application = Application(layout=layout, key_bindings=bindings, full_screen=True)


def run():
    """Start application."""
    application.run()


if __name__ == "__main__":
    run()
