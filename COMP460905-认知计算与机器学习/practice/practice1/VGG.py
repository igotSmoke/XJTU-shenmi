import torch
import torchvision
import torchvision.transforms as transforms
import matplotlib.pyplot as plt
import numpy as np
import torch.nn as nn
import argparse
import time
from sklearn.metrics import precision_score, recall_score, f1_score, accuracy_score

def print_memory_usage(device):
    if device.type == 'cuda':
        print(f"峰值显存占用: {torch.cuda.max_memory_allocated(device)/1024**2:.2f} MB")
    else:
        print("CPU训练模式，无法获取精确内存占用")

def parse_args():
    parser = argparse.ArgumentParser(description='VGG11 Training Script')
    parser.add_argument('--epochs', type=int, default=10, help='Number of epochs for training')
    parser.add_argument('--batch_size', type=int, default=64, help='Batch size for training')
    parser.add_argument('--mode', type=str, choices=['train', 'test'], default='train', help='Mode: train or test')
    parser.add_argument('--lr', type=float, default=0.001, help='Learning rate')
    parser.add_argument('--weight_decay', type=float, default=5e-4, help='Weight decay')
    parser.add_argument('--save_path', type=str, default='cifar10_vgg11.pth', help='Model save path')
    parser.add_argument('--load_path', type=str, help='Model load path')
    args = parser.parse_args()
    return args

# 数据的预处理
transform = transforms.Compose([
    transforms.ToTensor(), # C,H,W
    transforms.Resize(36),       # 先放大尺寸
    transforms.CenterCrop(32), 
])

trainset = torchvision.datasets.CIFAR10(
    root='./data',
    train=True,
    download=True,
    transform=transform
)

trainloader = torch.utils.data.DataLoader(
    trainset,
    batch_size=parse_args().batch_size,
    shuffle=True
)

testset = torchvision.datasets.CIFAR10(
    root='./data',
    train=False,
    download=True,
    transform=transform
)

testloader = torch.utils.data.DataLoader(
    testset,
    batch_size=parse_args().batch_size,
    shuffle=False
)

# 搭VGG11
class VGG11(nn.Module):
    def __init__(self):
        super(VGG11, self).__init__()

        self.features = nn.Sequential(
            nn.Conv2d(3, 64, kernel_size=3, padding=1), nn.ReLU(inplace=True),
            nn.Conv2d(64, 64, kernel_size=3, padding=1), nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),  # 32 -> 16
            
            nn.Conv2d(64, 128, kernel_size=3, padding=1), nn.ReLU(inplace=True),
            nn.Conv2d(128, 128, kernel_size=3, padding=1), nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),  # 16 -> 8
            
            nn.Conv2d(128, 256, kernel_size=3, padding=1), nn.BatchNorm2d(256), nn.ReLU(inplace=True),
            nn.Conv2d(256, 256, kernel_size=3, padding=1), nn.BatchNorm2d(256), nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),  # 8 -> 4

            nn.Conv2d(256, 512, kernel_size=3, padding=1), nn.BatchNorm2d(512), nn.ReLU(inplace=True),
            nn.Conv2d(512, 512, kernel_size=3, padding=1), nn.BatchNorm2d(512), nn.ReLU(inplace=True),

        )

        self.classifier = nn.Sequential(
            nn.Linear(512 * 4 * 4, 256), nn.ReLU(inplace = True),
            nn.Dropout(0.3),
            nn.Linear(256, 128), nn.ReLU(inplace = True),
            nn.Dropout(0.3),
            nn.Linear(128, 10)
        )
    
    def forward(self, x):
        x = self.features(x)
        x = x.view(x.size(0), -1)
        x = self.classifier(x)
        return x
    

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = VGG11().to(device)
criterion = nn.CrossEntropyLoss()


def main():
    args = parse_args()

    optimizer = torch.optim.Adam(model.parameters(), lr=args.lr, weight_decay = args.weight_decay)

    if args.mode == 'train':
        start_time = time.time()

        train_losses = []  # 新增：用于记录每个epoch的loss

        for epoch in range(args.epochs):
            print(f"Train Epoch: {epoch:.2f} ... ")
            model.train()
            running_loss = 0.0
            correct = 0
            total = 0

            for inputs, labels in trainloader:
                
                if torch.cuda.is_available():
                    torch.cuda.reset_peak_memory_stats()

                inputs, labels = inputs.to(device), labels.to(device)
        
                optimizer.zero_grad()
                outputs = model(inputs)

                loss = criterion(outputs, labels)
                loss.backward()
                
                optimizer.step()
                running_loss += loss.item()
                _, predicted = torch.max(outputs, 1)
                total += labels.size(0)
                correct += (predicted == labels).sum().item()

            epoch_loss = running_loss / len(trainloader)
            train_losses.append(epoch_loss)
            print(f"Epoch [{epoch+1}/{args.epochs}], Loss: {running_loss/len(trainloader):.4f}, Accuracy: {100 * correct/total:.2f}%")
        
        training_time = time.time() - start_time
        print(f"Training Time: {training_time:.2f} seconds")

        # 新增：绘制loss曲线
        plt.figure(figsize=(10, 6))
        plt.plot(train_losses, 'b-o', linewidth=2, markersize=8)
        plt.title("Training Loss Curve", fontsize=16)
        plt.xlabel("Epoch", fontsize=14)
        plt.ylabel("Loss", fontsize=14)
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.savefig('training_loss.png')  # 保存为图片文件
        print("已保存训练损失曲线图至 training_loss.png")
        
        # 新增：打印内存使用
        print_memory_usage(device)
        print(f"Training Time: {training_time:.2f} seconds")
        
        torch.save(model.state_dict(), args.save_path)
        print(f"Model saved to {args.save_path}")

    elif args.mode == 'test':
        if args.load_path:
            model.load_state_dict(torch.load(args.load_path))
            model.eval()
            print(f"Model loaded from {args.load_path}")
        else:
            print("Please provide a valid model path to load the model!")
            return

        start_time = time.time()

        all_labels = []
        all_preds = []
        correct = 0
        total = 0
        with torch.no_grad(): 
            for inputs, labels in testloader:
                inputs, labels = inputs.to(device), labels.to(device)
                outputs = model(inputs)
                _, predicted = torch.max(outputs, 1)
                total += labels.size(0)
                correct += (predicted == labels).sum().item()

                all_labels.extend(labels.cpu().numpy())
                all_preds.extend(predicted.cpu().numpy())

        # 输出测试结果
        accuracy = accuracy_score(all_labels, all_preds)
        precision = precision_score(all_labels, all_preds, average='weighted')
        recall = recall_score(all_labels, all_preds, average='weighted')
        f1 = f1_score(all_labels, all_preds, average='weighted')
        test_time = time.time() - start_time  # 记录测试时间

        print(f"Test Accuracy: {accuracy*100:.2f}%")
        print(f"Precision: {precision:.2f}")
        print(f"Recall: {recall:.2f}")
        print(f"F1 Score: {f1:.2f}")
        print(f"Test Time: {test_time:.2f} seconds")
    
if __name__ == "__main__":
    main()