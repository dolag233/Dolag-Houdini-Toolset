# Doalg-Houdini-Toolset
Dolag的Houdini工具集，详细文档在[此处](http://www.vis.dolag.work/houdini-toolset/%E7%AE%80%E4%BB%8B.html)。

---
在使用前需要进行安装配置：
1. 在**HOUDINI_USER_PREF_DIR**文件夹下(一般来说在windows下就是C:\\Users\\用户名\\Documents\\houdini X.Y)，使用git bash运行如下命令
```bash
git clone https://github.com/dolag233/Doalg-Houdini-Toolset.git -b dev DolagPlugin
```
2. 将其中的**DolagPlugin.json**文件拷贝到**HOUDINI_USER_PREF_DIR/packages**文件夹下，若没有此文件夹则进行创建后再拷贝。
3. 某些节点使用了SideFX的Game Development Toolset中的部分节点，而Game Development Toolset或称Labs在Houdini的安装过程中是可选的，如果遇到某些节点无法使用，请尝试安装[Game Development Toolset](https://github.com/sideeffects/GameDevelopmentToolset)。
   
这样就完成了，dev分支下一般是最新进度，而master分支会在有比较大的更新后一并合并，因此会有滞后性。