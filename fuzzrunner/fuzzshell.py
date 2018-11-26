import curses
import curses.ascii

from .fuzzrunner import FuzzRunner


class FuzzShell:
    def __init__(self, settings, digit_confirm=False):
        self.fuzzrunner = FuzzRunner.from_settings(settings)
        self.cmd = ""
        self.results = []
        self.digit_confirm = digit_confirm
        self.selected_idx = 0

    def draw_loop(self, stdscr):
        stdscr.clear()
        _, screen_width = stdscr.getmaxyx()
        max_desc_len = max([len(c.description) for c in self.results])
        desc_width = min(max(max_desc_len + 2, screen_width // 2), 9999)

        stdscr.addstr(0, 0, "Fuzz Command Query: {}".format(self.cmd))
        stdscr.addstr(2, 0, "Results:")
        for i, cmd in enumerate(self.results):
            output_line = "[{idx}] {desc:<{width}} {script}".format(
                idx=i,
                desc=cmd.description,
                width=desc_width,
                script=' '.join(cmd.script))
            if len(output_line) > screen_width:
                output_line = output_line[:screen_width - 2] + ".."
            if i == self.selected_idx:
                stdscr.addstr(3 + i, 0, output_line, curses.A_UNDERLINE | curses.A_BOLD)
            else:
                stdscr.addstr(3 + i, 0, output_line, curses.A_BOLD)
        stdscr.refresh()

    def get_cmd(self, stdscr):
        curses.start_color()
        curses.use_default_colors()
        curses.curs_set(0)
        while True:
            self.results = self.fuzzrunner.recommend(self.cmd)
            self.selected_idx = min(max(0, self.selected_idx), len(self.results) - 1)
            self.draw_loop(stdscr)

            try:
                ch = stdscr.getch()
            except KeyboardInterrupt:
                return None

            if ch in (curses.KEY_BACKSPACE, curses.ascii.DEL, curses.ascii.BS):
                self.cmd = self.cmd[:-1]
            elif ch in (curses.KEY_ENTER, curses.ascii.LF, curses.ascii.NL):
                if len(self.results) > 0:
                    return self.results[self.selected_idx]
            elif ch in (curses.KEY_EXIT, curses.ascii.ESC):
                return None
            elif ch == curses.KEY_UP:
                self.selected_idx -= 1
            elif ch == curses.KEY_DOWN:
                self.selected_idx += 1
            elif curses.ascii.isdigit(ch) and self.digit_confirm:
                idx = ch - ord('0')
                if idx < len(self.results):
                    return self.results[idx]
            elif curses.ascii.isascii(ch):
                self.cmd += chr(ch)

    def run(self):
        cmd = curses.wrapper(self.get_cmd)
        if cmd is not None:
            return self.fuzzrunner.run(cmd)
        return 1
