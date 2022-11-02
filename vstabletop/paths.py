# Define paths

from pathlib import Path
ROOT_PATH = Path(__file__).parent
ULTIMATE_PATH = Path(__file__).parent.parent
IMG_PATH = ROOT_PATH / 'static' / 'img'
DATA_PATH = ROOT_PATH / 'static' / 'data'
LOCAL_CONFIG_PATH = ULTIMATE_PATH / 'external' / 'marcos_pack' / 'marcos_client' / 'local_config.py'

if __name__ == "__main__":
    # Print the paths
    print(f'ROOT_PATH: {ROOT_PATH}')
    print(f'IMG_PATH: {IMG_PATH}')
    print(f'DATA_PATH: {DATA_PATH}')
    print(f'LOCAL_CONFIG_PATH : {LOCAL_CONFIG_PATH}')