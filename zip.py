import os
import zipfile

# zf = zipfile.ZipFile("myzipfile.zip", "w")
# for dirname, subdirs, files in os.walk("core/adis/created_dir/"):
#     zf.write(dirname)
#     for filename in files:
#         zf.write(os.path.join(dirname, filename))
# zf.close()


# for dirname, subdirs, files in os.walk("core/adis/created_dir"):
#     print subdirs, dirname
#     for filename in files:
#         print filename

import shutil
shutil.make_archive('cona', 'zip', 'core/adis/created_dir')