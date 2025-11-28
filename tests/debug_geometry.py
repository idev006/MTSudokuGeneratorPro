"""
Debug script for testing Jigsaw region generation
"""
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.geometry import GeometryFactory

# Test geometry generation
factory = GeometryFactory()

print("Testing Jigsaw Region Generation (9×9)...")
print("=" * 50)

for attempt in range(3):
    print(f"\nAttempt {attempt + 1}:")
    try:
        grid = factory._balanced_grow(9)
        
        # Print grid
        for r in range(9):
            row_str = ""
            for c in range(9):
                region_id = grid[r][c]
                if region_id == -1:
                    row_str += "X "
                else:
                    row_str += f"{region_id} "
            print(row_str)
        
        # Validate
        is_valid = factory._validate_regions(grid, 9)
        print(f"\nValid: {is_valid}")
        
        if is_valid:
            print("✅ SUCCESS - Generated irregular regions!")
            
            # Count region sizes
            region_counts = {}
            for r in range(9):
                for c in range(9):
                    rid = grid[r][c]
                    region_counts[rid] = region_counts.get(rid, 0) + 1
            
            print("\nRegion sizes:")
            for rid in sorted(region_counts.keys()):
                print(f"  Region {rid}: {region_counts[rid]} cells")
            break
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

print("\n" + "=" * 50)
print("Testing different sizes...")

for size in [6, 9, 12]:
    print(f"\nTesting {size}×{size}:")
    grid = factory.get_jigsaw_map(size)
    
    # Validate
    is_valid = factory._validate_regions(grid, size)
    print(f"  Valid: {is_valid}")
    
    if is_valid:
        print(f"  ✅ {size}×{size} works!")
    else:
        print(f"  ❌ {size}×{size} failed")
