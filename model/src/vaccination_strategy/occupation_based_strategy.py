import random

def vaccination_strategy(model):
    vaccination_count = int(0.2 * model.metadata.shape[0])
    working_people = [int(person) for idx, person in enumerate(model.metadata['ID']) if int(model.metadata['Office'][idx]) != -1]
    return random.sample(working_people, k=vaccination_count)
