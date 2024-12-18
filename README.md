# Resume Scorer

一个基于预定义标准对简历进行评分的系统。

## 功能特点

- 支持 PDF 格式的简历文件
- 基于可配置评分标准进行评估
- 使用 Gradio 提供简单直观的用户界面

## 安装

```bash
# 创建并激活 conda 环境
conda env create -f environment.yml
conda activate tf2

# 安装项目
pip install -e .
```

## 使用方法

```bash
# 启动 Gradio 界面
python tf2/app.py
``` 