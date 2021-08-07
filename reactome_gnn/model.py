import torch
import torch.nn as nn
import dgl
from dgl.nn import GraphConv


class GCNModel(nn.Module):
    """
    A model based on GCN layers. In a simple manner it takes the graph
    and its features, first 
    """

    def __init__(self, dim_latent, num_layers=1, train=False):
        """
        Parameters
        ----------
        dim_latent : int, optional
            Dimension of the graph embeddings, default 16
        num_layers : int, optional
            Number of GCN layers in the GCNModel, deafult 1
        """
        super().__init__()
        self.embedder = nn.Embedding(2, 2)
        self.linear = nn.Linear(3, dim_latent)
        self.conv_0 = GraphConv(dim_latent, dim_latent, allow_zero_in_degree=True)
        self.relu = nn.LeakyReLU()
        self.layers = nn.ModuleList([GraphConv(dim_latent, dim_latent, allow_zero_in_degree=True)
                                     for _ in range(num_layers - 1)])
        self.predict = nn.Linear(dim_latent, 1)

    def forward(self, graph):
        """Return the embedding of a graph."""
        significance = graph.ndata['significance'].int()
        significance = self.embedder(significance)
        weights = graph.ndata['weight'].unsqueeze(-1)
        features = torch.cat((weights, significance), dim=1)
        features = self.linear(features)
        graph = dgl.add_self_loop(graph)
        embedding = self.conv_0(graph, features)
        for conv in self.layers:
            embedding = self.relu(embedding)
            embedding = conv(graph, embedding)
        if self.train:
            logits = self.predict(embedding)
            return logits
        else:
            return embedding.detach()
