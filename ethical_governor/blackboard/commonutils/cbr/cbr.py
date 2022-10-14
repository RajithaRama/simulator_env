import numpy as np
import pandas as pd
from sklearn.neighbors import NearestNeighbors


class CBR:
    def __init__(self, k=3, algorithm='brute'):
        self.col_names = None
        self.data = NearestNeighbors(n_neighbors=k, metric=self.distance, algorithm=algorithm)

    def add_data(self, X):
        self.data.fit(X)
        self.col_names = self.data.feature_names_in_

    def distance(self, a, b):
        return 1
