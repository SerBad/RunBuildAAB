生产aab格式的文件后，为了上传到google play还需要签名的，还有从生成aab到生成可以安装用的apk要花蛮多步骤的。
所以，这里用Python做下自动化简化下步骤

其中``bundletool-all-1.13.1.jar``是来自于https://github.com/google/bundletool/releases 可以替换成你自己需要的jar
需要配置正确的apksigner环境，举例：/Users/zhou/Library/Android/sdk/build-tools/33.0.0/apksigner

使用方法是：

```commandline
python build_aab.py --path 'abb file path' --jks_path 'jks file path' --password 'your jks password' --alias 'your jks alias'
```
或者，在Android项目中的``build.gradle``，新建一个task，可以替换成自己需要的文件目录

```gradle
task buildAAB(type: Exec) {
    commandLine 'python3', '../build_aab.py', '--path', "$buildDir/outputs/bundle/*.aab", '--jks_path', 'jks file path', '--password', 'your jks password', ' --alias', 'your jks alias'
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
