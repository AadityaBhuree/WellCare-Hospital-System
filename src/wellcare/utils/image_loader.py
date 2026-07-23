"""Image loading utilities for CustomTkinter widgets."""

from pathlib import Path
import customtkinter as ctk
from PIL import Image
from src.wellcare.logger import logger


def load_ctk_image(
    image_path: Path,
    size: tuple[int, int],
) -> ctk.CTkImage | None:
    """Safely load PIL image as CTkImage or return None if failed/missing."""
    if not image_path.exists():
        logger.debug("Image file not found: %s", image_path)
        return None
    try:
        pil_img = Image.open(image_path)
        return ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=size)
    except Exception as exc:
        logger.warning("Failed to load image %s: %s", image_path, exc)
        return None
