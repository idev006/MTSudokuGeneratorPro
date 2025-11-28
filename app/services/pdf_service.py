from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from typing import List
import os
from app.models.grid import SudokuGrid

class PDFService:
    """
    Service for generating PDF files from Sudoku grids.
    """
    THAI_DIGITS = ['ก', 'ข', 'ค', 'ง', 'จ', 'ฉ', 'ช', 'ซ', 'ฌ']
    HEX_DIGITS = ['1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F']

    def __init__(self):
        # Register Thai font from Config
        from app.services.config_manager import ConfigManager
        self.config_manager = ConfigManager()
        
        self.thai_font = 'Helvetica' # Default fallback
        
        # Load Visual Settings
        self.gray_color = self.config_manager.get_visual_setting("gray_color", "#c5c5c5")
        self.gray_margin = self.config_manager.get_visual_setting("gray_margin", 3)
        
        try:
            thai_font_path = self.config_manager.get_font_path('thai_font')
            if thai_font_path:
                # Use font filename (without extension) as font name
                font_name = os.path.splitext(os.path.basename(thai_font_path))[0]
                pdfmetrics.registerFont(TTFont(font_name, thai_font_path))
                self.thai_font = font_name
                print(f"PDFService: Registered Thai font '{font_name}'")
            else:
                print("PDFService: Thai font not configured or not found, using Helvetica")
        except Exception as e:
            print(f"PDFService: Error registering font: {e}")
            self.thai_font = 'Helvetica'

    def create_pdf(self, puzzles: List[SudokuGrid], filename: str):
        """
        Creates a PDF containing the given puzzles and their solutions.
        """
        c = canvas.Canvas(filename, pagesize=A4)
        width, height = A4
        
        if not puzzles:
            c.save()
            return

        # 0. Draw Cover Page
        self._draw_cover_page(c, width, height, puzzles[0], len(puzzles))
        
        # Layout settings
        margin = 50
        grid_size = 400
        cell_size = grid_size / 9 # Default, will adjust per grid
        
        # 1. Draw Puzzles
        self._draw_section(c, puzzles, width, height, margin, grid_size, is_solution=False)
        
        # 2. Draw Solutions (New Page)
        c.showPage()
        
        # Add a title page for Solutions? Or just start.
        # Let's just start solutions on a new page.
        font_name = self.thai_font if hasattr(self, 'thai_font') and self.thai_font else "Helvetica-Bold"
        c.setFont(font_name, 24)
        c.drawCentredString(width / 2, height / 2, "เฉลย (Solutions)")
        c.showPage()
        
        self._draw_section(c, puzzles, width, height, margin, grid_size, is_solution=True)

        c.save()

    def _draw_cover_page(self, c, width, height, sample_grid: SudokuGrid, count: int):
        """Draws the first page with Thai details."""
        font_name = self.thai_font if hasattr(self, 'thai_font') and self.thai_font else "Helvetica"
        
        # Title
        c.setFont(font_name, 36)
        c.drawCentredString(width / 2, height - 150, "แบบฝึกหัดซูโดกุ (Sudoku)")
        
        # Details
        c.setFont(font_name, 20)
        y_start = height - 250
        line_height = 40
        
        # Map Type to Thai Name (Optional, or just use English name)
        type_name = sample_grid.type_name.replace("_", " ").title()
        
        c.drawString(100, y_start, f"ประเภท (Type): {type_name}")
        c.drawString(100, y_start - line_height, f"จำนวนข้อ (Count): {count} ข้อ")
        
        # Instructions
        c.drawString(100, y_start - line_height * 3, "วิธีการเล่น (Instructions):")
        c.setFont(font_name, 16)
        
        instructions = self._get_instructions(sample_grid.type_name)
        inst_y = y_start - line_height * 4
        for line in instructions:
            c.drawString(120, inst_y, f"- {line}")
            inst_y -= 30
            
        c.showPage()

    def _get_instructions(self, type_name: str) -> List[str]:
        """Returns Thai instructions based on Sudoku type."""
        base_rules = ["เติมตัวเลข 1-9 ลงในช่องว่าง (Fill numbers 1-9)", 
                      "ห้ามซ้ำกันในแถวแนวนอน (No duplicates in rows)", 
                      "ห้ามซ้ำกันในแถวแนวตั้ง (No duplicates in columns)",
                      "ห้ามซ้ำกันในตารางย่อย 3x3 (No duplicates in 3x3 boxes)"]
        
        tn = type_name.lower()
        if "6x6" in tn:
             base_rules = ["เติมตัวเลข 1-6 ลงในช่องว่าง", "ห้ามซ้ำกันในแถวและคอลัมน์", "ห้ามซ้ำกันในตารางย่อย 2x3"]
        
        if "alphabet" in tn:
            if "thai" in tn:
                base_rules[0] = "เติมตัวอักษร ก-ฮ ลงในช่องว่าง"
            else:
                base_rules[0] = "เติมตัวอักษร A-Z ลงในช่องว่าง"

        specific_rules = []
        if "diagonal" in tn:
            specific_rules.append("ห้ามซ้ำกันในแนวทแยงมุมทั้งสอง (No duplicates in main diagonals)")
        if "jigsaw" in tn:
            # Replace the last rule (Box rule) with Jigsaw rule
            base_rules[-1] = "ห้ามซ้ำกันในพื้นที่รูปทรงอิสระ (No duplicates in irregular regions)"
        if "windoku" in tn:
            specific_rules.append("ห้ามซ้ำกันในหน้าต่างระบายสี 4 แห่ง (No duplicates in 4 shaded windows)")
        if "asterisk" in tn:
            specific_rules.append("ห้ามซ้ำกันในช่องที่มีดอกจัน/ระบายสี (No duplicates in asterisk cells)")
        if "consecutive" in tn:
            specific_rules.append("ขีดคั่นระหว่างช่อง หมายถึงเลขเรียงกัน (Bar means consecutive numbers)")
        if "even" in tn and "odd" in tn:
            specific_rules.append("ช่องระบายสีคือเลขคู่ (Shaded cells are Even numbers)")
            
        return base_rules + specific_rules

    def _draw_section(self, c, puzzles, width, height, margin, grid_size, is_solution):
        if not puzzles:
            return
            
        # Get layout based on first puzzle size (assume all same size)
        rows, cols, puzzle_size = self._calculate_layout(puzzles[0].size, width, height, margin)
        puzzles_per_page = rows * cols
        
        # Calculate spacing
        h_spacing = (width - cols * puzzle_size) / (cols + 1)
        v_spacing = (height - rows * puzzle_size) / (rows + 1)
        
        for i, grid in enumerate(puzzles):
            # Check if we need a new page
            if i > 0 and i % puzzles_per_page == 0:
                c.showPage()
            
            # Calculate position on current page
            page_index = i % puzzles_per_page
            row = page_index // cols
            col = page_index % cols
            
            x = h_spacing + col * (puzzle_size + h_spacing)
            y = height - v_spacing - (row + 1) * puzzle_size - row * v_spacing
            
            # Adjust cell size for grid size
            current_cell_size = puzzle_size / grid.size
            
            self._draw_grid(c, grid, x, y, puzzle_size, current_cell_size, grid.size)
            self._draw_numbers(c, grid, x, y, current_cell_size, is_solution)
            
            # Label
            font_name = self.thai_font if hasattr(self, 'thai_font') and self.thai_font else "Helvetica"
            c.setFont(font_name, 10)
            label = f"#{i+1}"
            if is_solution:
                label += " (เฉลย)"
            c.drawCentredString(x + puzzle_size / 2, y + puzzle_size + 5, label)

    def _draw_grid(self, c, grid: SudokuGrid, x, y, size_px, cell_size, grid_size_cells):
        """Draws the grid lines."""
        c.setStrokeColor(colors.black)
        
        # For Jigsaw: Draw thin grid lines + thick region borders
        if "jigsaw" in grid.type_name.lower():
            # 1. Draw thin grid lines for all cells
            c.setLineWidth(1)
            for i in range(grid_size_cells + 1):
                # Vertical
                c.line(x + i * cell_size, y, x + i * cell_size, y + size_px)
                # Horizontal
                c.line(x, y + i * cell_size, x + size_px, y + i * cell_size)
            
            # 2. Draw thick region borders (on top of thin lines)
            c.setLineWidth(3)
            
            # Draw outer border
            c.rect(x, y, size_px, size_px)
            
            # Draw internal region borders
            for r in range(grid_size_cells):
                for col in range(grid_size_cells):
                    current_region = grid.cells[r][col].region_id
                    
                    # Check Right neighbor
                    if col < grid_size_cells - 1:
                        right_region = grid.cells[r][col+1].region_id
                        if right_region != current_region:
                            # Draw vertical line between regions
                            line_x = x + (col + 1) * cell_size
                            line_y_bottom = y + (grid_size_cells - 1 - r) * cell_size
                            line_y_top = line_y_bottom + cell_size
                            c.line(line_x, line_y_bottom, line_x, line_y_top)
                    
                    # Check Bottom neighbor
                    if r < grid_size_cells - 1:
                        bottom_region = grid.cells[r+1][col].region_id
                        if bottom_region != current_region:
                            # Draw horizontal line between regions
                            line_y = y + (grid_size_cells - 1 - r) * cell_size
                            line_x_left = x + col * cell_size
                            line_x_right = line_x_left + cell_size
                            c.line(line_x_left, line_y, line_x_right, line_y)
            
            # Draw Diagonal Lines for Jigsaw Diagonal
            if "diagonal" in grid.type_name.lower():
                c.setLineWidth(1)
                c.setStrokeColor(colors.HexColor("#9999FF"))  # Lighter Blue for diagonals
                
                # Main diagonal (top-left to bottom-right)
                c.line(x, y + size_px, x + size_px, y)
                
                # Anti-diagonal (top-right to bottom-left)
                c.line(x + size_px, y + size_px, x, y)
                
                c.setStrokeColor(colors.black)  # Reset color

            return  # Done for Jigsaw
        
        # For non-Jigsaw: Draw all thin grid lines first
        c.setLineWidth(1)
        for i in range(grid_size_cells + 1):
            # Vertical
            c.line(x + i * cell_size, y, x + i * cell_size, y + size_px)
            # Horizontal
            c.line(x, y + i * cell_size, x + size_px, y + i * cell_size)
        
        # For standard Sudoku: Draw thick box lines
        c.setLineWidth(3)
        
        # Determine box size
        if grid_size_cells == 6: box_rows, box_cols = 2, 3
        elif grid_size_cells == 8: box_rows, box_cols = 2, 4
        elif grid_size_cells == 9: box_rows, box_cols = 3, 3
        elif grid_size_cells == 10: box_rows, box_cols = 2, 5
        elif grid_size_cells == 12: box_rows, box_cols = 3, 4
        elif grid_size_cells == 14: box_rows, box_cols = 2, 7
        elif grid_size_cells == 15: box_rows, box_cols = 3, 5
        elif grid_size_cells == 16: box_rows, box_cols = 4, 4
        else:
            box_rows = int(grid_size_cells ** 0.5)
            box_cols = grid_size_cells // box_rows

        # Vertical thick lines (every box_cols)
        for i in range(0, grid_size_cells + 1, box_cols):
            c.line(x + i * cell_size, y, x + i * cell_size, y + size_px)
            
        # Horizontal thick lines (every box_rows)
        for i in range(0, grid_size_cells + 1, box_rows):
            c.line(x, y + i * cell_size, x + size_px, y + i * cell_size)
        
        # Draw diagonal lines for Diagonal Sudoku
        if "diagonal" in grid.type_name.lower():
            c.setLineWidth(1)
            c.setStrokeColor(colors.HexColor("#9999FF"))  # Lighter Blue for diagonals
            
            # Main diagonal (top-left to bottom-right)
            c.line(x, y + size_px, x + size_px, y)
            
            # Anti-diagonal (top-right to bottom-left)
            c.line(x + size_px, y + size_px, x, y)
            
            c.setStrokeColor(colors.black)  # Reset color

        # Windoku Shading (9x9 only)
        if "windoku" in grid.type_name.lower() and grid_size_cells == 9:
            c.setFillColor(colors.HexColor(self.gray_color))
            # 4 Windows: R2-4 C2-4, R2-4 C6-8, R6-8 C2-4, R6-8 C6-8 (1-based)
            # 0-based: R1-3 C1-3, R1-3 C5-7, R5-7 C1-3, R5-7 C5-7
            windows = [
                (1, 1), (1, 5),
                (5, 1), (5, 5)
            ]
            margin = self.gray_margin
            for start_r, start_c in windows:
                for r in range(start_r, start_r + 3):
                    for col in range(start_c, start_c + 3):
                        rect_y = y + (grid_size_cells - 1 - r) * cell_size
                        c.rect(x + col * cell_size + margin, rect_y + margin, cell_size - 2*margin, cell_size - 2*margin, fill=1, stroke=0)
            c.setFillColor(colors.black) # Reset

        # Asterisk Shading (9x9 only)
        if "asterisk" in grid.type_name.lower() and grid_size_cells == 9:
            c.setFillColor(colors.HexColor(self.gray_color))
            asterisk_cells = [
                (1, 4), (2, 2), (2, 6),
                (4, 1), (4, 4), (4, 7),
                (6, 2), (6, 6), (7, 4)
            ]
            margin = self.gray_margin
            for r, col in asterisk_cells:
                # Draw gray rect
                # y is inverted in my logic above? No, y grows up.
                # Row r corresponds to y + (size - 1 - r) * cell_size
                rect_y = y + (grid_size_cells - 1 - r) * cell_size
                c.rect(x + col * cell_size + margin, rect_y + margin, cell_size - 2*margin, cell_size - 2*margin, fill=1, stroke=0)
            c.setFillColor(colors.black) # Reset

        # Even-Odd Shading
        if grid.even_odd_mask:
            c.setFillColor(colors.HexColor(self.gray_color))
            margin = self.gray_margin
            for r in range(grid_size_cells):
                for col in range(grid_size_cells):
                    if grid.even_odd_mask[r][col]:
                        # Draw gray rect
                        rect_y = y + (grid_size_cells - 1 - r) * cell_size
                        c.rect(x + col * cell_size + margin, rect_y + margin, cell_size - 2*margin, cell_size - 2*margin, fill=1, stroke=0)
            c.setFillColor(colors.black) # Reset

        # Consecutive Bars
        if grid.consecutive_pairs:
            c.setLineWidth(2)
            c.setStrokeColor(colors.black) # or white if on gray? Black is fine.
            bar_len = cell_size * 0.2
            for (r1, c1), (r2, c2) in grid.consecutive_pairs:
                # Calculate center between cells
                # r1, c1 is first cell. r2, c2 is neighbor.
                # Coordinates
                x1 = x + c1 * cell_size + cell_size / 2
                y1 = y + (grid_size_cells - 1 - r1) * cell_size + cell_size / 2
                x2 = x + c2 * cell_size + cell_size / 2
                y2 = y + (grid_size_cells - 1 - r2) * cell_size + cell_size / 2
                
                cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
                
                if r1 == r2: # Horizontal neighbors
                    # Vertical bar
                    c.line(cx, cy - bar_len, cx, cy + bar_len)
                else: # Vertical neighbors
                    # Horizontal bar
                    c.line(cx - bar_len, cy, cx + bar_len, cy)

    def _draw_numbers(self, c, grid: SudokuGrid, x, y, cell_size, is_solution):
        """Draws the numbers in the cells."""
        # Use configured font (supports Thai)
        font_name = self.thai_font if hasattr(self, 'thai_font') and self.thai_font else "Helvetica"
        c.setFont(font_name, 24)
        
        data_source = grid.solution if is_solution and grid.solution else [[c.value for c in row] for row in grid.cells]

        for r in range(grid.size):
            for col in range(grid.size):
                val = data_source[r][col]
                if val != 0:
                    display_val = self._get_display_value(val, grid.type_name)
                    
                    text_x = x + col * cell_size + cell_size / 2
                    text_y = y + (grid.size - r) * cell_size - cell_size / 2 - 8
                    
                    c.drawCentredString(text_x, text_y, display_val)

    def _get_display_value(self, val: int, type_name: str) -> str:
        if "thai" in type_name.lower():
            if 1 <= val <= 9:
                return self.THAI_DIGITS[val - 1]
            return str(val)
        elif "alphabet" in type_name.lower() and "thai" not in type_name.lower():
            # A=1, B=2, ...
            if 1 <= val <= 26:
                return chr(64 + val)
            return str(val)
        elif val > 9:
            # Hex/Alpha for >9
            return self.HEX_DIGITS[val - 1]
        return str(val)

    def _calculate_layout(self, grid_size: int, page_width: float, page_height: float, margin: float) -> tuple:
        """
        Calculate optimal layout based on actual dimensions
        
        Args:
            grid_size: Number of cells per side (e.g., 6, 9, 12)
            page_width: PDF page width in points
            page_height: PDF page height in points
            margin: Margin in points
            
        Returns:
            (rows, cols, puzzle_size_px): Layout configuration
        """
        # Define minimum cell size for readability (in points)
        MIN_CELL_SIZE = 20
        
        available_width = page_width - 2 * margin
        available_height = page_height - 2 * margin
        
        # Try different grid layouts (rows x cols)
        # We want to maximize puzzles per page while keeping cell size readable
        
        # Heuristic: Start with 2x2 for 9x9, 3x2 for 6x6
        if grid_size <= 6:
            rows, cols = 3, 2
        elif grid_size <= 9:
            rows, cols = 2, 2
        else:
            rows, cols = 1, 1 # Large puzzles, one per page
            
        spacing = 30 # Space between puzzles
        
        # Calculate max possible puzzle size
        actual_puzzle_width = (available_width - spacing * (cols - 1)) / cols
        actual_puzzle_height = (available_height - spacing * (rows - 1)) / rows
        
        # Use the smaller dimension to ensure square cells
        final_puzzle_size = min(actual_puzzle_width, actual_puzzle_height)
        
        # Ensure cell size is within acceptable range
        final_cell_size = final_puzzle_size / grid_size
        if final_cell_size < MIN_CELL_SIZE:
            # Reduce number of puzzles per page
            if cols > rows:
                cols = max(1, cols - 1)
            else:
                rows = max(1, rows - 1)
            # Recalculate
            actual_puzzle_width = (available_width - spacing * (cols - 1)) / cols
            actual_puzzle_height = (available_height - spacing * (rows - 1)) / rows
            final_puzzle_size = min(actual_puzzle_width, actual_puzzle_height)
        
        return (rows, cols, final_puzzle_size)
