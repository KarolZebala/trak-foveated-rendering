import argparse
import json
import math
import numpy as np


class Vector:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, scalar: float):
        return Vector(self.x * scalar, self.y * scalar, self.z * scalar)

    def __truediv__(self, scalar: float):
        return Vector(self.x / scalar, self.y / scalar, self.z / scalar)

    def dot(self, other):
        return self.x * other.x + self.y * other.y + self.z * other.z

    def cross(self, other):
        return Vector(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x
        )

    def length(self):
        return math.sqrt(self.x * self.x + self.y * self.y + self.z * self.z)

    def normalize(self):
        l = self.length()
        if l > 0:
            return self / l
        return self

    def to_array(self):
        return np.array([self.x, self.y, self.z])


class Camera:
    def __init__(self, position: Vector, look_at: Vector, up: Vector, fov: float, aspect_ratio: float):
        self.aspect_ratio = aspect_ratio
        self.fov = fov
        self.up = up
        self.position = position
        self.look_at = look_at

        self.forward = (look_at - position).normalize()

class Light:
    def __init__(self, position: Vector, intensity: float):
        self.position = position
        self.intensity = intensity

class Material:
    def __init__(self, color: Vector, ambient: float = 0.1, diffuse: float=0.8, specular: float=0.2, shininess: float=32, reflectivity: float=0.0):
        self.reflectivity = reflectivity
        self.shininess = shininess
        self.specular = specular
        self.diffuse = diffuse
        self.ambient = ambient
        self.color = color

class Sphere:
    def __init__(self, center: Vector, radius: float, material: Material):
        self.material = material
        self.radius = radius
        self.center = center

class Plane:
    def __init__(self, point: Vector, normal: Vector, material: Material):
        self.normal = normal
        self.point = point
        self.material = material

class Scene:
    def __init__(self):
        self.objects = []
        self.lights = []
        self.camera = None
        self.background_color = Vector(0.1, 0.1, 0.1)

def load_scene(path: str) -> Scene:
    with open(path, "r") as f:
        data = json.load(f)

    scene = Scene()

    camera = data["camera"]
    scene.camera = Camera(
        position=Vector(**data["position"]),
        look_at=Vector(**data["look_at"]),
        up=Vector(**data["up"]),
        fov=data["fov"],
        aspect_ratio=data["aspect_ratio"]
    )

    for obj in data.get("objects", []):
        if obj["type"] == "sphere":
            material = Material(
                color=Vector(**obj['material']['color']),
                ambient=obj['material'].get('ambient', 0.1),
                diffuse=obj['material'].get('diffuse', 0.7),
                specular=obj['material'].get('specular', 0.2),
                shininess=obj['material'].get('shininess', 32.0),
                reflectivity=obj['material'].get('reflectivity', 0.0)
            )

            sphere = Sphere(
                center=Vector(**obj['center']),
                radius=obj['radius'],
                material=material
            )

            scene.objects.append(sphere)
        elif obj["type"] == "plane":
            material = Material(
                color=Vector(**obj['material']['color']),
                ambient=obj['material'].get('ambient', 0.1),
                diffuse=obj['material'].get('diffuse', 0.7),
                specular=obj['material'].get('specular', 0.2),
                shininess=obj['material'].get('shininess', 32.0),
                reflectivity=obj['material'].get('reflectivity', 0.0)
            )

            plane = Plane(
                point=Vector(**obj['point']),
                normal=Vector(**obj['normal']),
                material=material
            )

            scene.objects.append(plane)

    for obj in data.get("lights", []):
        light = Light(
            position=Vector(**obj['position']),
            intensity=obj.get('intensity', 1)
        )

        scene.lights.append(light)

    if 'background_color' in data:
        background_color = Vector(**data['background_color'])

    return scene


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('--scene', type=str, help='Plik ze sceną w formacie JSON')
    parser.add_argument('--output', type=str, help='Ścieżka do pliku wyjściowego')
    parser.add_argument('width', default=800, help='Szerokość')
    parser.add_argument('height', default=600, help='Wysokość')
    parser.add_argumemt('--rays', default=10, help='Liczba promieni na piksel')

    args = parser.parse_args()

    scene = load_scene(args.scene)

if __name__ == '__main__':
    main()