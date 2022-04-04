import pandas as pd
import random
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx

class SIR:
    # Can be modified according to the disease scenario
    beta = 0.8 # Probability of getting infected on interaction with an infected person. 
    gamma = 0.3 # Probability of natural recovery for an infected person
    alpha = 0.05 # Probablity of an infected person dying
    initial_infected = 30

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
            try:
                self.susceptible.add(int(person))
            except:
                pass
        
        self.infected = random.sample(list(self.susceptible), self.initial_infected)
        for infected_person in self.infected:
            self.susceptible.remove(infected_person)

        self.graph, self.positions = self.create_contact_graph()

    # Determine which category person belongs to
    def person_type(self, person):
        if person in self.susceptible:
            return 'susceptible'
        if person in self.infected:
            return 'infected'
        return 'recovered'

    # Simulate new infected people
    def get_new_infected(self, infected_contact):
        new_infected = [person for person in infected_contact if random.random() <= self.beta]
        # Add them to infected
        for infected_person in new_infected:
            self.infected.append(infected_person)
            self.susceptible.remove(infected_person)

    # Simulate natural recovery
    def get_new_recovered(self):
        new_recovered = [person for person in self.infected if random.random() <= self.gamma]
        # Add them to recovered
        for recovered_person in new_recovered:
            self.infected.remove(recovered_person)
            self.recovered.add(recovered_person)

    # Simulate deaths
    def get_new_deaths(self):
        new_deaths = [person for person in self.infected if random.random() <= self.alpha]
        # Add them to deceased
        for deceased_person in new_deaths:
            self.infected.remove(deceased_person)
            self.deceased.add(deceased_person)
    
    # Create contact graph
    def create_contact_graph(self):
        index = 0
        graph = nx.Graph()
        while index < self.metadata.shape[0]:
            graph.add_node(int(self.metadata['ID'][index]))
            index += 1
        pos = nx.random_layout(graph)
        return graph, pos
    
    # Visualize the contact graph
    def visualize_graph(self, vaccinated):
        plt.figure(figsize=(40,40)) 
        nx.draw_networkx(self.graph, pos=self.positions, nodelist=list(self.susceptible), node_size=1800,node_color='dodgerblue', font_size = 17)   
        nx.draw_networkx(self.graph, pos=self.positions, nodelist=list(self.infected), node_size=1800,node_color='orange', font_size = 17)         
        nx.draw_networkx(self.graph, pos=self.positions, nodelist=list(self.recovered), node_size=1800,node_color='limegreen', font_size = 17)         
        nx.draw_networkx(self.graph, pos=self.positions, nodelist=list(self.deceased), node_size=1800,node_color='orangered', font_size = 17)     
        nx.draw_networkx(self.graph, pos=self.positions, nodelist=list(vaccinated), node_size=1800,node_color='yellow', font_size = 17)
        s_blue = mpatches.Patch(color='dodgerblue', label='Susceptible')
        i_orange = mpatches.Patch(color='orange', label='Infected')
        r_green = mpatches.Patch(color='limegreen', label='Recovered')
        d_red = mpatches.Patch(color='orangered', label='Deceased')
        v_yellow = mpatches.Patch(color='yellow', label='Vaccinated')
        plt.legend(handles=[s_blue, i_orange, r_green, d_red, v_yellow], prop={"size":20})
        plt.show()
            
def visualize(result):
    no_sus = np.array(result['stats']['susceptible'])
    no_inf = np.array(result['stats']['infected'])
    no_rec = np.array(result['stats']['recovered'])
    no_dec = np.array(result['stats']['deceased'])
    
    time = np.array(range(len(no_sus)))
    
    plt.plot(time, no_sus, label='Suscepted')
    plt.plot(time, no_inf, label='Infected')
    plt.plot(time, no_rec, label='Recovered')
    plt.plot(time, no_dec, label='Deceased')
    
    plt.legend()

def display_stats(day, model):
    print(f"At day {day}")
    print("Number of susceptible: ", len(model.susceptible))
    print("Number of infected: ", len(model.infected))
    print("Number of recovered: ", len(model.recovered))
    print("Number of deceased: ", len(model.deceased))
    
def simulate(model, timespan, vaccinated, vaccination_day):
    total_count = 0
    days = -1
    previous_timestamp = 0
    
    no_susceptible = []
    no_infected = []
    no_recovered = []
    no_deceased = []
    max_infections = -1

    while days <= timespan:
        model.graph.remove_edges_from(list(model.graph.edges()))

        count = 0
        infected_contact = set()
        while total_count < model.df.shape[0] and model.df['Time'][total_count] <= days * 4:
            person1 = int(model.df['Person 1'][total_count])
            person2 = int(model.df['Person 2'][total_count])
            # Check for transitions from susceptible to infected
            if model.person_type(person1) == 'susceptible' and model.person_type(person2) == 'infected':
                infected_contact.add(person1)
                model.graph.add_edge(person1, person2)
            if model.person_type(person2) == 'susceptible' and model.person_type(person1) == 'infected':
                infected_contact.add(person2)
                model.graph.add_edge(person2, person1)
            # If new timestamp, then increase count
            if(model.df['Time'][total_count] != previous_timestamp):
                previous_timestamp = model.df['Time'][total_count]
                count = count + 1
            total_count = total_count + 1
        
        model.get_new_recovered()
        model.get_new_infected(infected_contact)
        model.get_new_deaths()
        
        no_susceptible.append(len(model.susceptible))
        no_infected.append(len(model.infected))
        no_recovered.append(len(model.recovered))
        no_deceased.append(len(model.deceased))

        days = days + 1

        if(days == vaccination_day):
            model.vaccinate(vaccinated)

        display_stats(days, model)
        model.visualize_graph(vaccinated)

        max_infections = max(max_infections, len(model.infected))
    
    return {
        'metrics': {
            'total_deaths': len(model.deceased),
            'peak_infections': max_infections
        },
        'stats': {
            'susceptible': no_susceptible,
            'infected': no_infected,
            'recovered': no_recovered,
            'deceased': no_deceased
        }
    }

# The variable vaccination_day specifies the day after which the population must be vaccinated
def run(model, vaccinated, vaccination_day):
    # 105 timestamps are going to be clustered together and considered as one day.
    # This would make the dataset into 30 days
    timespan = 30 # months
    model.init()
    result = simulate(model, timespan, vaccinated, vaccination_day)
    visualize(result)
    return result