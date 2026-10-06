"""
FILE: backend/utils/metadata_tool.py
PURPOSE: OPTIONAL safe, LOCAL photo-metadata viewer/cleaner for images YOU choose.
Nothing is uploaded. It only shows metadata that is explicitly present, and never guesses location.
Usage:  python -m backend.utils.metadata_tool view photo.jpg
        python -m backend.utils.metadata_tool strip photo.jpg photo_clean.jpg
"""
import sys
from PIL import Image, ExifTags


def view_metadata(path):
    with Image.open(path) as img:
        exif = img.getexif()
        out = {ExifTags.TAGS.get(k, str(k)): str(v) for k, v in exif.items()}
        gps = exif.get_ifd(0x8825)            # GPS block, present only if the photo contains it
        if gps:
            out["GPS"] = {ExifTags.GPSTAGS.get(k, str(k)): str(v) for k, v in gps.items()}
        return out


def strip_metadata(src, dst):
    """Save a metadata-free COPY (original untouched)."""
    with Image.open(src) as img:
        clean = Image.new(img.mode, img.size)
        clean.putdata(list(img.getdata()))
        clean.save(dst)
    return dst


if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "view":
        md = view_metadata(sys.argv[2])
        print("\n".join(f"{k}: {v}" for k, v in md.items()) or "No metadata found.")
    elif len(sys.argv) == 4 and sys.argv[1] == "strip":
        print("Saved clean copy:", strip_metadata(sys.argv[2], sys.argv[3]))
    else:
        print(__doc__)
