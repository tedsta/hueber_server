def success_page(image_path, driver_name, driver_phone):
    """Takes an image path, returns HTML page displaying that image"""
    file = open('site/success.html', 'r').read()
    return file.format(image_path, driver_name, driver_phone)
