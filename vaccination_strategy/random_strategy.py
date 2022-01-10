import random

# Vaccination strategy: Random 20% of people


def vaccination_strategy(model):
    vaccination_count = 0.2*(model.end_range - model.start_range)
    vaccinated = random.sample(
        range(model.start_range, model.end_range), int(vaccination_count))
    return vaccinated
