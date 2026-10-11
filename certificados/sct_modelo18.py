"""Modelo SCT de 18 parámetros usado en la estimación por evolución diferencial (ETCM 2025):
A sin realimentación (β21, β25, β42, β43, β45, β46), entradas por γ33..γ68, τ1..τ6; ξ4 = 1
constante; entradas y salida normalizadas min-max (sklearn); simulación día a día con entrada
constante en [k, k+1] y salida y[k] = x4(k+1) (como el código de Colab, con odeint)."""
import numpy as np
import pandas as pd
from pathlib import Path
from scipy.linalg import expm

HERE = Path(__file__).resolve().parent
NAMES = ['beta21', 'beta25', 'beta42', 'beta43', 'beta45', 'beta46',
         'gamma33', 'gamma35', 'gamma36', 'gamma57', 'gamma64', 'gamma68',
         'tau1', 'tau2', 'tau3', 'tau4', 'tau5', 'tau6']
INI = np.array([1.0315308121582962, 1.554763253176936, 1.222879691022082, 1.4957543070633692,
                0.3447332244765122, 1.848981904771306, 1874.9073431914826, 1573.4100537310014,
                1310.497027070374, 136.6476923135876, 243.78553108963163, 260.0861021421147,
                6.8740079585783365, 4.65097923802117, 2.6000033906715907, 0.16298158714575095,
                1.1356326215183783, 4.5934281467706635])
BOUNDS = [(0, 2)] * 6 + [(0, 3000)] * 6 + [(0.01, 10)] * 6

d = pd.read_csv(HERE / "datos_sct" / "datos_sct_31dias.csv")
X = d[['xi3', 'xi5', 'xi6', 'xi7', 'xi8']].copy(); X.insert(1, 'xi4', 1.0); X = X.to_numpy(float)
_r = X.max(0) - X.min(0)
U = (X - X.min(0)) / np.where(_r == 0, 1, _r)
Y_RAW = d['eta4'].to_numpy(float)
Y = (Y_RAW - Y_RAW.min()) / (Y_RAW.max() - Y_RAW.min())
N = len(Y)


def AB(p):
    b21, b25, b42, b43, b45, b46, g33, g35, g36, g57, g64, g68, t1, t2, t3, t4, t5, t6 = p
    t1, t2, t3, t4, t5, t6 = np.maximum([t1, t2, t3, t4, t5, t6], 1e-9)
    A = np.array([[-1 / t1, 0, 0, 0, 0, 0], [b21 / t2, -1 / t2, 0, 0, b25 / t2, 0], [0, 0, -1 / t3, 0, 0, 0],
                  [0, b42 / t4, b43 / t4, -1 / t4, b45 / t4, b46 / t4], [0, 0, 0, 0, -1 / t5, 0], [0, 0, 0, 0, 0, -1 / t6]])
    B = np.zeros((6, 6))
    B[2, 0], B[2, 2], B[2, 3] = g33 / t3, -g35 / t3, g36 / t3
    B[4, 4] = g57 / t5
    B[5, 1], B[5, 5] = g64 / t6, g68 / t6
    return A, B


def sim(p, x0=None):
    A, B = AB(p)
    M = np.zeros((12, 12)); M[:6, :6] = A; M[:6, 6:] = B
    E = expm(M); Ad, Bd = E[:6, :6], E[:6, 6:]
    x = np.zeros(6) if x0 is None else np.asarray(x0, float)
    y = np.empty(N)
    for k in range(N):
        x = Ad @ x + Bd @ U[k]; y[k] = x[3]
    return y


def r2(yh, idx=slice(None)):
    yy = Y[idx]; return float(1 - np.sum((yy - yh[idx]) ** 2) / np.sum((yy - yy.mean()) ** 2))
