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
    display_message(stdscr,'No users.json file found. Initialized empty users dictionary.', color_pair=5, bottom=True)

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
    display_message(stdscr, '🎉 Welcome to Tiny Task App 🎉', attr=curses.A_BOLD, y_offset=-6)

    username = prompt_user_input(stdscr, 'USERNAME: ', -4)

    # Validate username
    if username not in users:
      display_message(stdscr, "❌ User not found!", color_pair=5, y_offset=5)
      display_message(stdscr, "Register? (y/n)", attr=curses.A_DIM, y_offset=1)
      key = stdscr.getch()

      if key in [ord('y'), ord('Y')]:
          pin_int = register_user(stdscr)
          if pin_int is not None:
            users[username] = {"pin": pin_int, "tasks": []}
            save_users()  # Save to users.json
            display_message(stdscr, 'Registration successful! Press any key to continue.', color_pair=4, y_offset=5)
            stdscr.getch()
            return username
      continue

    pin = prompt_user_input(stdscr, 'PIN:', 1)

    try:
      pin_int = int(pin)
    except ValueError:
      display_message(stdscr, "❌ Invalid PIN format!", color_pair=5, y_offset=4)
      display_message(stdscr, "Press any key to try again.", attr=curses.A_DIM, y_offset=5)
      stdscr.getch()
      continue

    if pin_int == users[username]['pin']:
      display_message(stdscr, "✅ Login successful!", color_pair=4, y_offset=4)
      display_message(stdscr, "Press any key to continue.", attr=curses.A_DIM, y_offset=5)
      stdscr.getch()
      return username
    else:
      display_message(stdscr, "❌ Incorrect PIN!",  color_pair=5, y_offset=4)
      display_message(stdscr, "Press any key to try again.", attr=curses.A_DIM, y_offset=5)
      stdscr.getch()

def display_tasks(stdscr, user, current_row, selected_category=None):
  # Function to display tasks on the screen
  tasks = users[user]['tasks']

  # Filter tasks based on the selected category

  filtered_tasks = [task for task in tasks if task['category'] == selected_category] if selected_category else tasks
  h ,w = stdscr.getmaxyx()

  # Display the current category at the top
  if selected_category:
    category_display = f'Category: {selected_category}'
  else:
    category_display = 'Category: All'

  stdscr.addstr(0,w//2-len(category_display) // 2, category_display, curses.A_BOLD)
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
        stdscr.addstr(h//2 - len(filtered_tasks)//2 + idx, w//2 - len(task_display)//2, task_display)

        stdscr.attroff(curses.color_pair(1))
        stdscr.attroff(curses.color_pair(2))
        stdscr.attroff(curses.color_pair(3))

def display_message(stdscr, message, color_pair=None, y_offset = 0, bottom=False, attr=None):
  """
    Displays a message on the screen, centered with optional color, positioning and tex attributes.

    Args:
      stdscr: The curses screen object.
      message (str): The message to display.
      color_pair (int, optional): The curses color pair to use.
      y_offset (int, optional): Vertical offset for the message.
      bottom (bool, optional): If True, display the message at the bottom of the screen.
      attr (int, optional): Curses text attribute (e.g., curses.A_BOLD, curses.A_DIM).
  """
  h, w = stdscr.getmaxyx()

  if bottom:
    y = h - 2 # Displays near the bottom
    stdscr.move(y, 0)
    stdscr.clrtoeol()  # Clear the line before displaying the message
  else:
    y = h // 2 + y_offset # Display the message at the center with offset

  # Apply color if provided
  if color_pair:
    stdscr.attron(curses.color_pair(color_pair))

  if attr:
    stdscr.attron(attr)

  stdscr.addstr(y, w // 2 - len(message) // 2, message)

  if color_pair:
    stdscr.attroff(curses.color_pair(color_pair))
  if attr:
    stdscr.attroff(attr)

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
    display_message(stdscr, "Task added successfully!", color_pair=4, bottom=True, attr=curses.A_DIM)
  else:
    display_message(stdscr, "No task entered. Task not added.", color_pair=5, bottom=True, attr=curses.A_DIM)


def handle_task_completion(user, current_row):
  users[user]['tasks'][current_row]['status'] = 'completed'
  save_users()

def handle_task_removal(user,current_row):
  del users[user]['tasks'][current_row]
  save_users()

def task_screen(stdscr, user):
  current_row = 0
  selected_category = None
  categories = {task['category'] for task in users[user]['tasks']} # Get unique categories
  categories = ['All'] + list(categories) # 'All' will show all tasks
  category_index = 0

  while True:
    stdscr.clear()
    # Filter tasks by the current selected category
    category_to_display = None if categories[category_index] == 'All' else categories[category_index]
    stdscr.clear()

    display_tasks(stdscr, user, current_row, category_to_display)
    stdscr.refresh()

    key = stdscr.getch()

    # Navigation
    if key == curses.KEY_UP and current_row > 0:
      current_row -= 1
    elif key == curses.KEY_DOWN and current_row < len(users[user]['tasks']) - 1:
      current_row += 1
    # Switch category filter
    elif key == ord('f'):
      category_index = (category_index + 1) % len(categories)
      current_row = 0 # Reset the selected row when switching categories
    # Mark task as completed
    elif key == ord('c'):
      handle_task_completion(user,current_row)
      display_message(stdscr, "Task marked as completed!", 4, True)
    # Delete task
    elif key == ord('x'):
      handle_task_removal(user,current_row)
      current_row = min(current_row, len(users[user]['tasks']) - 1)
      if not users[user]['tasks']:
        current_row = 0 # Reset if no tasks remain
      display_message(stdscr, 'Task removed successfully!', 4, True)
    # Add new task
    elif key == ord('n'):
      handle_task_addition(stdscr, user)
    # Exit
    elif key == 27:  # ESC key to exit
      break

