import pandas as pd
import os
import random


class SIR:
    suscepted = []
    infected = []
    recovered = []
    vaccinated = []
    # Can be modified according to the disease scenario
    alpha = 0.8
    beta = 0.3
    initial_infected = 12

    #  As per the data in the dataset
    start_range = 1426
    end_range = 1922+1

    def random_sample(self, start_range, end_range, select):
        return random.sample(range(start_range, end_range), select)

    # Vaccinate the people in the list 'vaccinated_people'
    def vaccinate(self, vaccinated_people):
        for person in vaccinated_people:
            # Remove vaccinated person from suscepted people
            if person in self.suscepted:
                self.suscepted.remove(person)
                self.recovered.append(person)
            # Remove vaccinated person from infected people
            elif person in self.infected:
                self.infected.remove(person)
                self.recovered.append(person)

    def init(self):
        for person in range(self.start_range, self.end_range):
            self.suscepted.append(person)
        self.infected = self.random_sample(
            self.start_range, self.end_range, self.initial_infected)

        for infected_person in self.infected:
            self.suscepted.remove(infected_person)

    # determine which category person belongs to
    def person_type(self, person):
        if(person in self.suscepted):
            return 'suscepted'
        if(person in self.infected):
            return 'infected'
        return 'recovered'

    # Simulate new infected people
    def get_new_infected(self, infected_contact):
        total = len(infected_contact)
        new_infected_total = self.alpha*total
        new_infected = random.sample(
            infected_contact, k=int(new_infected_total))

        # Remove duplicates
        new_infected = list(set(new_infected))

        # Add them to infected
        for infected_person in new_infected:
            self.infected.append(infected_person)
            self.suscepted.remove(infected_person)

    # Simulate new recovered people
    def get_new_recovered(self):
        recovered_count = self.beta*(len(self.infected))
        new_recovered = random.sample(self.infected, k=int(recovered_count))

        # Add them to recovered
        for recovered_person in new_recovered:
            self.infected.remove(recovered_person)
            self.recovered.append(recovered_person)


def simulate(model, df, timestamps, vaccinated, d):
    total_count = 0
    days = 0
    previous_timestamp = 0

    print("At day 0")
    print("Number of susceptible: ", len(model.suscepted))
    print("Number of infected: ", len(model.infected))
    print("Number of recovered: ", len(model.recovered))
    
    while total_count < df.shape[0]:
        count = 0
        infected_contact = []
        while count < timestamps and total_count < df.shape[0]:
            person1 = df["Person 1"][total_count]
            person2 = df["Person 2"][total_count]

            # Check for transitions from Suscepted to Infected
            if model.person_type(person1) == 'suscepted' and model.person_type(person2) == 'infected':
                infected_contact.append(person1)
            if model.person_type(person2) == 'suscepted' and model.person_type(person1) == 'infected':
                infected_contact.append(person2)

            # If new timestamp, then increase count
            if(df["Time"][total_count] != previous_timestamp):
                previous_timestamp = df["Time"][total_count]
                count = count + 1
            total_count = total_count + 1
            

        days = days + 1
        model.get_new_recovered()
        model.get_new_infected(infected_contact)
        if(days == d):
            model.vaccinate(vaccinated)
        print("After Day ", days)
        print("Number of susceptible: ", len(model.suscepted))
        print("Number of infected: ", len(model.infected))
        print("Number of recovered: ", len(model.recovered))

# the variable d specifies the day after which the population must be vaccinated
def run(model, vaccinated, d):
    df = pd.read_csv('../primaryschool.csv')
    # 105 timestamps are going to be clustered together and considered as one day.
    # This would make the dataset into 30 days
    timestamps_in_a_day = 105    
    model.init()
    simulate(model, df, timestamps_in_a_day, vaccinated, d)
