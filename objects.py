import math
import numpy as np
from typing import Optional


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
        self.right = self.forward.cross(up).normalize()
        self.up = self.right.cross(self.forward)

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

class Hit:
    def __init__(self, distance: float, point: Vector, normal: Vector, material: Material):
        self.material = material
        self.normal = normal
        self.point = point
        self.distance = distance

class Ray:
    def __init__(self, origin: Vector, direction: Vector):
        self.direction = direction
        self.origin = origin


class Sphere:
    def __init__(self, center: Vector, radius: float, material: Material):
        self.material = material
        self.radius = radius
        self.center = center

    def intersect(self, ray: Ray) -> Optional[Hit]:
        oc = ray.origin - self.center
        a = ray.direction.dot(ray.direction)
        b = 2 * oc.dot(ray.direction)
        c = oc.dot(oc) - self.radius * self.radius
        discriminant = b * b - 4 * a * c

        if discriminant < 0:
            return None

        dist = (-b - np.sqrt(discriminant)) / (2 * a)

        if dist < 0.001:
            dist = (-b + np.sqrt(discriminant)) / (2 * a)
            if dist < 0.001:
                return None

        point = Vector(
            ray.origin.x + dist * ray.direction.x,
            ray.origin.y + dist * ray.direction.y,
            ray.origin.z + dist * ray.direction.z
        )

        normal = (point - self.center).normalize()

        return Hit(dist, point,  normal, self.material)


class Plane:
    def __init__(self, point: Vector, normal: Vector, material: Material):
        self.normal = normal
        self.point = point
        self.material = material

    def intersect(self, ray: Ray) -> Optional[Hit]:
        denon = self.normal.dot(ray.direction)

        if abs(denon) > 0.0001:
            dist = (self.point - ray.origin).dot(self.normal) / denon
            if dist >= 0.001:
                point = Vector(
                    ray.origin.x + dist * ray.direction.x,
                    ray.origin.y + dist * ray.direction.y,
                    ray.origin.z + dist * ray.direction.z
                )

                return Hit(dist, point, self.normal, self.material)

        return None


class Scene:
    def __init__(self):
        self.objects = []
        self.lights = []
        self.camera = None
        self.background_color = Vector(0.1, 0.1, 0.1)

    def intersect(self, ray: Ray) -> Optional[Hit]:
        closest_hit = None
        min_distance = math.inf

        for obj in self.objects:
            hit = obj.intersect(ray)
            if hit and hit.distance < min_distance:
                min_distance = hit.distance
                closest_hit = hit

        return closest_hit

