import pandas as pd
import os
import random


class SIR:
    # Sets to keep track of people in the model
    susceptible = set()
    infected = set()
    recovered = set()
    vaccinated = set()
    # Can be modified according to the disease scenario
    alpha = 0.8
    beta = 0.3
    initial_infected = 12

    # Vaccinate the people in the list 'vaccinated_people'
    def vaccinate(self, vaccinated_people):
        for person in vaccinated_people:
            # Remove vaccinated person from susceptible people
            if person in self.susceptible:
                self.susceptible.remove(person)
                self.recovered.add(person)
            # Remove vaccinated person from infected people
            elif person in self.infected:
                self.infected.remove(person)
                self.recovered.add(person)

    def __init__(self, df, metadata):
        self.df = df
        self.metadata = metadata
        df.head()
        
    def init(self):
        for person in self.metadata['ID']:
            self.susceptible.add(person)
        self.infected = random.sample(self.susceptible, self.initial_infected)

        for infected_person in self.infected:
            self.susceptible.remove(infected_person)

    # Determine which category person belongs to
    def person_type(self, person):
        if(person in self.susceptible):
            return 'susceptible'
        if(person in self.infected):
            return 'infected'
        return 'recovered'

    # Simulate new infected people
    def get_new_infected(self, infected_contact):
        total = len(infected_contact)
        new_infected_total = self.alpha * total
        new_infected = random.sample(infected_contact, k=int(new_infected_total))
        # Remove duplicates
        new_infected = list(set(new_infected))
        # Add them to infected
        for infected_person in new_infected:
            self.infected.append(infected_person)
            self.susceptible.remove(infected_person)

    # Simulate natural recovery
    def get_new_recovered(self):
        recovered_count = self.beta * (len(self.infected))
        new_recovered = random.sample(self.infected, k=int(recovered_count))
        # Add them to recovered
        for recovered_person in new_recovered:
            self.infected.remove(recovered_person)
            self.recovered.add(recovered_person)


def simulate(model, timestamps, vaccinated, vaccination_day):
    total_count = 0
    days = 0
    previous_timestamp = 0

    print("At day 0")
    print("Number of susceptible: ", len(model.susceptible))
    print("Number of infected: ", len(model.infected))
    print("Number of recovered: ", len(model.recovered))
    
    while total_count < model.df.shape[0]:
        count = 0
        infected_contact = []
        while count < timestamps and total_count < model.df.shape[0]:
            person1 = model.df["Person 1"][total_count]
            person2 = model.df["Person 2"][total_count]
            # Check for transitions from susceptible to infected
            if model.person_type(person1) == 'susceptible' and model.person_type(person2) == 'infected':
                infected_contact.append(person1)
            if model.person_type(person2) == 'susceptiblee' and model.person_type(person1) == 'infected':
                infected_contact.append(person2)
            # If new timestamp, then increase count
            if(model.df["Time"][total_count] != previous_timestamp):
                previous_timestamp = model.df["Time"][total_count]
                count = count + 1
            total_count = total_count + 1
        
        model.get_new_recovered()
        model.get_new_infected(infected_contact)
        
        days = days + 1

        if(days == vaccination_day):
            model.vaccinate(vaccinated)
        
        print("After Day ", days)
        print("Number of susceptible: ", len(model.susceptible))
        print("Number of infected: ", len(model.infected))
        print("Number of recovered: ", len(model.recovered))

# The variable vaccination_day specifies the day after which the population must be vaccinated
def run(model, vaccinated, vaccination_day):
    # 105 timestamps are going to be clustered together and considered as one day.
    # This would make the dataset into 30 days
    timestamps_in_a_day = 105    
    model.init()
    simulate(model, timestamps_in_a_day, vaccinated, vaccination_day)
