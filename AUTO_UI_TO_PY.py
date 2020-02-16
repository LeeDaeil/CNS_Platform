import os
import glob

get_py_file = glob.glob('./Interface/*.ui')
get_cns_interface_py = [f for f in get_py_file if 'CNS' in f == f]
print(get_cns_interface_py)

# Make ui -> Py
# pyside2-uic test.ui > test.py
for file_name in get_cns_interface_py:
    target_file_name = file_name.split('.')[1]
    print(f'pyside2-uic ./{target_file_name}.ui > ./{target_file_name}.py')
    os.system(f'pyside2-uic ./{target_file_name}.ui > ./{target_file_name}.py')

# Make qrc -> py
print(f'pyside2-rcc ./Interface/resource/CNS_resource.qrc > ./CNS_resource_rc.py')
os.system(f'pyside2-rcc ./Interface/resource/CNS_resource.qrc > ./CNS_resource_rc.py')