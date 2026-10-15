"""
Social cognitive theory (SCT) model with 22 parameters (Bandura, with feedback) used in the
motivating example of the paper (Supplementary Note "The social cognitive theory model").

Inputs xi3..xi8 and output eta4 (daily steps) are standardised (z-score). The model is the linear
system tau_i dx_i/dt = -x_i + sum_j beta_ij x_j + sum_k gamma_ik u_k, simulated day by day with a
constant input on [k, k+1] and output y[k] = x4(k+1) (exact solution with the matrix exponential).
Bounds: beta in [-1.5, 1.5], gamma in [0, 3], tau in [0.3, 12]; stability constraint
max Re eig(A) <= -1e-3 and |A| <= 50.

The data of the participant (31 days) are not public; they are available from the authors on
reasonable request. Place the file (columns xi3, xi4, xi5, xi6, xi7, xi8, eta4; one row per day) at
data/sct/datos_sct_31dias.csv or give its path in the environment variable SCT_DATA.
"""
import os

import numpy as np
import pandas as pd
from scipy.linalg import expm

from config import ROOT

DATA = os.environ.get("SCT_DATA", str(ROOT / "data" / "sct" / "datos_sct_31dias.csv"))
NAMES = ['beta14', 'beta21', 'beta25', 'beta31', 'beta34', 'beta42', 'beta43', 'beta45', 'beta46', 'beta54',
         'gamma33', 'gamma35', 'gamma36', 'gamma57', 'gamma64', 'gamma68',
         'tau1', 'tau2', 'tau3', 'tau4', 'tau5', 'tau6']
BOUNDS = [(-1.5, 1.5)] * 10 + [(0.0, 3.0)] * 6 + [(0.3, 12.0)] * 6

d = pd.read_csv(DATA)
X = d[['xi3', 'xi4', 'xi5', 'xi6', 'xi7', 'xi8']].to_numpy(float)
U = (X - X.mean(0)) / X.std(0)
Y_RAW = d['eta4'].to_numpy(float)
Y = (Y_RAW - Y_RAW.mean()) / Y_RAW.std()
N = len(Y)


def AB(th):
    (b14, b21, b25, b31, b34, b42, b43, b45, b46, b54, g33, g35, g36, g57, g64, g68, t1, t2, t3, t4, t5, t6) = th
    A = np.array([[-1 / t1, 0, 0, b14 / t1, 0, 0], [b21 / t2, -1 / t2, 0, 0, b25 / t2, 0],
                  [b31 / t3, 0, -1 / t3, b34 / t3, 0, 0], [0, b42 / t4, b43 / t4, -1 / t4, b45 / t4, b46 / t4],
                  [0, 0, 0, b54 / t5, -1 / t5, 0], [0, 0, 0, 0, 0, -1 / t6]])
    B = np.zeros((6, 6))
    B[2, 0], B[2, 2], B[2, 3] = g33 / t3, -g35 / t3, g36 / t3
    B[4, 4] = g57 / t5
    B[5, 1], B[5, 5] = g64 / t6, g68 / t6
    return A, B


def stable(th):
    A, _ = AB(th)
    return bool(np.all(np.isfinite(A)) and np.max(np.abs(A)) <= 50 and np.max(np.linalg.eigvals(A).real) <= -1e-3)


def sim(th, x0=None):
    A, B = AB(th)
    M = np.zeros((12, 12)); M[:6, :6] = A; M[:6, 6:] = B
    E = expm(M); Ad, Bd = E[:6, :6], E[:6, 6:]
    x = np.zeros(6) if x0 is None else np.asarray(x0, float)
    y = np.empty(N)
    for k in range(N):
        x = Ad @ x + Bd @ U[k]; y[k] = x[3]
    return y


def cost(th):
    """Objective function of the original estimation (MSE in z-score, with penalties)."""
    if not stable(th): return 1e6
    y = sim(th)
    if not np.all(np.isfinite(y)) or np.max(np.abs(y)) > 10: return 1e6
    return float(np.mean((Y - y) ** 2))


def r2(yh, idx=slice(None)):
    yy = Y[idx]; return float(1 - np.sum((yy - yh[idx]) ** 2) / np.sum((yy - yy.mean()) ** 2))
