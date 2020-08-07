#!/usr/bin/env python3
import urwid

txt = urwid.Text(u"Hello World")
fill = urwid.Filler(txt, "top")
loop = urwid.MainLoop(fill)
loop.run()