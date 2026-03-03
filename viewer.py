import pickle
import pprint
import numpy as np

file_type = 'pickle'
#file_type = 'npy'
#file_type = 'npz'

file_path = '/data1/sparc/calvin/dataset/univla/processed_data/meta/calvin_abcd_norm.pkl'
file_path = '/home/ksshin/projects/sparc/UD-VLA/calvin_debug_norm.pkl'

#file_path = '/data1/sparc/calvin/dataset/univla/processed_data/meta/calvin_abcd_norm.pkl'
#file_path = '/data1/sparc/calvin/dataset/univla/processed_data/meta/calvin_abcd_norm.pkl'

if file_type == 'pickle':
    with open(file_path, 'rb') as f:
        data = pickle.load(f)
elif file_type == 'npy':
    data = np.load(file_path)
elif file_type == 'npz':
    data = np.load(file_path)

breakpoint()