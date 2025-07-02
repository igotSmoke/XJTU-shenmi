import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import pandas as pd
import numpy as np
import argparse
import matplotlib.pyplot as plt

class TimeSeriesDataset(Dataset):
    def __init__(self, X, y):
        self.X = X
        self.y = y

    def __len__(self):
        return len(self.X)

    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]

class LSTMForecaster:
    def __init__(self, data_path, window_size, hidden_size, num_layers, epochs, batch_size, lr):
        self.data_path = data_path
        self.window_size = window_size
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.epochs = epochs
        self.batch_size = batch_size
        self.lr = lr
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # 数据相关参数
        self.mean = 0
        self.std = 1
        self.X_train = None
        self.y_train = None
        self.X_test = None
        self.y_test = None
        
        # 模型组件
        self.model = None
        self.criterion = nn.MSELoss()
        self.optimizer = None

    class LSTMModel(nn.Module):
        def __init__(self, input_size, hidden_size, num_layers):
            super().__init__()
            self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
            self.fc = nn.Linear(hidden_size, 1)

        def forward(self, x):
            out, _ = self.lstm(x)
            out = out[:, -1, :]
            out = self.fc(out)
            return out

    def prepare_data(self):
        # 读取并预处理数据
        data = pd.read_csv(self.data_path).values.astype(np.float32)
        
        # 划分训练测试集
        train_size = int(len(data) * 0.7)
        train_data = data[:train_size]
        test_data = data[train_size - self.window_size:]  # 保持窗口连续性
        
        # 标准化
        self.mean = train_data.mean()
        self.std = train_data.std()
        train_data = (train_data - self.mean) / self.std
        test_data = (test_data - self.mean) / self.std

        # 创建滑动窗口样本
        def create_samples(dataset):
            X, y = [], []
            for i in range(len(dataset)-self.window_size):
                X.append(dataset[i:i+self.window_size])
                y.append(dataset[i+self.window_size])
            return np.array(X), np.array(y)

        X_train, y_train = create_samples(train_data)
        X_test, y_test = create_samples(test_data)

        # 转换为Tensor
        self.X_train = torch.from_numpy(X_train).float().view(-1, self.window_size, 1)
        self.y_train = torch.from_numpy(y_train).float().view(-1, 1)
        self.X_test = torch.from_numpy(X_test).float().view(-1, self.window_size, 1)
        self.y_test = torch.from_numpy(y_test).float().view(-1, 1)

    def build_model(self):
        self.model = self.LSTMModel(1, self.hidden_size, self.num_layers).to(self.device)
        self.optimizer = optim.Adam(self.model.parameters(), lr=self.lr)

    def train(self):
        train_dataset = TimeSeriesDataset(self.X_train, self.y_train)
        train_loader = DataLoader(train_dataset, batch_size=self.batch_size, shuffle=True)

        self.model.train()
        for epoch in range(self.epochs):
            total_loss = 0
            for X_batch, y_batch in train_loader:
                X_batch, y_batch = X_batch.to(self.device), y_batch.to(self.device)
                self.optimizer.zero_grad()
                outputs = self.model(X_batch)
                loss = self.criterion(outputs, y_batch)
                loss.backward()
                self.optimizer.step()
                total_loss += loss.item()
            print(f'Epoch [{epoch+1}/{self.epochs}], Loss: {total_loss/len(train_loader):.4f}')
        torch.save(self.model.state_dict(), 'lstm_model.pth')

    def test(self):
        test_dataset = TimeSeriesDataset(self.X_test, self.y_test)
        test_loader = DataLoader(test_dataset, batch_size=self.batch_size, shuffle=False)
        
        self.model.load_state_dict(torch.load('lstm_model.pth'))
        self.model.eval()
        predictions = []
        actuals = []
        with torch.no_grad():
            for X_batch, y_batch in test_loader:
                X_batch = X_batch.to(self.device)
                pred = self.model(X_batch).cpu().numpy()
                predictions.extend(pred)
                actuals.extend(y_batch.numpy())

        # 反标准化
        predictions = np.array(predictions) * self.std + self.mean
        actuals = np.array(actuals) * self.std + self.mean
        mse = np.mean((predictions - actuals) ** 2)
        print(f'Test MSE: {mse:.4f}')
        return actuals, predictions

    def plot_results(self, actuals, predictions):
        plt.figure(figsize=(12, 6))
        plt.plot(actuals, label='Actual')
        plt.plot(predictions, label='Predicted')
        plt.legend()
        plt.title('Time Series Prediction Results')
        plt.savefig('prediction_results.png')
        plt.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', type=str, required=True, choices=['train', 'test'])
    parser.add_argument('--data_path', type=str, required=True)
    parser.add_argument('--window_size', type=int, default=10)
    parser.add_argument('--hidden_size', type=int, default=50)
    parser.add_argument('--num_layers', type=int, default=1)
    parser.add_argument('--epochs', type=int, default=20)
    parser.add_argument('--batch_size', type=int, default=32)
    parser.add_argument('--lr', type=float, default=0.001)
    args = parser.parse_args()

    forecaster = LSTMForecaster(
        data_path=args.data_path,
        window_size=args.window_size,
        hidden_size=args.hidden_size,
        num_layers=args.num_layers,
        epochs=args.epochs,
        batch_size=args.batch_size,
        lr=args.lr
    )

    forecaster.prepare_data()
    forecaster.build_model()

    if args.mode == 'train':
        forecaster.train()
    elif args.mode == 'test':
        actuals, predictions = forecaster.test()
        forecaster.plot_results(actuals, predictions)
