import curses
from functions import init_curses_colors, save_users, load_users, login_screen, task_screen, users


def main(stdscr):

  init_curses_colors()

  curses.curs_set(0)
  stdscr.clear()
  stdscr.refresh()

  load_users(stdscr)

  user = login_screen(stdscr)
  if not user:
    return
  task_screen(stdscr, user)

curses.wrapper(main)
