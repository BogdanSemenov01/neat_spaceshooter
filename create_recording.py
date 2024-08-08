from spaceshooter import SpaceShooterGame
import os
import pickle

import neat

def run_with_recording():
    with open('winner-feedforward', 'rb') as file:
        winner = pickle.load(file)

    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'spaceshooter_config.config')
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_path)
    nn = neat.nn.FeedForwardNetwork.create(winner, config)
    game = SpaceShooterGame.SpaceShooterGame(f'Best NN', nn, record_gameplay=True)
    game.run_game()
    game.frames_to_images()
    game.images_to_gif()

if __name__ == '__main__':
    run_with_recording()
