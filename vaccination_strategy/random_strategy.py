import random

# Vaccination strategy: Random 20% of people
def vaccination_strategy(model):
    vaccination_count = int(0.2 * model.metadata.shape[0])
    vaccinated = random.sample(list(model.metadata['ID']), vaccination_count)
    return vaccinated
