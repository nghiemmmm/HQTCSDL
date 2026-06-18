def score_to_words(score: float) -> str:
    """
    Convert a score (0.0 to 10.0) into Vietnamese spelled-out words.
    E.g., 8.5 -> "Tám phẩy năm", 8.25 -> "Tám phẩy hai mươi lăm"
    """
    if score is None:
        return ""
    
    score = round(score, 2)
    
    number_words = {
        0: "Không", 1: "Một", 2: "Hai", 3: "Ba", 4: "Bốn",
        5: "Năm", 6: "Sáu", 7: "Bảy", 8: "Tám", 9: "Chín", 10: "Mười"
    }
    
    integer_part = int(score)
    decimal_part = round((score - integer_part) * 100)
    
    integer_word = number_words.get(integer_part, "")
    
    if decimal_part == 0:
        return integer_word
    
    if decimal_part % 10 == 0:
        dec_val = decimal_part // 10
        dec_word = "năm" if dec_val == 5 else number_words.get(dec_val, "").lower()
        return f"{integer_word} phẩy {dec_word}"
    
    tens = decimal_part // 10
    ones = decimal_part % 10
    
    tens_word = "mười" if tens == 1 else f"{number_words.get(tens, '').lower()} mươi"
    if ones == 5:
        ones_word = "lăm"
    elif ones == 1 and tens > 1:
        ones_word = "mốt"
    else:
        ones_word = number_words.get(ones, "").lower()
        
    return f"{integer_word} phẩy {tens_word} {ones_word}"


def score_to_letter(score: float) -> str:
    """
    Convert a score (0.0 to 10.0) into standard PTIT college letter grade (A, B+, etc.).
    """
    if score is None:
        return ""
    
    if score >= 8.5:
        return "A"
    elif score >= 8.0:
        return "B+"
    elif score >= 7.0:
        return "B"
    elif score >= 6.5:
        return "C+"
    elif score >= 5.5:
        return "C"
    elif score >= 5.0:
        return "D+"
    elif score >= 4.0:
        return "D"
    else:
        return "F"
