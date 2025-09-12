"""
08.15_terrain_high_res.py - HIGH RESOLUTION Kent terrain (with erosion smoothing)
Massive scale: 59,000 x 59,000 units with ULTRA HIGH RESOLUTION geometry
Features: Focus on smooth, granular terrain with thermal erosion and tuned ridges/warping
"""

from direct.showbase.ShowBase import ShowBase
from panda3d.core import (
    WindowProperties, Point3, Vec3,
    GeomNode, GeomTriangles, Geom,
    GeomVertexFormat, GeomVertexData, GeomVertexWriter,
    AmbientLight, DirectionalLight, Fog
)
from direct.task import Task
from direct.showbase.DirectObject import DirectObject
from direct.gui.DirectGui import DirectWaitBar, DirectLabel
import numpy as np
import math
import time
import logging
from datetime import datetime, timedelta


class TerrainLogger:
    """Handles all logging functionality for terrain generation"""
    
    def __init__(self, name='TerrainSystem'):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # Clear existing handlers
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        
        # File handler
        try:
            file_handler = logging.FileHandler('terrain_system.log')
            file_handler.setLevel(logging.DEBUG)
            file_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)
        except Exception as e:
            print(f"Could not create log file: {e}")
        
        self.logger.info("=== Terrain System Initialized ===")
    
    def info(self, msg):
        self.logger.info(msg)
    
    def debug(self, msg):
        self.logger.debug(msg)
    
    def error(self, msg):
        self.logger.error(msg)


class NoiseGenerator:
    """Handles all noise generation algorithms for terrain"""
    
    # Cache permutation tables per seed to avoid reseeding/allocating per sample
    _perm_cache = {}

    @classmethod
    def _get_perm(cls, seed: int):
        if seed not in cls._perm_cache:
            rng = np.random.RandomState(seed)
            base = rng.permutation(256).astype(np.int32)
            cls._perm_cache[seed] = np.concatenate([base, base])
        return cls._perm_cache[seed]

    @staticmethod
    def fade(t):
        """Improved fade function for smoother noise"""
        return t * t * t * (t * (t * 6 - 15) + 10)
    
    @staticmethod
    def lerp(t, a, b):
        """Linear interpolation"""
        return a + t * (b - a)
    
    @staticmethod
    def grad(hash_val, x, y):
        """Gradient function for Perlin noise"""
        h = hash_val & 15
        u = x if h < 8 else y
        v = y if h < 4 else (x if h == 12 or h == 14 else 0)
        return (u if (h & 1) == 0 else -u) + (v if (h & 2) == 0 else -v)
    
    @classmethod
    def perlin_noise(cls, x, y, seed=0):
        """High-quality Perlin noise implementation"""
        p = cls._get_perm(seed)
        
        X = int(math.floor(x)) & 255
        Y = int(math.floor(y)) & 255
        
        x -= math.floor(x)
        y -= math.floor(y)
        
        u = cls.fade(x)
        v = cls.fade(y)
        
        A = p[X] + Y
        AA = p[A & 255]
        AB = p[(A + 1) & 255]
        B = p[(X + 1) & 255] + Y
        BA = p[B & 255]
        BB = p[(B + 1) & 255]
        
        return cls.lerp(v, 
                       cls.lerp(u, cls.grad(p[AA & 255], x, y),
                                  cls.grad(p[BA & 255], x-1, y)),
                       cls.lerp(u, cls.grad(p[AB & 255], x, y-1),
                                  cls.grad(p[BB & 255], x-1, y-1)))
    
    @classmethod
    def fractal_brownian_motion(cls, x, y, octaves=6, frequency=0.01, amplitude=1.0, lacunarity=2.0, persistence=0.5, seed=42):
        """Advanced fractal Brownian motion for natural terrain"""
        value = 0.0
        current_amplitude = amplitude
        current_frequency = frequency
        
        for i in range(octaves):
            value += current_amplitude * cls.perlin_noise(x * current_frequency, y * current_frequency, seed + i)
            current_amplitude *= persistence
            current_frequency *= lacunarity
        
        return value
    
    @classmethod
    def ridged_noise(cls, x, y, octaves=4, frequency=0.01, seed=42):
        """Ridged noise for mountain ridges and cliff faces"""
        value = 0.0
        amplitude = 1.0
        current_frequency = frequency
        
        for i in range(octaves):
            n = cls.perlin_noise(x * current_frequency, y * current_frequency, seed + i * 10)
            n = abs(n)  # Create ridges
            n = 1.0 - n  # Invert so ridges are peaks
            n = n * n  # Sharpen ridges
            value += n * amplitude
            amplitude *= 0.5
            current_frequency *= 2.0
        
        return value
    
    @classmethod
    def domain_warp(cls, x, y, strength=50.0, seed=42):
        """Domain warping to break up artificial patterns"""
        offset_x = cls.fractal_brownian_motion(x * 0.002, y * 0.002, octaves=3, seed=seed) * strength
        offset_y = cls.fractal_brownian_motion(x * 0.002, y * 0.002, octaves=3, seed=seed + 100) * strength
        return x + offset_x, y + offset_y

# --- Erosion Helpers ---------------------------------------------------------

def thermal_erosion(h, iterations=25, talus=3.0, c=0.3):
    """Simple thermal erosion (talus slope) to remove spikes/needles.
    h: heightmap (numpy array), talus in meters, c in [0..1] controls flow fraction.
    """
    h = h.copy()
    for _ in range(iterations):
        up    = np.pad(h[:-1, :], ((1,0),(0,0)), mode='edge')
        down  = np.pad(h[1:,  :], ((0,1),(0,0)), mode='edge')
        left  = np.pad(h[:, :-1], ((0,0),(1,0)), mode='edge')
        right = np.pad(h[:, 1: ], ((0,0),(0,1)), mode='edge')

        du = h - up;    mask_u = du > talus
        dd = h - down;  mask_d = dd > talus
        dl = h - left;  mask_l = dl > talus
        dr = h - right; mask_r = dr > talus

        move_u = np.where(mask_u, c * (du - talus), 0.0)
        move_d = np.where(mask_d, c * (dd - talus), 0.0)
        move_l = np.where(mask_l, c * (dl - talus), 0.0)
        move_r = np.where(mask_r, c * (dr - talus), 0.0)

        outflow = move_u + move_d + move_l + move_r
        inflow  = np.pad(move_d[:-1, :], ((1,0),(0,0)), mode='constant') \
                + np.pad(move_u[1:,  :], ((0,1),(0,0)), mode='constant') \
                + np.pad(move_r[:, :-1], ((0,0),(1,0)), mode='constant') \
                + np.pad(move_l[:, 1: ], ((0,0),(0,1)), mode='constant')

        h = h - outflow + inflow
    return h

# Optional: lightweight hydraulic erosion (not enabled by default)

def hydraulic_erosion(h, iterations=60, rain=0.02, evap=0.02, carry=0.05):
    h = h.copy()
    water = np.zeros_like(h)
    sed   = np.zeros_like(h)
    for _ in range(iterations):
        water += rain
        up    = np.pad(h[:-1, :], ((1,0),(0,0)), mode='edge')
        down  = np.pad(h[1:,  :], ((0,1),(0,0)), mode='edge')
        left  = np.pad(h[:, :-1], ((0,0),(1,0)), mode='edge')
        right = np.pad(h[:, 1: ], ((0,0),(0,1)), mode='edge')

        hu = up + np.pad(water[:-1, :], ((1,0),(0,0)), mode='edge')
        hd = down + np.pad(water[1:,  :], ((0,1),(0,0)), mode='edge')
        hl = left + np.pad(water[:, :-1], ((0,0),(1,0)), mode='edge')
        hr = right + np.pad(water[:, 1: ], ((0,0),(0,1)), mode='edge')
        hc = h + water

        du = np.maximum(0.0, hc - hu)
        dd = np.maximum(0.0, hc - hd)
        dl = np.maximum(0.0, hc - hl)
        dr = np.maximum(0.0, hc - hr)
        sumd = du+dd+dl+dr + 1e-6

        flow_u = water * (du/sumd) * 0.5
        flow_d = water * (dd/sumd) * 0.5
        flow_l = water * (dl/sumd) * 0.5
        flow_r = water * (dr/sumd) * 0.5

        outflow = flow_u+flow_d+flow_l+flow_r
        inflow  = np.pad(flow_d[:-1,:], ((1,0),(0,0))) \
                + np.pad(flow_u[1: ,:], ((0,1),(0,0))) \
                + np.pad(flow_r[:, :-1], ((0,0),(1,0))) \
                + np.pad(flow_l[:, 1: ], ((0,0),(0,1)))
        water = water - outflow + inflow

        capacity = carry * water
        delta = capacity - sed
        erode = np.clip(delta, 0, 0.2)
        deposit = -np.clip(delta, -0.2, 0)

        h -= erode
        sed += erode
        h += deposit
        sed += deposit

        water *= (1.0 - evap)
    return h

# --- Utility: Bilinear resize (2D or 3D last-channel arrays) -----------------

def bilinear_resize(arr: np.ndarray, new_h: int, new_w: int) -> np.ndarray:
    h, w = arr.shape[:2]
    if h == new_h and w == new_w:
        return arr.copy()
    y = np.linspace(0, h - 1, new_h, dtype=np.float32)
    x = np.linspace(0, w - 1, new_w, dtype=np.float32)
    y0 = np.floor(y).astype(np.int32)
    x0 = np.floor(x).astype(np.int32)
    y1 = np.clip(y0 + 1, 0, h - 1)
    x1 = np.clip(x0 + 1, 0, w - 1)
    wy = y - y0
    wx = x - x0
    wy0 = (1.0 - wy)[:, None]
    wy1 = wy[:, None]
    wx0 = (1.0 - wx)[None, :]
    wx1 = wx[None, :]
    if arr.ndim == 2:
        A = arr[y0[:, None], x0[None, :]]
        B = arr[y0[:, None], x1[None, :]]
        C = arr[y1[:, None], x0[None, :]]
        D = arr[y1[:, None], x1[None, :]]
        return (A * wy0 * wx0 + B * wy0 * wx1 + C * wy1 * wx0 + D * wy1 * wx1).astype(arr.dtype, copy=False)
    else:
        A = arr[y0[:, None], x0[None, :], :]
        B = arr[y0[:, None], x1[None, :], :]
        C = arr[y1[:, None], x0[None, :], :]
        D = arr[y1[:, None], x1[None, :], :]
        return (
            A * wy0[..., None] * wx0[..., None]
            + B * wy0[..., None] * wx1[..., None]
            + C * wy1[..., None] * wx0[..., None]
            + D * wy1[..., None] * wx1[..., None]
        ).astype(arr.dtype, copy=False)


class LoadingManager:
    """Handles loading screen UI and progress tracking"""
    
    def __init__(self, base, logger, total_steps=12):
        self.base = base
        self.logger = logger
        self.total_steps = total_steps
        self.start_time = time.time()
        self.current_step = ""
        self.current_step_num = 0
        self.step_start_time = time.time()
        self.progress_history = []
        
        # Setup loading screen UI
        self._create_loading_ui()
    
    def _create_loading_ui(self):
        """Create the loading screen UI elements"""
        self.loading_title = DirectLabel(
            text="Generating Advanced Multi-Scale Terrain",
            text_scale=0.08,
            frameColor=(0, 0, 0, 0.7),
            text_fg=(1, 1, 0.8, 1),
            pos=(0, 0, 0.4)
        )
        
        self.loading_label = DirectLabel(
            text="Initializing advanced terrain algorithms...",
            text_scale=0.05,
            frameColor=(0, 0, 0, 0),
            text_fg=(0.9, 0.9, 0.9, 1),
            pos=(0, 0, 0.25)
        )
        
        self.progress_bar = DirectWaitBar(
            value=0,
            pos=(0, 0, 0.1),
            scale=(1.8, 1, 0.08),
            frameColor=(0.2, 0.2, 0.2, 1),
            barColor=(0.3, 0.7, 0.3, 1)
        )
        
        self.percentage_label = DirectLabel(
            text="0.0%",
            text_scale=0.06,
            frameColor=(0, 0, 0, 0),
            text_fg=(1, 1, 1, 1),
            pos=(0, 0, 0.02)
        )
        
        self.time_info_label = DirectLabel(
            text="Elapsed: 0s | ETA: Calculating...",
            text_scale=0.04,
            frameColor=(0, 0, 0, 0),
            text_fg=(0.8, 0.8, 1, 1),
            pos=(0, 0, -0.05)
        )
        
        self.step_info_label = DirectLabel(
            text="Step 0/12: Initializing",
            text_scale=0.04,
            frameColor=(0, 0, 0, 0),
            text_fg=(1, 0.8, 0.6, 1),
            pos=(0, 0, -0.12)
        )
    
    def update_progress(self, progress, step_name, step_num=None):
        """Update progress with enhanced tracking and ETA calculation"""
        current_time = time.time()
        elapsed = current_time - self.start_time
        
        # Update step tracking
        if step_name != self.current_step:
            if self.current_step:
                step_duration = current_time - self.step_start_time
                self.logger.info(f"Completed: {self.current_step} (took {step_duration:.2f}s)")
            
            self.current_step = step_name
            self.step_start_time = current_time
            if step_num is not None:
                self.current_step_num = step_num
            self.logger.info(f"Starting: {step_name}")
        
        # Store progress history for ETA calculation
        self.progress_history.append((current_time, progress))
        
        # Keep only recent history (last 10 data points)
        if len(self.progress_history) > 10:
            self.progress_history.pop(0)
        
        # Calculate ETA
        eta_text = "Calculating..."
        if len(self.progress_history) >= 2 and progress > 0.01:
            try:
                time_span = self.progress_history[-1][0] - self.progress_history[0][0]
                progress_span = self.progress_history[-1][1] - self.progress_history[0][1]
                
                if time_span > 0 and progress_span > 0:
                    rate = progress_span / time_span
                    remaining_progress = 1.0 - progress
                    eta_seconds = remaining_progress / rate
                    
                    if eta_seconds < 60:
                        eta_text = f"{int(eta_seconds)}s"
                    elif eta_seconds < 3600:
                        eta_text = f"{int(eta_seconds/60)}m {int(eta_seconds%60)}s"
                    else:
                        eta_text = f"{int(eta_seconds/3600)}h {int((eta_seconds%3600)/60)}m"
            except:
                eta_text = "Calculating..."
        
        # Update UI elements
        percentage = progress * 100
        self.progress_bar['value'] = percentage
        self.percentage_label['text'] = f"{percentage:.1f}%"
        
        elapsed_str = f"{int(elapsed)}s" if elapsed < 60 else f"{int(elapsed/60)}m {int(elapsed%60)}s"
        self.time_info_label['text'] = f"Elapsed: {elapsed_str} | ETA: {eta_text}"
        
        step_display = f"Step {self.current_step_num}/{self.total_steps}: {step_name}"
        self.step_info_label['text'] = step_display
        self.loading_label['text'] = step_name
        
        # Log progress periodically
        if int(percentage) % 5 == 0 and int(percentage) != getattr(self, '_last_logged_percent', -1):
            self.logger.info(f"Progress: {percentage:.1f}% - {step_name} - Elapsed: {elapsed_str} - ETA: {eta_text}")
            self._last_logged_percent = int(percentage)
    
    def finish_loading(self):
        """Clean up loading screen"""
        self.loading_title.destroy()
        self.loading_label.destroy()
        self.progress_bar.destroy()
        self.percentage_label.destroy()
        self.time_info_label.destroy()
        self.step_info_label.destroy()


class CameraController:
    """Handles all camera movement and control functionality"""
    
    def __init__(self, base, logger):
        self.base = base
        self.logger = logger
        
        # Camera state
        self.camera_pos = Point3(0, -5000, 2000)
        self.camera_hpr = Vec3(0, -30, 0)
        self.base.camera.setPos(self.camera_pos)
        self.base.camera.setHpr(self.camera_hpr)
        
        # Movement settings
        self.keys = {
            "w": False, "s": False, "a": False, "d": False,
            "space": False, "shift": False, "q": False, "e": False,
            "up": False, "down": False
        }
        self.move_speed = 2000.0
        self.fast_speed = 8000.0
        self.rotate_speed = 45.0
        self.fast_mode = False
        self.current_speed = self.move_speed
    
    def setup_controls(self):
        """Setup keyboard controls"""
        for key in self.keys:
            self.base.accept(key, self.set_key, [key, True])
            self.base.accept(f"{key}-up", self.set_key, [key, False])
        self.base.accept("arrow_up", self.set_key, ["up", True])
        self.base.accept("arrow_up-up", self.set_key, ["up", False])
        self.base.accept("arrow_down", self.set_key, ["down", True])
        self.base.accept("arrow_down-up", self.set_key, ["down", False])
        self.base.accept("r", self.reset_camera)
        self.base.accept("o", self.overview_camera)
        self.base.accept("f", self.toggle_fast_mode)
        
        # Start camera update task
        self.base.taskMgr.add(self.update_camera, "update_camera")
    
    def set_key(self, key, value):
        """Handle key press/release"""
        self.keys[key] = value
    
    def toggle_fast_mode(self):
        """Toggle between normal and fast movement speed"""
        self.fast_mode = not self.fast_mode
        speed_text = "FAST" if self.fast_mode else "NORMAL"
        self.logger.info(f"Movement speed: {speed_text}")
    
    def reset_camera(self):
        """Reset camera to default overview position"""
        self.camera_pos = Point3(0, -5000, 2000)
        self.camera_hpr = Vec3(0, -30, 0)
        self.base.camera.setPos(self.camera_pos)
        self.base.camera.setHpr(self.camera_hpr)
        self.logger.info("Camera reset to overview position")
    
    def overview_camera(self):
        """Move camera to high overview position to see entire map"""
        self.camera_pos = Point3(0, 0, 25000)  # 25km high
        self.camera_hpr = Vec3(0, -89, 0)  # Looking straight down
        self.base.camera.setPos(self.camera_pos)
        self.base.camera.setHpr(self.camera_hpr)
        self.logger.info("Camera moved to overview position - 25km high, full map view")
        print("OVERVIEW MODE: 25km altitude - Full 59km x 59km map visible")
    
    def lerp(self, a, b, t):
        """Linear interpolation for smooth transitions"""
        return a + t * (b - a)
    
    def update_camera(self, task):
        """Enhanced camera update with smooth, relative movement"""
        dt = 0.016  # Fixed delta time
        target_speed = self.fast_speed if self.fast_mode else self.move_speed
        
        # Smooth speed transition
        self.current_speed = self.lerp(self.current_speed, target_speed, 0.1)
        
        # FIRST: Handle camera rotation (before movement calculation)
        if self.keys["q"]:
            self.camera_hpr.x += self.rotate_speed * dt
        if self.keys["e"]:
            self.camera_hpr.x -= self.rotate_speed * dt
        if self.keys["up"]:
            self.camera_hpr.y = max(-89, self.camera_hpr.y - self.rotate_speed * dt)
        if self.keys["down"]:
            self.camera_hpr.y = min(89, self.camera_hpr.y + self.rotate_speed * dt)
        
        # Calculate movement vectors using UPDATED camera angles
        heading_rad = math.radians(self.camera_hpr.x)
        pitch_rad = math.radians(self.camera_hpr.y)
        
        # Forward vector (includes pitch for diving/soaring)
        forward_x = math.sin(heading_rad) * math.cos(pitch_rad)
        forward_y = math.cos(heading_rad) * math.cos(pitch_rad)
        forward_z = -math.sin(pitch_rad)
        
        # Enhanced right vector with pitch influence for less grid-like feel
        strafe_pitch_factor = 0.5
        right_x = math.cos(heading_rad) * math.cos(pitch_rad * strafe_pitch_factor)
        right_y = -math.sin(heading_rad) * math.cos(pitch_rad * strafe_pitch_factor)
        right_z = math.sin(pitch_rad * strafe_pitch_factor)
        
        # Normalize vectors to prevent speed scaling at extreme pitches
        forward_mag = math.sqrt(forward_x**2 + forward_y**2 + forward_z**2)
        if forward_mag > 0:
            forward_x /= forward_mag
            forward_y /= forward_mag
            forward_z /= forward_mag
        
        right_mag = math.sqrt(right_x**2 + right_y**2 + right_z**2)
        if right_mag > 0:
            right_x /= right_mag
            right_y /= right_mag
            right_z /= right_mag
        
        # Apply camera-relative movement
        if self.keys["w"]:  # Forward
            self.camera_pos.x += forward_x * self.current_speed * dt
            self.camera_pos.y += forward_y * self.current_speed * dt
            self.camera_pos.z += forward_z * self.current_speed * dt
            
        if self.keys["s"]:  # Backward
            self.camera_pos.x -= forward_x * self.current_speed * dt
            self.camera_pos.y -= forward_y * self.current_speed * dt
            self.camera_pos.z -= forward_z * self.current_speed * dt
            
        if self.keys["a"]:  # Strafe left
            self.camera_pos.x -= right_x * self.current_speed * dt
            self.camera_pos.y -= right_y * self.current_speed * dt
            self.camera_pos.z -= right_z * self.current_speed * dt
            
        if self.keys["d"]:  # Strafe right
            self.camera_pos.x += right_x * self.current_speed * dt
            self.camera_pos.y += right_y * self.current_speed * dt
            self.camera_pos.z += right_z * self.current_speed * dt
            
        # Vertical movement (world-relative)
        if self.keys["space"]:
            self.camera_pos.z += self.current_speed * dt
        if self.keys["shift"]:
            self.camera_pos.z -= self.current_speed * dt
        
        # Apply to Panda3D camera
        self.base.camera.setPos(self.camera_pos)
        self.base.camera.setHpr(self.camera_hpr)
        
        # Update status display
        mode = "FAST" if self.fast_mode else "NORM"
        if hasattr(self.base, 'state_text'):
            self.base.state_text.setText(
                f"Pos: ({self.camera_pos.x/1000:.1f}km, {self.camera_pos.y/1000:.1f}km, {self.camera_pos.z/1000:.1f}km) | "
                f"H: {self.camera_hpr.x:.0f}° P: {self.camera_hpr.y:.0f}° | Speed: {mode} ({self.current_speed:.0f}u/s)"
            )
        
        return Task.cont


class TerrainGenerator:
    """Handles terrain generation algorithms and mesh creation"""
    
    def __init__(self, base, logger, noise_gen):
        self.base = base
        self.logger = logger
        self.noise = noise_gen
    
    def create_advanced_terrain_generator(self):
        """Advanced multi-scale terrain generation with sophisticated algorithms"""
        size = 59000
        resolution = 1000  # ULTRA HIGH RESOLUTION: 1000x1000 = 1 MILLION vertices!
        
        self.logger.info(f"Advanced generation: {resolution}x{resolution} = {resolution*resolution:,} vertices")
        
        # Phase 1: Setup coordinate system (5%)
        yield (0.01, "Initializing advanced coordinate system", 1)
        np.random.seed(42)
        x = np.linspace(-size/2, size/2, resolution, dtype=np.float32)
        y = np.linspace(-size/2, size/2, resolution, dtype=np.float32)
        X, Y = np.meshgrid(x, y)
        yield (0.05, "Coordinate system initialized", 1)
        
        # Phase 2: Domain warping setup (5%) with COARSE sampling and upsampling
        yield (0.06, "Applying domain warping (coarse sampling) for organic shapes", 2)
        coarse = max(1, resolution // 8)  # 125x125 when 1000x1000
        warped_coarse = np.zeros((coarse, coarse, 2), dtype=np.float32)
        xs = np.linspace(-size/2, size/2, coarse, dtype=np.float32)
        ys = np.linspace(-size/2, size/2, coarse, dtype=np.float32)
        for cj in range(coarse):
            for ci in range(coarse):
                wx, wy = self.noise.domain_warp(xs[ci], ys[cj], strength=800.0)
                warped_coarse[cj, ci, 0] = wx
                warped_coarse[cj, ci, 1] = wy
            if cj % 16 == 0:
                progress = 0.05 + (0.04 * cj / coarse)
                yield (progress, f"Domain warping (coarse): {cj}/{coarse} rows", 2)
        warped_coords = bilinear_resize(warped_coarse, resolution, resolution)
        yield (0.10, "Domain warping complete (upsampled)", 2)
        
        # Phase 3: Advanced coastline generation (10%)
        yield (0.11, "Generating fractal coastlines with multi-scale detail", 3)
        coastline_mask = np.ones((resolution, resolution), dtype=np.uint8)
        
        # Vectorized coastline mask using upsampled warped coords
        wx = warped_coords[..., 0]
        wy = warped_coords[..., 1]
        dist = np.sqrt(wx * wx + wy * wy)
        base_radius = size * 0.35
        # Coarse noise for coastline using warped coordinates, then upsample
        coast_coarse = warped_coarse.shape[0]
        coast_noise_coarse = np.zeros((coast_coarse, coast_coarse), dtype=np.float32)
        for cj in range(coast_coarse):
            for ci in range(coast_coarse):
                wxc = warped_coarse[cj, ci, 0]
                wyc = warped_coarse[cj, ci, 1]
                coast_noise_coarse[cj, ci] = self.noise.fractal_brownian_motion(wxc, wyc, octaves=6, frequency=0.00005, amplitude=8000, seed=42)
        coast_noise = bilinear_resize(coast_noise_coarse, resolution, resolution)
        effective_radius = base_radius + coast_noise
        coastline_mask[...] = (dist <= effective_radius).astype(np.uint8)
        yield (0.20, "Advanced coastline generation complete", 3)
        
        yield (0.20, "Advanced coastline generation complete", 3)
        
        # Phase 4: Multi-octave base terrain (15%)
        yield (0.21, "Generating multi-octave base terrain", 4)
        heightmap = np.zeros((resolution, resolution), dtype=np.float32)
        ocean_depth = -200.0
        
        # Phase 4 compute: break into coarse land pass + vectorized fine detail to reduce noise calls
        land_idx = coastline_mask > 0
        wx_full = warped_coords[..., 0]
        wy_full = warped_coords[..., 1]
        dist_full = np.sqrt(wx_full * wx_full + wy_full * wy_full)

        # Coarse evaluate multi-octave stacks at reduced grid and upsample
        coarse = max(1, resolution // 4)  # 250x250 for 1000x1000
        warp_base = bilinear_resize(warped_coords, coarse, coarse)
        def fbm_grid(octaves, freq, amp, seed):
            g = np.zeros((coarse, coarse), dtype=np.float32)
            for cj in range(coarse):
                for ci in range(coarse):
                    wx_c = warp_base[cj, ci, 0]
                    wy_c = warp_base[cj, ci, 1]
                    g[cj, ci] = self.noise.fractal_brownian_motion(wx_c, wy_c, octaves=octaves, frequency=freq, amplitude=amp, seed=seed)
            return g
        continental_c = fbm_grid(4, 0.000008, 300, 42) * 0.8
        regional_c    = fbm_grid(6, 0.00003,  100, 123)
        local_c       = fbm_grid(8, 0.00015,  30, 456)
        fine_c        = fbm_grid(6, 0.0008,    7, 789)
        micro_c       = fbm_grid(4, 0.004,     2, 101112)
        ultra_c       = fbm_grid(3, 0.02,    0.5, 131415)

        continental = bilinear_resize(continental_c, resolution, resolution)
        regional    = bilinear_resize(regional_c,    resolution, resolution)
        local       = bilinear_resize(local_c,       resolution, resolution)
        fine        = bilinear_resize(fine_c,        resolution, resolution)
        micro       = bilinear_resize(micro_c,       resolution, resolution)
        ultra       = bilinear_resize(ultra_c,       resolution, resolution)

        base_heightmap = continental + regional + local + fine + micro + ultra

        # Coastal falloff
        max_distance = size * 0.4
        falloff = np.ones_like(base_heightmap, dtype=np.float32)
        mask_zone = dist_full > (max_distance * 0.5)
        falloff_distance = (dist_full - max_distance * 0.5)
        falloff[mask_zone] = np.clip(1.0 - (falloff_distance[mask_zone] / (max_distance * 0.5)) ** 1.5, 0.0, 1.0)
        base_heightmap *= falloff

        # Enforce 0..2000 and rare peaks
        base_heightmap = np.clip(base_heightmap, 0.0, 2000.0, out=base_heightmap)
        peak_prob = bilinear_resize(fbm_grid(2, 0.000005, 1.0, 999), resolution, resolution)
        peak_mask = (peak_prob > 0.95) & (base_heightmap > 800)
        peak_bonus = ((peak_prob - 0.95) * 20 * 400).astype(np.float32)
        base_heightmap[peak_mask] = np.minimum(2000.0, base_heightmap[peak_mask] + peak_bonus[peak_mask])

        # Oceans
        depth_c = fbm_grid(3, 0.00001, 80, 789)
        depth_full = bilinear_resize(depth_c, resolution, resolution)
        heightmap[~land_idx] = np.minimum(-5.0, ocean_depth + depth_full[~land_idx])
        # Land
        heightmap[land_idx] = base_heightmap[land_idx]

        for j in range(0, resolution, 100):
            progress = 0.20 + (0.15 * j / resolution)
            yield (progress, f"High-res terrain block: {j}/{resolution}", 4)
        
        yield (0.35, "Base terrain generation complete", 4)
        
        # --- Erosion pass to remove needles and smooth slopes ---
        heightmap = thermal_erosion(heightmap, iterations=25, talus=3.0, c=0.3)
        # Optional: enable if you want channels (slower)
        # heightmap = hydraulic_erosion(heightmap, iterations=60, rain=0.02, evap=0.02, carry=0.05)
        
        # Phase 5: Ridged mountain generation (10%)
        yield (0.36, "Adding ridged mountain ranges", 5)
        
        for j in range(resolution):
            for i in range(resolution):
                if coastline_mask[j, i] > 0 and heightmap[j, i] > 50:  # Only on elevated land
                    wx, wy = warped_coords[j, i]
                    
                    # Add CONSTRAINED ridged mountains
                    current_height = heightmap[j, i]
                    ridge_intensity = min(1.0, current_height / 800.0)  # More ridges at elevation
                    ridges = self.noise.ridged_noise(wx, wy, octaves=3, frequency=0.00006, seed=999) * 200 * ridge_intensity
                    
                    # Apply ridges but maintain 2km height limit
                    new_height = current_height + ridges
                    heightmap[j, i] = max(0, min(2000, new_height))
            
            if j % 25 == 0:
                progress = 0.35 + (0.10 * j / resolution)
                yield (progress, f"Ridged mountains: {j}/{resolution} rows", 5)
        
        yield (0.45, "Mountain ridge generation complete", 5)
        
        # Phase 6: Hydraulic erosion simulation (15%)
        yield (0.46, "Simulating hydraulic erosion for realistic valleys", 6)
        
        # Simple hydraulic erosion simulation
        erosion_iterations = 3
        for iteration in range(erosion_iterations):
            new_heightmap = heightmap.copy()
            
            for j in range(1, resolution-1):
                for i in range(1, resolution-1):
                    if coastline_mask[j, i] > 0:  # Only erode land
                        # Find steepest descent direction
                        neighbors = [
                            heightmap[j-1, i], heightmap[j+1, i],
                            heightmap[j, i-1], heightmap[j, i+1]
                        ]
                        current_height = heightmap[j, i]
                        min_neighbor = min(neighbors)
                        
                        if current_height > min_neighbor:
                            # Erode based on height difference
                            erosion_amount = (current_height - min_neighbor) * 0.1
                            new_heightmap[j, i] -= erosion_amount
            
            heightmap = new_heightmap
            progress = 0.45 + (0.15 * (iteration + 1) / erosion_iterations)
            yield (progress, f"Hydraulic erosion pass {iteration + 1}/{erosion_iterations}", 6)
        
        yield (0.60, "Erosion simulation complete", 6)
        
        # Precompute normals vectorized from final heightmap (after erosion/mountains)
        spacing = size / float(resolution - 1)
        h = heightmap.astype(np.float32, copy=False)
        
        h_left  = np.roll(h,  1, axis=1)
        h_right = np.roll(h, -1, axis=1)
        h_down  = np.roll(h,  1, axis=0)
        h_up    = np.roll(h, -1, axis=0)
        # Fix wrap edges to non-wrapping borders
        h_left[:, 0]   = h[:, 0]
        h_right[:, -1] = h[:, -1]
        h_down[0, :]   = h[0, :]
        h_up[-1, :]    = h[-1, :]
        
        dx = (h_right - h_left) / (2.0 * spacing)
        dy = (h_up - h_down)   / (2.0 * spacing)
        
        nx_arr = -dx
        ny_arr = -dy
        nz_arr = np.ones_like(h, dtype=np.float32)
        length = np.sqrt(nx_arr * nx_arr + ny_arr * ny_arr + nz_arr * nz_arr)
        # Prevent division by zero
        length[length == 0] = 1.0
        nx_arr = (nx_arr / length).astype(np.float32)
        ny_arr = (ny_arr / length).astype(np.float32)
        nz_arr = (nz_arr / length).astype(np.float32)
        
        # Phase 7: Mesh setup (5%)
        yield (0.61, "Setting up advanced mesh vertex format", 7)
        vformat = GeomVertexFormat.getV3n3c4()
        vdata = GeomVertexData('advanced_terrain', vformat, Geom.UHStatic)
        vdata.setNumRows(resolution * resolution)
        vertex = GeomVertexWriter(vdata, 'vertex')
        normal = GeomVertexWriter(vdata, 'normal')
        color = GeomVertexWriter(vdata, 'color')
        yield (0.65, "Advanced mesh setup complete", 7)
        
        # Phase 8: Enhanced vertex generation (10%)
        yield (0.66, "Generating vertices with advanced coloring", 8)
        for j in range(resolution):
            for i in range(resolution):
                h = heightmap[j, i]
                vertex.addData3(x[i], y[j], h)
                normal.addData3(nx_arr[j, i], ny_arr[j, i], nz_arr[j, i])
                
                # Advanced terrain coloring based on multiple factors
                wx, wy = warped_coords[j, i]
                
                # Base color from height
                if h < ocean_depth + 10:
                    r, g, b = 0.05, 0.15, 0.4  # Deep ocean
                elif h < ocean_depth + 50:
                    r, g, b = 0.1, 0.25, 0.6   # Shallow ocean
                elif h < 0:
                    r, g, b = 0.2, 0.4, 0.8    # Coastal water
                elif h < 5:
                    r, g, b = 0.9, 0.85, 0.7   # Beach sand
                elif h < 20:
                    r, g, b = 0.4, 0.7, 0.2    # Coastal grass
                elif h < 100:
                    r, g, b = 0.2, 0.5, 0.15   # Lowland forest
                elif h < 200:
                    r, g, b = 0.3, 0.4, 0.2    # Highland forest
                elif h < 350:
                    r, g, b = 0.5, 0.45, 0.35  # Rocky slopes
                elif h < 600:
                    r, g, b = 0.45, 0.4, 0.3   # Mid mountains
                elif h < 1200:
                    r, g, b = 0.55, 0.5, 0.4   # High mountains  
                elif h < 1800:
                    r, g, b = 0.7, 0.65, 0.55  # Alpine regions
                else:  # Above 1800m (rare peaks)
                    r, g, b = 0.9, 0.9, 0.95   # Snow peaks
                
                # Add climate and position-based variation
                climate_factor = math.sin(wy * 0.00002) * 0.1
                position_factor = math.cos(wx * 0.00003) * 0.05
                
                r = np.clip(r + climate_factor + position_factor, 0, 1)
                g = np.clip(g + climate_factor, 0, 1)
                b = np.clip(b - climate_factor + position_factor, 0, 1)
                
                color.addData4(r, g, b, 1.0)
            
            if j % 15 == 0:
                progress = 0.65 + (0.10 * j / resolution)
                yield (progress, f"Advanced vertices: {j}/{resolution} rows", 8)
        
        yield (0.75, "Advanced vertex generation complete", 8)
        
        # Phase 9: Normal calculation (5%)
        yield (0.76, "Normals precomputed (vectorized)", 9)
        yield (0.80, "Normal calculation complete", 9)
        
        # Phase 10: Optimized triangle generation (10%)
        yield (0.81, "Building optimized triangle mesh", 10)
        geom = Geom(vdata)
        prim = GeomTriangles(Geom.UHStatic)
        
        triangle_count = 0
        total_triangles = (resolution - 1) * (resolution - 1) * 2
        triangle_start_time = time.time()
        
        for j in range(resolution - 1):
            for i in range(resolution - 1):
                v0 = j * resolution + i
                v1 = v0 + 1
                v2 = v0 + resolution
                v3 = v2 + 1
                
                prim.addVertices(v0, v2, v1)
                prim.addVertices(v1, v2, v3)
                triangle_count += 2
            
            if j % 15 == 0:
                progress = 0.80 + (0.10 * j / (resolution - 1))
                yield (progress, f"Triangles: {triangle_count}/{total_triangles}", 10)
        
        prim.closePrimitive()
        geom.addPrimitive(prim)
        
        triangle_time = time.time() - triangle_start_time
        self.logger.info(f"Triangle generation: {triangle_time:.2f}s for {triangle_count:,} triangles")
        yield (0.90, "Triangle mesh complete", 10)
        
        # Phase 11: Final assembly (5%)
        yield (0.91, "Assembling final terrain node", 11)
        node = GeomNode('advanced_terrain')
        node.addGeom(geom)
        terrain_np = self.base.render.attachNewNode(node)
        terrain_np.setTwoSided(True)
        yield (0.95, "Terrain node assembled", 11)
        
        # Phase 12: Statistics and completion (5%)
        yield (0.96, "Calculating advanced terrain statistics", 12)
        min_h = np.min(heightmap)
        max_h = np.max(heightmap)
        land_area = np.sum(coastline_mask > 0) * (size/resolution)**2 / 1000000  # km²
        
        self.logger.info(f"=== ADVANCED TERRAIN STATISTICS ===")
        self.logger.info(f"Resolution: {resolution}x{resolution} = {resolution*resolution:,} vertices")
        self.logger.info(f"Height range: {min_h:.1f}m to {max_h:.1f}m")
        self.logger.info(f"Land area: {land_area:.0f} km² ({land_area/3500*100:.1f}% of total)")
        self.logger.info(f"Triangle count: {triangle_count:,}")
        self.logger.info(f"Techniques used: Multi-octave fBm, Domain warping, Ridged noise, Hydraulic erosion")
        
        yield (1.0, "Advanced terrain generation complete!", 12)
        return terrain_np


class HighResKentTerrain(ShowBase):
    """Main terrain application with ULTRA HIGH RESOLUTION geometry"""
    
    def __init__(self):
        ShowBase.__init__(self)
        
        # Initialize subsystems
        self.logger = TerrainLogger('RefactoredTerrain')
        self.loading_manager = LoadingManager(self, self.logger)
        self.camera_controller = CameraController(self, self.logger)
        self.noise_generator = NoiseGenerator()
        self.terrain_generator = TerrainGenerator(self, self.logger, self.noise_generator)
        
        # Window setup
        props = WindowProperties()
        props.setTitle("08.15 HIGH RESOLUTION Kent Terrain - Erosion Smoothed (1M verts)")
        self.win.requestProperties(props)
        
        # Sky color
        self.setBackgroundColor(0.4, 0.5, 0.7, 1)
        
        # Create UI elements
        self._setup_ui()
        
        # Start terrain generation
        self.generation_task = self.taskMgr.add(self.generate_terrain_task, "generate_terrain")
    
    def _setup_ui(self):
        """Setup UI elements"""
        from direct.gui.OnscreenText import OnscreenText
        self.title = OnscreenText(
            text="Refactored Multi-Scale Kent Terrain (3,500 km²)",
            pos=(0, 0.95), scale=0.045, fg=(1, 1, 1, 1)
        )
        self.controls = OnscreenText(
            text="WASD: Move (camera-relative) | Q/E: Yaw | Arrows: Pitch | Space/Shift: Up/Down | F: Fast | R: Reset | O: Overview",
            pos=(0, 0.89), scale=0.038, fg=(0.9, 0.9, 0.9, 1)
        )
        self.state_text = OnscreenText(
            text="",
            pos=(0, -0.95), scale=0.04,
            fg=(1, 1, 0, 1), mayChange=True
        )
        self.info_text = OnscreenText(
            text="Modular Design: Separated Logging, Camera, Noise, Loading | Clean Architecture",
            pos=(0, -0.89), scale=0.035,
            fg=(0.8, 0.8, 0.8, 1)
        )
        self.title.hide()
        self.controls.hide()
        self.state_text.hide()
        self.info_text.hide()
    
    def generate_terrain_task(self, task):
        """Main terrain generation task"""
        if not hasattr(self, 'generator'):
            self.generator = self.terrain_generator.create_advanced_terrain_generator()
        
        try:
            progress_data = next(self.generator)
            if isinstance(progress_data, tuple):
                progress, step_name, step_num = progress_data
                self.loading_manager.update_progress(progress, step_name, step_num)
            else:
                self.loading_manager.update_progress(progress_data, "Processing...", None)
        except StopIteration as e:
            total_time = time.time() - self.loading_manager.start_time
            self.logger.info(f"=== Terrain Generation Complete ===")
            self.logger.info(f"Total generation time: {total_time:.2f}s")
            self.finish_loading()
            return Task.done
        return Task.cont
    
    def finish_loading(self):
        """Complete the loading process and setup final scene"""
        # Clean up loading screen
        self.loading_manager.finish_loading()
        
        # Show UI
        self.title.show()
        self.controls.show()
        self.state_text.show()
        self.info_text.show()
        
        # Setup camera controls
        self.camera_controller.setup_controls()
        
        # Setup lighting
        self._setup_lighting()
        
        self.logger.info("Refactored Kent-sized terrain ready!")
    
    def _setup_lighting(self):
        """Setup advanced lighting system"""
        # Ambient light
        alight = AmbientLight('alight')
        alight.setColor((0.6, 0.6, 0.7, 1))
        alnp = self.render.attachNewNode(alight)
        self.render.setLight(alnp)
        
        # Main sun
        sun = DirectionalLight('sun')
        sun.setColor((1.2, 1.0, 0.9, 1))
        sun_np = self.render.attachNewNode(sun)
        sun_np.setHpr(-25, -40, 0)
        self.render.setLight(sun_np)
        
        # Fill light
        fill_light = DirectionalLight('fill')
        fill_light.setColor((0.4, 0.5, 0.6, 1))
        fill_np = self.render.attachNewNode(fill_light)
        fill_np.setHpr(130, -25, 0)
        self.render.setLight(fill_np)
        
        # Atmospheric fog
        fog = Fog("fog")
        fog.setColor(0.75, 0.85, 0.95)
        fog.setExpDensity(0.00003)
        self.render.setFog(fog)


if __name__ == "__main__":
    print("\n=== 08.15 ULTRA HIGH RESOLUTION Kent Terrain (Erosion Smoothed) ===")
    print("Scale: 59km x 59km (3,500 km²)")
    print("🔬 ULTRA HIGH RESOLUTION:")
    print("  • 1000x1000 = 1,000,000 vertices (vs 90,000 before)")
    print("  • 6 levels of detail from continental to 0.5m features")
    print("  • Much smoother, more granular terrain geometry")
    print("  • Realistic surface detail for ground-level exploration")
    print("⚡ PERFORMANCE:")
    print("  • Optimized single primitive for 2M triangles")
    print("  • Efficient progress updates (every 50-100 rows)")
    print("  • Modular architecture for maintainability")
    print("🎯 FOCUS:")
    print("  • Getting the geometry right first")
    print("  • Smooth, realistic terrain transitions")
    print("  • No more blocky, low-resolution appearance")
    print("\nStarting ULTRA HIGH RESOLUTION terrain generation...")
    app = HighResKentTerrain()
    app.run()
