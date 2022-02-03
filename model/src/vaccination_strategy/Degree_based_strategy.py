import pandas as pd

def vaccination_strategy(model,vac_percent,D_day):
    size = model.df.shape[0]
    start_index = int(model.metadata["ID"][0])
    end_index = int(model.metadata["ID"][model.metadata.shape[0] - 1])
    pop_count = end_index - start_index + 1

    days = 30
    start = int(model.df["Time"][1])
    end = int(model.df["Time"][size - 1])
    Range = (end - start + 1) / 20
    per_day = Range // days

    degree = []
    for i in range(pop_count):
        degree.append(0)

    prev_time = int(model.df["Time"][1])
    time = prev_time
    timecount = 0
    daycount = 0

    while daycount < D_day:
        if time != prev_time:
            prev_time = time
            timecount += 1
            if timecount % per_day == 0:
                daycount += 1

        n1 = int(model.df["Person 1"][time])
        n2 = int(model.df["Person 2"][time])
        degree[n1 - start_index] += 1
        degree[n2 - start_index] += 1
        time += 1

    no_vaccinated = int(pop_count * (vac_percent / 100))

    vaccinated = []
    deg_count = []  # stores degree of each node

    # Finding the list of vaccinated people
    for i in range(pop_count):
        if degree[i] != 0:
            deg_count.append([i + start_index, degree[i]])

    deg_count.sort(key=lambda x: x[1])
    L = len(deg_count)

    for i in range(no_vaccinated):
        if i < L:
            vaccinated.append(deg_count[i][0])
        else:
            break

    return vaccinated

