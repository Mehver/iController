OLD_VERSION = input('Give the old version number > ')
NEW_VERSION = input('Give the new version number > ')


def UpdateVersionNumber(filename, encoder, lines_list, old_version, new_version):
    filename = "./../" + filename
    with open(filename, 'r', encoding=encoder) as file:
        lines = file.readlines()

    with open(filename, 'w', encoding=encoder) as file:
        for i, line in enumerate(lines, 1):
            if i in lines_list:
                lines[i - 1] = line.replace(old_version, new_version)
        file.writelines(lines)


UpdateVersionNumber('README.md', "utf-8", [3, 6], OLD_VERSION, NEW_VERSION)
UpdateVersionNumber('#README/README-cn.md', "utf-8", [3, 6], OLD_VERSION, NEW_VERSION)
UpdateVersionNumber('iController.py', "utf-8", [16], OLD_VERSION, NEW_VERSION)
