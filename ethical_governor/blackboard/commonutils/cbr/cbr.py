import numpy as np
import pandas as pd
import imblearn.metrics.pairwise as imb_pairwise
from sklearn.neighbors import NearestNeighbors


class CBR:
    def __init__(self, k=3):
        self.col_names = None
        self.data = pd.DataFrame()
        self.dist_feature_map = {}
        self.value_diff_mat = imb_pairwise.ValueDifferenceMetric()

    def add_data(self, data):
        self.data = data
        self.col_names = self.data.col_names

    def get_neighbours(self, query, k=3):
        q_col_names = query.index
        distances = {}

        # get the subset of cases that have the features
        subset_df = self.data[q_col_names.extend('action')].dropna()

        # Tune value difference Metric for query
        self.value_diff_mat = imb_pairwise.ValueDifferenceMetric().fit(subset_df[q_col_names], subset_df['action'])

        data_inv = subset_df.T
        for col in data_inv.columns:
            vec_s = data_inv[col]
            distances.setdefault(self.distance(vec_s[q_col_names], query), []).append(vec_s['case_id'])
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
        col_names = a.index
        distance = 0
        for col in col_names:
            if col in ['follower_seen_location', 'last_seen_location', 'robot_location', 'action']:
                distance += self.vdm()
        return 1

    # def vdm(self, a, b):

