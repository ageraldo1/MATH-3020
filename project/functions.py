import json
import argparse
import datetime
import os
import numpy as np
import random
import pandas as pd
import math

# constants
INFECTED = 1
UNINFECTED = 0

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def init():
    global print_summary
    global csv_location
    global computers
    global initial_infection
    global prob
    global tech_threshold
    global simulations
    global start_exec

    start_exec = datetime.datetime.now()

    parser = argparse.ArgumentParser(description='Monte Carlo Methods')

    req = parser.add_argument_group('Required arguments') 
    req.add_argument('--simulations', type=int, metavar='<integer>', required=True, help='Total number of simulations')
    
    opt = parser.add_argument_group('Optional arguments') 
    opt.add_argument('--print-summary',type=lambda x: (str(x).lower() in ['true','1', 'yes']), metavar='<boolean>', required=False, help='print summary on screen', default=True)
    opt.add_argument('--csv-location',type=str, metavar='<path>', required=False, help='Directory location to save simulation results', default='output')
    opt.add_argument('--computers', type=int, metavar='<int>', required=False, help='Numbers of computers on the network', default=20)
    opt.add_argument('--initial-infection', type=int, metavar='<int>', required=False, help='Initial number of infected computers', default=1)
    opt.add_argument('--prob', type=float, metavar='<float>', required=False, help='Probability of a computer get infected', default=0.10)
    opt.add_argument('--tech-threshold', type=int, metavar='<int>', required=False, help='Numbers of computers a technical can fix by day', default=5)

    args = vars(parser.parse_args())

    simulations = args['simulations']
    print_summary = args['print_summary']
    csv_location = args['csv_location']
    computers = args['computers']
    initial_infection = args['initial_infection']
    prob = args['prob']
    tech_threshold = args['tech_threshold']

    splash_screen()

def splash_screen():
    clear()
    
    print (f'''
Monte Carlo Methods
    Applied Probability and Statistics for Computer Science - Spring 2020
    Georgia State University

Parameters:
    Total simulations.................................: {simulations}
    Print summary to screen...........................: {print_summary}
    Directory location to save simulation results.....: {csv_location}
    Numbers of computers on the network...............: {computers}
    Initial number of infected computers..............: {initial_infection}
    Probability of a computer get infected............: {prob}
    Numbers of computers a technical can fix by day...: {tech_threshold}
''')     

def is_network_clear(network):
    for item in network:
        if item['state'] == INFECTED:
            return False        
    return True      

def print_network(network):
    for item in network:
        print(item)


def setComputerState(network, id, state):
    for item in network:
        if item['computer'] == id:
            
            if (item['state'] == UNINFECTED):
                item['infections'] += 1
                
            elif (item['state'] == INFECTED):
                item['recovers'] += 1
                
            item['state'] = state
            
            break

def clearRandomNetwork(network, fromState, toState, count):
    infected = [item for item in network if item['state'] == fromState]
    
    if len(infected) > count:
        for item in random.sample(infected, k=count):
            setComputerState(network, item['computer'], toState)
    else:
        for item in infected:
            setComputerState(network, item['computer'], toState)



def process():
    simulations_list = []

    for simulation in range(simulations):
        print (f"\rSimulation {simulation}/{simulations}", end=" ")

        # construct network
        network = [{'computer' : id, 'state' : UNINFECTED, 'infections': 0, 'recovers' : 0} for id in range(0, computers)]
        days = None
        
        # initial infection (random)
        for _ in range(initial_infection):
            setComputerState(network, random.randrange(0, len(network), step=1), INFECTED)        
            
        # network_clear loop        
        while (not is_network_clear(network)):
            if (days is None):
                days = 0
            else:
                days += 1


            # spread the virus across uninfected computers
            # this virus spreads from any infected computer to any uninfected
            infected = [item for item in network if item['state'] == INFECTED]            

            for _ in infected:
                uninfected = [item for item in network if item['state'] == UNINFECTED]

                for item in uninfected:
                    if (np.random.binomial(n=1, p=prob, size=1)[0] == INFECTED):
                        setComputerState(network, item["computer"], INFECTED)

            # computer technician arrives, finds a new_k number of infected computers
            clearRandomNetwork(network, INFECTED, UNINFECTED, tech_threshold)

        # save results    
        distinct_infections = sum([1 for item in network if item['infections'] > 0])

        simulations_list.append({
            'simulation' : simulation,
            'days'       : days,
            'infected'   : distinct_infections,
            'uninfected' : computers - distinct_infections
        })   

    print (f"\rSimulation {simulations}/{simulations}", end=" ")
    print("", end="\n")

    if (print_summary):
        summary = pd.DataFrame(data=simulations_list, columns=list(simulations_list[0].keys()))
        expected_days = summary['days'].sum()/simulations

        cond = summary['infected'] == computers
        p = summary[cond].count()[0]/simulations

        expected_computers = summary['infected'].sum()/simulations   

        print(f"\tThe expected time it takes to remove the virus from the whole network...: {math.ceil(expected_days)} day(s)")
        print(f"\tThe probability that each computer gets infected at least once..........: {p}")
        print(f"\tThe expected number of computers that get infected......................: {math.ceil(expected_computers)}")             

    ts = datetime.datetime.now()
    csv_output = f"{csv_location}/{ts.year}-{ts.month}-{ts.day}-{ts.hour}-{ts.minute}-{ts.second}.csv"
    summary.to_csv(csv_output, index=False)

    print(f"Simulation results saved at : {csv_output}")

def end():
    seconds_elapsed = (datetime.datetime.now() - start_exec).total_seconds()
    print (f"\nProcess completed in {seconds_elapsed} second(s)")
