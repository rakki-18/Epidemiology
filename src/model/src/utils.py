import pandas as pd
import random
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx

import cv2
import glob
import os

figArr = []

class SIR:
    # Can be modified according to the disease scenario
    beta = 0.1  # Probability of getting infected on interaction with an infected person.
    gamma = 0.03  # Probability of natural recovery for an infected person
    alpha = 0.006  # Probablity of an infected person dying
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
        self.G = None
        self.df = df
        self.metadata = metadata

    def init(self):
        # Sets to keep track of people in the model
        self.susceptible = set()
        self.infected = set()
        self.recovered = set()
        self.vaccinated = set()
        self.deceased = set()
        for person in self.metadata['id']:  # id -> ID
            try:
                self.susceptible.add(int(person))
            except:
                pass

        self.infected = random.sample(
            list(self.susceptible), self.initial_infected)
        for infected_person in self.infected:
            self.susceptible.remove(infected_person)

    # Determine which category person belongs to
    def person_type(self, person):
        if person in self.susceptible:
            return 'susceptible'
        if person in self.infected:
            return 'infected'
        return 'recovered'

    # Simulate new infected people
    def get_new_infected(self, infected_contact):
        new_infected = [
            person for person in infected_contact if random.random() <= self.beta]
        # Add them to infected
        for infected_person in new_infected:
            self.infected.append(infected_person)
            self.susceptible.remove(infected_person)

    # Simulate natural recovery
    def get_new_recovered(self):
        new_recovered = [
            person for person in self.infected if random.random() <= self.gamma]
        # Add them to recovered
        for recovered_person in new_recovered:
            self.infected.remove(recovered_person)
            self.recovered.add(recovered_person)

    # Simulate deaths
    def get_new_deaths(self):
        new_deaths = [
            person for person in self.infected if random.random() <= self.alpha]
        # Add them to deceased
        for deceased_person in new_deaths:
            self.infected.remove(deceased_person)
            self.deceased.add(deceased_person)

    # Create contact graph
    def create_contact_graph(self):
        self.G = nx.Graph()
        self.G.add_nodes_from(self.metadata['id'])
        self.pos = nx.spring_layout(self.G, k = 1, iterations = 3)
        return
    
    def add_edge(self, p1, p2):
        if p1 != p2:
            self.G.add_edge(p1, p2)
    
    def erase_edges(self):
        self.G.remove_edges_from(self.G.edges())

    # Visualize the contact graph
    def visualize_graph(self, vaccinated, days, vaccination_day):
        fig = plt.figure(figsize=(20, 12))
        nx.draw_networkx(self.G, pos = self.pos, nodelist=list(
            self.susceptible), node_size=1000, node_color='dodgerblue', font_size=12, width = 0.05)
        nx.draw_networkx(self.G, pos = self.pos, nodelist=list(self.infected),
                         node_size=1000, node_color='orange', font_size=12, width = 0.05)
        nx.draw_networkx(self.G, pos = self.pos, nodelist=list(
            self.recovered), node_size=1000, node_color='limegreen', font_size=12, width = 0.05)
        nx.draw_networkx(self.G, pos = self.pos, nodelist=list(self.deceased),
                         node_size=1000, node_color='orangered', font_size=12, width = 0.05)
        if (days >= vaccination_day):
            nx.draw_networkx(self.G, pos = self.pos, nodelist=list(
                vaccinated), node_size=1000, node_color='yellow', font_size=12, width = 0.05)
        S_blue = mpatches.Patch(color='dodgerblue', label='Susceptible')
        I_orange = mpatches.Patch(color='orange', label='Infected')
        R_green = mpatches.Patch(color='limegreen', label='Recovered')
        D_red = mpatches.Patch(color='orangered', label='Deceased')
        V_yellow = mpatches.Patch(color='yellow', label='Vaccinated')
        plt.legend(handles=[S_blue, I_orange, R_green,  D_red, V_yellow], prop={"size": 15}, loc='upper right')
        plt.tight_layout()
        fig.savefig(f"graph_screenshots/{days}.jpeg")
        plt.close(fig)

def visualize(result):

    fig = plt.figure(figsize=(10, 10))

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



def simulate(model, timespan, vaccinated, vaccination_day, generated_video_name = False):

    total_count = 0
    days = -1
    previous_timestamp = 0

    if generated_video_name:
        model.create_contact_graph()
        os.system('mkdir -p graph_screenshots')
        model.visualize_graph(vaccinated, days, vaccination_day)

    no_susceptible = [len(model.susceptible)]
    no_infected = [len(model.infected)]
    no_recovered = [len(model.recovered)]
    no_deceased = [len(model.deceased)]
    max_infections = len(model.infected)

    while days <= timespan:
        count = 0
        infected_contact = set()
        while total_count < model.df.shape[0] and model.df['timestamp'][total_count] < days * 4:
            person1 = int(model.df['p1'][total_count])  # p1 -> Person 1
            person2 = int(model.df['p2'][total_count])  # p2 -> Person 2
            # Check for transitions from susceptible to infected
            if model.person_type(person1) == 'susceptible' and model.person_type(person2) == 'infected':
                infected_contact.add(person1)
                if generated_video_name:
                    model.add_edge(person1, person2)
            if model.person_type(person2) == 'susceptible' and model.person_type(person1) == 'infected':
                infected_contact.add(person2)
                if generated_video_name:
                    model.add_edge(person1, person2)
            # If new timestamp, then increase count
            if(model.df['timestamp'][total_count] != previous_timestamp):   # timestamp -> Time
                previous_timestamp = model.df['timestamp'][total_count]     # timestamp -> Time
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

        print(f"After {days} day(s) ")
        print("Number of susceptible: ", len(model.susceptible))
        print("Number of infected: ", len(model.infected))
        print("Number of recovered: ", len(model.recovered))
        print("Number of deceased: ", len(model.deceased))

        if generated_video_name:
            model.visualize_graph(vaccinated, days, vaccination_day)
            model.erase_edges()

        max_infections = max(max_infections, len(model.infected))

    if generated_video_name:
        makeVideo(generated_video_name)

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


def run(model, vaccinated, vaccination_day, generated_video_name = False):
    timespan = 30
    model.init()
    result = simulate(model, timespan, vaccinated, vaccination_day, generated_video_name)
    visualize(result)
    return result


def makeVideo(generated_video_name):
    img = cv2.imread('graph_screenshots/0.jpeg')
    height, width, layers = img.shape
    size = (width,height)
    os.system('mkdir -p assets')
    out = cv2.VideoWriter(filename="assets/" + generated_video_name, fourcc=cv2.VideoWriter_fourcc(*"vp80"), frameSize=size, fps=1)
    for i in range(32):
        filename = 'graph_screenshots/' + str(i) + '.jpeg'
        print(filename)
        img = cv2.imread(filename)
        height, width, layers = img.shape
        size = (width,height)
        out.write(img)
    out.release()
