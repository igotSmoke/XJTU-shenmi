import torch
import torchvision
import torchvision.transforms as transforms
import matplotlib.pyplot as plt
import numpy as np
import torch.nn as nn
import argparse
import time
from sklearn.metrics import precision_score, recall_score, f1_score, accuracy_score
import torch.nn.functional as F

def parse_args():
    parser = argparse.ArgumentParser(description='Resnet Training Script')
    parser.add_argument('--epochs', type=int, default=10, help='Number of epochs for training')
    parser.add_argument('--batch_size', type=int, default=64, help='Batch size for training')
    parser.add_argument('--mode', type=str, choices=['train', 'test'], default='train', help='Mode: train or test')
    parser.add_argument('--lr', type=float, default=0.1, help='Learning rate')
    parser.add_argument('--weight_decay', type=float, default=5e-4, help='Weight decay')
    parser.add_argument('--save_path', type=str, default='cifar10_resnet.pth', help='Model save path')
    parser.add_argument('--load_path', type=str, help='Model load path')
    parser.add_argument('--momentum', type=float, default = 0.9, help='Momentum')
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

class BasicBlock(nn.Module):
    def __init__(self, in_channels, out_channels, stride=1):
        super().__init__()
        self.conv1 = nn.Conv2d(
            in_channels, out_channels, kernel_size=3, stride=stride, padding=1, bias=False)
        self.bn1 = nn.BatchNorm2d(out_channels)
        self.conv2 = nn.Conv2d(
            out_channels, out_channels, kernel_size=3, stride=1, padding=1, bias=False)
        self.bn2 = nn.BatchNorm2d(out_channels)
        self.conv3 = nn.Conv2d(
            out_channels, out_channels, kernel_size=3, stride=1, padding=1, bias=False)
        self.bn3 = nn.BatchNorm2d(out_channels)
        
        self.shortcut = nn.Sequential()
        if stride != 1 or in_channels != out_channels:
            self.shortcut = nn.Sequential(
                nn.Conv2d(in_channels, out_channels, kernel_size=1,
                          stride=stride, bias=False),
                nn.BatchNorm2d(out_channels)
            )

    def forward(self, x):

        out = F.relu(self.bn1(self.conv1(x)))
        out = F.relu(self.bn2(self.conv2(out)))
        out = self.bn3(self.conv3(out))
        out += self.shortcut(x)
        return F.relu(out)
    
class Resnet(nn.Module):
    def __init__(self):
        super().__init__()
        self.in_channels = 32
        self.conv1 = nn.Conv2d(3, 32, kernel_size=3, stride=1, padding=1, bias=False)
        self.bn1 = nn.BatchNorm2d(32)

        self.layer1 = self._make_layer(32, 2, stride=1)
        self.layer2 = self._make_layer(64, 2, stride=2)
        self.layer3 = self._make_layer(128, 2, stride=2)

        self.avgpool = nn.AdaptiveAvgPool2d((1, 1))
        self.fc = nn.Linear(128, 10)

    def _make_layer(self, out_channels, num_blocks, stride):
        strides = [stride] + [1]*(num_blocks-1)  
        layers = []
        for stride in strides:
            layers.append(BasicBlock(self.in_channels, out_channels, stride))
            self.in_channels = out_channels
        return nn.Sequential(*layers)
    
    def forward(self, x):
        x = F.relu(self.bn1(self.conv1(x)))

        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)

        x = self.avgpool(x)
        x = x.view(x.size(0), -1)
        x = self.fc(x)
        return x
    
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = Resnet().to(device)
criterion = nn.CrossEntropyLoss()



def main():
    args = parse_args()

    optimizer = torch.optim.SGD(model.parameters(), lr=args.lr, momentum=args.momentum, weight_decay = args.weight_decay)
 
    
    if args.mode == 'train':
        start_time = time.time()
        train_losses = []  # 存储每个epoch的loss

        for epoch in range(args.epochs):
            print(f"Train Epoch: {epoch:.2f} ... ")
            model.train()
            running_loss = 0.0
            correct = 0
            total = 0

            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                torch.cuda.reset_peak_memory_stats()

            for inputs, labels in trainloader:
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

            if torch.cuda.is_available():
                peak_memory = torch.cuda.max_memory_allocated() / (1024 ** 2)
                print(f"Peak GPU Memory Usage: {peak_memory:.2f} MB")

            print(f"Epoch [{epoch+1}/{args.epochs}], Loss: {running_loss/len(trainloader):.4f}, Accuracy: {100 * correct/total:.2f}%")

        plt.figure()
        plt.plot(range(1, args.epochs + 1), train_losses, 'b-o', label='Training Loss')
        plt.title('Training Loss Curve')
        plt.xlabel('Epoch')
        plt.ylabel('Loss')
        plt.legend()
        plt.grid(True)
        plt.savefig('training_loss_curve.png')
        plt.close()

        training_time = time.time() - start_time
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