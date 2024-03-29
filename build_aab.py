import os
import subprocess
import time
import zipfile
import shutil
import argparse

# 当前使用的bundletool的路径
# https://github.com/google/bundletool/releases
bundletool = './bundletool-all-1.13.1.jar'


class BuildOptions:
    def __init__(self):
        self.parser = argparse.ArgumentParser(description="自动打包文件")
        self.parser.add_argument("--path", type=str, required=True, help="aab的路径")
        self.parser.add_argument("--password", type=str, required=True, help="你自己的密码")
        self.parser.add_argument("--jks_path", type=str, required=True, help="你自己jks的地址")
        self.parser.add_argument("--alias", type=str, default="release", help="你自己alias")

    def parse(self):
        return self.parser.parse_args()


# 用来执行jar包的
def query_by_java_jar(jar_path, param):
    execute = "java -jar {} {}".format(jar_path, param)
    print(execute)
    output = subprocess.Popen(execute, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    res = output.stdout.readlines()
    return res


def get_min_sdk_version(file: str) -> str:
    res = query_by_java_jar(bundletool,
                            "dump manifest --bundle {} --xpath=/manifest/uses-sdk/@android:minSdkVersion".format(file))
    return res[0].decode('UTF-8').replace('\n', '')


def query_by_apksigner(input_path: str, output_path: str):
    # apksigner 是来自于sdk.dir
    execute = "apksigner sign --ks {} --ks-key-alias {} --min-sdk-version {} --out {} {}".format(jks_path,
                                                                                                 args.alias,
                                                                                                 get_min_sdk_version(
                                                                                                     input_path),
                                                                                                 output_path,
                                                                                                 input_path)
    print(execute)
    # 这个是为了自动输入密码
    echo = subprocess.Popen(['echo', password], stdout=subprocess.PIPE)
    output = subprocess.Popen(execute, shell=True, stdout=subprocess.PIPE, stdin=echo.stdout, stderr=subprocess.STDOUT)
    while output.poll() is None:
        print(output.stdout.readline())
    print("签名完成，开始校验==========》》》》》")
    execute = "jarsigner -verify {}".format(output_path)
    print(execute)
    output = subprocess.Popen(execute, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    while output.poll() is None:
        print(output.stdout.readline().decode('UTF-8'))
    print("校验完成==========》》》》》")


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

    apks_path = dir_name + os.sep + os.path.basename(aab_path).replace('.aab', '.apks')
    query_by_apksigner(aab_path, aab_path)
    query_by_java_jar(bundletool,
                      'build-apks --bundle=' + aab_path + ' --output=' + apks_path + ' --mode=universal --ks=' + jks_path + ' --ks-pass=pass:' + password + ' --ks-key-alias=' + args.alias + ' --key-pass=pass:' + password)
    zip_path = apks_path.replace('.apks', '.zip')
    os.renames(apks_path, zip_path)
    zFile = zipfile.ZipFile(zip_path, "r")
    zip_apk_path = dir_name + os.sep + 'apk'
    os.remove(zip_path)
    if os.path.exists(zip_apk_path):
        shutil.rmtree(zip_apk_path)
    for fileM in zFile.namelist():
        zFile.extract(fileM, zip_apk_path)

    rename = zip_apk_path + os.sep + time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime()) + '_' + os.path.basename(apks_path).replace(
        '.apks', '.apk')

    os.renames(zip_apk_path + os.sep + 'universal.apk', rename)
    print("output apk", rename)
    zFile.close()
