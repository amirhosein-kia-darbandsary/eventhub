
def calculate_available(total_quantity: int, reserved_quantity: int, sold_quantity: int) -> int:
    return total_quantity - reserved_quantity - sold_quantity