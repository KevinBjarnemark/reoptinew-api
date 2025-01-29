from django.utils.timezone import now


def user_is_mature(birth_date, age_restriction):
    """
    Determines if a user meets the minimum age requirement.

    This function calculates the user's age based on their birth date
    and the current date, then compares it against a specified age restriction.

    Args:
        birth_date (datetime.date): The user's date of birth.
        age_restriction (int): The minimum age requirement.

    Returns:
        bool: True if the user's age is greater than the age restriction,
            otherwise False.
    """
    if birth_date:
        today = now().date()
        age = today.year - birth_date.year

        # Check if birthday has not yet passed this year
        birthday_not_passed = today.month < birth_date.month or (
            today.month == birth_date.month and today.day < birth_date.day
        )

        # Subtract 1 from the age if the birthday hasn't passed this year
        if birthday_not_passed:
            age -= 1

        return age > age_restriction
