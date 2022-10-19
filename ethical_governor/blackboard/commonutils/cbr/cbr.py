import numpy as np
import pandas as pd
from sklearn.neighbors import NearestNeighbors


class CBR:
    def __init__(self, k=3):
        self.col_names = None
        self.data = pd.DataFrame()
        self.dist_feature_map = {}

    def add_data(self, data):
        self.data = data
        self.col_names = self.data.get_table_col_names()

    def get_neighbours(self, query, k=3):
        q_col_names = query.col_names
        distances = {}
        data_inv = self.data.T
        for col in data_inv.columns:
            vec_s = data_inv[col]
            in_same_f_space = True
            for qcol in q_col_names:
                if vec_s[qcol] is None:
                    in_same_f_space = False
                    break
            if in_same_f_space:
                distances.setdefault(self.distance(vec_s, query), []).append(vec_s['case_id'])
                # distances[self.distance(vec_s, query)] = vec_s['case_id']

        neighbours = []
        while len(neighbours) <= k:
            if len(distances[min(distances.keys())]) + len(neighbours) <= k:
                for case in distances[min(distances.keys())]:
                    neighbours.append(data_inv[case])
            else:
                i = len(neighbours)
                for case in distances[min(distances.keys())]:
                    if i > k:
                        break
                    neighbours.append(data_inv[case])
                    i += 1
        return neighbours






    def distance(self, a, b):
        return 1
