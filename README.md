# Doalg-Houdini-Toolset
Dolag的Houdini工具集

---

在使用前需要进行安装配置：

1. 将此文件夹。即“Dolag-Houdini-Toolset”文件夹放置于用户文档目录下，例如如果当前用户名叫“Dolag”则放置此文件夹到“C:\Users\Dolag\Documents”下。可以将此文件夹重命名为“DolagHoudiniToolset”。

2. 将文档目录下的houdiniX.Y(X和Y为houdini版本号)目录中的houdini.env文件的HOUDINI_PATH行末尾添加文件夹路径(例如“C:\Users\Dolag\Documents\DolagHoudiniToolSet”)，并用分号“;”与前面的路径分开。

   例如，一个合适的HOUDINI_PATH行为“HOUDINI_PATH = C:\Users\Dolag\Documents\GameDevelopmentToolset;C:\Users\Dolag\Documents\DolagHoudiniToolset;&;”。

3. vex自定义文件夹的路径为此工具集文件夹下的vex/custom，例如“C:\Users\Dolag\Documents\DolagHoudiniToolset\vex\custom”。
   然后在2中的houdini.env中以相同的方式添加自定义vex文件夹路径到HOUDINI_VEX_PATH。

   若不存在HOUDINI_VEX_PATH则新建HOUDINI_VEX_PATH行，并在其后输入“ = ”和vex文件夹路径。例如“HOUDINI_VEX_PATH = C:\Users\Dolag\Documents\DolagHoudiniToolSet\vex\custom;&;”。
   
---

注意：当前分支为主分支，而开发分支dev及其子分支为进行开发的分支。目前dev分支尚未合并到主分支，因此新功能目前都集中在dev分支和其子分支下。
