def format_compact(number: float) -> str:
    sign = "-" if number < 0 else ""
    abs_number = abs(int(number))

    if abs_number >= 1_000_000:
        millions = abs_number // 1_000_000
        decimal = (abs_number % 1_000_000) // 100_000  # Lấy 1 chữ số thập phân
        remainder_thousands = (abs_number % 1_000_000) % 100_000 // 1_000

        result = f"{sign}{millions}.{decimal}M"
        if remainder_thousands > 0:
            result += f" {remainder_thousands}K"
        return result

    elif abs_number >= 1_000:
        thousands = abs_number // 1_000
        remainder = abs_number % 1_000
        result = f"{sign}{thousands}K"
        if remainder > 0:
            result += f" {remainder}"
        return result

    else:
        return f"{sign}{abs_number}"
