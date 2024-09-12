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
  try:
    with open('users.json', 'w') as f:
      json.dump(users, f, indent=4)
  except IOError as e:
    display_message(stdscr, f'Error saving data: {e}', color_pair=5, bottom=True, attr=curses.A_BOLD)

def load_users(stdscr):
  global users
  if os.path.exists('users.json'):
    with open('users.json', 'r') as f:
      users=json.load(f)
  else:
    users={}
    display_message(stdscr,'No users.json file found. Initialized empty users dictionary.', color_pair=5, bottom=True)

def prompt_user_input(stdscr, prompt, y_offset):
  h, w = stdscr.getmaxyx()
  display_message(stdscr, prompt, y=h // 2 + y_offset, x=w // 2 - len(prompt) // 2)
  curses.echo()
  while True:
    user_input = stdscr.getstr(h // 2 + y_offset + 1, w // 2 - len(prompt) // 2).decode('utf-8').strip()
    if user_input:
      curses.noecho()
      return user_input
    else:
      display_message(stdscr, "Input cannot be empty. Please try again.", color_pair=5,y_offset=3)

def register_user(stdscr):
  stdscr.clear()
  pin = prompt_user_input(stdscr, 'Enter a PIN to register:', y_offset=3)
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
    display_message(stdscr, '🎉 Welcome to Tiny Task App 🎉', attr=curses.A_BOLD, y_offset=8)

    username = prompt_user_input(stdscr, 'USERNAME: ', y_offset=-4)

    # Validate username
    if username not in users:
      display_message(stdscr, "❌ User not found!", color_pair=5, y=5)
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

    pin = prompt_user_input(stdscr, 'USERPIN:', y_offset=-2)

    try:
      pin_int = int(pin)
    except ValueError:
      display_message(stdscr, "❌ Invalid PIN format!", color_pair=5, y_offset=-3)
      display_message(stdscr, "Press any key to try again.", attr=curses.A_DIM, y_offset=-4)
      stdscr.getch()
      continue

    if pin_int == users[username]['pin']:
      display_message(stdscr, "✅ Login successful!", color_pair=4, y_offset=-3)
      display_message(stdscr, "Press any key to continue.", attr=curses.A_DIM, y_offset=-4)
      stdscr.getch()
      return username
    else:
      display_message(stdscr, "❌ Incorrect PIN!",  color_pair=5, y_offset=-3)
      display_message(stdscr, "Press any key to try again.", attr=curses.A_DIM, y_offset=-4)
      stdscr.getch()

def display_tasks(stdscr, user, current_row, selected_category=None, sort_by='date_added', ascending=True):
  # Function to display tasks on the screen
  tasks = users[user]['tasks']
  # Filter tasks based on the selected category
  filtered_tasks = [task for task in tasks if task['category'] == selected_category] if selected_category else tasks

  # Sort tasks based on the sort_by parameter
  if sort_by == 'date_added':
    sorted_tasks = sorted(
      filtered_tasks, key=lambda x: datetime.datetime.strptime(x[sort_by], '%Y-%m-%d'),
      reverse = not ascending
    )
  elif sort_by == 'status':
    sorted_tasks = sorted(filtered_tasks, key=lambda x: x['status'])
  else:
    sorted_tasks = filtered_tasks

  h ,w = stdscr.getmaxyx()

  # Display the current category at the top
  category_display = f'Category: {selected_category}' if selected_category else 'Category: All'

  display_message(stdscr, category_display, y=0,x=w//2-len(category_display)//2, attr=curses.A_BOLD)

  if not sorted_tasks:
    display_message(stdscr, "No tasks available.", y=h // 2, x=w // 2 - len("No tasks available.") // 2)
  else:
      for idx, task_info in enumerate(sorted_tasks):
        task = task_info['task']
        status = task_info['status']
        checkbox = '☑' if status == 'completed' else '☐'

        if idx == current_row:
          stdscr.attron(curses.color_pair(1))  # Selected row: black text, white background
        elif status == 'completed':
          stdscr.attron(curses.color_pair(2))  # Green for completed
        else:
          stdscr.attron(curses.color_pair(3))  # Yellow for pending

        task_display = f'{checkbox} {task[:w-4]}'
        display_message(stdscr, task_display, y=h // 2 - len(sorted_tasks) // 2 + idx, x=w // 2 - len(task_display) // 2)

        stdscr.attroff(curses.color_pair(1))
        stdscr.attroff(curses.color_pair(2))
        stdscr.attroff(curses.color_pair(3))

def display_message(stdscr, message, color_pair=None, y_offset=None,y = None, x=None, bottom=False, attr=None):
  """
    Displays a message on the screen, centered with optional color, positioning and tex attributes.

    Args:
      stdscr: The curses screen object.
      message (str): The message to display.
      color_pair (int, optional): The curses color pair to use.
      y (int, optional): The row to display the message, if none, it centers vertically.
      x (int, opitional): The column to display the message, if none it centers horizontally.
      bottom (bool, optional): If True, display the message at the bottom of the screen.
      attr (int, optional): Curses text attribute (e.g., curses.A_BOLD, curses.A_DIM).
  """
  h, w = stdscr.getmaxyx()

  if bottom:
    y = h - 2 # Displays near the bottom
    stdscr.move(y, 0)
    stdscr.clrtoeol()  # Clear the line before displaying the message
  elif y is None:
    y = h // 2 - y_offset # Display the message at the center with offset
  if x is None:
    x = w//2 - len(message)//2 # Center horizontally if no x is provided
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
  display_message(stdscr, 'Enter the new task: ', y=0,x=0)
  curses.echo()
  new_task = stdscr.getstr(1, 0).decode('utf-8').strip()

  if not new_task:
    display_message(stdscr, 'No task entered. Task not added,', color_pair=5, bottom=True, attr=curses.A_DIM)
    return

  display_message(stdscr, 'Enter the task category: ', y=2,x=0)
  new_category = stdscr.getstr(3,0).decode('utf-8').strip() or 'General'
  curses.noecho()

  if new_task:
    users[user]['tasks'].append({
      'task': new_task,
      'status': 'pending',
      'category': new_category if new_category else 'General',
      'date_added': str(datetime.date.today()),
      'description': [] # Add an empty description list
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
  sort_ascending = True # Variable to keep track of sorting order (True for ascending)

  while True:
    stdscr.clear()
    # Filter tasks by the current selected category
    category_to_display = None if categories[category_index] == 'All' else categories[category_index]

    # Display tasks, sorted by date (ascending or descending)
    sort_by = 'date_added'

    sorting_state_display = 'Sorting: Ascending' if sort_ascending else 'Sorting: Descending'
    stdscr.addstr(0, 0, sorting_state_display, curses.A_BOLD)

    display_tasks(stdscr, user, current_row, selected_category=category_to_display, sort_by=sort_by, ascending=sort_ascending)
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
    elif key == ord('s'):
      sort_ascending = not sort_ascending
      display_message(stdscr, 'toggle toggling ', bottom=True)

    elif key == ord('d'):
      task_detail_screen(stdscr, user, current_row)
    # Mark task as completed
    elif key == ord('c'):
      handle_task_completion(user,current_row)
    # Delete task
    elif key == ord('x'):
      handle_task_removal(user,current_row)
      current_row = min(current_row, len(users[user]['tasks']) - 1)
      if not users[user]['tasks']:
        current_row = 0 # Reset if no tasks remain
    # Add new task
    elif key == ord('n'):
      handle_task_addition(stdscr, user)
    # Exit
    elif key == 27:  # ESC key to exit
      break

def task_detail_screen(stdscr, user, task_index):
  task_info = users[user]['tasks'][task_index]
  task_name = task_info['task']
  description = task_info['description']
  current_row = 0

  while True:
    stdscr.clear()
    h, w = stdscr.getmaxyx()

    # Display the task name at the top
    stdscr.addstr(0, w // 2 - len(task_name) // 2, task_name, curses.A_BOLD)

    if description:
      for idx, subtask_info in enumerate(description):
        subtask = subtask_info['subtask']
        status = subtask_info['status']
        checkbox = '☑' if status == 'completed' else '☐'

        if idx == current_row:
          stdscr.attron(curses.color_pair(1))  # Highlight selected sub-task
        elif status == 'completed':
          stdscr.attron(curses.color_pair(2))  # Completed sub-task color
        else:
          stdscr.attron(curses.color_pair(3))  # Pending sub-task color

        subtask_display = f'{checkbox} {subtask}'
        stdscr.addstr(h // 2 - len(description) // 2 + idx, w // 2 - len(subtask_display) // 2, subtask_display)

        stdscr.attroff(curses.color_pair(1))
        stdscr.attroff(curses.color_pair(2))
        stdscr.attroff(curses.color_pair(3))
    else:
      stdscr.addstr(h // 2, w // 2 - len("No description available.") // 2, "No description available.")

    # Refresh screen
    stdscr.refresh()

    key = stdscr.getch()

    # Navigation
    if key == curses.KEY_UP and current_row > 0:
      current_row -= 1
    elif key == curses.KEY_DOWN and current_row < len(description) - 1:
      current_row += 1
    # Rename task
    elif key == ord('r'):
      new_name = prompt_user_input(stdscr, "Rename task:", 1)
      if new_name:
        task_info['task'] = new_name
        task_name = new_name
        save_users()
    # Add sub-task
    elif key == ord('n'):
      new_subtask = prompt_user_input(stdscr, "New sub-task:", 1)
      if new_subtask:
        description.append({'subtask': new_subtask, 'status': 'pending'})
        save_users()
    # Mark sub-task as completed
    elif key == ord('c'):
      description[current_row]['status'] = 'completed'
      save_users()
    # Remove sub-task
    elif key == ord('x'):
      del description[current_row]
      current_row = min(current_row, len(description) - 1)
      save_users()
    # Exit detail screen
    elif key == 27:  # ESC key to exit
      break
