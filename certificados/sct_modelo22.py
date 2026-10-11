"""Modelo SCT de 22 parámetros (Bandura, con realimentación) del pipeline de 6 metaheurísticas
(«pruebasrobustas100»): entradas ξ3..ξ8 y salida η4 estandarizadas (z-score, StandardScaler);
A, B como en build_AB del pipeline; simulación día a día con entrada constante en [k, k+1] y
salida y[k] = x4(k+1) (el pipeline integra con odeint; aquí con la exponencial de matriz, que es
la solución exacta del mismo problema). Límites: β ∈ [−1,5; 1,5], γ ∈ [0; 3], τ ∈ [0,3; 12];
restricción de estabilidad max Re eig(A) ≤ −10⁻³ y |A| ≤ 50."""
import numpy as np
import pandas as pd
from pathlib import Path
from scipy.linalg import expm

HERE = Path(__file__).resolve().parent
NAMES = ['beta14', 'beta21', 'beta25', 'beta31', 'beta34', 'beta42', 'beta43', 'beta45', 'beta46', 'beta54',
         'gamma33', 'gamma35', 'gamma36', 'gamma57', 'gamma64', 'gamma68',
         'tau1', 'tau2', 'tau3', 'tau4', 'tau5', 'tau6']
BOUNDS = [(-1.5, 1.5)] * 10 + [(0.0, 3.0)] * 6 + [(0.3, 12.0)] * 6

d = pd.read_csv(HERE / "datos_sct" / "datos_sct_31dias.csv")
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


def estable(th):
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


def costo(th):
    """Función objetivo del pipeline (MSE en z-score con penalizaciones)."""
    if not estable(th): return 1e6
    y = sim(th)
    if not np.all(np.isfinite(y)) or np.max(np.abs(y)) > 10: return 1e6
    return float(np.mean((Y - y) ** 2))


def r2(yh, idx=slice(None)):
    yy = Y[idx]; return float(1 - np.sum((yy - yh[idx]) ** 2) / np.sum((yy - yy.mean()) ** 2))
