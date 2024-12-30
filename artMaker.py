import pygame
import sys
from typing import List, Tuple
import random


class PixelArtMaker:
    def __init__(self):
        pygame.init()
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.font = pygame.font.SysFont("Arial", 12)

    def get_dimensions(self) -> Tuple[int, int]:
        while True:
            try:
                rows = int(input("Enter number of rows: "))
                cols = int(input("Enter number of columns: "))
                if rows > 0 and cols > 0:
                    return rows, cols
                print("Please enter positive numbers.")
            except ValueError:
                print("Please enter valid numbers.")

    def get_gradient_info(self) -> Tuple[str, List[Tuple[int, int, int]], int]:
        print("\nGradient types available:")
        print("1. Horizontal")
        print("2. Vertical")
        print("3. Diagonal")
        print("4. Radial")  # Add radial gradient option

        while True:
            gradient_type = input("Select gradient type (1-4): ")
            if gradient_type in ["1", "2", "3", "4"]:
                break
            print("Please select a valid option.")

        colors = []
        num_colors = int(input("How many colors do you want in your gradient? (2-5): "))

        print("\nEnter RGB values for each color (0-255 for each component)")
        for i in range(num_colors):
            while True:
                try:
                    r = int(input(f"Color {i+1} - Red: "))
                    g = int(input(f"Color {i+1} - Green: "))
                    b = int(input(f"Color {i+1} - Blue: "))
                    if 0 <= r <= 255 and 0 <= g <= 255 and 0 <= b <= 255:
                        colors.append((r, g, b))
                        break
                    print("Please enter values between 0 and 255.")
                except ValueError:
                    print("Please enter valid numbers.")

        while True:
            try:
                max_colors = int(
                    input("Enter the maximum number of colors to generate (e.g., 10): ")
                )
                if max_colors > 0:
                    return gradient_type, colors, max_colors
                print("Please enter a positive number.")
            except ValueError:
                print("Please enter a valid number.")

    def interpolate_color(
        self, color1: Tuple[int, int, int], color2: Tuple[int, int, int], factor: float
    ) -> Tuple[int, int, int]:
        return tuple(
            int(color1[i] + (color2[i] - color1[i]) * factor) for i in range(3)
        )

    def dither_color(
        self, color: Tuple[int, int, int], x: int, y: int
    ) -> Tuple[int, int, int]:
        dither_matrix = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]
        threshold_map = [
            [dither_matrix[i % 4][j % 4] for j in range(4)] for i in range(4)
        ]
        threshold = threshold_map[y % 4][x % 4]
        return tuple(min(255, max(0, c + threshold - 8)) for c in color)

    def map_to_limited_palette(
        self, color: Tuple[int, int, int], palette: List[Tuple[int, int, int]]
    ) -> Tuple[int, int, int]:
        return min(palette, key=lambda p: sum((color[i] - p[i]) ** 2 for i in range(3)))

    def get_color_for_position(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        gradient_type: str,
        colors: List[Tuple[int, int, int]],
    ) -> Tuple[int, int, int]:
        if gradient_type == "1":  # Horizontal
            factor = x / (width - 1)
        elif gradient_type == "2":  # Vertical
            factor = y / (height - 1)
        elif gradient_type == "3":  # Diagonal
            factor = (x + y) / (width + height - 2)
        else:  # Radial
            center_x, center_y = width / 2, height / 2
            max_distance = ((center_x) ** 2 + (center_y) ** 2) ** 0.5
            distance = ((x - center_x) ** 2 + (y - center_y) ** 2) ** 0.5
            factor = distance / max_distance

        segment_size = 1.0 / (len(colors) - 1)
        segment_index = int(factor / segment_size)
        if segment_index >= len(colors) - 1:
            return colors[-1]

        segment_factor = (factor - segment_index * segment_size) / segment_size
        color = self.interpolate_color(
            colors[segment_index], colors[segment_index + 1], segment_factor
        )
        return self.dither_color(color, x, y)

    def save_image(self, screen, filename):
        """Save the current screen as a PNG image."""
        pygame.image.save(screen, filename)

    def draw_pixel_art(
        self,
        screen,
        grid_colors,
        rows,
        cols,
        cell_size,
        draw_grid=True,
        draw_numbers=True,
    ):
        """Draw the pixel art on the screen."""
        for row in range(rows):
            for col in range(cols):
                x = col * cell_size
                y = row * cell_size

                color = grid_colors[row][col]

                # Draw the colored rectangle
                pygame.draw.rect(screen, color, (x, y, cell_size, cell_size))

                if draw_grid:
                    # Draw the border
                    pygame.draw.rect(
                        screen, self.BLACK, (x, y, cell_size, cell_size), 1
                    )

                if draw_numbers:
                    # Draw the number
                    color_key = tuple(color)
                    color_number = self.unique_colors[color_key]
                    text = self.font.render(str(color_number), True, self.BLACK)
                    text_rect = text.get_rect(
                        center=(x + cell_size / 2, y + cell_size / 2)
                    )
                    screen.blit(text, text_rect)

    def run(self):
        rows, cols = self.get_dimensions()
        gradient_type, colors, max_colors = self.get_gradient_info()

        # Calculate cell size and window dimensions
        CELL_SIZE = 60
        WINDOW_WIDTH = cols * CELL_SIZE
        WINDOW_HEIGHT = rows * CELL_SIZE

        # Generate a limited palette
        palette = [
            self.interpolate_color(colors[i], colors[i + 1], j / max_colors)
            for i in range(len(colors) - 1)
            for j in range(max_colors)
        ]

        # Initialize the display
        screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Pixel Art Maker")

        self.unique_colors = {}
        color_counter = 1

        # Create a grid to store colors
        grid_colors = [[None for _ in range(cols)] for _ in range(rows)]

        # Main game loop
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False

            screen.fill(self.WHITE)

            # Draw the grid and fill cells with colors
            for row in range(rows):
                for col in range(cols):
                    original_color = self.get_color_for_position(
                        col, row, cols, rows, gradient_type, colors
                    )
                    limited_color = self.map_to_limited_palette(original_color, palette)

                    # Assign unique number to each color
                    color_key = tuple(limited_color)
                    if color_key not in self.unique_colors:
                        self.unique_colors[color_key] = color_counter
                        color_counter += 1

                    grid_colors[row][col] = limited_color  # Store the color in the grid

            # Draw the pixel art with grid lines and numbers
            self.draw_pixel_art(
                screen,
                grid_colors,
                rows,
                cols,
                CELL_SIZE,
                draw_grid=True,
                draw_numbers=True,
            )
            pygame.display.flip()

        # Save the image with grid lines and numbers
        self.save_image(screen, "pixel_art_with_grid.png")

        # Draw the pixel art without grid lines and numbers
        screen.fill(self.WHITE)
        self.draw_pixel_art(
            screen,
            grid_colors,
            rows,
            cols,
            CELL_SIZE,
            draw_grid=False,
            draw_numbers=False,
        )
        pygame.display.flip()

        # Save the image without grid lines and numbers
        self.save_image(screen, "pixel_art.png")

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    art_maker = PixelArtMaker()
    art_maker.run()
