from __future__ import print_function

from spaceshooter import SpaceShooterGame
import multiprocessing
import os
import pickle

import neat
import visualize

runs_per_net = 5


def eval_genome(genome, config):
    net = neat.nn.FeedForwardNetwork.create(genome, config)
    fitnesses = []

    for runs in range(runs_per_net):
        game = SpaceShooterGame.SpaceShooterGame(f'NN_{runs}', net)
        game.run_game()
        # Run the given simulation for up to num_steps time steps.
        fitness = game.result
        fitnesses.append(fitness)

    return max(fitnesses)

def eval_genomes(genomes, config):
    for genome_id, genome in genomes:
        genome.fitness = eval_genome(genome, config)



def run():
    # Load the config file, which is assumed to live in
    # the same directory as this script.
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'spaceshooter_config.config')
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_path)
    pop = neat.Population(config)
    stats = neat.StatisticsReporter()
    pop.add_reporter(stats)
    pop.add_reporter(neat.StdOutReporter(True))

    pe = neat.ParallelEvaluator(multiprocessing.cpu_count(), eval_genome)
    winner = pop.run(pe.evaluate)

    # Save the winner.
    with open('winner-feedforward', 'wb') as f:
        pickle.dump(winner, f)


def show_results():
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'spaceshooter_config.config')
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_path)
    
    with open('winner-feedforward', 'rb') as file:
        winner = pickle.load(file)


    node_names = {
        -1: 'left_mob_count', 
        -2: 'left_powerup_count', 
        -3: 'middle_mob_count', 
        -4: 'middle_powerup_count', 
        -5: 'right_mob_count',
        -6: 'right_powerup_count',
        -7: 'shield level',
        0: 'move left', 
        1: 'dont move', 
        2: 'move right'
    }
    visualize.draw_net(config, winner, True, node_names=node_names)


if __name__ == '__main__':
    run()
    show_results()