# TODO, tomorrow: add speed slider, make speed able to be per second and show how much time is passing per second (YAY!), orbiting planets in the solar system, zoom in/out, move around with mouse, make collision work

import math, pygame, pygame_gui
from itertools import accumulate
def human_format(num):
    magnitude=math.floor(math.log(num,1000))
    return(str(num/1000**magnitude)[:4]+['', 'K', 'M', 'B', 'T'][magnitude])

#intervals=tuple(zip(('seconds','minutes','hours','days','weeks','year(s)'),accumulate((60,60,24,7,52),int.__mul__,initial=1)))
intervals = (('years',31536000),
             ('weeks',  604800),  # 60 * 60 * 24 * 7
             ('days',    86400),    # 60 * 60 * 24
             ('hours',    3600),    # 60 * 60
             ('minutes',    60),
             ('seconds',     1),)

def display_time(seconds, granularity=2):
    result = []
    for name, count in intervals:
        value = seconds // count
        if value:
            seconds -= value * count
            if value == 1:
                name = name.rstrip('s')
            result.append("{} {}".format(value, name))
    return ', '.join(result[:granularity])


def inbetween_points(a1, b1, a2, b2, r): # I'm proud of this. Here's a Desmos link: https://www.desmos.com/calculator/aauki3uiph
    dist_coords = [a1 - a2, b1 - b2]

    # normalized_dist_coords = [dist_coords[0] / dist_coords[0], dist_coords[1] / dist_coords[1]]
    # print(normalized_dist_coords)

    flip = ((math.pi * 2) * ((((a1 - a2) / abs(a1 - a2)) + 1) / 2))
    if flip == 0: 
        flip = math.pi * 2
    else: 
        flip = 0
        
    print(flip)
    theta = (90 - ((math.atan2(a2 - a1 , b2 - b1) + flip) * RAD2DEG)) / RAD2DEG

    position = [
        a1 + (r * math.cos(theta)),
        b1 + (r * math.sin(theta))
    ]

    return dist_coords, theta, position, flip

def calculate_acceleration_coordinates(object1, object2, speed):
    a1 = object1.position[0]
    b1 = object1.position[1]
    a2 = object2.position[0]
    b2 = object2.position[1]

    dist_coords, theta, position, flip = inbetween_points(a1, b1, a2, b2, speed)

    acceleration = [
        position[0] - a1,
        position[1] - b1
    ]

    return acceleration, dist_coords, theta, position, flip

# all masses are in kg
# all distances are in meters
# all accelerations are in meters/second
# all _____+_positions are in meters

open("latest.log", "w").close()
logfile = open("latest.log", "a") 

million = 1000000
billion = 1000000000
metersInKilometers = 1000

G = 6.67 * math.pow(10, -11)

RAD2DEG = 57.2958

def log(*message):
    finalMessage = ""
    for text in message:
        finalMessage += f"{text} "
    
    logfile.write(finalMessage + "\n")
    print(finalMessage)

def dist(p1, p2):
    return math.sqrt( ((p1[0]-p2[0])**2)+((p1[1]-p2[1])**2) )

def distSquared(p1, p2):
    return ((p1[0]-p2[0])**2)+((p1[1]-p2[1])**2)

def diff(n1, n2):
    return max(n1, n2) - min(n1, n2)

class Object:
    id = 0

    def __init__(self, name, position, radius, mass, color = (255, 255, 255), starting_velocity = [0, 0]):
        self.name = name
        self.position = list(position)
        self.radius = radius
        self.mass = mass
        self.color = color

        self.velocity = [0, 0]
        self.acceleration = [0, 0]
        self.id = Object.id
        Object.id = Object.id + 1
        self.trail = [(self.position, 0)]

        print(f"Created new objects ({self.name}) with ID {self.id}")
    
    def tick(self, fps, frame):
        self.velocity[0] = self.velocity[0] + self.acceleration[0]
        self.velocity[1] = self.velocity[1] + self.acceleration[1]
        # self.velocity[2] = self.velocity[2] + self.acceleration[2]

        self.acceleration = [0, 0]

        self.trail.append((self.position.copy(), frame + 1))
        # print(self.trail)

        self.position[0] = self.position[0] + ((self.velocity[0] * system.runtimeScale) / fps)
        self.position[1] = self.position[1] + ((self.velocity[1] * system.runtimeScale) / fps)

        log(f"Ticked {self.name}, velocity {self.velocity}")

class System():
    def __init__(self, name = "Unnamed", gridScale = 1000000, radiusScale = 500000, objects = [], runtimeScale = 2332800, sliders = False, offset_function = lambda: [0, 0]):
        self.name = name
        self.gridScale = gridScale
        self.radiusScale = radiusScale
        self.objects = objects
        self.runtimeScale = runtimeScale
        self.sliders = sliders
        self.offset_function = offset_function
    
    def get_object(self, name):
        for _object in self.objects:
            if _object.name == name:
                return _object

MoonEarth = System(
    name = "Moon-Earth",
    gridScale = 1000000,
    radiusScale = 500000,
    objects = [
        Object("Moon", (384467 * 1000, 0), 1737.4 * 1000, 7.34767309 * math.pow(10, 22), (125, 125, 125), starting_velocity = [
            0,
            (math.sqrt(((6.67 * math.pow(10, -11)) * MoonEarth.get_object("Earth").mass) / dist(MoonEarth.get_object("Earth").position, MoonEarth.get_object("Moon").position)))
        ]),
        Object("Earth", (0, 0), (6371 * 1000), 5.9722 * (10 ** 24), (0, 255, 0))
    ],
    runtimeScale = 2332800,
    sliders = False,
    offset_function = lambda: [MoonEarth.get_object("Earth").position[0], MoonEarth.get_object("Earth").position[1]]
)

SolarSystem = System(
    name = "Solar System",
    gridScale = 50000000,
    radiusScale = 50000000,
    objects = [
        Object("Sun", (0, 0), 696340 * 1000, 1.989 * (10 ** 30), (255, 0, 0)),
        Object("Mercury", (69892000000, 0), (2439.7 * metersInKilometers), 3.285 * (10 ** 23), (200, 200, 200)),
        Object("Venus", (107490000000, 0), (6051.8 * metersInKilometers), 4.867 * (10 ** 24), (255, 255, 255)),
        Object("Earth", (149600000000, 0), (6371 * metersInKilometers), 5.9722 * (10 ** 24), (0, 0, 255)),
        Object("Mars", (214650000000, 0), (3389.5 * metersInKilometers), 6.39 * (10 ** 23), (255, 100, 100)),
        Object("Jupiter", (741.56 * million * metersInKilometers, 0), (69911 * 1000), 1.898 * (10 ** 27), (200, 20, 200)),
        Object("Saturn", (1.4734 * billion * metersInKilometers, 0), (58232 * 1000), 5.683 * (10 ** 26), (234,214,184)),
        Object("Uranus", (4.474 * billion * metersInKilometers, 0), (24622 * 1000), 1.024 * (10 ** 26), (133,173,219))
    ],
    runtimeScale = 31536000 * 1000,
    sliders = True,
    offset_function = lambda: [SolarSystem.get_object("Sun").position[0], SolarSystem.get_object("Sun").position[1]]
)

system = MoonEarth




windowSize = (1920, 1080)

x_offset = 0
y_offset = 0

def to_pygame(coords):
    # x_offset = Sun.position[0]

    x_offset = system.offset_function()[0]
    y_offset = system.offset_function()[1]

    """Convert coordinates into pygame coordinates (center => top left)."""
    return ((coords[0] / system.gridScale) + (windowSize[0] / 2) - (x_offset / system.gridScale), (coords[1] / system.gridScale) + (windowSize[1] / 2) - (y_offset / system.gridScale))

pygame.init()

pygame.font.init() # you have to call this at the start, 
                   # if you want to use this module.
font = pygame.font.SysFont('Comic Sans MS', 30)

pygame.display.set_caption('Gravity Physics Simulation (59101)')
window_surface = pygame.display.set_mode((1920, 1080))

background = pygame.Surface((1920, 1080))
background.fill(pygame.Color('#000000'))

manager = pygame_gui.UIManager((1920, 1080))

linesToggles = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((0, 0), (100, 50)),
                                            text='Lines',
                                            manager=manager)
gravityToggle = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((0, 70), (100, 50)),
                                            text='Gravity',
                                            manager=manager)
velocityLines = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((0, 140), (100, 50)),
                                            text='Velocity',
                                            manager=manager)
distances = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((0, 210), (100, 50)),
                                            text='Distances',
                                            manager=manager)
trails = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((0, 280), (100, 50)),
                                            text='Trails',
                                            manager=manager)
if system.sliders:
    positionSlider = pygame_gui.elements.UIHorizontalSlider(relative_rect=pygame.Rect((120, 0), (200, 50)), manager=manager, start_value=0, value_range=(0, 4.474 * billion * metersInKilometers, 1))
    gridScaleSlider = pygame_gui.elements.UIHorizontalSlider(relative_rect=pygame.Rect((120, 70), (200, 50)), manager=manager, start_value=0, value_range=(10000, 50000000 * 25))
    radiusScaleSlider = pygame_gui.elements.UIHorizontalSlider(relative_rect=pygame.Rect((120, 140), (200, 50)), manager=manager, start_value=0, value_range=(10000, 50000000 * 5))

lines = False
gravityOn = False

clock = pygame.time.Clock()
is_running = True

frame = 0
framesSinceStarted = 0

velocityLinesShow = False
showDistances = False
showTrails = False

fps = 1

while is_running:
    fps = clock.get_fps()

    log("\n----- TICK -----")
    log(f"\n Frame {frame}")
    if (gravityOn):
        log(f"\n Frames Since Simulation Start: {framesSinceStarted}\n")

    # PHYSICS
    if gravityOn:
        for object1 in system.objects:
            for object2 in system.objects:
                if not(object1.id == object2.id):
                    log(f"Applying gravity to {object1.name} and {object2.name}")
                    Fgravity = G * ((object1.mass * object2.mass) / distSquared(object1.position, object2.position))
                    movementAmount = ((Fgravity / object1.mass) * system.runtimeScale) / fps

                    acceleration, dist_coords, theta, position, flip = calculate_acceleration_coordinates(object1, object2, movementAmount)
                    log("Distance Coords: ", dist_coords)
                    print(flip)
                    log("Theta: ", theta * 57.2958)
                    log("Acceleration: ", object1.acceleration)

                    object1.acceleration = acceleration
        
        for _object in system.objects:
            _object.tick(fps, framesSinceStarted)


    # DISPLAY
    
    time_delta = clock.tick(60)/1000.0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            is_running = False
            logfile.close()

        elif event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == linesToggles:
                lines ^= True
                if lines:
                    log("\n\n Now drawing lines. \n\n")
                else:
                    log("\n\n No longer drawing lines. \n\n")
            if event.ui_element == gravityToggle:
                # The simulation is started

                gravityOn = True
                log("\n\n Simulation Started. \n\n")
            if event.ui_element == velocityLines:
                velocityLinesShow ^= True
            if event.ui_element == distances:
                showDistances ^= True
            if event.ui_element == trails:
                showTrails ^= True
        
        elif event.type == pygame.KEYDOWN:
            if event.unicode == 'q':
                system.radiusScale -= 50000000 / 100
            if event.unicode == 'w':
                system.radiusScale += 50000000 / 100
            if event.unicode == 'e':
                system.gridScale -= 50000000 / 100
            if event.unicode == 'r':
                system.gridScale += 50000000 / 100
            if event.unicode == 't':
                system.gridScale -= 50000000 / 100
                system.radiusScale -= 50000000 / 100
            if event.unicode == 'y':
                system.gridScale += 50000000 / 100
                system.radiusScale += 50000000 / 100
            
            print(system.gridScale, system.radiusScale)
        
        # print(positionSlider.get_current_value())
        if system.sliders:
            x_offset = positionSlider.get_current_value()
            system.gridScale = gridScaleSlider.get_current_value()
            system.radiusScale = radiusScaleSlider.get_current_value()

        manager.process_events(event)

    manager.update(time_delta)

    window_surface.blit(background, (0, 0))

    # pygame.draw.circle(window_surface, (255, 0, 0), to_pygame(Sun.position), Sun.radius / gridScale)
    # pygame.draw.circle(window_surface, (0, 255, 0), to_pygame(Earth.position), Earth.radius / gridScale)
    for _object in system.objects:
        print(_object.name, _object.position)
        log(f"[Object Position] {_object.name} is now at {_object.position}")
        log(f"[Object Velocity] {_object.name} has a velocity of {_object.velocity}")

        pygame.draw.circle(window_surface, _object.color, to_pygame(_object.position), _object.radius / system.radiusScale)
        window_surface.blit(font.render(_object.name, False, (255, 255, 255)), to_pygame(_object.position))

        if velocityLinesShow:
            velocity_point = [_object.position[0] + _object.velocity[0] * 500000, _object.position[1] + _object.velocity[1] * 500000]
            pygame.draw.line(window_surface, _object.color, to_pygame(_object.position), to_pygame(velocity_point), 5)
        if lines:
            for _object2 in system.objects:
                pygame.draw.line(window_surface, (255, 255, 255), to_pygame(_object.position), to_pygame(_object2.position), 1)
        if showDistances:
            for _object2 in system.objects[:_object.id]:
                window_surface.blit(font.render(str(human_format(dist(_object.position, _object2.position))), False, (255, 255, 255)), to_pygame(inbetween_points(_object.position[0], _object.position[1], _object2.position[0], _object2.position[1], dist(_object.position, _object2.position) / 2)[2]))
        if showTrails:
            for idx, trailPoint in enumerate(_object.trail):
                if idx == 0 or idx == 1: continue
                if (frame - trailPoint[1]) >= fps * 15: continue
                pygame.draw.line(window_surface, _object.color, to_pygame(_object.trail[idx - 1][0]), to_pygame(trailPoint[0]), 5)
    
    window_surface.blit(font.render(display_time(system.runtimeScale), False, (255, 255, 255)), (windowSize[0] / 2, 0))

    # pygame.draw.line(window_surface, (255, 255, 255), to_pygame(Sun.position), to_pygame(Earth.position), 1)
    # pygame.draw.line(window_surface, (255, 255, 255), to_pygame(Earth.position), to_pygame(Moon.position), 1)

    manager.draw_ui(window_surface)

    pygame.display.update()

    log("----- END TICK -----\n")

    frame += 1

    if (gravityOn):
        framesSinceStarted += 1
