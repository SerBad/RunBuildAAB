生产aab格式的文件后，为了上传到google play还需要签名的，还有从生成aab到生成可以安装用的apk要花蛮多步骤的。
所以，这里用Python做下自动化简化下步骤

```python
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
        self.parser.add_argument("--alias", type=str, default="release", help="你自己jks的地址")

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
    # jarsigner 是来自于java的，确保自己本地的java环境正确即可
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

    rename = zip_apk_path + os.sep + time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime()) + '_' + apks_path.replace(
        '.apks', '.apk')
    os.renames(zip_apk_path + '/universal.apk', rename)
    print("output apk", rename)
    zFile.close()
```

其中``bundletool-all-1.9.1.jar``是来自于https://github.com/google/bundletool/releases，可以替换成你自己需要的jar

使用方法是：

```commandline
python build.py --path 'abb file path' --jks_path 'jks file path' --password 'your jks password' --alias 'your jks alias'
```
或者，在Android项目中的``build.gradle``，新建一个task，可以替换成自己需要的文件目录

```gradle
task buildAAB(type: Exec) {
    commandLine 'python3', '../build.py', '--path', "$buildDir/outputs/bundle/*.aab", '--jks_path', 'jks file path', '--password', 'your jks password', ' --alias', 'your jks alias'
}
```
然后使用下面的命令就可以上传了。

```
./gradlew buildAAB
```
本项目地址存放在，https://github.com/SerBad/RunBuildAAB.git

# git子模块
可以使用git的submodule方法来把其他git的子模块添加到项目里面去 使用方法是
```commandline
git submodule add https://github.com/SerBad/RunBuildAAB.git
```
