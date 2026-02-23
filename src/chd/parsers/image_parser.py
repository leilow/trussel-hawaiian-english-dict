"""Parse entry images — <img class="hwimg"> elements."""

from __future__ import annotations

from bs4 import Tag

from chd.models import ImageInfo


def extract_images(p_tag: Tag) -> list[ImageInfo]:
    """Extract all <img class="hwimg"> from an entry <p> tag."""
    images = []
    for img in p_tag.find_all("img", class_="hwimg"):
        info = ImageInfo(
            thumbnail_url=img.get("src", ""),
            alt_text=img.get("alt", ""),
            height=int(img.get("height", 0) or 0),
        )

        # The img is usually wrapped in an <a> linking to the full image page
        parent_a = img.find_parent("a")
        if parent_a:
            href = parent_a.get("href", "")
            if href:
                info.full_image_url = href

        images.append(info)

    return images
