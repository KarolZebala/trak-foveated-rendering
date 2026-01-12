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


class Box:
    def __init__(self, min_point: Vector, max_point: Vector, material: Material):
        self.min_point = min_point
        self.max_point = max_point
        self.material = material

    def intersect(self, ray: Ray) -> Optional[Hit]:
        t_min = -math.inf
        t_max = math.inf

        for i in range(3):
            ray_origin_comp = [ray.origin.x, ray.origin.y, ray.origin.z][i]
            ray_dir_comp = [ray.direction.x, ray.direction.y, ray.direction.z][i]
            box_min_comp = [self.min_point.x, self.min_point.y, self.min_point.z][i]
            box_max_comp = [self.max_point.x, self.max_point.y, self.max_point.z][i]

            if abs(ray_dir_comp) < 1e-6:
                if ray_origin_comp < box_min_comp or ray_origin_comp > box_max_comp:
                    return None
            else:
                t1 = (box_min_comp - ray_origin_comp) / ray_dir_comp
                t2 = (box_max_comp - ray_origin_comp) / ray_dir_comp
                t_min = max(t_min, min(t1, t2))
                t_max = min(t_max, max(t1, t2))

        if t_max < t_min or t_max < 0:
            return None

        dist = t_min if t_min > 0 else t_max
        if dist < 0.001:
            return None

        point = Vector(
            ray.origin.x + dist * ray.direction.x,
            ray.origin.y + dist * ray.direction.y,
            ray.origin.z + dist * ray.direction.z
        )

        # Calculate normal
        eps = 1e-4
        normal = Vector(0, 0, 0)
        if abs(point.x - self.min_point.x) < eps: normal = Vector(-1, 0, 0)
        elif abs(point.x - self.max_point.x) < eps: normal = Vector(1, 0, 0)
        elif abs(point.y - self.min_point.y) < eps: normal = Vector(0, -1, 0)
        elif abs(point.y - self.max_point.y) < eps: normal = Vector(0, 1, 0)
        elif abs(point.z - self.min_point.z) < eps: normal = Vector(0, 0, -1)
        elif abs(point.z - self.max_point.z) < eps: normal = Vector(0, 0, 1)

        return Hit(dist, point, normal, self.material)


class Cone:
    def __init__(self, center: Vector, radius: float, height: float, material: Material):
        self.center = center
        self.radius = radius
        self.height = height
        self.material = material

    def intersect(self, ray: Ray) -> Optional[Hit]:
        ro = ray.origin - self.center
        rd = ray.direction

        k = self.radius / self.height
        k2 = k * k

        a = rd.x**2 + rd.z**2 - k2 * rd.y**2
        b = 2 * (ro.x * rd.x + ro.z * rd.z - k2 * ro.y * rd.y + k2 * self.height * rd.y)
        c = ro.x**2 + ro.z**2 - k2 * ro.y**2 - k2 * self.height**2

        discriminant = b * b - 4 * a * c
        if discriminant < 0:
            return None

        dist = (-b - math.sqrt(discriminant)) / (2 * a)
        if dist < 0.001:
            dist = (-b + math.sqrt(discriminant)) / (2 * a)
            if dist < 0.001:
                return None

        point = Vector(
            ray.origin.x + dist * ray.direction.x,
            ray.origin.y + dist * ray.direction.y,
            ray.origin.z + dist * ray.direction.z
        )

        normal = Vector(
            point.x - self.center.x,
            point.y - self.center.y,
            point.z - self.center.z
        ).normalize()

        return Hit(dist, point, normal, self.material)
        
        k = self.radius / self.height
        k2 = k * k
        
        a = rd.x**2 + rd.z**2 - k2 * rd.y**2
        b = 2 * (ro.x * rd.x + ro.z * rd.z - k2 * ro.y * rd.y + k2 * self.height * rd.y)
        
        c = ro.x**2 + ro.z**2 - k2 * ro.y**2 + 2 * k2 * self.height * ro.y - k2 * self.height**2
        
        discriminant = b*b - 4*a*c
        
        hits = []

        if discriminant >= 0:
            sqrt_d = math.sqrt(discriminant)
            vals = []
            if abs(a) > 1e-6:
                vals.append((-b - sqrt_d) / (2 * a))
                vals.append((-b + sqrt_d) / (2 * a))
            
            for t in vals:
                if t > 0.001:
                    y = ro.y + t * rd.y
                    if 0 <= y <= self.height:
                         hits.append(t)

        if abs(rd.y) > 1e-6:
            t_base = -ro.y / rd.y
            if t_base > 0.001:
                p_base = ro + rd * t_base
                dist2 = p_base.x**2 + p_base.z**2
                if dist2 <= self.radius**2:
                    hits.append(t_base)

        if not hits:
            return None

        closest_t = min(hits)
        
        point = ray.origin + ray.direction * closest_t
        local_point = point - self.center

        if abs(local_point.y) < 0.001:
             normal = Vector(0, -1, 0)
        else:
             normal = Vector(local_point.x, k2 * (self.height - local_point.y), local_point.z).normalize()

        return Hit(closest_t, point, normal, self.material)


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

