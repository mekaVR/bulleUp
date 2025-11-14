from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.core.files.base import ContentFile
from PIL import Image, ImageOps
from io import BytesIO
import os
import logging

from .models import User

logger = logging.getLogger(__name__)


@receiver(pre_save, sender=User)
def optimize_avatar(sender, instance, **kwargs):
    if not instance.avatar:
        return

    try:
        old_instance = User.objects.get(pk=instance.pk)
        if old_instance.avatar == instance.avatar:
            return
    except User.DoesNotExist:
        pass

    try:
        instance.avatar.file
    except (ValueError, IOError):
        return

    try:
        optimized_avatar = _optimize_image(instance.avatar)

        if optimized_avatar:
            instance.avatar = optimized_avatar

    except Exception as e:
        logger.error(f"Erreur lors de l'optimisation de l'avatar pour {instance.username}: {e}")


def _optimize_image(image_field):
    img = Image.open(image_field)
    img = ImageOps.exif_transpose(img)

    if img.mode in ('RGBA', 'LA', 'P'):
        background = Image.new('RGB', img.size, (255, 255, 255))

        if img.mode == 'P':
            img = img.convert('RGBA')

        if img.mode == 'RGBA':
            background.paste(img, mask=img.split()[-1])
        else:
            background.paste(img)

        img = background

    max_size = (500, 500)
    img.thumbnail(max_size, Image.Resampling.LANCZOS)

    output = BytesIO()
    img.save(
        output,
        format='JPEG',
        quality=85,
        optimize=True,
        progressive=True
    )
    output.seek(0)

    original_name = os.path.splitext(image_field.name)[0]
    new_filename = f"{original_name}.jpg"

    return ContentFile(output.read(), name=new_filename)


def _make_square_avatar(img, size=500):
    width, height = img.size

    min_dimension = min(width, height)

    left = (width - min_dimension) / 2
    top = (height - min_dimension) / 2
    right = (width + min_dimension) / 2
    bottom = (height + min_dimension) / 2

    img = img.crop((left, top, right, bottom))

    img = img.resize((size, size), Image.Resampling.LANCZOS)

    return img
