import pandas as pd
import os
import random
import numpy as np
import matplotlib.pyplot as plt

class SIR:
    # Can be modified according to the disease scenario
    beta = 0.8 # Probability of getting infected on interaction with an infected person. 
    gamma = 0.3 # Probability of natural recovery for an infected person
    alpha = 0.05 # Probablity of an infected person dying
    initial_infected = 12
    no_susceptible = []
    no_infected = []
    no_recovered = []
    no_deceased = []

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
        
    def init(self):
        # Sets to keep track of people in the model
        self.susceptible = set()
        self.infected = set()
        self.recovered = set()
        self.vaccinated = set()
        self.deceased = set()
        for person in self.metadata['ID']:
            self.susceptible.add(person)
        
        self.infected = random.sample(list(self.susceptible), self.initial_infected)
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
        new_infected_total = self.beta * total
        new_infected = random.sample(infected_contact, k=int(new_infected_total))
        # Remove duplicates
        new_infected = list(set(new_infected))
        # Add them to infected
        for infected_person in new_infected:
            self.infected.append(infected_person)
            self.susceptible.remove(infected_person)

    # Simulate natural recovery
    def get_new_recovered(self):
        recovered_count = int(self.gamma * len(self.infected))
        new_recovered = random.sample(self.infected, k=recovered_count)
        # Add them to recovered
        for recovered_person in new_recovered:
            self.infected.remove(recovered_person)
            self.recovered.add(recovered_person)

    # Simulate deaths
    def get_new_deaths(self):
        death_count = int(self.alpha * len(self.infected))
        new_deaths = random.sample(self.infected, k=death_count)
        # Add them to deceased
        for deceased_person in new_deaths:
            self.infected.remove(deceased_person)
            self.deceased.add(deceased_person)
            
def visualize(model):
    no_sus = np.array(model.no_susceptible)
    no_inf = np.array(model.no_infected)
    no_rec = np.array(model.no_recovered)
    no_dec = np.array(model.no_deceased)
    
    time = []
    for i in range(31):
        time.append(i)
    
    time = np.array(time)
    
    plt.plot(time,no_sus,label = 'Suscepted')
    plt.plot(time,no_inf,label = 'Infected')
    plt.plot(time,no_rec,label = 'Recovered')
    plt.plot(time,no_dec,label = 'Deceased')
    
    plt.legend()
    
def simulate(model, timestamps, vaccinated, vaccination_day):
    total_count = 0
    days = 0
    previous_timestamp = 0
    
    model.no_susceptible.append(len(model.susceptible))
    model.no_infected.append(len(model.infected))
    model.no_recovered.append(len(model.recovered))
    model.no_deceased.append(len(model.deceased))

    print("At day 0")
    print("Number of susceptible: ", model.no_susceptible[0])
    print("Number of infected: ", model.no_infected[0])
    print("Number of recovered: ", model.no_recovered[0])
    print("Number of deceased: ", model.no_deceased[0])

    max_infections = model.no_infected[0]

    while total_count < model.df.shape[0]:
        count = 0
        infected_contact = []
        while count < timestamps and total_count < model.df.shape[0]:
            person1 = model.df["Person 1"][total_count]
            person2 = model.df["Person 2"][total_count]
            # Check for transitions from susceptible to infected
            if model.person_type(person1) == 'susceptible' and model.person_type(person2) == 'infected':
                infected_contact.append(person1)
            if model.person_type(person2) == 'susceptible' and model.person_type(person1) == 'infected':
                infected_contact.append(person2)
            # If new timestamp, then increase count
            if(model.df["Time"][total_count] != previous_timestamp):
                previous_timestamp = model.df["Time"][total_count]
                count = count + 1
            total_count = total_count + 1
        
        model.get_new_recovered()
        model.get_new_infected(infected_contact)
        model.get_new_deaths()
        
        model.no_susceptible.append(len(model.susceptible))
        model.no_infected.append(len(model.infected))
        model.no_recovered.append(len(model.recovered))
        model.no_deceased.append(len(model.deceased))
        
        days = days + 1

        if(days == vaccination_day):
            model.vaccinate(vaccinated)
            
        
        print("After Day ", days)
        print("Number of susceptible: ", len(model.susceptible))
        print("Number of infected: ", len(model.infected))
        print("Number of recovered: ", len(model.recovered))
        print("Number of deceased: ", len(model.deceased))

        max_infections = max(max_infections, len(model.infected))
    
    return {
        'metrics': {
            'total_deaths': len(model.deceased),
            'peak_infections': max_infections
        }
    }

# The variable vaccination_day specifies the day after which the population must be vaccinated
def run(model, vaccinated, vaccination_day):
    # 105 timestamps are going to be clustered together and considered as one day.
    # This would make the dataset into 30 days


    timestamps_in_a_day = 105    
    model.init()
    result = simulate(model, timestamps_in_a_day, vaccinated, vaccination_day)
    visualize(model)
    print(result)
    return result

