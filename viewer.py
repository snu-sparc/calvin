import pickle
import pprint
import numpy as np
import yaml

#file_type = 'pickle'
#file_type = 'npy'
#file_type = 'npz'
file_type = 'yaml'

#file_path = '/data1/sparc/calvin/dataset/univla/processed_data/meta/calvin_abcd_norm.pkl'
#file_path = '/home/ksshin/projects/sparc/UD-VLA/calvin_debug_norm.pkl'

file_path = '/home/ksshin/projects/sparc/UD-VLA/reference/RoboVLMs/log/0_action_pred/action_pred_000.npy'
file_path = '/data3/ksshin/datasets/CALVIN/calvin_debug_dataset/training/episode_0358656_noisy_action_image_added.npz'
#file_path = '/data1/sparc/calvin/dataset/univla/processed_data/meta/calvin_abcd_norm.pkl'
#file_path = '/data1/sparc/calvin/dataset/univla/processed_data/meta/calvin_abcd_norm.pkl'

file_path = '/data1/sparc/calvin/dataset/calvin_debug_dataset/validation/scene_info.npy'
file_path = '/data1/sparc/calvin/dataset/calvin_debug_dataset/validation/.hydra/merged_config.yaml'

if file_type == 'pickle':
    with open(file_path, 'rb') as f:
        data = pickle.load(f)
elif file_type == 'npy':
    data = np.load(file_path, allow_pickle=True)
elif file_type == 'npz':
    data = np.load(file_path)
elif file_type == 'yaml':
    with open(file_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
breakpoint()