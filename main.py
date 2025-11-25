import argparse
import json
from tkinter import Image
import numpy as np
from objects import Scene, Camera, Vector, Material, Sphere, Plane, Light, Ray
from PIL import Image


class Raytracer:
    def __init__(self, scene: Scene, width: float, height: float):
        self.height = height
        self.width = width
        self.scene = scene

    def render(self, ray_per_pixel: float) -> np.ndarray:
        image = np.zeros((self.height, self.width, 3), dtype=np.float32)

        camera = self.scene.camera

        view_height = 2 * np.tan(np.radians(camera.fov / 2))
        wiew_width = view_height * camera.aspect_ratio

        for y in range(self.height):
            for x in range(self.width):
                color = Vector(0, 0, 0)

                for _ in range(ray_per_pixel):
                    u = (2 * (x + np.random.random()) / self.width -1) * wiew_width / 2
                    v = (1 - 2 * (y + np.random.random()) / self.height) * view_height / 2

                    direction = (
                        camera.forward +
                        camera.right * u +
                        camera.up * v
                    ).normalize()

                    ray = Ray(camera.position, direction)

                    color = color + self.trace_ray(ray)

                color = color / ray_per_pixel

                r = min(1, max(0, color.x)) ** (1/2.2)
                g = min(1, max(0, color.y)) ** (1/2.2)
                b = min(1, max(0, color.z)) ** (1/2.2)

                image[y][x] = [r, g, b]

        return image

    def trace_ray(self, ray: Ray, depth: int = 0, max_depth: int = 3) -> Vector:
        if depth > max_depth:
            return self.scene.background_color

        hit = self.scene.intersect(ray)

        if not hit:
            return self.scene.background_color

        color = Vector(0, 0, 0)

        ambient = hit.material.color * hit.material.ambient
        color = color + ambient

        for light in self.scene.lights:
            light_dir = (light.position - hit.point).normalize()

            shadow_ray = Ray(hit.point, light_dir)
            shadow_hit = self.scene.intersect(shadow_ray)

            if shadow_hit:
                light_distance = (light.position - hit.point).length()
                if shadow_hit.distance < light_distance:
                    continue

            diff = max(0, hit.normal.dot(light_dir))
            diffuse = hit.material.color * hit.material.diffuse * diff * light.intensity
            color = color + diffuse

            view_dir = (self.scene.camera.position - hit.point).normalize()
            reflect_dir = self.reflect(light_dir * -1, hit.normal)
            spec = max(0, view_dir.dot(reflect_dir)) ** hit.material.shininess
            specular = Vector(1, 1, 1) * hit.material.specular * spec * light.intensity
            color = color + specular

        if hit.material.reflectivity > 0 and depth < max_depth:
            reflect_dir = self.reflect(ray.direction, hit.normal)
            reflect_ray = Ray(hit.point, reflect_dir)
            reflect_color = self.trace_ray(reflect_ray, depth + 1, max_depth)
            color = color * (1 - hit.material.reflectivity) + reflect_color * hit.material.reflectivity

        return color

    def reflect(self, direction: Vector, normal: Vector) -> Vector:
        return direction - normal * (2 * direction.dot(normal))


def load_scene(path: str) -> Scene:
    with open(path, "r") as f:
        data = json.load(f)

    scene = Scene()

    camera = data["camera"]
    scene.camera = Camera(
        position=Vector(**camera["position"]),
        look_at=Vector(**camera["look_at"]),
        up=Vector(**camera["up"]),
        fov=camera["fov"],
        aspect_ratio=camera["aspect_ratio"]
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
        scene.background_color = Vector(**data['background_color'])

    return scene

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('--scene', type=str, help='Plik ze sceną w formacie JSON')
    parser.add_argument('--output', type=str, help='Ścieżka do pliku wyjściowego')
    parser.add_argument('--width', type=int, default=800, help='Szerokość')
    parser.add_argument('--height', type=int, default=600, help='Wysokość')
    parser.add_argument('--rays', type=int, default=4, help='Liczba promieni na piksel')

    args = parser.parse_args()

    scene = load_scene(args.scene)

    raytracer = Raytracer(scene, args.width, args.height)

    image = raytracer.render(ray_per_pixel=args.rays)

    image_unit8 = (image * 255).astype(np.uint8)
    Image.fromarray(image_unit8).save(args.output)


if __name__ == '__main__':
    main()

    #python main.py --scene scene.json --output obraz.png --width 800 --height 450 --rays 4