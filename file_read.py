import json

def ls_command(current_directory):
    ff = ""
    for node in current_directory['subnodes']:
        ff = ff+str(node['name'])+"  "
    return ff


def find_directory_recursive(current_directory, path):
    path_parts = path.strip('/').split('/')
    
    for part in path_parts:
        current_directory = find_directory(current_directory, part)
        if not current_directory:
            ff = f"Directory '{part}' not found"
            return ff
    return current_directory

def find_directory(current_directory, dir_name):
    for node in current_directory['subnodes']:
        if node['name'] == dir_name and node['type'] == 'directory':
            return node
    return None

def change_directory(pwd):
    with open('dir.json', 'r') as file:
        file_structure = json.load(file)

    print("fist="+pwd)
    pwd_dir = find_directory_recursive(file_structure, pwd)
    print(pwd_dir)
    #print(type(pwd_dir))
    
    return pwd_dir


def Dir_Handler(pwd):
    with open('dir.json', 'r') as file:
        file_structure = json.load(file)
    
    if pwd == "" or pwd == "/var/www/html":
        return ls_command(file_structure)
    else:
        #pwd = pwd.replace("/var/www/html/","")
        dfd = pwd.split("/")
        pwd = dfd[-1]
        pwd_dir = find_directory_recursive(file_structure, pwd)
        
        if pwd_dir:
            print('-----------------------------')
            pwd_dir['root'] = file_structure['root'] + '/'+pwd
            print(pwd_dir['root'])
            return ls_command(pwd_dir)
        else:
            print(f"Directory '{pwd}' not found")
