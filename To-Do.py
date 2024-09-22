"""
Elegant Console-Based To-Do List Application

This is a console based tasks app.
It uses the curses library to create an interactive terminal interface.
Supports two lists, one for to-do and one for done. 

Key Features:
- Manage two lists, to-do and done.
- Add new tasks to the To-Do list.
- Move tasks between the To-Do and Done lists.
- Delete tasks from either list.
- Clear all completed done tasks.
- Mark all to-do tasks as done.
- Persistent list storage using JSON.
- Scrollable lists for managing longs lists.
- Cursor-based task selection.

Author: Tim Kitterman
Date: 22Sept2024
"""

import curses
import json

TASKS_FILE = 'tasks.json'
MENU_ITEMS = ["Add Task", "Mark Done/Not Done", "Delete Task", "Clear Done", "Mark All Done", "Quit"]

def load_tasks():
    """Load tasks from JSON file or return empty lists if file not found."""
    try:
        with open(TASKS_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {'todo': [], 'done': []}

def save_tasks(tasks):
    """Save tasks to JSON file."""
    with open(TASKS_FILE, 'w') as f:
        json.dump(tasks, f)

def draw_list(stdscr, tasks, list_name, x, current_list, cursor, in_menu):
    """Draw a single task list (either 'todo' or 'done')."""
    h, w = stdscr.getmaxyx()
    stdscr.addstr(2, x, f"{list_name.capitalize()}:", curses.A_BOLD | 
                    (curses.color_pair(1) if list_name == current_list and not in_menu else 0))
    
    for i, task in enumerate(tasks[list_name][cursor['start']:cursor['start']+h-8]):
        y = i + 3
        attr = curses.color_pair(2 if not in_menu else 1) if list_name == current_list and i == cursor['pos'] else 0
        stdscr.addstr(y, x, f"{i+cursor['start']+1}. {task[:w//2-6]}", attr)

def draw_app(stdscr, tasks, current_list, cursors, menu_pos, in_menu):
    """Draw the entire application interface."""
    h, w = stdscr.getmaxyx()
    stdscr.clear()
    stdscr.addstr(0, w//2 - 10, "TO-DO LIST APP", curses.A_BOLD)

    draw_list(stdscr, tasks, 'todo', 2, current_list, cursors['todo'], in_menu)
    draw_list(stdscr, tasks, 'done', w//2 + 2, current_list, cursors['done'], in_menu)

    for i, item in enumerate(MENU_ITEMS):
        y, x = h - len(MENU_ITEMS) - 1 + i, w//2 - len(item)//2
        attr = curses.color_pair(2) if i == menu_pos and in_menu else 0
        stdscr.addstr(y, x, item, attr)

    instructions = "M: Menu, ←/→: Switch Lists, ↑/↓: Navigate" if not in_menu else "↑/↓: Navigate, Enter: Select, M: Exit Menu"
    stdscr.addstr(h-1, 2, instructions)

def handle_menu_action(stdscr, tasks, current_list, cursor, menu_pos):
    """Handle menu item selection and perform corresponding action."""
    h, _ = stdscr.getmaxyx()
    if menu_pos == 0:  # Add Task
        curses.echo()
        stdscr.addstr(h-3, 2, "Enter task: ")
        task = stdscr.getstr(h-3, 14, 50).decode('utf-8')
        curses.noecho()
        if task: tasks['todo'].append(task)
    elif menu_pos == 1 and tasks[current_list]:  # Mark Done/Not Done
        other_list = 'done' if current_list == 'todo' else 'todo'
        task = tasks[current_list].pop(cursor['start'] + cursor['pos'])
        tasks[other_list].append(task)
    elif menu_pos == 2 and tasks[current_list]:  # Delete Task
        del tasks[current_list][cursor['start'] + cursor['pos']]
    elif menu_pos == 3:  # Clear Done
        tasks['done'].clear()
    elif menu_pos == 4:  # Mark All Done
        tasks['done'].extend(tasks['todo'])
        tasks['todo'].clear()
    cursor['pos'] = min(cursor['pos'], max(0, len(tasks[current_list])-1))
    return menu_pos == 5  # Return True if Quit was selected

def main(stdscr):
    """Main function to set up the environment and run the application loop."""
    curses.curs_set(0)
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_CYAN)

    tasks = load_tasks()
    current_list = 'todo'
    cursors = {'todo': {'start': 0, 'pos': 0}, 'done': {'start': 0, 'pos': 0}}
    menu_pos, in_menu = 0, False

    while True:
        draw_app(stdscr, tasks, current_list, cursors, menu_pos, in_menu)
        key = stdscr.getch()
        cursor = cursors[current_list]
        h, _ = stdscr.getmaxyx()

        if key in [ord('q'), ord('Q')]: break
        elif key in [ord('m'), ord('M')]: in_menu = not in_menu
        elif key == curses.KEY_UP:
            if in_menu: menu_pos = (menu_pos - 1) % len(MENU_ITEMS)
            elif cursor['pos'] > 0: cursor['pos'] -= 1
            elif cursor['start'] > 0: cursor['start'] -= 1
        elif key == curses.KEY_DOWN:
            if in_menu: menu_pos = (menu_pos + 1) % len(MENU_ITEMS)
            elif cursor['pos'] < min(h-9, len(tasks[current_list])-cursor['start']-1): cursor['pos'] += 1
            elif cursor['start'] + h - 8 < len(tasks[current_list]): cursor['start'] += 1
        elif key == curses.KEY_LEFT and not in_menu: current_list = 'todo'
        elif key == curses.KEY_RIGHT and not in_menu: current_list = 'done'
        elif key in [curses.KEY_ENTER, 10, 13] and in_menu:
            if handle_menu_action(stdscr, tasks, current_list, cursor, menu_pos): break
            in_menu = False
        
        save_tasks(tasks)

if __name__ == "__main__":
    curses.wrapper(main)