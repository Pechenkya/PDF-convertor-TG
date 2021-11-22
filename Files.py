import os
from PIL import Image


class FileHandler:
    # Deleting file on path
    @staticmethod
    def delete_file(path):
        os.remove(path)

    # Deleting all files in folder
    @staticmethod
    def clear_folder(path):
        for file_name in os.listdir(path):
            os.remove(path + file_name)

    # Collecting all .jpg files from <base_path> to pdf and saving it into <result_path>
    @staticmethod
    def compile_pdf(base_path, result_path, name):
        size = len(os.listdir(base_path))

        images = [(Image.open(base_path + str(i) + '.jpg')).convert('RGB') for i in range(1, size + 1)]
        start = images.pop(0)
        start.save(result_path + name + '.pdf', save_all=True, append_images=images)
        return result_path + name + '.pdf'

    # Creating folders if needed
    @staticmethod
    def create_folder(folder_path):
        if not os.path.exists(folder_path):  # Creating folder if needed
            os.makedirs(folder_path)

    # Method to rename file
    @staticmethod
    def rename_file(folder, old_name, new_name):
        os.rename(folder + old_name, folder + new_name)

    # Returns amount of files in folder
    @staticmethod
    def folder_size(folder_path):
        return len(os.listdir(folder_path))

    # Saving image on device
    @staticmethod
    def save_image(image, path, name):
        open(path + name, 'wb').write(image.content)
