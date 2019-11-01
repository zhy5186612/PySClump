"""
A Python Implementation of 'Spectral Clustering in Heterogeneous Information Networks' by Xiang Li, Ben Kao, Zhaochun Ren, Dawei Yin, at AAAI 2019.
"""

# External dependencies.
from sklearn.cluster import KMeans
import numpy as np

# Internal dependencies.
from utils import eigenvectors, laplacian

class SClump:
    def __init__(self, similarity_matrices, num_clusters, random_seed=0):
        
        self.num_clusters = num_clusters
        self.random_seed = random_seed
        self.num_nodes = None
        self.similarity_matrices = []
        self.metapath_index = {}

        for index, (metapath, matrix) in enumerate(similarity_matrices.items()):
            if self.num_nodes is None:
                self.num_nodes = similarity_matrices.shape[0]
            
            if matrix.shape != (self.num_nodes, self.num_nodes):
                raise ValueError('Invalid shape of similarity matrix.')
            
            # Normalize so that row sums are 1.
            row_normalized_matrix = matrix/matrix.sum(axis=1, keepdims=True)
            
            self.similarity_matrices.append(row_normalized_matrix)
            self.metapath_index[metapath] = index

        self.similarity_matrices = np.array(self.similarity_matrices)
        self.num_metapaths = len(similarity_matrices)

    def run(self):
        """
        Returns a dictionary of:
        * labels: The predicted cluster labels for each node.
        * similarity: The learnt similarity matrix, from the optimization procedure.
        """
        similarity_matrix = self.optimize()
        labels = self.cluster(similarity_matrix)

        return {
            'labels': labels,
            'similarity': similarity_matrix,
        }
    
    
    def cluster(self, feature_matrix):
        """
        Cluster row-wise entries in the feature matrix. Currently, k-means clustering is used.
        TODO: Add spectral rotation as an alternative to k-means.
        """
        return KMeans(self.num_clusters, random_state=self.random_seed).fit_transform(feature_matrix)

    def optimize(self, num_iterations=20):
        """
        Learn weights to optimize the similarity matrix.
        """
        lambdas = np.ones(self.num_metapaths)/self.num_metapaths
        W = np.tensordot(lambdas, self.similarity_matrices, axes=[[0], [0]])
        S = W

        for iteration in range(num_iterations):
            
            # Update F.
            LS = laplacian(S)    
            F = eigenvectors(LS, num_eigenvectors=self.num_clusters)

            # Update S.
            update_S()

            # Update lambdas.
            update_lambdas()

            W = np.tensordot(lambdas, self.similarity_matrices, axes=[[0], [0]])

        return S