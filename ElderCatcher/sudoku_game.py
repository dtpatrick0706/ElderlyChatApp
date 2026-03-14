from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.graphics import Color, Rectangle
from rounded_button import RoundedButton
import random


class SudokuGamePage(Screen):
    """Proper 9x9 Sudoku game"""
    
    BACKGROUND_COLOR = (1.0, 0.98, 0.85, 1.0)  # Very light yellow
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'sudoku_game'
        
        # Game grid (9x9 standard Sudoku)
        self.grid_size = 9
        self.grid = [[0 for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        self.solution = [[0 for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        self.cells = []
        
        # Create main layout
        main_layout = BoxLayout(
            orientation='vertical',
            padding='5dp',
            spacing='5dp'
        )
        
        # Set background color
        with main_layout.canvas.before:
            Color(*self.BACKGROUND_COLOR)
            self.rect = Rectangle(size=main_layout.size, pos=main_layout.pos)
        
        main_layout.bind(size=self._update_rect, pos=self._update_rect)
        
        # Back button
        back_button = RoundedButton(
            text='← Back',
            font_size='18sp',
            size_hint_y=None,
            height='45dp',
            bg_color=(0.7, 0.7, 0.7, 1)
        )
        back_button.bind(on_press=self.go_back)
        main_layout.add_widget(back_button)
        
        # Title
        title_label = Label(
            text='Sudoku',
            font_size='22sp',
            size_hint_y=None,
            height='40dp',
            halign='center',
            bold=True,
            color=(0, 0, 0, 1)
        )
        main_layout.add_widget(title_label)
        
        # Instructions
        instruction_label = Label(
            text='Fill each row, column, and 3x3 box with numbers 1-9',
            font_size='12sp',
            size_hint_y=None,
            height='30dp',
            halign='center',
            color=(0.3, 0.3, 0.3, 1)
        )
        main_layout.add_widget(instruction_label)
        
        # Status
        self.status_label = Label(
            text='',
            font_size='14sp',
            size_hint_y=None,
            height='30dp',
            halign='center',
            color=(0, 0, 0, 1)
        )
        main_layout.add_widget(self.status_label)
        
        # Scrollable area for Sudoku grid
        from kivy.uix.scrollview import ScrollView
        scroll = ScrollView(size_hint_y=1, do_scroll_x=True, do_scroll_y=True)
        
        # Sudoku grid container
        grid_container = BoxLayout(
            orientation='vertical',
            size_hint_x=None,
            width='350dp',
            padding='5dp'
        )
        
        # Create 9x9 grid of TextInputs
        self.sudoku_grid = GridLayout(
            cols=self.grid_size,
            spacing='1dp',
            size_hint_x=None,
            width='340dp'
        )
        
        # Create cells with 3x3 box borders
        for row in range(self.grid_size):
            row_cells = []
            for col in range(self.grid_size):
                cell = TextInput(
                    text='',
                    font_size='14sp',
                    halign='center',
                    multiline=False,
                    size_hint_y=None,
                    height='35dp',
                    background_color=(1, 1, 1, 1),
                    foreground_color=(0, 0, 0, 1),
                    input_filter='int',
                    input_type='number'
                )
                # Add border styling for 3x3 boxes
                if (row // 3 + col // 3) % 2 == 0:
                    cell.background_color = (0.95, 0.95, 0.95, 1)
                
                cell.row = row
                cell.col = col
                cell.bind(text=self.validate_input)
                self.sudoku_grid.add_widget(cell)
                row_cells.append(cell)
            self.cells.append(row_cells)
        
        grid_container.add_widget(self.sudoku_grid)
        scroll.add_widget(grid_container)
        main_layout.add_widget(scroll)
        
        # Buttons
        button_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height='45dp',
            spacing='8dp'
        )
        
        check_button = RoundedButton(
            text='Check',
            font_size='16sp',
            bg_color=(0.8, 0.5, 0.2, 1)
        )
        check_button.bind(on_press=self.check_solution)
        button_layout.add_widget(check_button)
        
        new_game_button = RoundedButton(
            text='New Game',
            font_size='16sp',
            bg_color=(0.6, 0.6, 0.6, 1)
        )
        new_game_button.bind(on_press=self.new_game)
        button_layout.add_widget(new_game_button)
        
        main_layout.add_widget(button_layout)
        self.add_widget(main_layout)
        
        self.new_game()
    
    def _update_rect(self, instance, value):
        """Update background rectangle"""
        self.rect.pos = instance.pos
        self.rect.size = instance.size
    
    def is_valid(self, grid, row, col, num):
        """Check if placing num at (row, col) is valid"""
        # Check row
        for x in range(9):
            if grid[row][x] == num:
                return False
        
        # Check column
        for x in range(9):
            if grid[x][col] == num:
                return False
        
        # Check 3x3 box
        start_row = row - row % 3
        start_col = col - col % 3
        for i in range(3):
            for j in range(3):
                if grid[i + start_row][j + start_col] == num:
                    return False
        
        return True
    
    def solve_sudoku(self, grid):
        """Solve Sudoku using backtracking"""
        for i in range(9):
            for j in range(9):
                if grid[i][j] == 0:
                    for num in range(1, 10):
                        if self.is_valid(grid, i, j, num):
                            grid[i][j] = num
                            if self.solve_sudoku(grid):
                                return True
                            grid[i][j] = 0
                    return False
        return True
    
    def generate_puzzle(self):
        """Generate a valid 9x9 Sudoku puzzle"""
        # Start with empty grid
        base_grid = [[0 for _ in range(9)] for _ in range(9)]
        
        # Fill diagonal 3x3 boxes (they are independent)
        for box in range(3):
            values = list(range(1, 10))
            random.shuffle(values)
            idx = 0
            for i in range(3):
                for j in range(3):
                    base_grid[box * 3 + i][box * 3 + j] = values[idx]
                    idx += 1
        
        # Solve the rest
        self.solve_sudoku(base_grid)
        
        # Copy solution
        for i in range(9):
            for j in range(9):
                self.solution[i][j] = base_grid[i][j]
        
        # Remove numbers to create puzzle (remove 40-50 numbers)
        cells_to_remove = random.sample(range(81), 45)
        for cell_idx in cells_to_remove:
            row = cell_idx // 9
            col = cell_idx % 9
            base_grid[row][col] = 0
        
        # Copy to game grid
        for i in range(9):
            for j in range(9):
                self.grid[i][j] = base_grid[i][j]
    
    def new_game(self, instance=None):
        """Start a new game"""
        self.generate_puzzle()
        self.status_label.text = ''
        
        # Update cells
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                cell = self.cells[row][col]
                if self.grid[row][col] > 0:
                    cell.text = str(self.grid[row][col])
                    cell.background_color = (0.85, 0.85, 0.85, 1)  # Gray for given numbers
                    cell.readonly = True
                else:
                    cell.text = ''
                    # Alternate 3x3 box colors (reset to default)
                    if (row // 3 + col // 3) % 2 == 0:
                        cell.background_color = (0.95, 0.95, 0.95, 1)
                    else:
                        cell.background_color = (1, 1, 1, 1)
                    cell.readonly = False
    
    def validate_input(self, instance, value):
        """Validate input - only allow 1-9 and check if correct"""
        if value and value not in '123456789':
            instance.text = ''
            return
        elif len(value) > 1:
            instance.text = value[-1]
            value = value[-1]
        
        # Check if the entered number is correct
        if value and value in '123456789':
            row = instance.row
            col = instance.col
            entered_num = int(value)
            correct_num = self.solution[row][col]
            
            # Only check if this is a user-entered cell (not a given)
            if not instance.readonly:
                if entered_num == correct_num:
                    # Correct - green background
                    instance.background_color = (0.6, 0.9, 0.6, 1)
                else:
                    # Wrong - red background
                    instance.background_color = (0.9, 0.6, 0.6, 1)
    
    def check_solution(self, instance):
        """Check if the current solution is correct"""
        # Read values from cells
        current_grid = []
        for row in range(self.grid_size):
            current_row = []
            for col in range(self.grid_size):
                text = self.cells[row][col].text
                current_row.append(int(text) if text else 0)
            current_grid.append(current_row)
        
        # Check if complete and correct
        if all(all(cell > 0 for cell in row) for row in current_grid):
            if current_grid == self.solution:
                self.status_label.text = 'Correct! 🎉'
                for row in self.cells:
                    for cell in row:
                        if not cell.readonly:
                            cell.background_color = (0.6, 0.8, 0.4, 1)
            else:
                self.status_label.text = 'Not quite right. Try again!'
        else:
            self.status_label.text = 'Please fill all cells!'
    
    def go_back(self, instance):
        """Navigate back to practice page"""
        self.manager.current = 'practice_page'
