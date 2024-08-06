from spaceshooter import SpaceShooterGame




import multiprocessing
import os
import pickle

import neat

runs_per_net = 5

def eval_genome(genome, config):
    net = neat.nn.FeedForwardNetwork.create(genome, config)
    fitnesses = []

    for runs in range(runs_per_net):
        game = SpaceShooterGame.SpaceShooterGame(f'NN_{runs}', net)
        game.run_game()
        # Run the given simulation for up to num_steps time steps.
        fitness = game.result

        print(fitness, 'score') 


        

        fitnesses.append(fitness)

    # The genome's fitness is its worst performance across all runs.
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
    # with open('winner-feedforward', 'wb') as f:
    #     pickle.dump(winner, f)

    # print(winner)

    # visualize.plot_stats(stats, ylog=True, view=True, filename="feedforward-fitness.svg")
    # visualize.plot_species(stats, view=True, filename="feedforward-speciation.svg")

    # node_names = {-1: 'x', -2: 'dx', -3: 'theta', -4: 'dtheta', 0: 'control'}
    # visualize.draw_net(config, winner, True, node_names=node_names)

    # visualize.draw_net(config, winner, view=True, node_names=node_names,
    #                    filename="winner-feedforward.gv")
    # visualize.draw_net(config, winner, view=True, node_names=node_names,
    #                    filename="winner-feedforward-enabled-pruned.gv", prune_unused=True)


if __name__ == '__main__':
    # game = SpaceShooterGame.SpaceShooterGame(f'NN_{1}', None)
    # game.run_game()

    # eval_genome()

    run()
