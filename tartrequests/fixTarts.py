import os


symbols = (u"абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ",
           u"abvgdeejzijklmnoprstufhzcss_y_euaABVGDEEJZIJKLMNOPRSTUFHZCSS_Y_EUA")
tr = dict([(ord(a), ord(b)) for (a, b) in zip(*symbols)])

symbols_reverse = (u"abvgdeejzijklmnoprstufhzcss_y_euaABVGDEEJZIJKLMNOPRSTUFHZCSS_Y_EUA",
                   u"абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ")
tr_reverse = dict([(ord(a), ord(b)) for (a, b) in zip(*symbols_reverse)])


def fix_code(code):
    return code.translate(tr).upper()

def fix_code_reverse(code):
    return code.translate(tr_reverse).upper()


target_folder = "G:/prj/ostrovaweb/tartImages"

for categoty_folder in os.listdir(target_folder):
    if os.path.isdir('/'.join((target_folder,categoty_folder,))):
        #directories.append((categoty_folder, categoty_folder),)

        for fl in os.listdir('/'.join((target_folder,categoty_folder,))):
            if fl.split('.')[-1] in ('png','jpg'):
                os.rename(os.path.join(target_folder,categoty_folder,fl), os.path.join(target_folder,categoty_folder,fix_code(fl).upper()))
