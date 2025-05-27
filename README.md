# LSTM 量化选股模型

## 项目概述

本项目旨在使用 LSTM (长短期记忆网络) 构建一个量化选股模型。模型将使用模拟生成的因子数据作为特征，历史收益率作为预测目标，以辅助进行量化选股决策。项目包含数据生成、预处理、模型训练、评估和结果可视化等完整流程。

## 代码架构说明

本项目包含以下核心 Python 脚本：

*   **`generate_data.py`**:
    *   **功能**: 生成模拟的因子数据和收益率数据。
    *   **输入**: 无，脚本内部定义生成逻辑。
    *   **输出**: `simulated_data.csv` 文件，包含日期、三个模拟因子 (`factor1`, `factor2`, `factor3`) 和日收益率 (`returns`)。

*   **`preprocess_data.py`**:
    *   **功能**: 对原始数据进行预处理，为模型训练做准备。
    *   **输入**: `simulated_data.csv`。
    *   **输出**: `processed_data.npz` 文件，包含经过以下处理的数据：
        *   特征和目标分离。
        *   特征数据使用 `MinMaxScaler`进行归一化处理。
        *   数据划分为训练集 (80%) 和验证集 (20%)，保持时间序列顺序。
        *   输入特征被重塑为 LSTM 模型所需的 3D 格式 (样本数, 时间步长=1, 特征数)。
    *   **关键步骤**: 加载数据 -> 特征与目标分离 -> 特征缩放 -> 数据集划分 -> 数据重塑。

*   **`train_lstm_model.py`**:
    *   **功能**: 构建、训练并保存 LSTM 模型。
    *   **输入**: `processed_data.npz` (训练集和验证集数据)。
    *   **输出**: `lstm_model.h5` (保存的 Keras 模型文件)。
    *   **模型架构**:
        *   一个 LSTM 层 (64个单元，relu激活函数)。
        *   一个 Dense 输出层 (1个单元，用于预测收益率)。
        *   优化器: 'adam'。
        *   损失函数: 'mean_squared_error'。
    *   **训练参数**: 50个 epochs, batch_size 为 32。

*   **`evaluate_model.py`**:
    *   **功能**: 加载训练好的模型，在验证集上进行预测并评估模型性能。
    *   **输入**: `processed_data.npz` (验证集数据 `X_val`, `y_val`) 和 `lstm_model.h5`。
    *   **输出**: 在控制台打印以下评估指标：
        *   均方误差 (Mean Squared Error - MSE)
        *   夏普比率 (Sharpe Ratio): `mean(预测日收益率) / std(预测日收益率) * sqrt(252)` (假设无风险利率为0)
        *   年化收益率 (Annualized Return): `mean(预测日收益率) * 252`

*   **`visualize_results.py`**:
    *   **功能**: 可视化模型在验证集上的表现。
    *   **输入**: `processed_data.npz` (验证集数据 `X_val`, `y_val`) 和 `lstm_model.h5`。
    *   **输出**: `return_curves.png` 图片文件，展示以下内容：
        *   实际累积收益率曲线 (基于 `y_val`)。
        *   模型预测的累积收益率曲线。
        *   图表包含标题、图例和坐标轴标签。

## 文件结构

```
.
├── generate_data.py         # 模拟数据生成脚本
├── preprocess_data.py       # 数据预处理脚本
├── train_lstm_model.py      # LSTM模型训练脚本
├── evaluate_model.py        # 模型评估脚本
├── visualize_results.py     # 结果可视化脚本
├── requirements.txt         # 项目依赖包
├── simulated_data.csv       # 生成的原始模拟数据
├── processed_data.npz       # 预处理后的数据
├── lstm_model.h5            # 训练好的LSTM模型
├── return_curves.png        # 累积收益曲线图
└── README.md                # 本文档
```

## 安装指南

### 1. 设置虚拟环境 (推荐使用 `uv`)

`uv` 是一个非常快速的 Python 包安装和管理工具。

首先，安装 `uv` (如果尚未安装):
```bash
# 根据你的操作系统选择合适的安装方式，详情请见 uv 官方文档: https://github.com/astral-sh/uv
pip install uv
```

创建虚拟环境:
```bash
uv venv .venv
```
或者，如果你想指定 Python 版本 (例如 3.9):
```bash
uv venv .venv -p 3.9
```

激活虚拟环境:
*   macOS / Linux:
    ```bash
    source .venv/bin/activate
    ```
*   Windows (PowerShell):
    ```bash
    .venv\Scripts\Activate.ps1
    ```
*   Windows (CMD):
    ```bash
    .venv\Scripts\activate.bat
    ```

### 2. 安装依赖包

在激活的虚拟环境下，使用 `uv` 安装 `requirements.txt` 中的依赖包：
```bash
uv pip install -r requirements.txt
```
这将安装 `pandas`, `numpy`, `scikit-learn`, `tensorflow`, 和 `matplotlib`。

## 如何使用

请按照以下顺序执行脚本，以完成整个量化模型的流程：

1.  **生成模拟数据**:
    ```bash
    python generate_data.py
    ```
    这会创建 `simulated_data.csv`。

2.  **预处理数据**:
    ```bash
    python preprocess_data.py
    ```
    这会使用 `simulated_data.csv` 并创建 `processed_data.npz`。

3.  **训练 LSTM 模型**:
    ```bash
    python train_lstm_model.py
    ```
    这会使用 `processed_data.npz` 进行训练，并将模型保存为 `lstm_model.h5`。

4.  **评估模型**:
    ```bash
    python evaluate_model.py
    ```
    这将加载 `lstm_model.h5` 和 `processed_data.npz`，并在控制台输出 MSE、夏普比率和年化收益率。

5.  **可视化结果**:
    ```bash
    python visualize_results.py
    ```
    这将加载模型和数据，生成并保存 `return_curves.png`，显示实际与预测的累积收益对比。

### 查看结果

*   **性能指标**: `evaluate_model.py` 脚本的控制台输出将显示关键的性能指标。
*   **收益曲线**: `return_curves.png` 文件提供了模型预测收益与实际收益的视觉对比。

## 如何对接本地数据源

要将此模型应用于您自己的本地数据，主要需要修改数据加载和预处理部分。以下是基本步骤和注意事项：

1.  **准备您的数据文件**:
    *   建议将您的数据整理成 CSV 文件格式。
    *   文件应至少包含以下列：
        *   一个日期/时间列 (用于排序和潜在的时间序列分析)。
        *   一个或多个因子列 (特征值，数值类型)。
        *   一个收益率列 (预测目标，数值类型)。
    *   确保数据清洗完毕，没有缺失值或异常值。

2.  **修改数据加载逻辑**:
    *   **选项 A: 修改 `preprocess_data.py`** (推荐用于相似结构的数据)
        *   打开 `preprocess_data.py` 文件。
        *   修改 `pd.read_csv('simulated_data.csv')` 这一行，使其指向您的本地数据文件名，例如 `pd.read_csv('my_local_data.csv')`。
        *   根据您的 CSV 文件列名，调整 `features = df[['factor1', 'factor2', 'factor3']]` 和 `target = df['returns']` 部分，确保正确选取了特征列和目标列。

    *   **选项 B: 创建新的数据加载脚本** (如果数据格式差异较大或需要复杂处理)
        *   您可以创建一个新的 Python 脚本，例如 `load_my_data.py`。
        *   在此脚本中，编写加载、清洗和转换您的特定数据格式的代码。
        *   此脚本的最终输出应与 `preprocess_data.py` 中 `X_train, y_train, X_val, y_val` 类似，或者直接输出一个与 `processed_data.npz` 结构相同的 `.npz` 文件。如果选择后者，后续脚本可能无需大的改动。

3.  **调整特征数量**:
    *   在 `preprocess_data.py` 中，如果您使用的因子数量不是3个，请确保 `X.shape[1]` 能正确反映您的特征数量。
    *   在 `train_lstm_model.py` 中，LSTM 模型的输入层 `input_shape=(1, X_train.shape[2])` 会根据 `X_train` 的第二维（特征数）自动调整。通常这里不需要手动修改，除非您在 `preprocess_data.py` 中硬编码了特征数量。

4.  **数据归一化**:
    *   `MinMaxScaler` 通常适用于多种类型的因子数据。如果您的因子特性有特殊需求（例如，已经是特定范围或需要不同类型的缩放），可以调整 `sklearn.preprocessing` 中的缩放器。

5.  **时间步长 (Timesteps)**:
    *   当前模型假设每个样本的时间步长为 1 (`X_train_reshaped = X_train_scaled.reshape((X_train_scaled.shape[0], 1, X_train_scaled.shape[1]))`)。这意味着模型在每个时间点独立地使用当前因子进行预测。
    *   如果您希望模型考虑过去N个时间点的因子序列来预测当前收益，您需要：
        *   在 `preprocess_data.py` 中修改数据重塑逻辑，以创建包含N个时间步的序列。例如，对于每个样本，输入是 `(N, num_features)` 的形状。
        *   相应地，在 `train_lstm_model.py` 中调整 LSTM 层的 `input_shape=(N, num_features)`。

6.  **执行流程**:
    *   如果您修改了 `preprocess_data.py`，则可以直接运行后续脚本。
    *   如果您创建了新的数据加载脚本，请确保其输出与后续脚本的输入兼容。

通过以上调整，您应该能够将此 LSTM 量化模型框架应用于您自己的本地数据源。
