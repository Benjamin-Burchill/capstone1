"""
08.06_terrain_kent_loading.py - Kent-sized terrain with enhanced loading screen
Massive scale: 59,000 x 59,000 units
Features: Detailed progress tracking, ETA calculation, comprehensive logging
"""

from direct.showbase.ShowBase import ShowBase
from panda3d.core import (
    WindowProperties, Point3, Vec3,
    GeomNode, GeomTriangles, Geom,
    GeomVertexFormat, GeomVertexData, GeomVertexWriter,
    AmbientLight, DirectionalLight, Fog
)
from direct.task import Task
from direct.gui.DirectGui import DirectWaitBar, DirectLabel
import numpy as np
import math
import time
import logging
from datetime import datetime, timedelta

class KentSizedTerrain(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        
        # Setup logging
        self.setup_logging()
        
        # Window setup
        props = WindowProperties()
        props.setTitle("Kent-Sized Terrain - 3,500 km² (Enhanced Loading)")
        self.win.requestProperties(props)
        
        # Sky color
        self.setBackgroundColor(0.4, 0.5, 0.7, 1)
        
        # Loading progress tracking
        self.start_time = time.time()
        self.current_step = ""
        self.total_steps = 10
        self.current_step_num = 0
        self.step_start_time = time.time()
        self.progress_history = []  # For ETA calculation
        
        # Setup enhanced loading screen
        self.loading_title = DirectLabel(
            text="Generating Kent-Sized Terrain",
            text_scale=0.08,
            frameColor=(0, 0, 0, 0.7),
            text_fg=(1, 1, 0.8, 1),
            pos=(0, 0, 0.4)
        )
        
        self.loading_label = DirectLabel(
            text="Initializing terrain generation...",
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
            text="Step 0/10: Initializing",
            text_scale=0.04,
            frameColor=(0, 0, 0, 0),
            text_fg=(1, 0.8, 0.6, 1),
            pos=(0, 0, -0.12)
        )
        
        # Start generation task
        self.generation_task = self.taskMgr.add(self.generate_terrain_task, "generate_terrain")
        
        # Camera state management (initial)
        self.camera_pos = Point3(0, -5000, 2000)  # Start very high up
        self.camera_hpr = Vec3(0, -30, 0)  # Look down
        self.camera.setPos(self.camera_pos)
        self.camera.setHpr(self.camera_hpr)
        
        # Movement controls (disabled until loaded)
        self.keys = {
            "w": False, "s": False, "a": False, "d": False,
            "space": False, "shift": False, "q": False, "e": False,
            "up": False, "down": False
        }
        self.move_speed = 2000.0
        self.fast_speed = 8000.0
        self.rotate_speed = 45.0
        self.fast_mode = False
        
        # UI Elements (hidden until loaded)
        from direct.gui.OnscreenText import OnscreenText
        self.title = OnscreenText(
            text="Kent-Sized Terrain (3,500 km²)",
            pos=(0, 0.95), scale=0.045, fg=(1, 1, 1, 1)
        )
        self.controls = OnscreenText(
            text="WASD: Move | Q/E: Yaw | Arrows: Pitch | Space/Shift: Up/Down | F: Fast mode | R: Reset",
            pos=(0, 0.89), scale=0.038, fg=(0.9, 0.9, 0.9, 1)
        )
        self.state_text = OnscreenText(
            text="",
            pos=(0, -0.95), scale=0.04,
            fg=(1, 1, 0, 1), mayChange=True
        )
        self.info_text = OnscreenText(
            text="Scale: 59km x 59km | Features: Mountains, Valleys, Rivers, Coastlines",
            pos=(0, -0.89), scale=0.035,
            fg=(0.8, 0.8, 0.8, 1)
        )
        self.title.hide()
        self.controls.hide()
        self.state_text.hide()
        self.info_text.hide()
    
    def setup_logging(self):
        """Setup comprehensive logging for terrain generation"""
        # Create logger
        self.logger = logging.getLogger('TerrainGeneration')
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
            file_handler = logging.FileHandler('terrain_generation.log')
            file_handler.setLevel(logging.DEBUG)
            file_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)
        except Exception as e:
            print(f"Could not create log file: {e}")
        
        self.logger.info("=== Terrain Generation Session Started ===")
        self.logger.info(f"Target size: 59,000 x 59,000 units (3,500 km²)")
    
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
                # Calculate average progress rate
                time_span = self.progress_history[-1][0] - self.progress_history[0][0]
                progress_span = self.progress_history[-1][1] - self.progress_history[0][1]
                
                if time_span > 0 and progress_span > 0:
                    rate = progress_span / time_span  # progress per second
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
    
    def generate_terrain_task(self, task):
        if not hasattr(self, 'generator'):
            self.generator = self.create_kent_terrain_generator()
        
        try:
            progress_data = next(self.generator)
            if isinstance(progress_data, tuple):
                progress, step_name, step_num = progress_data
                self.update_progress(progress, step_name, step_num)
            else:
                # Fallback for simple progress values
                self.update_progress(progress_data, "Processing...", None)
        except StopIteration as e:
            self.terrain = e.value
            total_time = time.time() - self.start_time
            self.logger.info(f"=== Terrain Generation Complete ===")
            self.logger.info(f"Total generation time: {total_time:.2f}s")
            self.finish_loading()
            return Task.done
        return Task.cont
    
    def create_kent_terrain_generator(self):
        # KENT-SIZED scale parameters
        size = 59000
        resolution = 200
        
        # Phase 1: Setup (5%)
        yield (0.01, "Initializing random seed and coordinate system", 1)
        np.random.seed(42)
        x = np.linspace(-size/2, size/2, resolution)
        y = np.linspace(-size/2, size/2, resolution)
        X, Y = np.meshgrid(x, y)
        distance_from_center = np.sqrt(X**2 + Y**2)
        max_distance = size / 2
        yield (0.05, "Coordinate system and distance calculations complete", 1)
        
        # Phase 2: Land mask (10%)
        yield (0.08, "Generating land boundaries and coastline patterns", 2)
        land_width = size * 0.8
        land_height = size * 0.6
        coastline_noise = (
            np.sin(np.arctan2(Y, X) * 3) * 0.2 +
            np.sin(np.arctan2(Y, X) * 7) * 0.1 +
            np.sin(np.arctan2(Y, X) * 15) * 0.05
        )
        yield (0.12, "Computing ocean and coastal areas", 2)
        land_mask = np.ones((resolution, resolution))
        ocean_areas = (
            (np.abs(X) > land_width/2) | 
            (np.abs(Y) > land_height/2) |
            (distance_from_center > size * 0.4)
        )
        coastal_variation = coastline_noise * (distance_from_center / max_distance)
        ocean_areas = ocean_areas | (coastal_variation > 0.1)
        land_mask[ocean_areas] = 0
        yield (0.15, "Land mask generation complete", 2)
        
        # Phase 3: Heightmap base (20%)
        yield (0.18, "Creating base heightmap and ocean depth", 3)
        ocean_depth = -100.0
        heightmap = np.ones((resolution, resolution)) * ocean_depth
        yield (0.25, "Applying base land elevation", 3)
        land_elevation = land_mask * 200
        yield (0.35, "Base heightmap established", 3)
        
        # Phase 4: Terrain features (20%)
        yield (0.38, "Generating highland regions", 4)
        highland_mask = np.maximum(0, land_mask - 0.2) / 0.8
        highlands = highland_mask * 300 * (1 - distance_from_center / max_distance)
        yield (0.42, "Creating mountain ridges and valleys", 4)
        ridge_spacing = 5000.0
        ridges = 50 * np.sin(X / ridge_spacing * 2 * np.pi) * highland_mask
        ridges += 30 * np.cos(Y / (ridge_spacing * 1.5) * 2 * np.pi) * highland_mask
        yield (0.47, "Carving river systems", 4)
        river_pattern = np.sin(X * 0.0001) * np.cos(Y * 0.0001)
        rivers = river_pattern * 20 * land_mask
        yield (0.52, "Defining coastal regions", 4)
        coastal_areas = (distance_from_center > size * 0.25) & (land_mask > 0.5)
        heightmap[coastal_areas] = ocean_depth + 10
        heightmap = ocean_depth * (1 - land_mask) + land_elevation
        heightmap += highlands
        heightmap += ridges
        heightmap += rivers
        yield (0.55, "Major terrain features complete", 4)
        
        # Phase 5: Noise (10%)
        yield (0.58, "Generating large-scale terrain noise", 5)
        noise_large = np.random.randn(resolution, resolution) * 10
        from scipy.ndimage import gaussian_filter
        try:
            noise_large = gaussian_filter(noise_large, sigma=3)
        except ImportError:
            for _ in range(5):
                noise_smooth = np.zeros_like(noise_large)
                noise_smooth[1:-1, 1:-1] = (
                    noise_large[1:-1, 1:-1] * 0.4 +
                    noise_large[:-2, 1:-1] * 0.15 +
                    noise_large[2:, 1:-1] * 0.15 +
                    noise_large[1:-1, :-2] * 0.15 +
                    noise_large[1:-1, 2:] * 0.15
                )
                noise_large = noise_smooth
        heightmap += noise_large * land_mask
        yield (0.62, "Adding fine detail noise", 5)
        noise_small = np.random.randn(resolution, resolution) * 2
        heightmap += noise_small * land_mask
        far_ocean = distance_from_center > size * 0.45
        heightmap[far_ocean] = ocean_depth
        yield (0.65, "Terrain noise application complete", 5)
        
        # Phase 6: Mesh setup (5%)
        yield (0.67, "Setting up 3D mesh vertex format", 6)
        vformat = GeomVertexFormat.getV3n3c4()
        vdata = GeomVertexData('terrain', vformat, Geom.UHStatic)
        vdata.setNumRows(resolution * resolution)
        vertex = GeomVertexWriter(vdata, 'vertex')
        normal = GeomVertexWriter(vdata, 'normal')
        color = GeomVertexWriter(vdata, 'color')
        yield (0.70, "Mesh vertex writers initialized", 6)
        
        # Phase 7: Vertices (10%)
        yield (0.72, "Generating terrain vertices and colors", 7)
        for j in range(resolution):
            for i in range(resolution):
                h = heightmap[j, i]
                vertex.addData3(x[i], y[j], h)
                normal.addData3(0, 0, 1)
                if h < ocean_depth + 5:
                    r, g, b = 0.1, 0.2, 0.4
                elif h < ocean_depth + 15:
                    r, g, b = 0.15, 0.3, 0.5
                elif h < 0:
                    r, g, b = 0.2, 0.4, 0.6
                elif h < 5:
                    r, g, b = 0.8, 0.7, 0.5
                elif h < 20:
                    r, g, b = 0.3, 0.5, 0.2
                elif h < 50:
                    r, g, b = 0.2, 0.4, 0.15
                elif h < 100:
                    r, g, b = 0.25, 0.35, 0.15
                elif h < 150:
                    r, g, b = 0.4, 0.35, 0.3
                elif h < 200:
                    r, g, b = 0.5, 0.45, 0.4
                else:
                    r, g, b = 0.9, 0.9, 0.95
                variation = (np.random.random() - 0.5) * 0.05
                r = np.clip(r + variation, 0, 1)
                g = np.clip(g + variation, 0, 1)
                b = np.clip(b + variation, 0, 1)
                color.addData4(r, g, b, 1.0)
            # Update progress every 20 rows for smoother progress
            if j % 20 == 0 or j == resolution - 1:
                progress = 0.70 + (0.10 * (j + 1) / resolution)
                step_text = f"Generating vertices: {j+1}/{resolution} rows ({((j+1)/resolution)*100:.0f}%)"
                yield (progress, step_text, 7)
        
        # Phase 8: Normals (5%)
        yield (0.82, "Calculating surface normals for lighting", 8)
        for j in range(resolution):
            for i in range(resolution):
                idx = j * resolution + i
                if i > 0 and i < resolution-1 and j > 0 and j < resolution-1:
                    h_center = heightmap[j, i]
                    h_left = heightmap[j, i-1]
                    h_right = heightmap[j, i+1]
                    h_down = heightmap[j-1, i]
                    h_up = heightmap[j+1, i]
                    dx = (h_right - h_left) / (2.0 * size / resolution)
                    dy = (h_up - h_down) / (2.0 * size / resolution)
                    nx = -dx
                    ny = -dy
                    nz = 1.0
                    length = math.sqrt(nx*nx + ny*ny + nz*nz)
                    normal.setRow(idx)
                    normal.setData3(nx/length, ny/length, nz/length)
            # Update progress every 40 rows for normals
            if j % 40 == 0 or j == resolution - 1:
                progress = 0.80 + (0.05 * (j + 1) / resolution)
                step_text = f"Computing normals: {j+1}/{resolution} rows ({((j+1)/resolution)*100:.0f}%)"
                yield (progress, step_text, 8)
        
        # Phase 9: Geometry and triangles (10%)
        yield (0.87, "Building triangle mesh geometry", 9)
        geom = Geom(vdata)
        for j in range(resolution - 1):
            for i in range(resolution - 1):
                v0 = j * resolution + i
                v1 = v0 + 1
                v2 = v0 + resolution
                v3 = v2 + 1
                prim = GeomTriangles(Geom.UHStatic)
                prim.addVertices(v0, v2, v1)
                prim.addVertices(v1, v2, v3)
                prim.closePrimitive()
                geom.addPrimitive(prim)
            # Update progress every 20 rows for triangles
            if j % 20 == 0 or j == resolution - 2:
                progress = 0.85 + (0.10 * (j + 1) / (resolution - 1))
                step_text = f"Creating triangles: {j+1}/{resolution-1} rows ({((j+1)/(resolution-1))*100:.0f}%)"
                yield (progress, step_text, 9)
        
        # Phase 10: Final node (5%)
        yield (0.96, "Creating terrain node and attaching to scene", 10)
        node = GeomNode('terrain')
        node.addGeom(geom)
        terrain_np = self.render.attachNewNode(node)
        terrain_np.setTwoSided(True)
        
        yield (0.98, "Calculating terrain statistics", 10)
        min_h = np.min(heightmap)
        max_h = np.max(heightmap)
        self.logger.info(f"Height range: {min_h:.1f} to {max_h:.1f} meters")
        self.logger.info(f"Land area: ~{int(land_width/1000)}km x {int(land_height/1000)}km")
        self.logger.info(f"Total area: ~{int(size*size/1000000)} km²")
        
        yield (1.0, "Terrain generation complete!", 10)
        return terrain_np  # This will be raised in StopIteration.value
    
    def finish_loading(self):
        # Hide loading screen
        self.loading_title.destroy()
        self.loading_label.destroy()
        self.progress_bar.destroy()
        self.percentage_label.destroy()
        self.time_info_label.destroy()
        self.step_info_label.destroy()
        
        # Show UI
        self.title.show()
        self.controls.show()
        self.state_text.show()
        self.info_text.show()
        
        # Enable controls
        for key in self.keys:
            self.accept(key, self.set_key, [key, True])
            self.accept(f"{key}-up", self.set_key, [key, False])
        self.accept("arrow_up", self.set_key, ["up", True])
        self.accept("arrow_up-up", self.set_key, ["up", False])
        self.accept("arrow_down", self.set_key, ["down", True])
        self.accept("arrow_down-up", self.set_key, ["down", False])
        self.accept("escape", self.userExit)
        self.accept("r", self.reset_camera)
        self.accept("f", self.toggle_fast_mode)
        
        # Add update task
        self.taskMgr.add(self.update_camera, "update_camera")
        
        # Lighting
        alight = AmbientLight('alight')
        alight.setColor((0.4, 0.45, 0.5, 1))
        alnp = self.render.attachNewNode(alight)
        self.render.setLight(alnp)
        
        sun = DirectionalLight('sun')
        sun.setColor((0.7, 0.65, 0.6, 1))
        sun_np = self.render.attachNewNode(sun)
        sun_np.setHpr(-45, -60, 0)
        self.render.setLight(sun_np)
        
        # Fog
        fog = Fog("fog")
        fog.setColor(0.6, 0.7, 0.8)
        fog.setExpDensity(0.0001)
        self.render.setFog(fog)
        
        print("Kent-sized terrain ready!")
    
    def set_key(self, key, value):
        self.keys[key] = value
    
    def toggle_fast_mode(self):
        self.fast_mode = not self.fast_mode
        speed_text = "FAST" if self.fast_mode else "NORMAL"
        print(f"Movement speed: {speed_text}")
    
    def reset_camera(self):
        self.camera_pos = Point3(0, -5000, 2000)
        self.camera_hpr = Vec3(0, -30, 0)
        self.camera.setPos(self.camera_pos)
        self.camera.setHpr(self.camera_hpr)
        print("Camera reset to overview position")
    
    def update_camera(self, task):
        dt = 0.016
        
        speed = self.fast_speed if self.fast_mode else self.move_speed
        
        heading_rad = math.radians(self.camera_hpr.x)
        pitch_rad = math.radians(self.camera_hpr.y)
        
        forward_x = math.sin(heading_rad) * math.cos(pitch_rad)
        forward_y = math.cos(heading_rad) * math.cos(pitch_rad)
        forward_z = -math.sin(pitch_rad)
        
        right_x = math.cos(heading_rad)
        right_y = -math.sin(heading_rad)
        
        if self.keys["w"]:
            self.camera_pos.x += forward_x * speed * dt
            self.camera_pos.y += forward_y * speed * dt
            self.camera_pos.z += forward_z * speed * dt
        if self.keys["s"]:
            self.camera_pos.x -= forward_x * speed * dt
            self.camera_pos.y -= forward_y * speed * dt
            self.camera_pos.z -= forward_z * speed * dt
        if self.keys["a"]:
            self.camera_pos.x -= right_x * speed * dt
            self.camera_pos.y -= right_y * speed * dt
        if self.keys["d"]:
            self.camera_pos.x += right_x * speed * dt
            self.camera_pos.y += right_y * speed * dt
        if self.keys["space"]:
            self.camera_pos.z += speed * dt
        if self.keys["shift"]:
            self.camera_pos.z -= speed * dt
        
        if self.keys["q"]:
            self.camera_hpr.x += self.rotate_speed * dt
        if self.keys["e"]:
            self.camera_hpr.x -= self.rotate_speed * dt
        if self.keys["up"]:
            self.camera_hpr.y = max(-89, self.camera_hpr.y - self.rotate_speed * dt)
        if self.keys["down"]:
            self.camera_hpr.y = min(89, self.camera_hpr.y + self.rotate_speed * dt)
        
        self.camera.setPos(self.camera_pos)
        self.camera.setHpr(self.camera_hpr)
        
        mode = "FAST" if self.fast_mode else "NORM"
        self.state_text.setText(
            f"Pos: ({self.camera_pos.x/1000:.1f}km, {self.camera_pos.y/1000:.1f}km, {self.camera_pos.z/1000:.1f}km) | "
            f"H: {self.camera_hpr.x:.0f}° P: {self.camera_hpr.y:.0f}° | Mode: {mode}"
        )
        
        return Task.cont

if __name__ == "__main__":
    print("\n=== Kent-Sized Terrain with Enhanced Loading System ===")
    print("Scale: 59km x 59km (3,500 km²)")
    print("Features:")
    print("  • Detailed progress tracking with ETA calculation")
    print("  • Step-by-step loading information")
    print("  • Comprehensive logging to console and file")
    print("  • Accurate percentage display")
    print("  • Elapsed time tracking")
    print("\nStarting terrain generation...")
    app = KentSizedTerrain()
    app.run()

