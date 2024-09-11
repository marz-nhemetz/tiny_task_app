import curses
import json
import os
import datetime

users={}

def

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

def load_users():
  global users
  if os.path.exists('users.json'):
    with open('users.json', 'r') as f:
      users=json.load(f)
  else:
    users={}
    display_message(stdscr,'No users.json file found. Initialized empty users dictionary.',5)

def login_screen(stdscr):
  if users is None:
    raise ValueError('The users dictionary is not properly initialized.')

  while True:
    stdscr.clear()
    h, w = stdscr.getmaxyx()

    # Display welcome message
    welcome_msg = '🎉 Welcome to Tiny Task App 🎉'
    stdscr.addstr(h//2-6, w//2 - len(welcome_msg)//2, welcome_msg, curses.A_BOLD)

    # Prompt for username
    stdscr.addstr(h//2-4, w//2 - len('Please enter your username:')//2, 'Please enter your username:')
    curses.echo()
    username = stdscr.getstr(h//2-3, w//2 - len('username:')//2).decode('utf-8').strip()
    curses.noecho()

    # Validate username
    if username not in users:
      stdscr.addstr(h//2, w//2 - len("❌ User not found!")//2, "❌ User not found!", curses.A_BOLD | curses.color_pair(5))
      stdscr.addstr(h//2 + 1, w//2 - len("Register? (y/n)")//2, "Register? (y/n)", curses.A_DIM)
      stdscr.refresh()
      key = stdscr.getch()

      if key in [ord('y'), ord('Y')]:
        # Register the new user
        stdscr.addstr(h//2+3,w//2-len('Enter a PIN to register:')//2,'Enter a PIN to register:')
        curses.echo()
        pin = stdscr.getstr(h//2+4,w//2-len('PIN:')//2).decode('utf-8')
        curses.noecho()

        try:
          pin_int=int(pin.strip())
        except ValueError:
          stdscr.addstr(h // 2 + 5, w // 2 - len('Invalid PIN format! Press any key to try again.') // 2, 'Invalid PIN format! Press any key to try again.')
          stdscr.refresh()
          stdscr.getch()
          continue
        # Add new user to the users dictionary and save to file
        users[username] = {"pin": pin_int, "tasks": []}
        save_users()  # Save to users.json
        stdscr.addstr(h // 2 + 5, w // 2 - len('Registration successful! Press any key to continue.') // 2, 'Registration successful! Press any key to continue.')
        stdscr.refresh()
        stdscr.getch()
        return username
      else:
        # User chose not to register, try again
        continue
    else:
      # Exiting user, ask for PIN
      # Prompt for PIN
      stdscr.addstr(h//2+1, w//2 - len('Please enter your PIN:')//2, 'Please enter your PIN:')
      curses.echo()
      pin = stdscr.getstr(h//2+2, w//2 - len('PIN:')//2).decode('utf-8').strip()
      curses.noecho()
      stdscr.refresh()
      stdscr.getch()

      # PIN validation
      try:
        pin_int = int(pin)
      except ValueError:
        stdscr.addstr(h//2+4, w//2 - len("❌ Invalid PIN format!")//2, "❌ Invalid PIN format!", curses.A_BOLD | curses.color_pair(5))
        stdscr.addstr(h//2+5, w//2 - len("Press any key to try again.")//2, "Press any key to try again.", curses.A_DIM)
        stdscr.refresh()
        stdscr.getch()
        continue

      if pin_int == users[username]['pin']:
        stdscr.addstr(h//2+4, w//2 - len("✅ Login successful!")//2, "✅ Login successful!", curses.A_BOLD | curses.color_pair(4))
        stdscr.addstr(h//2+5, w//2 - len("Press any key to continue.")//2, "Press any key to continue.", curses.A_DIM)
        stdscr.refresh()
        stdscr.getch()
        return username
      else:
        stdscr.addstr(h//2+4, w//2 - len("❌ Incorrect PIN!")//2, "❌ Incorrect PIN!", curses.A_BOLD | curses.color_pair(5))
        stdscr.addstr(h//2+5, w//2 - len("Press any key to try again.")//2, "Press any key to try again.", curses.A_DIM)
        stdscr.refresh()
        stdscr.getch()
        continue

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

        #stdscr.addstr(h//2 - len(tasks)//2 + idx, w//2 - len(task)//2, f'{checkbox} {task}')

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

  stdscr.addstr(2,0 'Enter the task category: ')
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

