import os
import sys
project_directory = os.path.dirname(os.path.dirname(__file__))
sys.path.append(project_directory)
from backend.dbms import Database


database = Database('data/test.db')

database.admin_account_creation('admin1', 'password', 'admin1@gmail.com') # returns a hash of the password

with open("data/placeholder.jpg", "rb") as image:
    image_bytes = image.read()

database.insert_new_product_thumbnail(1, 'Image1', image_bytes) # returns the image name
database.insert_new_product_thumbnail(2, 'Image1', image_bytes) # returns the image name
database.insert_new_product_thumbnail(3, 'Image1', image_bytes) # returns the image name
database.insert_new_product_thumbnail(4, 'Image1', image_bytes) # returns the image name

database.insert_new_product_image(1, 'Image1', image_bytes) # returns the image name
database.insert_new_product_image(2, 'Image1', image_bytes) # returns the image name
database.insert_new_product_image(3, 'Image1', image_bytes) # returns the image name
database.insert_new_product_image(4, 'Image1', image_bytes) # returns the image name
database.insert_new_product_image(1, 'Image2', image_bytes) # returns the image name
database.insert_new_product_image(2, 'Image2', image_bytes) # returns the image name
database.insert_new_product_image(3, 'Image2', image_bytes) # returns the image name
database.insert_new_product_image(4, 'Image2', image_bytes) # returns the image name