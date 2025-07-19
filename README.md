# Dolag-Houdini-Toolset

[![中文](https://img.shields.io/badge/lang-中文-blue.svg)](#简介) [![English](https://img.shields.io/badge/lang-English-red.svg)](#introduction)

## 简介

一款功能强大的Houdini工具集，为您带来海量实用SOP节点、无缝的菜单功能扩展以及高效的快捷命令。

[功能概览](#功能概览) | [效果演示](#效果演示) | [安装方法](#安装方法) | [使用文档](#使用文档)

---

## 功能概览

- **100+ 实用HDA**：提供海量HDA，涵盖建模、虚幻引擎、体积、高度场等多个模块。所有节点均可在Tab菜单的 `Dolag` 分类下找到。

<p align="center">
  <img src="img/节点一览.png" alt="节点一览" width="80%">
</p>

- **快捷控制台**：在网络编辑器（Network Editor）面板中，按下`Ctrl+空格`即可唤出一个快速搜索列表，允许用户通过关键词搜索并执行指令。

- **增强菜单功能**：
    1. **扩充右键菜单**：为节点和参数的右键菜单添加了丰富的“Dolag”分类功能。例如，右键点击按钮类型的参数，会显示“Dolag > Copy Button”等扩展选项。部分功能包括：
        - 一键整理节点布局。
        - 保存与加载节点参数。
        - 一键设置Ramp参数的插值方式，并支持细分、随机、平滑等操作。
        - 复制与粘贴节点样式。
        - 递归解锁当前节点内的所有子节点。

    2. **主菜单功能**：在Houdini主菜单中添加了实用功能，如增量保存、为内置Python自动**安装pip**及通过pip**安装模块**等。

- **节点编辑器增强**：

    **移动和复制节点连接线**：按住`Ctrl+Alt`或`Shift+Ctrl`并拖动节点连接线，可以移动或复制它们，体验类似于在Unreal Engine中按住`Ctrl`键操作连接线。

## 效果演示

**HDA效果展示**
<p align="center">
  <img src="img/节点布局整理.png" alt="节点布局整理" width="60%">
</p>

**连接交换器**
<p align="center">
  <img src="img/连接交换器.gif" alt="连接交换器" width="40%">
</p>

**快捷控制台**
<p align="center">
  <img src="img/快捷控制台.gif" alt="快捷控制台" width="30%">
</p>

## 安装方法

在使用前，请按照以下步骤进行安装配置：

0. **安装SideFX Labs**：许多节点依赖于Labs插件，请确保已安装。本工具集未内嵌相关节点。

1. 在 `C:\Users\你的用户名\Documents\houdiniX.Y` 目录下，使用Git克隆本仓库至 `DolagPlugin` 文件夹：

   ```bash
   git clone https://github.com/dolag233/Dolag-Houdini-Toolset.git DolagPlugin
   ```

2. 将 `DolagPlugin` 文件夹下的 `DolagPlugin.json` 文件复制到 `C:\Users\你的用户名\Documents\houdiniX.Y\packages` 目录下。如果 `packages` 目录不存在，请先创建它。

## 使用文档

详细使用方法请参见[在线文档](https://www.vis.dolag.work/houdini-toolset/%E7%AE%80%E4%BB%8B.html)。

---
<br>

## Introduction

A powerful Houdini toolset that brings you a massive number of practical SOP nodes, seamless menu function extensions, and efficient shortcut commands.

[Features](#features) | [Demos](#demos) | [Installation](#installation) | [Usage](#usage)

---

## <a name="features"></a>Features

- **100+ Practical HDAs**: Provides a massive collection of HDAs covering modules like modeling, Unreal Engine, volumes, and height fields. All nodes can be found under the `Dolag` category in the Tab menu.

<p align="center">
  <img src="img/节点一览.png" alt="Node Overview" width="80%">
</p>

- **Quick Console**: In the Network Editor pane, press `Ctrl+Space` to bring up a quick search list, allowing users to find and execute commands via keywords.

- **Enhanced Menu Functions**:
    1. **Extended Right-Click Menu**: Adds a "Dolag" category to the right-click menus for nodes and parameters. For example, right-clicking a button-type parameter will show extended options like "Dolag > Copy Button". Some features include:
        - One-click node layout arrangement.
        - Save and load node parameters.
        - One-click setting of interpolation modes for Ramp parameters, with support for subdivision, randomization, and smoothing.
        - Copy and paste node styles.
        - Recursively unlock all child nodes within the current node.

    2. **Main Menu Functions**: Adds useful features to Houdini's main menu, such as incremental saving, and tools to automatically **install pip** for the built-in Python and **install modules** via pip.

- **Node Editor Enhancements**:

    **Move and Copy Node Wires**: Hold `Ctrl+Alt` or `Shift+Ctrl` while dragging node wires to move or copy them, similar to the experience of holding the `Ctrl` key in Unreal Engine to manage connections.

## <a name="demos"></a>Demos

**HDA Showcase**
<p align="center">
  <img src="img/节点布局整理.png" alt="Node Layout Arrangement" width="60%">
</p>

**Connection Swapper**
<p align="center">
  <img src="img/连接交换器.gif" alt="Connection Swapper" width="40%">
</p>

**Quick Console**
<p align="center">
  <img src="img/快捷控制台.gif" alt="Quick Console" width="30%">
</p>

## <a name="installation"></a>Installation

Before using, please follow these steps for installation and setup:

0. **Install SideFX Labs**: Many nodes depend on the Labs plugin, so please ensure it is installed. This toolset does not embed the required Labs nodes.

1. In your `C:\Users\YourUsername\Documents\houdiniX.Y` directory, clone this repository into a folder named `DolagPlugin` using Git:

   ```bash
   git clone https://github.com/dolag233/Dolag-Houdini-Toolset.git DolagPlugin
   ```

2. Copy the `DolagPlugin.json` file from the `DolagPlugin` folder to the `C:\Users\YourUsername\Documents\houdiniX.Y\packages` directory. If the `packages` directory does not exist, please create it first.

## <a name="usage"></a>Usage

For detailed usage instructions, please refer to the [online documentation](https://www.vis.dolag.work/houdini-toolset/%E7%AE%80%E4%BB%8B.html).
