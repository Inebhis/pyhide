import mimetypes, os
from numpy import asarray
from flask import Blueprint, current_app, render_template, request, flash, send_from_directory
from werkzeug.utils import secure_filename
from PIL import Image

views = Blueprint('views', __name__)

@views.route('/')
def home():
    return render_template("home.html")

@views.route('/steg')
def steg():
    return render_template("steg.html")

@views.route('/hide', methods=['GET', 'POST'])
def input():
    if request.method == 'POST':
        text = request.form.get('text')
        image = request.files['image']

        if image.filename != '' and text != '':
            mimetype = mimetypes.guess_type(image.filename)[-0]
            extension = image.filename.rsplit(".", 1)[-1]

            if (
                extension == "jpeg"
                and mimetype == "image/jpeg"
                or extension == "png"
                and mimetype == "image/png"
            ):

                img_to_hide = Image.open(image)
                data_img_to_hide = asarray(img_to_hide).copy()
                final_result = ""
                for letter in text:
                    ascii_pos = ord(letter)
                    # byte to bin convert (+ rem "0b")
                    binary = bin(ascii_pos)[2:]
                    while len(binary) < 8:
                        # add 0 to have a byte (8 char)
                        binary = "0" + binary
                    final_result += binary

                # get length to avoid decode every pixels and write it on 2 bytes
                length = len(final_result)
                binary = bin(length)[2:]
                while len(binary) < 16:
                    # add 0 to have 2 bytes (16 char)
                    binary = "0" + binary
                res = binary + final_result

                round = 0
                y = 0
                # get pixel value
                for line in data_img_to_hide:
                    x = 0
                    for col in line:
                        rgb = 0
                        for color in col:
                            value = data_img_to_hide[y][x][rgb]
                            binary = bin(value)[2:]
                            binary_list = list(binary)
                            # remove last pixel byte
                            del binary_list[-1]
                            # replace with first res byte
                            binary_list.append(res[round])
                            # reconvert to decimal
                            decimal = int("".join(binary_list), 2)
                            data_img_to_hide[y][x][rgb] = decimal
                            round += 1
                            rgb += 1
                            if round >= len(res):
                                break
                        x += 1
                        if round >= len(res):
                            break
                    y += 1
                    if round >= len(res):
                        break

                filename = secure_filename(image.filename)
                image = Image.fromarray(data_img_to_hide)
                if os.path.exists(current_app.config['IMAGE_FOLDER'] + filename):
                    os.remove(current_app.config['IMAGE_FOLDER'] + filename)
                image.save(os.path.join(current_app.config['IMAGE_FOLDER'], filename))

                flash('Message hided')
                return render_template("hide.html", extentison = extension, image_name = filename)
            else:
                print(image.filename, extension, mimetype)
                flash('The image format is not accepted (only .jpeg & .png allowed)')
        else:
            flash('Empty input(s)')

    return render_template("hide.html")

@views.route('/upload/<filename>')
def display(filename):
    return send_from_directory("static/images", filename)

@views.route('/unhide', methods=['GET', 'POST'])
def output():

    if request.method == 'POST':
        image = request.files['image']

        if image.filename != '':
            mimetype = mimetypes.guess_type(image.filename)[-0]
            extension = image.filename.rsplit(".", 1)[-1]

            if (
                extension == "jpeg"
                and mimetype == "image/jpeg"
                or extension == "png"
                and mimetype == "image/png"
            ):

                img = Image.open(image)
                data_img = asarray(img).copy()

                msg = ""
                size = ""
                new_size = 1
                round = 0
                y = 0
                for line in data_img:
                    x = 0
                    for col in line:
                        rgb = 0
                        for color in col:
                            valeur = data_img[y][x][rgb]
                            binary = bin(valeur)[2:]
                            last = binary[- 1]
                            if round < 16:
                                size += last
                            if round == 16:
                                new_size = int(size, 2)
                            if round - 16 < new_size:
                                msg += last
                            if round - 16 >= new_size:
                                break
                            round += 1
                            rgb += 1
                        if round - 16 >= new_size:
                            break
                        x += 1
                    if round - 16 >= new_size:
                        break
                    y += 1

                bytes = []
                for i in range(len(msg) // 8):
                    bytes.append(msg[i * 8 : (i + 1) * 8])

                result = ""
                for byte in bytes:
                    index = int(byte, 2)
                    ascii_char = chr(index)
                    result += ascii_char
                    
                final = str(result)[2:]
                flash('Message unhided')
                return render_template("unhide.html", final = final)
            else:
                flash('The image format is not accepted (only .jpeg & .png allowed)')
        else:
            flash('Empty input')

    return render_template("unhide.html")