import random

# Vaccination strategy: Random 20% of people
def random_vaccination_strategy(model):
    vaccination_count = int(0.2 * model.metadata.shape[0])
    vaccinated = random.sample(list(model.metadata['id']), vaccination_count)
    return vaccinated
