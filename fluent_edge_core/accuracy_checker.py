def calculate_accuracy(text, corrections):
    """
    Calculates the accuracy of the transcribed speech based on the number of detected grammar errors.

    :param text: The full transcribed text.
    :param corrections: A list of detected grammar errors.
    :return: Accuracy percentage (float).
    """
    if not text.strip():
        return 0  # No text means 0% accuracy

    if not isinstance(corrections, list):
        return 0  # Invalid corrections format

    total_words = len(text.split())
    error_count = len(corrections)

    accuracy = max(0, 100 - (error_count / total_words * 100))  # Ensure accuracy is not negative
    return round(accuracy, 2)