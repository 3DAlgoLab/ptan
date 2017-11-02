import numpy as np


def distr_projection(next_distr, rewards, dones, Vmin, Vmax, n_atoms, gamma):
    """
    Perform distribution projection aka Catergorical Algorithm from the
    "A Distributional Perspective on RL" paper
    """
    batch_size = len(rewards)
    proj_distr = np.zeros((batch_size, n_atoms), dtype=np.float32)
    delta_z = (Vmax - Vmin) / (n_atoms - 1)
    for atom in range(n_atoms):
        tz_j = rewards + (Vmin + atom * delta_z) * gamma
        b_j = 1e-6 + (tz_j - Vmin) / delta_z
        l = np.floor(b_j).astype(np.int64)
        u = np.ceil(b_j).astype(np.int64)
        l_mask = np.logical_and(l >= 0, l < n_atoms)
        u_mask = np.logical_and(u >= 0, u < n_atoms)
        proj_distr[l_mask, l[l_mask]] += next_distr[l_mask, atom] * ((u - b_j)[l_mask])
        proj_distr[u_mask, u[u_mask]] += next_distr[u_mask, atom] * ((b_j - l)[u_mask])
    if dones.any():
        proj_distr[dones] = 0.0
        # Warning: here we assume that our rewards at the end of the episode will be in Vmin...Vmax range
        b_j = 1e-6 + (rewards[dones] - Vmin) / delta_z
        l = np.floor(b_j).astype(np.int64)
        u = np.ceil(b_j).astype(np.int64)
        proj_distr[dones, l] += u - b_j
        proj_distr[dones, u] += b_j - l
    return proj_distr
