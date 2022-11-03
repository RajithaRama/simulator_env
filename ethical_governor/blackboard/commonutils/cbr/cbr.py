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
        self.categorical_data_cols = ['follower_seen_location', 'last_seen_location', 'robot_location', 'time',
                                      'action']
        self.numerical_data_cols = ['seen', 'follower_time_since_last_seen', 'not_follow_request', 'battery_level',
                                    'instructions_given', 'follower_autonomy', 'follower_wellbeing',
                                    'follower_availability']
        self.list_data_cols = ['not_follow_locations', 'instructions_given']
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

        query[query.columns.intersection(self.categorical_data_cols)] = self.encoder.transform(
            query[query.columns.intersection(self.categorical_data_cols)])

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
            distances.setdefault(self.pairwise_distance(vec_s[q_col_names], query.T[0]), []).append(vec_s['case_id'])
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

    def get_neighbours_with_distances(self, query, k=3):
        q_col_names = query.columns
        distances = {}

        query[query.columns.intersection(self.categorical_data_cols)] = self.encoder.transform(
            query[query.columns.intersection(self.categorical_data_cols)])

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
            distances.setdefault(self.pairwise_distance(vec_s[q_col_names], query.T[0]), []).append(vec_s['case_id'])
            # distances[self.distance(vec_s, query)] = vec_s['case_id']

        neighbours = []
        while len(neighbours) < k:
            min_dist = min(distances.keys())
            if len(distances[min_dist]) + len(neighbours) <= k:
                for case in distances[min_dist]:
                    neighbours.append((case, min_dist))
                distances.pop(min_dist)
            else:
                i = len(neighbours)
                for case in distances[min_dist]:
                    if i > k:
                        break
                    neighbours.append(case, min_dist)
                    i += 1
                distances.pop(min_dist)
        return neighbours

    def pairwise_distance(self, a, b):
        col_names = a.index
        distances = []
        for col in col_names:
            if col in ['case_id', 'acceptability']:
                continue
            elif col in self.categorical_data_cols:
                distances.append(self.vdm_distance(col, a[col], b[col]))
            elif col in self.numerical_data_cols:
                distances.append(self.minkowski_distance(a[col], b[col], p=1))
            elif col in self.list_data_cols:
                distances.append(self.jaccard_distance(a[col], b[col]))
            else:
                continue
        return sum(distances)

    def encode_dataset(self, data):
        col_data = data[data.columns.intersection(self.categorical_data_cols)]
        data[data.columns.intersection(self.categorical_data_cols)] = self.encoder.fit_transform(X=col_data)
        return data

    def vdm_distance(self, feature, a, b):
        distance = self.value_diff_mat.item_distance(feature=feature, a=a, b=b)
        return distance

    def minkowski_distance(self, a, b, p):
        if type(a) != type(b):
            raise ValueError("a and b have different types.")

        distance = 0
        if (type(a) == list) or (type(a) == tuple):
            if len(a) != len(b):
                raise ValueError("a and b are different in sizes.")
            for i in range(len(a)):
                distance += abs(a[i] - b[i]) ** p
            return distance ** (1 / p)
        else:
            return abs(a - b)

    def jaccard_distance(self, a, b):
        """
        :param a: list
        :param b: list
        :return: distance
        """
        A = set(a)
        B = set(b)

        sym_dif = A.symmetric_difference(B)
        union = A.union(B)

        if len(union) > 0:
            distance = len(sym_dif) / len(union)
        else:
            distance = 0
        return distance

    def get_case(self, case_id):
        return self.data_original.T[case_id]

    def distance_weighted_vote(self, neighbours_with_dist, threshold):
        """ Calculate the distance_weighted vote of k neighbours"""
        vote = 0
        for neighbour, distance in neighbours_with_dist:
            # If the distance is 0, then give it weight of K (number of neighbours)
            if distance < 1/len(neighbours_with_dist):
                vote += len(neighbours_with_dist)*self.get_case(neighbour)['acceptability']
            else:
                vote += self.get_case(neighbour)['acceptability']/distance

        if vote > threshold:
            return 1
        else:
            return 0
