import numpy as np
from sklearn.neighbors import NearestNeighbors
from scipy.special import digamma

def entropy_histogram(data, bins=32):
    """
    Classic Shannon Entropy using histograms (with Miller-Madow correction).
    """
    if len(data) == 0: return 0.0
    counts, _ = np.histogram(data, bins=bins, range=(0, 1))
    probs = counts / np.sum(counts)
    probs = probs[probs > 0]
    shannon = -np.sum(probs * np.log2(probs))
    
    # Miller-Madow correction
    correction = (len(probs) - 1) / (2 * len(data))
    return max(0.0, shannon + correction)

def entropy_ksg(data, k=3):
    """
    Kraskov-Stögbauer-Grassberger (KSG) Entropy Estimator.
    Calculates differential entropy. Note: results can be negative for 
    distributions with density > 1 (e.g., highly clustered points).
    """
    n = len(data)
    if n <= k: return 0.0
    
    x = np.array(data).reshape(-1, 1)
    nn = NearestNeighbors(n_neighbors=k+1).fit(x)
    distances, _ = nn.kneighbors(x)
    
    eps = distances[:, k]
    eps = eps + 1e-15
    
    h = digamma(n) - digamma(k) + np.log(2.0) + np.mean(np.log(eps))
    return h / np.log(2.0)

def estimate_entropy(data, method='histogram'):
    """
    Unified entropy estimator interface.
    """
    if method == 'histogram':
        return entropy_histogram(data)
    elif method == 'ksg':
        # Clip to 0 for tracking 'information potential' although technically incorrect for differential h.
        return max(0.0, entropy_ksg(data))
    return 0.0
