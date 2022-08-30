# Define paths

from pathlib import Path
ROOT_PATH = Path(__file__).parent

IMG_PATH = ROOT_PATH / 'static' / 'img'
DATA_PATH = ROOT_PATH / 'static' / 'data'

if __name__ == "__main__":
    # Print the paths
    print(f'ROOT_PATH: {ROOT_PATH}')
    print(f'IMG_PATH: {IMG_PATH}')
    print(f'DATA_PATh: {DATA_PATH}')