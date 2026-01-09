import argparse
import json
import math
import numpy as np
from objects import Scene, Camera, Vector, Material, Sphere, Plane, Light, Ray
from PIL import Image

class Raytracer:
    def __init__(self, scene: Scene, width: int, height: int):
        self.height = height
        self.width = width
        self.scene = scene

    def render(self, ray_per_pixel: int, fovea_center: tuple[int, int]) -> np.ndarray:
        image = np.zeros((self.height, self.width, 3), dtype=np.float32)
        camera = self.scene.camera

        view_height = 2 * np.tan(np.radians(camera.fov / 2))
        view_width = view_height * camera.aspect_ratio

        # Pobieramy środek fovea w pikselach
        fx, fy = fovea_center
        
        # Parametry obszarów (w pikselach)
        # Promień pełnej ostrości (np. 20% szerokości ekranu)
        min_dim = min(self.width, self.height)
        radius_inner = min_dim * 0.20 
        # Promień, gdzie zaczyna się pełne rozmycie (np. 60% szerokości)
        radius_outer = min_dim * 0.60

        print(f"Rendering with Fovea Center at: X={fx}, Y={fy}")

        for y in range(self.height):
            # Prosty log postępu co 50 linii
            if y % 50 == 0:
                print(f"Progress: {y}/{self.height}")

            for x in range(self.width):
                color = Vector(0, 0, 0)
                
                # Obliczamy odległość aktualnego piksela od środka fovea
                dx = x - fx
                dy = y - fy
                dist = math.sqrt(dx*dx + dy*dy)
                
                # Obliczamy współczynnik ostrości (1.0 = ostry, 0.0 = rozmyty)
                if dist < radius_inner:
                    sharpness = 1.0
                elif dist > radius_outer:
                    sharpness = 0.0
                else:
                    # Liniowe przejście (lerp) między strefami
                    t = (dist - radius_inner) / (radius_outer - radius_inner)
                    sharpness = 1.0 - t

                # --- Optymalizacja i Efekt Foveated Rendering ---
                
                # 1. Redukcja liczby promieni (Variable Rate Shading)
                # W centrum pełna liczba promieni, na obrzeżach schodzimy do 1
                current_rays = max(1, int(ray_per_pixel * sharpness))
                if sharpness < 0.05:
                    current_rays = 1

                # 2. Efekt rozmycia (Stochastic Sampling/Jitter)
                # Im dalej od centrum, tym większy "rozrzut" promieni
                blur_factor = (1.0 - sharpness) * 4.0 # Siła rozmycia

                for _ in range(current_rays):
                    # Losowe przesunięcie wewnątrz piksela (antyaliasing) 
                    # powiększone o czynnik rozmycia na peryferiach
                    jitter_x = (np.random.random() - 0.5)
                    jitter_y = (np.random.random() - 0.5)
                    
                    # Modyfikujemy pozycję próbkowania
                    offset_x = x + 0.5 + jitter_x * (1 + blur_factor * 5.0)
                    offset_y = y + 0.5 + jitter_y * (1 + blur_factor * 5.0)

                    u = (2 * offset_x / self.width - 1) * view_width / 2
                    v = (1 - 2 * offset_y / self.height) * view_height / 2

                    direction = (
                        camera.forward +
                        camera.right * u +
                        camera.up * v
                    ).normalize()

                    ray = Ray(camera.position, direction)
                    color = color + self.trace_ray(ray)

                color = color / current_rays

                # Gamma correction (uproszczona)
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

        # Ambient
        ambient = hit.material.color * hit.material.ambient
        color = color + ambient

        for light in self.scene.lights:
            light_dir = (light.position - hit.point).normalize()

            # Cienie
            shadow_ray = Ray(hit.point, light_dir)
            shadow_hit = self.scene.intersect(shadow_ray)
            
            in_shadow = False
            if shadow_hit:
                light_distance = (light.position - hit.point).length()
                # Mały bias, aby uniknąć "shadow acne"
                if shadow_hit.distance < light_distance - 0.001:
                    in_shadow = True
            
            if in_shadow:
                continue

            # Diffuse
            diff = max(0, hit.normal.dot(light_dir))
            diffuse = hit.material.color * hit.material.diffuse * diff * light.intensity
            color = color + diffuse

            # Specular
            view_dir = (self.scene.camera.position - hit.point).normalize()
            reflect_dir = self.reflect(light_dir * -1, hit.normal)
            spec = max(0, view_dir.dot(reflect_dir)) ** hit.material.shininess
            specular = Vector(1, 1, 1) * hit.material.specular * spec * light.intensity
            color = color + specular

        # Odbicia (Reflections)
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
    camera_data = data["camera"]
    scene.camera = Camera(
        position=Vector(**camera_data["position"]),
        look_at=Vector(**camera_data["look_at"]),
        up=Vector(**camera_data["up"]),
        fov=camera_data["fov"],
        aspect_ratio=camera_data["aspect_ratio"]
    )

    for obj in data.get("objects", []):
        mat_data = obj['material']
        material = Material(
            color=Vector(**mat_data['color']),
            ambient=mat_data.get('ambient', 0.1),
            diffuse=mat_data.get('diffuse', 0.7),
            specular=mat_data.get('specular', 0.2),
            shininess=mat_data.get('shininess', 32.0),
            reflectivity=mat_data.get('reflectivity', 0.0)
        )

        if obj["type"] == "sphere":
            scene.objects.append(Sphere(
                center=Vector(**obj['center']),
                radius=obj['radius'],
                material=material
            ))
        elif obj["type"] == "plane":
            scene.objects.append(Plane(
                point=Vector(**obj['point']),
                normal=Vector(**obj['normal']),
                material=material
            ))

    for obj in data.get("lights", []):
        scene.lights.append(Light(
            position=Vector(**obj['position']),
            intensity=obj.get('intensity', 1)
        ))

    if 'background_color' in data:
        scene.background_color = Vector(**data['background_color'])

    return scene


def main(args_list=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--scene', type=str, required=True, help='Plik sceny JSON')
    parser.add_argument('--output', type=str, required=True, help='Plik wyjściowy')
    parser.add_argument('--width', type=int, default=800)
    parser.add_argument('--height', type=int, default=600)
    parser.add_argument('--rays', type=int, default=4)
    # Nowe argumenty: współrzędne pikselowe środka fovea
    parser.add_argument('--fovea_x', type=int, default=400, help='Współrzędna X środka ostrości')
    parser.add_argument('--fovea_y', type=int, default=300, help='Współrzędna Y środka ostrości')

    args = parser.parse_args(args_list)

    scene = load_scene(args.scene)
    raytracer = Raytracer(scene, args.width, args.height)

    # Przekazujemy współrzędne środka (X, Y) do renderera
    image = raytracer.render(
        ray_per_pixel=args.rays, 
        fovea_center=(args.fovea_x, args.fovea_y)
    )

    image_uint8 = (image * 255).astype(np.uint8)
    Image.fromarray(image_uint8).save(args.output)

if __name__ == '__main__':
    main()