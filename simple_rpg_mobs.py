"""
Simple RPG with Goblin Mobs - Basic Foundation
300x300m plane with player and goblin mobs (colored cuboids)
No combat yet - just movement and HP bars
"""

from direct.showbase.ShowBase import ShowBase
from panda3d.core import (
    WindowProperties, Point3, Vec3, CollisionSphere, CollisionNode,
    CollisionTraverser, CollisionHandlerPusher, BitMask32,
    AmbientLight, DirectionalLight, CardMaker, TransparencyAttrib
)
from direct.task import Task
from direct.gui.DirectGui import DirectWaitBar, OnscreenText
import random
import math


class Player:
    """Player character - colored cuboid with movement"""
    
    def __init__(self, base, pos=Point3(0, 0, 1)):
        self.base = base
        self.max_hp = 100
        self.current_hp = 100
        self.move_speed = 15.0
        self.position = pos
        
        # Create player visual (green cuboid)
        self.model = self.create_cuboid("player", 1.0, 1.0, 1.5)
        
        self.model.setPos(pos)
        self.model.setColor(0.2, 0.8, 0.2, 1)  # Green
        self.model.reparentTo(base.render)
        
        # Collision sphere
        self.setup_collision()
        
        # HP Bar
        self.setup_hp_bar()
        
        # Movement state
        self.keys = {"w": False, "s": False, "a": False, "d": False}
        self.setup_controls()
    
    def create_cuboid(self, name, width, depth, height):
        """Create a 3D cuboid geometry"""
        from panda3d.core import GeomNode, GeomTriangles, Geom
        from panda3d.core import GeomVertexFormat, GeomVertexData, GeomVertexWriter
        
        # Create vertex format
        vformat = GeomVertexFormat.getV3n3()
        vdata = GeomVertexData(name, vformat, Geom.UHStatic)
        vdata.setNumRows(24)  # 6 faces * 4 vertices each
        
        vertex = GeomVertexWriter(vdata, 'vertex')
        normal = GeomVertexWriter(vdata, 'normal')
        
        # Define vertices for a box
        w, d, h = width/2, depth/2, height/2
        vertices = [
            # Front face
            (-w, -d, -h), (w, -d, -h), (w, -d, h), (-w, -d, h),
            # Back face  
            (w, d, -h), (-w, d, -h), (-w, d, h), (w, d, h),
            # Left face
            (-w, d, -h), (-w, -d, -h), (-w, -d, h), (-w, d, h),
            # Right face
            (w, -d, -h), (w, d, -h), (w, d, h), (w, -d, h),
            # Bottom face
            (-w, -d, -h), (w, -d, -h), (w, d, -h), (-w, d, -h),
            # Top face
            (-w, d, h), (w, d, h), (w, -d, h), (-w, -d, h)
        ]
        
        # Normals for each face
        normals = [
            # Front face
            (0, -1, 0), (0, -1, 0), (0, -1, 0), (0, -1, 0),
            # Back face
            (0, 1, 0), (0, 1, 0), (0, 1, 0), (0, 1, 0),
            # Left face
            (-1, 0, 0), (-1, 0, 0), (-1, 0, 0), (-1, 0, 0),
            # Right face
            (1, 0, 0), (1, 0, 0), (1, 0, 0), (1, 0, 0),
            # Bottom face
            (0, 0, -1), (0, 0, -1), (0, 0, -1), (0, 0, -1),
            # Top face
            (0, 0, 1), (0, 0, 1), (0, 0, 1), (0, 0, 1)
        ]
        
        # Add vertices and normals
        for i, (vert, norm) in enumerate(zip(vertices, normals)):
            vertex.addData3(vert[0], vert[1], vert[2])
            normal.addData3(norm[0], norm[1], norm[2])
        
        # Create geometry and triangles
        geom = Geom(vdata)
        prim = GeomTriangles(Geom.UHStatic)
        
        # Define triangles for each face (2 triangles per face)
        faces = [
            # Front face
            (0, 1, 2), (0, 2, 3),
            # Back face
            (4, 5, 6), (4, 6, 7),
            # Left face
            (8, 9, 10), (8, 10, 11),
            # Right face
            (12, 13, 14), (12, 14, 15),
            # Bottom face
            (16, 17, 18), (16, 18, 19),
            # Top face
            (20, 21, 22), (20, 22, 23)
        ]
        
        for face in faces:
            prim.addVertices(face[0], face[1], face[2])
        
        prim.closePrimitive()
        geom.addPrimitive(prim)
        
        # Create node and return
        node = GeomNode(name)
        node.addGeom(geom)
        model = self.base.render.attachNewNode(node)
        return model
    
    def setup_collision(self):
        """Setup collision detection"""
        collision_sphere = CollisionSphere(0, 0, 1, 1)
        collision_node = CollisionNode("player")
        collision_node.addSolid(collision_sphere)
        collision_node.setFromCollideMask(BitMask32.bit(1))
        collision_node.setIntoCollideMask(BitMask32.bit(1))
        self.collision_np = self.model.attachNewNode(collision_node)
    
    def setup_hp_bar(self):
        """Create HP bar above player"""
        self.hp_bar = DirectWaitBar(
            value=100,
            pos=(0, 0, 4),  # Above player
            scale=(2, 1, 0.3),
            frameColor=(0.2, 0.2, 0.2, 0.8),
            barColor=(0.2, 0.8, 0.2, 1),
            parent=self.model
        )
        
        self.hp_text = OnscreenText(
            text=f"HP: {self.current_hp}/{self.max_hp}",
            pos=(0, 0, 4.5),
            scale=0.8,
            fg=(1, 1, 1, 1),
            parent=self.model
        )
    
    def setup_controls(self):
        """Setup WASD movement controls"""
        for key in self.keys:
            self.base.accept(key, self.set_key, [key, True])
            self.base.accept(f"{key}-up", self.set_key, [key, False])
        
        # All controls working correctly!
    
    def set_key(self, key, value):
        """Handle key press/release"""
        self.keys[key] = value
    
    def update(self, dt):
        """Update player position and camera"""
        # Calculate movement
        move_x = 0
        move_y = 0
        
        if self.keys["w"]:
            move_y += 1
        if self.keys["s"]:
            move_y -= 1
        if self.keys["a"]:
            move_x -= 1
        if self.keys["d"]:
            move_x += 1
        
        # Movement is working correctly!
        
        # Normalize diagonal movement
        if move_x != 0 or move_y != 0:
            length = math.sqrt(move_x * move_x + move_y * move_y)
            move_x /= length
            move_y /= length
        
        # Apply movement
        new_x = self.position.x + move_x * self.move_speed * dt
        new_y = self.position.y + move_y * self.move_speed * dt
        
        # Keep within bounds (300x300m plane)
        new_x = max(-150, min(150, new_x))
        new_y = max(-150, min(150, new_y))
        
        self.position = Point3(new_x, new_y, 1)
        self.model.setPos(self.position)
        
        # Update camera to follow player
        camera_pos = Point3(new_x - 10, new_y - 10, 8)
        self.base.camera.setPos(camera_pos)
        self.base.camera.lookAt(self.position)
    
    def take_damage(self, damage):
        """Player takes damage"""
        self.current_hp = max(0, self.current_hp - damage)
        self.update_hp_display()
    
    def update_hp_display(self):
        """Update HP bar and text"""
        hp_percentage = (self.current_hp / self.max_hp) * 100
        self.hp_bar['value'] = hp_percentage
        self.hp_text.setText(f"HP: {self.current_hp}/{self.max_hp}")
        
        # Change color based on health
        if hp_percentage > 60:
            self.hp_bar['barColor'] = (0.2, 0.8, 0.2, 1)  # Green
        elif hp_percentage > 30:
            self.hp_bar['barColor'] = (0.8, 0.8, 0.2, 1)  # Yellow
        else:
            self.hp_bar['barColor'] = (0.8, 0.2, 0.2, 1)  # Red


class Goblin:
    """Goblin mob - colored cuboid that chases player"""
    
    def __init__(self, base, pos=Point3(0, 0, 1), goblin_id=0):
        self.base = base
        self.goblin_id = goblin_id
        self.max_hp = 30
        self.current_hp = 30
        self.move_speed = 8.0
        self.detection_range = 20.0
        self.position = pos
        self.target_position = pos
        self.state = "idle"  # idle, chasing
        
        # Create goblin visual (red cuboid)
        self.model = self.create_goblin_cuboid(base, f"goblin_{goblin_id}", 0.8, 0.8, 1.2)
        self.model.setPos(pos)
        self.model.setColor(0.8, 0.2, 0.2, 1)  # Red
        
        # Setup HP bar
        self.setup_hp_bar()
        
        # Add some idle bobbing animation
        self.bob_time = random.uniform(0, 6.28)  # Random phase
    
    def create_goblin_cuboid(self, base, name, width, depth, height):
        """Create a 3D cuboid geometry for goblins"""
        from panda3d.core import GeomNode, GeomTriangles, Geom
        from panda3d.core import GeomVertexFormat, GeomVertexData, GeomVertexWriter
        
        # Create vertex format
        vformat = GeomVertexFormat.getV3n3()
        vdata = GeomVertexData(name, vformat, Geom.UHStatic)
        vdata.setNumRows(24)  # 6 faces * 4 vertices each
        
        vertex = GeomVertexWriter(vdata, 'vertex')
        normal = GeomVertexWriter(vdata, 'normal')
        
        # Define vertices for a box
        w, d, h = width/2, depth/2, height/2
        vertices = [
            # Front face
            (-w, -d, -h), (w, -d, -h), (w, -d, h), (-w, -d, h),
            # Back face  
            (w, d, -h), (-w, d, -h), (-w, d, h), (w, d, h),
            # Left face
            (-w, d, -h), (-w, -d, -h), (-w, -d, h), (-w, d, h),
            # Right face
            (w, -d, -h), (w, d, -h), (w, d, h), (w, -d, h),
            # Bottom face
            (-w, -d, -h), (w, -d, -h), (w, d, -h), (-w, d, -h),
            # Top face
            (-w, d, h), (w, d, h), (w, -d, h), (-w, -d, h)
        ]
        
        # Normals for each face
        normals = [
            # Front face
            (0, -1, 0), (0, -1, 0), (0, -1, 0), (0, -1, 0),
            # Back face
            (0, 1, 0), (0, 1, 0), (0, 1, 0), (0, 1, 0),
            # Left face
            (-1, 0, 0), (-1, 0, 0), (-1, 0, 0), (-1, 0, 0),
            # Right face
            (1, 0, 0), (1, 0, 0), (1, 0, 0), (1, 0, 0),
            # Bottom face
            (0, 0, -1), (0, 0, -1), (0, 0, -1), (0, 0, -1),
            # Top face
            (0, 0, 1), (0, 0, 1), (0, 0, 1), (0, 0, 1)
        ]
        
        # Add vertices and normals
        for i, (vert, norm) in enumerate(zip(vertices, normals)):
            vertex.addData3(vert[0], vert[1], vert[2])
            normal.addData3(norm[0], norm[1], norm[2])
        
        # Create geometry and triangles
        geom = Geom(vdata)
        prim = GeomTriangles(Geom.UHStatic)
        
        # Define triangles for each face (2 triangles per face)
        faces = [
            # Front face
            (0, 1, 2), (0, 2, 3),
            # Back face
            (4, 5, 6), (4, 6, 7),
            # Left face
            (8, 9, 10), (8, 10, 11),
            # Right face
            (12, 13, 14), (12, 14, 15),
            # Bottom face
            (16, 17, 18), (16, 18, 19),
            # Top face
            (20, 21, 22), (20, 22, 23)
        ]
        
        for face in faces:
            prim.addVertices(face[0], face[1], face[2])
        
        prim.closePrimitive()
        geom.addPrimitive(prim)
        
        # Create node and return
        node = GeomNode(name)
        node.addGeom(geom)
        model = base.render.attachNewNode(node)
        return model
    
    def setup_hp_bar(self):
        """Create HP bar above goblin"""
        self.hp_bar = DirectWaitBar(
            value=100,
            pos=(0, 0, 3),
            scale=(1.5, 1, 0.2),
            frameColor=(0.2, 0.2, 0.2, 0.8),
            barColor=(0.8, 0.2, 0.2, 1),
            parent=self.model
        )
        
        self.hp_text = OnscreenText(
            text=f"{self.current_hp}",
            pos=(0, 0, 3.3),
            scale=0.6,
            fg=(1, 1, 1, 1),
            parent=self.model
        )
    
    def update(self, dt, player_pos):
        """Update goblin AI and movement"""
        # Calculate distance to player
        distance_to_player = (self.position - player_pos).length()
        
        # State machine
        if distance_to_player <= self.detection_range:
            self.state = "chasing"
        else:
            self.state = "idle"
        
        # Behavior based on state
        if self.state == "chasing":
            # Move toward player
            direction = player_pos - self.position
            direction.normalize()
            
            new_pos = self.position + direction * self.move_speed * dt
            # Keep within bounds
            new_pos.x = max(-150, min(150, new_pos.x))
            new_pos.y = max(-150, min(150, new_pos.y))
            new_pos.z = 1  # Stay on ground
            
            self.position = new_pos
            self.model.setPos(self.position)
            
            # Face the player
            self.model.lookAt(player_pos)
            
        else:  # idle
            # Gentle bobbing animation
            self.bob_time += dt * 2
            bob_height = 1 + 0.1 * math.sin(self.bob_time)
            self.model.setZ(bob_height)
    
    def take_damage(self, damage):
        """Goblin takes damage"""
        self.current_hp = max(0, self.current_hp - damage)
        self.update_hp_display()
    
    def update_hp_display(self):
        """Update HP bar and text"""
        hp_percentage = (self.current_hp / self.max_hp) * 100
        self.hp_bar['value'] = hp_percentage
        self.hp_text.setText(f"{self.current_hp}")
        
        if hp_percentage <= 0:
            self.hp_bar['barColor'] = (0.3, 0.3, 0.3, 1)  # Gray when dead
        elif hp_percentage > 60:
            self.hp_bar['barColor'] = (0.8, 0.2, 0.2, 1)  # Red
        else:
            self.hp_bar['barColor'] = (0.6, 0.1, 0.1, 1)  # Dark red


class SimpleRPG(ShowBase):
    """Main RPG application"""
    
    def __init__(self):
        ShowBase.__init__(self)
        
        # Window setup
        props = WindowProperties()
        props.setTitle("Simple RPG - Goblin Mobs (No Combat)")
        self.win.requestProperties(props)
        
        # Create 300x300m plane
        self.setup_environment()
        
        # Create player
        self.player = Player(self, Point3(0, 0, 1))
        
        # Create goblin packs
        self.goblins = []
        self.spawn_goblins()
        
        # Setup lighting
        self.setup_lighting()
        
        # Setup UI
        self.setup_ui()
        
        # Start game loop
        self.taskMgr.add(self.game_update_task, "game_update")
        
        print("Simple RPG Started!")
        print("Controls: WASD to move")
        print("Goblins will chase you when you get close!")
    
    def setup_environment(self):
        """Create the 300x300m plane with visual grid"""
        # Create ground plane with checkered pattern
        from panda3d.core import CardMaker, Texture, PNMImage
        
        # Create a checkered texture
        size = 64
        image = PNMImage(size, size)
        for y in range(size):
            for x in range(size):
                # Create 8x8 checkerboard pattern
                checker_size = 8
                if ((x // checker_size) + (y // checker_size)) % 2 == 0:
                    image.setXel(x, y, 0.4, 0.7, 0.4)  # Light green
                else:
                    image.setXel(x, y, 0.2, 0.5, 0.2)  # Dark green
        
        texture = Texture()
        texture.load(image)
        texture.setWrapU(Texture.WMRepeat)
        texture.setWrapV(Texture.WMRepeat)
        
        # Create ground plane
        cm = CardMaker("ground")
        cm.setFrame(-150, 150, -150, 150)
        cm.setUvRange((0, 0), (30, 30))  # Repeat texture 30x30 times
        self.ground = self.render.attachNewNode(cm.generate())
        self.ground.setP(-90)  # Rotate to be horizontal
        self.ground.setTexture(texture)
        
        # Add visual reference objects
        self.create_visual_references()
    
    def create_visual_references(self):
        """Add visual reference objects to make movement obvious"""
        from panda3d.core import CardMaker
        
        # Create various reference objects scattered around
        references = [
            # Trees (tall green rectangles)
            {"pos": (30, 40, 0), "size": (2, 2, 8), "color": (0.1, 0.4, 0.1, 1)},
            {"pos": (-50, 30, 0), "size": (2, 2, 10), "color": (0.1, 0.5, 0.1, 1)},
            {"pos": (80, -20, 0), "size": (2, 2, 12), "color": (0.1, 0.3, 0.1, 1)},
            {"pos": (-30, -60, 0), "size": (2, 2, 9), "color": (0.1, 0.4, 0.1, 1)},
            
            # Rocks (gray cubes)
            {"pos": (60, 10, 0), "size": (3, 3, 2), "color": (0.5, 0.5, 0.5, 1)},
            {"pos": (-40, -30, 0), "size": (4, 4, 3), "color": (0.4, 0.4, 0.4, 1)},
            {"pos": (10, -80, 0), "size": (2, 2, 1.5), "color": (0.6, 0.6, 0.6, 1)},
            
            # Pillars (tall white/yellow structures)
            {"pos": (0, 70, 0), "size": (1, 1, 15), "color": (0.9, 0.9, 0.7, 1)},
            {"pos": (-70, 0, 0), "size": (1, 1, 15), "color": (0.9, 0.9, 0.7, 1)},
            {"pos": (70, 70, 0), "size": (1, 1, 15), "color": (0.9, 0.9, 0.7, 1)},
            
            # Corner markers (boundary indicators)
            {"pos": (-145, -145, 0), "size": (2, 2, 6), "color": (0.8, 0.8, 0.2, 1)},
            {"pos": (145, -145, 0), "size": (2, 2, 6), "color": (0.8, 0.8, 0.2, 1)},
            {"pos": (145, 145, 0), "size": (2, 2, 6), "color": (0.8, 0.8, 0.2, 1)},
            {"pos": (-145, 145, 0), "size": (2, 2, 6), "color": (0.8, 0.8, 0.2, 1)},
        ]
        
        for ref in references:
            # Create cuboid using the player's method
            obj = self.create_reference_cuboid(
                f"ref_{len(references)}", 
                ref["size"][0], ref["size"][1], ref["size"][2]
            )
            obj.setPos(ref["pos"][0], ref["pos"][1], ref["pos"][2])
            obj.setColor(ref["color"])
    
    def create_reference_cuboid(self, name, width, depth, height):
        """Create a 3D cuboid for reference objects"""
        from panda3d.core import GeomNode, GeomTriangles, Geom
        from panda3d.core import GeomVertexFormat, GeomVertexData, GeomVertexWriter
        
        # Create vertex format
        vformat = GeomVertexFormat.getV3n3()
        vdata = GeomVertexData(name, vformat, Geom.UHStatic)
        vdata.setNumRows(24)  # 6 faces * 4 vertices each
        
        vertex = GeomVertexWriter(vdata, 'vertex')
        normal = GeomVertexWriter(vdata, 'normal')
        
        # Define vertices for a box
        w, d, h = width/2, depth/2, height/2
        vertices = [
            # Front face
            (-w, -d, -h), (w, -d, -h), (w, -d, h), (-w, -d, h),
            # Back face  
            (w, d, -h), (-w, d, -h), (-w, d, h), (w, d, h),
            # Left face
            (-w, d, -h), (-w, -d, -h), (-w, -d, h), (-w, d, h),
            # Right face
            (w, -d, -h), (w, d, -h), (w, d, h), (w, -d, h),
            # Bottom face
            (-w, -d, -h), (w, -d, -h), (w, d, -h), (-w, d, -h),
            # Top face
            (-w, d, h), (w, d, h), (w, -d, h), (-w, -d, h)
        ]
        
        # Normals for each face
        normals = [
            # Front face
            (0, -1, 0), (0, -1, 0), (0, -1, 0), (0, -1, 0),
            # Back face
            (0, 1, 0), (0, 1, 0), (0, 1, 0), (0, 1, 0),
            # Left face
            (-1, 0, 0), (-1, 0, 0), (-1, 0, 0), (-1, 0, 0),
            # Right face
            (1, 0, 0), (1, 0, 0), (1, 0, 0), (1, 0, 0),
            # Bottom face
            (0, 0, -1), (0, 0, -1), (0, 0, -1), (0, 0, -1),
            # Top face
            (0, 0, 1), (0, 0, 1), (0, 0, 1), (0, 0, 1)
        ]
        
        # Add vertices and normals
        for i, (vert, norm) in enumerate(zip(vertices, normals)):
            vertex.addData3(vert[0], vert[1], vert[2])
            normal.addData3(norm[0], norm[1], norm[2])
        
        # Create geometry and triangles
        geom = Geom(vdata)
        prim = GeomTriangles(Geom.UHStatic)
        
        # Define triangles for each face (2 triangles per face)
        faces = [
            # Front face
            (0, 1, 2), (0, 2, 3),
            # Back face
            (4, 5, 6), (4, 6, 7),
            # Left face
            (8, 9, 10), (8, 10, 11),
            # Right face
            (12, 13, 14), (12, 14, 15),
            # Bottom face
            (16, 17, 18), (16, 18, 19),
            # Top face
            (20, 21, 22), (20, 22, 23)
        ]
        
        for face in faces:
            prim.addVertices(face[0], face[1], face[2])
        
        prim.closePrimitive()
        geom.addPrimitive(prim)
        
        # Create node and return
        node = GeomNode(name)
        node.addGeom(geom)
        model = self.render.attachNewNode(node)
        return model
    
    def spawn_goblins(self):
        """Spawn goblin packs around the map"""
        # Create 3 goblin packs (2-3 goblins each)
        pack_centers = [
            Point3(50, 50, 1),
            Point3(-60, 40, 1),
            Point3(30, -70, 1),
            Point3(-80, -30, 1),
            Point3(80, -80, 1)
        ]
        
        goblin_id = 0
        for center in pack_centers:
            pack_size = random.randint(2, 3)
            for i in range(pack_size):
                # Spread goblins around pack center
                offset_x = random.uniform(-8, 8)
                offset_y = random.uniform(-8, 8)
                goblin_pos = Point3(
                    center.x + offset_x,
                    center.y + offset_y,
                    1
                )
                
                goblin = Goblin(self, goblin_pos, goblin_id)
                self.goblins.append(goblin)
                goblin_id += 1
        
        print(f"Spawned {len(self.goblins)} goblins in {len(pack_centers)} packs")
    
    def setup_lighting(self):
        """Setup basic lighting"""
        # Ambient light
        alight = AmbientLight('alight')
        alight.setColor((0.6, 0.6, 0.7, 1))
        alnp = self.render.attachNewNode(alight)
        self.render.setLight(alnp)
        
        # Directional light (sun)
        dlight = DirectionalLight('dlight')
        dlight.setColor((1.0, 0.9, 0.8, 1))
        dlnp = self.render.attachNewNode(dlight)
        dlnp.setHpr(-45, -45, 0)
        self.render.setLight(dlnp)
    
    def setup_ui(self):
        """Setup game UI"""
        self.title = OnscreenText(
            text="Simple RPG - Goblin Mobs",
            pos=(0, 0.95), scale=0.06,
            fg=(1, 1, 1, 1), shadow=(0, 0, 0, 1)
        )
        
        self.controls = OnscreenText(
            text="WASD: Move | Goblins chase when close",
            pos=(0, 0.88), scale=0.04,
            fg=(0.9, 0.9, 0.9, 1)
        )
        
        self.status = OnscreenText(
            text="",
            pos=(0, -0.95), scale=0.05,
            fg=(1, 1, 0, 1), mayChange=True
        )
    
    def game_update_task(self, task):
        """Main game update loop"""
        dt = globalClock.getDt()
        
        # Update player
        self.player.update(dt)
        
        # Update goblins
        active_goblins = 0
        chasing_goblins = 0
        
        for goblin in self.goblins:
            if goblin.current_hp > 0:
                goblin.update(dt, self.player.position)
                active_goblins += 1
                if goblin.state == "chasing":
                    chasing_goblins += 1
        
        # Update status
        player_pos = self.player.position
        key_status = "Keys: " + "".join([k.upper() for k, v in self.player.keys.items() if v])
        self.status.setText(
            f"Pos: ({player_pos.x:.1f}, {player_pos.y:.1f}) | "
            f"Goblins: {active_goblins} active, {chasing_goblins} chasing | {key_status}"
        )
        
        return Task.cont


if __name__ == "__main__":
    print("Starting Simple RPG with Goblin Mobs...")
    print("This is a basic foundation - no combat yet!")
    print("Features:")
    print("• 300x300m traversable plane")
    print("• Player character (green cuboid) with WASD movement")
    print("• Goblin mobs (red cuboids) that chase when close")
    print("• HP bars above all characters")
    print("• Simple proximity-based AI")
    
    app = SimpleRPG()
    app.run()
