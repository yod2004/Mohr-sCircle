import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, FancyArrowPatch

# ページの設定
st.set_page_config(page_title="Mohr's Circle App", layout="wide")
st.title("モールの応力円と応力状態の変換")
st.write("スライダーを動かすか、横の「＜」「＞」ボタンで数値を調整してみてください。")

# セッションステート（状態の保持）の初期化
if 'sx' not in st.session_state: st.session_state.sx = 80.0
if 'sy' not in st.session_state: st.session_state.sy = 20.0
if 'txy' not in st.session_state: st.session_state.txy = 30.0
if 'theta' not in st.session_state: st.session_state.theta = 30.0

# 値を整数化して増減させる関数
def dec(key, min_val):
    st.session_state[key] = max(min_val, float(np.ceil(st.session_state[key]) - 1))

def inc(key, max_val):
    st.session_state[key] = min(max_val, float(np.floor(st.session_state[key]) + 1))

# --- 現在のパラメータを取得 ---
sx = st.session_state.sx
sy = st.session_state.sy
txy = st.session_state.txy
theta = st.session_state.theta

# ==========================================
# グラフの描画
# ==========================================
fig, (ax_real, ax_mohr) = plt.subplots(1, 2, figsize=(14, 7))

# -----------------
# 実空間 (微小要素)
# -----------------
ax_real.set_aspect('equal')
lim = 180
ax_real.set_xlim(-lim, lim)
ax_real.set_ylim(-lim, lim)
ax_real.set_title("Real World Stress State & Rotated Plane")
ax_real.set_xlabel("X")
ax_real.set_ylabel("Y")
ax_real.grid(True, linestyle='--', alpha=0.6)

rect_size = 80
rect = Rectangle((-rect_size/2, -rect_size/2), rect_size, rect_size, 
                 linewidth=2, edgecolor='black', facecolor='none')
ax_real.add_patch(rect)

def add_arrow(start, end, color, lw=2, mutation=15):
    arrow = FancyArrowPatch(start, end, color=color, mutation_scale=mutation, linewidth=lw, arrowstyle='->')
    ax_real.add_patch(arrow)

face_offset = rect_size / 2
face_arrow_offset = 10
scale = 1.0

# 基準面の応力描画
if sx != 0:
    dir_sx = 1 if sx > 0 else -1
    sx_pos = face_offset + face_arrow_offset
    add_arrow((sx_pos * dir_sx, 0), ((sx_pos + abs(sx)) * dir_sx, 0), 'red')
if sy != 0:
    dir_sy = 1 if sy > 0 else -1
    sy_pos = face_offset + face_arrow_offset
    add_arrow((0, sy_pos * dir_sy), (0, (sy_pos + abs(sy)) * dir_sy), 'blue')
if txy != 0:
    dir_txy = 1 if txy > 0 else -1
    add_arrow((face_offset, 0), (face_offset, txy * dir_txy), 'green')
    add_arrow((-face_offset, 0), (-face_offset, -txy * dir_txy), 'green')
    add_arrow((0, face_offset), (txy * dir_txy, face_offset), 'green')
    add_arrow((0, -face_offset), (-txy * dir_txy, -face_offset), 'green')

# 回転断面の計算
theta_rad = np.radians(theta)
center_x = (sx + sy) / 2
s_theta = center_x + ((sx - sy) / 2) * np.cos(2 * theta_rad) + txy * np.sin(2 * theta_rad)
t_theta = -((sx - sy) / 2) * np.sin(2 * theta_rad) + txy * np.cos(2 * theta_rad)

# 回転断面の線
line_len = rect_size * 0.8
p1 = (-line_len * np.sin(theta_rad), line_len * np.cos(theta_rad))
p2 = (line_len * np.sin(theta_rad), -line_len * np.cos(theta_rad))
ax_real.plot([p1[0], p2[0]], [p1[1], p2[1]], 'k--', linewidth=1.5, alpha=0.7)

n_dir = np.array([np.cos(theta_rad), np.sin(theta_rad)])
t_dir = np.array([-np.sin(theta_rad), np.cos(theta_rad)])

if s_theta != 0:
    s_end = n_dir * (s_theta * scale)
    add_arrow((0, 0), (s_end[0], s_end[1]), 'purple', lw=2.5, mutation=18)
if t_theta != 0:
    t_end = t_dir * (t_theta * scale)
    add_arrow((0, 0), (t_end[0], t_end[1]), 'orange', lw=2.5, mutation=18)

# -----------------
# モールの応力円
# -----------------
ax_mohr.set_aspect('equal')
ax_mohr.set_xlim(-lim, lim)
ax_mohr.set_ylim(-lim, lim)
ax_mohr.set_title("Mohr's Circle & Rotated State")
ax_mohr.set_xlabel(r"Normal Stress $\sigma$")
ax_mohr.set_ylabel(r"Shear Stress $\tau$")
ax_mohr.grid(True, linestyle='--', alpha=0.6)
ax_mohr.axhline(0, color='black', linewidth=1)
ax_mohr.axvline(0, color='black', linewidth=1)

radius = np.sqrt(((sx - sy) / 2)**2 + txy**2)
mohr_circle = Circle((center_x, 0), radius, linewidth=2, edgecolor='k', facecolor='none', alpha=0.3)
ax_mohr.add_patch(mohr_circle)

ax_mohr.plot([sx], [txy], 'ro', markersize=8, label=r'X-plane $(\sigma_x, \tau_{xy})$')
ax_mohr.plot([sy], [-txy], 'bo', markersize=8, label=r'Y-plane $(\sigma_y, -\tau_{xy})$')
ax_mohr.plot([sx, sy], [txy, -txy], 'k--', alpha=0.3)

ax_mohr.plot([s_theta], [t_theta], 'o', color='purple', markersize=10, label=r'Rotated $(\sigma_\theta, \tau_\theta)$')
ax_mohr.plot([center_x, s_theta], [0, t_theta], 'purple', linewidth=2, alpha=0.8)

ax_mohr.legend(loc='upper right', fontsize='small')

# matplotlibの図をStreamlitに表示
st.pyplot(fig)

# ==========================================
# 操作UI（スライダーとボタン）
# ==========================================
st.markdown("### パラメータ設定")

# スライダーとボタンを配置するためのレイアウト作成関数
def create_control(label, key, min_val, max_val):
    col1, col2, col3 = st.columns([8, 1, 1])
    with col1:
        st.slider(label, min_val, max_val, key=key)
    with col2:
        st.button("＜", key=f"dec_{key}", on_click=dec, args=(key, min_val), use_container_width=True)
    with col3:
        st.button("＞", key=f"inc_{key}", on_click=inc, args=(key, max_val), use_container_width=True)

create_control("σx (Sigma X)", "sx", -100.0, 100.0)
create_control("σy (Sigma Y)", "sy", -100.0, 100.0)
create_control("τxy (Tau XY)", "txy", -100.0, 100.0)
create_control("θ (Rotation Angle)", "theta", -90.0, 90.0)