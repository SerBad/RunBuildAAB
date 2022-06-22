import os
import subprocess
import time
import zipfile
import shutil
import argparse


class BuildOptions:
    def __init__(self):
        self.parser = argparse.ArgumentParser(description="自动打包文件")
        self.parser.add_argument("--path", type=str, required=True, help="aab的路径")
        self.parser.add_argument("--password", type=str, required=True, help="你自己的密码")
        self.parser.add_argument("--jks_path", type=str, required=True, help="你自己jks的地址")

    def parse(self):
        return self.parser.parse_args()


# 用来执行jar包的
def query_by_java_jar(jar_path, param):
    execute = "java -jar {} {}".format(jar_path, param)
    print(execute)
    output = subprocess.Popen(execute, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    res = output.stdout.readlines()
    return res


# 用来执行jarsigner命令的
def query_by_jarsigner(param):
    execute = "jarsigner {}".format(param)
    print(execute)
    # 这个是为了自动输入密码
    echo = subprocess.Popen(['echo', password], stdout=subprocess.PIPE)
    output = subprocess.Popen(execute, shell=True, stdout=subprocess.PIPE, stdin=echo.stdout, stderr=subprocess.STDOUT)
    res = output.stdout.readlines()
    return res


if __name__ == '__main__':
    parser = BuildOptions()
    args = parser.parse()
    # 替换自己的jks地址
    jks_path = args.jks_path
    # 替换自己的密码
    password = args.password

    aab_path = args.path
    print('aab_path', aab_path)
    dir_name = os.path.dirname(aab_path)

    apks_path = os.path.basename(aab_path).replace('.aab', '.apks')

    query_by_jarsigner(
        '-verbose -sigalg SHA256withRSA -digestalg SHA-256 -keystore ' + jks_path + ' ' + aab_path + ' release')
    query_by_java_jar('./bundletool-all-1.9.1.jar',
                      'build-apks --bundle=' + aab_path + ' --output=' + apks_path + ' --mode=universal --ks=' + jks_path + ' --ks-pass=pass:' + password + ' --ks-key-alias=release --key-pass=pass:' + password)
    zip_path = apks_path.replace('.apks', '.zip')
    os.renames(apks_path, zip_path)
    zFile = zipfile.ZipFile(zip_path, "r")
    zip_apk_path = dir_name + os.sep + 'apk'
    os.remove(zip_path)
    if os.path.exists(zip_apk_path):
        shutil.rmtree(zip_apk_path)
    for fileM in zFile.namelist():
        zFile.extract(fileM, zip_apk_path)

    os.renames(zip_apk_path + '/universal.apk',
               zip_apk_path + os.sep + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + '_' + apks_path.replace(
                   '.apks', '.apk'))
    zFile.close()
