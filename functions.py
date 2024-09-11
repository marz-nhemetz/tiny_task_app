import curses
import json
import os
import datetime

users={}

def init_curses_colors():
  curses.start_color()
  curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE) # Highlight
  curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK) # Completed task
  curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK) # Pending task
  curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_GREEN) # Success
  curses.init_pair(5, curses.COLOR_WHITE, curses.COLOR_RED) # Error

def save_users():
  with open('users.json', 'w') as f:
    json.dump(users, f, indent=4)

def load_users(stdscr):
  global users
  if os.path.exists('users.json'):
    with open('users.json', 'r') as f:
      users=json.load(f)
  else:
    users={}
    display_message(stdscr,'No users.json file found. Initialized empty users dictionary.',5)

def display_msg(stdscr, message, color_pair=None, y_offset=0):
  h, w = stdscr.getmaxyx()
  stdscr.addstr(h // 2 + y_offset, w // 2 - len(message) // 2, message)
  if color_pair:
    stdscr.attron(curses.color_pair(color_pair))
    stdscr.attroff(curses.color_pair(color_pair))
  stdscr.refresh()

def prompt_user_input(stdscr,prompt,y_offset):
  h, w = stdscr.getmaxyx()
  stdscr.addstr(h // 2 + y_offset, w // 2 - len(prompt) // 2, prompt)
  curses.echo()
  user_input = stdscr.getstr(h // 2 + y_offset + 1, w // 2 - len(prompt) // 2).decode('utf-8').strip()
  curses.noecho()
  return user_input

def register_user(stdscr):
  stdscr.clear()
  pin = prompt_user_input(stdscr, 'Enter a PIN to register:', 3)
  try:
    pin_int = int(pin)
    return pin_int
  except ValueError:
    display_message(stdscr, 'Invalid PIN format! Press any key to try again.', color_pair=5, y_offset=5)
    stdscr.getch()
    return None

def login_screen(stdscr):
  if users is None:
    raise ValueError('The users dictionary is not properly initialized.')

  while True:
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    display_msg(stdscr, '🎉 Welcome to Tiny Task App 🎉', curses.A_BOLD, -6)

    username = prompt_user_input(stdscr, 'USERNAME: ', -4)

    # Validate username
    if username not in users:
      display_message(stdscr, "❌ User not found!", curses.color_pair(5))
      display_message(stdscr, "Register? (y/n)", curses.A_DIM, 1)
      key = stdscr.getch()

      if key in [ord('y'), ord('Y')]:
          pin_int = register_user(stdscr)
          if pin_int is not None:
            users[username] = {"pin": pin_int, "tasks": []}
            save_users()  # Save to users.json
            display_message(stdscr, 'Registration successful! Press any key to continue.', curses.color_pair(4), 5)
            stdscr.getch()
            return username
      continue

  pin = prompt_user_input(stdscr, 'Please enter your PIN:', 1)

  try:
    pin_int = int(pin)
  except ValueError:
    display_message(stdscr, "❌ Invalid PIN format!", curses.color_pair(5), 4)
    display_message(stdscr, "Press any key to try again.", curses.A_DIM, 5)
    stdscr.getch()
    continue

  if pin_int == users[username]['pin']:
    display_message(stdscr, "✅ Login successful!", curses.color_pair(4), 4)
    display_message(stdscr, "Press any key to continue.", curses.A_DIM, 5)
    stdscr.getch()
    return username
  else:
    display_message(stdscr, "❌ Incorrect PIN!", curses.color_pair(5), 4)
    display_message(stdscr, "Press any key to try again.", curses.A_DIM, 5)
    stdscr.getch()

def display_tasks(stdscr,user,current_row):
  # Function to display tasks on the screen
  tasks = users[user]['tasks']
  h,w=stdscr.getmaxyx()

  if not tasks:
    stdscr.addstr(h//2, w//2 - len("No tasks available.")//2, "No tasks available.")
  else:
      for idx, task_info in enumerate(tasks):
        task = task_info['task']
        status = task_info['status']
        category = task_info['category']
        checkbox = '☑' if status == 'completed' else '☐'

        if idx == current_row:
          stdscr.attron(curses.color_pair(1))  # Selected row: black text, white background
        elif status == 'completed':
          stdscr.attron(curses.color_pair(2))  # Green for completed
        else:
          stdscr.attron(curses.color_pair(3))  # Yellow for pending

        max_task_length = w - 4  # Adjust based on screen width
        task_display = f'{checkbox} {task[:max_task_length]}' if len(task) > max_task_length else f'{checkbox} {task}'
        stdscr.addstr(h//2 - len(tasks)//2 + idx, w//2 - len(task_display)//2, task_display)

        stdscr.attroff(curses.color_pair(1))
        stdscr.attroff(curses.color_pair(2))
        stdscr.attroff(curses.color_pair(3))

def display_message(stdscr,message,color_pair=None):
  # Function to display a message at the bottom of the screen
  h, w = stdscr.getmaxyx()
  stdscr.move(h - 2, 0)
  stdscr.clrtoeol()  # Clear the line before displaying the message

  if color_pair:
    stdscr.attron(curses.color_pair(color_pair))

  stdscr.addstr(h - 2, w // 2 - len(message) // 2, message)

  if color_pair:
    stdscr.attroff(curses.color_pair(color_pair))

  stdscr.refresh()

def handle_task_addition(stdscr, user):
  stdscr.clear()
  stdscr.addstr(0, 0, 'Enter the new task: ')
  curses.echo()
  new_task = stdscr.getstr(1, 0).decode('utf-8').strip()

  stdscr.addstr(2,0, 'Enter the task category: ')
  new_category = stdscr.getstr(3,0).decode('utf-8').strip()

  curses.noecho()

  if new_task:
    users[user]['tasks'].append({
      'task': new_task,
      'status': 'pending',
      'category': new_category if new_category else 'General',
      'date_added': str(datetime.date.today())
    })
    save_users()
    display_message(stdscr, "Task added successfully!", 4)
  else:
    display_message(stdscr, "No task entered. Task not added.", 5)


def handle_task_completion(user, current_row):
  users[user]['tasks'][current_row]['status'] = 'completed'
  save_users()

def handle_task_removal(user,current_row):
  del users[user]['tasks'][current_row]
  save_users()

def task_screen(stdscr, user):
  current_row = 0
  tasks = users[user]['tasks']

  while True:
    stdscr.clear()
    display_tasks(stdscr,user,current_row)
    stdscr.refresh()

    key = stdscr.getch()

    # Navigation
    if key == curses.KEY_UP and current_row > 0:
      current_row -= 1
    elif key == curses.KEY_DOWN and current_row < len(tasks) - 1:
      current_row += 1
    # Mark task as completed
    elif key == ord('c'):
      handle_task_completion(user,current_row)
      display_message(stdscr, "Task marked as completed!", 4)
    # Delete task
    elif key == ord('x'):
      handle_task_removal(user,current_row)
      current_row = min(current_row, len(users[user]['tasks']) - 1)
      display_message(stdscr, 'Task removed successfully!', 4)
    # Add new task
    elif key == ord('n'):
      handle_task_addition(stdscr, user)
    # Exit
    elif key == 27:  # ESC key to exit
      break

