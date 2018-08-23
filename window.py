"""
Class for window of ncurses
"""
import curses

class Window(object):

    def __init__(self, stdscr):
        """Initialize all values as default and set state as top"""
        self.highlight = 0
        self.page = 0
        self.state = "top"
        self.stdscr = stdscr
        self.stdscr.clear()
        self.size = stdscr.getmaxyx()
        self.stdscr.addstr(self.size[0]//2-1, self.size[1]//2-5, "Loading...")
        self.stdscr.move(0,0)
        self.stdscr.refresh()
        self.maxlen = self.size[1] // 4 - 2
        self.maxitems = self.size[0] // 2 - 1
        self.win_l = curses.newwin(self.size[0], self.size[1] // 2, 0, 0)
        self.win_r = curses.newwin(self.size[0], self.size[1] // 2, 0, self.size[1] // 2)

    def reset_window(self):
        self.win_l.erase()
        self.win_l.border(0)
        self.win_r.erase()
        self.win_r.border(0)

    def refresh_window(self):
        self.highlight = 0
        self.page = 0

    def move_down(self, totalitems):
        if self.highlight + self.page * self.maxitems + 1 < totalitems:
            if self.highlight + 1 == self.maxitems:
                self.page += 1
                self.highlight = 0
            else:
                self.highlight += 1

    def move_up(self, totalitems):
        if self.highlight == 0 and self.page > 0:
            self.page -= 1
            self.highlight = self.maxitems - 1
        elif self.highlight > 0:
            self.highlight -= 1
    
