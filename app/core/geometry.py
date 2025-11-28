import random
from typing import List, Set, Tuple

class GeometryFactory:
    """
    Singleton factory for generating Jigsaw Sudoku irregular region maps.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GeometryFactory, cls).__new__(cls)
        return cls._instance

    @classmethod
    def clear_instance(cls):
        """Clear singleton instance for testing"""
        cls._instance = None

    def get_jigsaw_template(self, size: int, is_diagonal: bool = False) -> dict:
        """
        Get a Jigsaw template (regions + optional solution)
        """
        try:
            from app.core.template_cache import TemplateCache
            cache = TemplateCache()
            
            if cache.has_templates(size, is_diagonal):
                return cache.get_random_template(size, is_diagonal)
        except Exception as e:
            print(f"Warning: Template cache failed ({e})")
            
        # Fallback: Generate regions only (no solution)
        return {
            'regions': self._generate_irregular_regions(size),
            'solution': None
        }

    def get_jigsaw_map(self, size: int) -> List[List[int]]:
        """
        Legacy method for backward compatibility.
        Returns just the region map.
        """
        template = self.get_jigsaw_template(size, is_diagonal=False)
        return template['regions']

    def _generate_irregular_regions(self, size: int) -> List[List[int]]:
        """
        Generates irregular regions using a balanced region-growing algorithm.
        """
        for attempt in range(1000):
            try:
                grid = self._balanced_grow(size)
                if self._validate_regions(grid, size):
                    # Success!
                    return grid
            except Exception:
                continue
        
        # Fallback: standard boxes
        box_size = int(size ** 0.5)
        return [[(r // box_size) * box_size + (c // box_size) for c in range(size)] for r in range(size)]

    def _balanced_grow(self, size: int) -> List[List[int]]:
        """
        Balanced region growing with better seed placement.
        """
        grid = [[-1 for _ in range(size)] for _ in range(size)]
        
        # Step 1: Place seeds with better distribution
        region_cells = {i: [] for i in range(size)}
        
        # Use a grid-based approach for better seed distribution
        grid_dim = int(size ** 0.5)
        if grid_dim * grid_dim == size:
            # Perfect square - use regular grid for seeds
            for i in range(size):
                row_base = (i // grid_dim) * grid_dim
                col_base = (i % grid_dim) * grid_dim
                # Add some randomness within each cell
                r = row_base + random.randint(0, grid_dim - 1)
                c = col_base + random.randint(0, grid_dim - 1)
                # Ensure no collision
                while grid[r][c] != -1:
                    r = random.randint(0, size - 1)
                    c = random.randint(0, size - 1)
                grid[r][c] = i
                region_cells[i].append((r, c))
        else:
            # Not perfect square - use random with minimum distance
            all_cells = [(r, c) for r in range(size) for c in range(size)]
            random.shuffle(all_cells)
            for i in range(size):
                r, c = all_cells[i]
                grid[r][c] = i
                region_cells[i].append((r, c))
        
        # Track unassigned cells
        unassigned = set()
        for r in range(size):
            for c in range(size):
                if grid[r][c] == -1:
                    unassigned.add((r, c))
        
        # Step 2: Balanced growth
        max_iterations = size * size * 20
        iteration = 0
        
        while unassigned and iteration < max_iterations:
            iteration += 1
            progress = False
            
            # Sort regions by size (smallest first)
            regions_by_size = sorted(range(size), key=lambda r: len(region_cells[r]))
            
            for region_id in regions_by_size:
                if len(region_cells[region_id]) >= size:
                    continue
                
                if not unassigned:
                    break
                
                # Find neighbors
                neighbors = []
                for r, c in region_cells[region_id]:
                    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        nr, nc = r + dr, c + dc
                        if (nr, nc) in unassigned:
                            neighbors.append((nr, nc))
                
                neighbors = list(set(neighbors))
                
                if neighbors:
                    nr, nc = random.choice(neighbors)
                    grid[nr][nc] = region_id
                    region_cells[region_id].append((nr, nc))
                    unassigned.remove((nr, nc))
                    progress = True
            
            if not progress:
                raise Exception("Deadlock")
        
        if unassigned:
            raise Exception(f"Failed to assign {len(unassigned)} cells")
        
        return grid

    def _validate_regions(self, grid: List[List[int]], size: int) -> bool:
        """
        Validate that all regions have correct size and are contiguous.
        """
        # Check all cells assigned
        for row in grid:
            if -1 in row:
                return False
        
        # Check region sizes
        region_counts = {}
        for r in range(size):
            for c in range(size):
                region_id = grid[r][c]
                region_counts[region_id] = region_counts.get(region_id, 0) + 1
        
        # All regions must have exactly 'size' cells
        for rid, count in region_counts.items():
            if count != size:
                return False
        
        # Check contiguity
        for region_id in range(size):
            if not self._is_contiguous(grid, region_id, size):
                return False
        
        return True

    def _is_contiguous(self, grid: List[List[int]], region_id: int, size: int) -> bool:
        """
        Check if a region is contiguous using flood fill.
        """
        # Find first cell of this region
        start = None
        for r in range(size):
            for c in range(size):
                if grid[r][c] == region_id:
                    start = (r, c)
                    break
            if start:
                break
        
        if not start:
            return False
        
        # Flood fill
        visited = set()
        stack = [start]
        
        while stack:
            r, c = stack.pop()
            if (r, c) in visited:
                continue
            visited.add((r, c))
            
            # Check neighbors
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < size and 0 <= nc < size:
                    if grid[nr][nc] == region_id and (nr, nc) not in visited:
                        stack.append((nr, nc))
        
        # Count expected cells
        expected = sum(1 for r in range(size) for c in range(size) if grid[r][c] == region_id)
        
        return len(visited) == expected
