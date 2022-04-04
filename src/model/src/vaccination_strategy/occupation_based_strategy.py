import random

def occupation_based_vaccination_strategy(model):
    vaccination_count = int(0.2 * model.metadata.shape[0])
    working_people = [int(person) for idx, person in enumerate(model.metadata['id']) if int(model.metadata['office'][idx + 1]) != -1]
    # working_people = [int(person) for idx, person in enumerate(model.metadata['id'])]
    return random.sample(working_people, k=vaccination_count)