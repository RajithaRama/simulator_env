import numpy as np
import pandas as pd
import ethical_governor.blackboard.commonutils.cbr.vdm as vdm
from sklearn.preprocessing import OrdinalEncoder


class CBR:
    def __init__(self, k=3):
        self.data_encoded = None
        self.col_names = None
        self.data_original = pd.DataFrame()
        self.dist_feature_map = {}
        self.value_diff_mat = vdm.VDM()
        self.categorical_data_cols = ['follower_seen_location', 'last_seen_location', 'robot_location', 'action']
        self.encoder = OrdinalEncoder()

    def add_data(self, data):
        self.data_original = data
        self.data_original.index = self.data_original.case_id
        self.data_encoded = self.encode_dataset(data)
        self.data_encoded.index = self.data_encoded.case_id
        self.col_names = self.data_encoded.columns

    def get_neighbours(self, query, k=3):
        q_col_names = query.columns
        distances = {}

        query[query.columns.intersection(self.categorical_data_cols)] = self.encoder.transform(query[query.columns.intersection(self.categorical_data_cols)])

        # get the subset of cases that have the features
        required_col_names = q_col_names.insert(0, 'case_id')
        required_col_names = required_col_names.insert(len(required_col_names), 'acceptability')
        subset_df = self.data_encoded[required_col_names].dropna()

        # Tune value difference Metric for query
        self.value_diff_mat = vdm.VDM().fit(X=subset_df[q_col_names.intersection(self.categorical_data_cols)],
                                            y=subset_df['acceptability'])

        data_inv = subset_df.T
        for col in data_inv.columns:
            vec_s = data_inv[col]
            distances.setdefault(self.distance(vec_s[q_col_names], query.squeeze()), []).append(vec_s['case_id'])
            # distances[self.distance(vec_s, query)] = vec_s['case_id']

        neighbours = []
        while len(neighbours) < k:
            if len(distances[min(distances.keys())]) + len(neighbours) <= k:
                for case in distances[min(distances.keys())]:
                    neighbours.append(case)
                distances.pop(min(distances.keys()))
            else:
                i = len(neighbours)
                for case in distances[min(distances.keys())]:
                    if i > k:
                        break
                    neighbours.append(case)
                    i += 1
                distances.pop(min(distances.keys()))
        return neighbours

    def distance(self, a, b):
        col_names = a.index
        distance = 0
        for col in col_names:
            if col in ['case_id', 'acceptability']:
                continue
            if col in self.categorical_data_cols:
                distance += self.vdm_distance(col, a[col], b[col])
        return distance

    def encode_dataset(self, data):
        col_data = data[data.columns.intersection(self.categorical_data_cols)]
        data[data.columns.intersection(self.categorical_data_cols)] = self.encoder.fit_transform(X=col_data)
        return data

    def vdm_distance(self, feature, a, b):
        distance = self.value_diff_mat.item_distance(feature=feature, a=a, b=b)
        return distance

    def get_case(self, case_id):
        return self.data_original.T[case_id]
