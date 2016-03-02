import PIL


def get_exif_data(f):
    exif_data = img._getexif()
    return exif_data

def get_field(exif,field):
  for (k,v) in exif.iteritems():
     if PIL.ExifTags.TAGS.get(k) == field:
        return v


exif = image._getexif()
print get_field(exif,'ExposureTime')


def open_image(image_path):
    img = PIL.Image.open(image_path)


