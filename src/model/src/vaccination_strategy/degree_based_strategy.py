def degree_based_vaccination_strategy(model, vac_percent, D_day):
    size = model.df.shape[0]
    start_index = int(model.metadata["id"][1])
    end_index = int(model.metadata["id"][model.metadata.shape[0] - 1])
    pop_count = end_index - start_index + 1

    days = 30
    start = int(model.df["timestamp"][1])
    end = int(model.df["timestamp"][size - 1])
    Range = (end - start + 1) / 20
    per_day = Range // days

    degree = []
    adj = []

    for i in range(pop_count):
        degree.append(0)
        adj.append([])

    prev_time = int(model.df["timestamp"][1])
    time = prev_time
    timecount = 0
    daycount = 0

    while daycount < D_day:
        if time != prev_time:
            prev_time = time
            timecount += 1
            if timecount % 4 == 1:  # 4 timestamps makes one day
                daycount += 1

        n1 = int(model.df["p1"][time])
        n2 = int(model.df["p2"][time])

        if n2 not in adj[n1 - start_index]:
            degree[n1 - start_index] += 1
            degree[n2 - start_index] += 1

            adj[n1 - start_index].append(n2)
            adj[n2 - start_index].append(n1)

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
