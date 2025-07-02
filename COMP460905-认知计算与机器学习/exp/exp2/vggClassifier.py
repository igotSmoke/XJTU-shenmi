import torch
import torch.nn as nn
import torch.optim as optim
import torchvision
import torchvision.transforms as transforms
from torch.utils.data import DataLoader
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix
import argparse

class VGG7(nn.Module):
    def __init__(self):
        super(VGG7, self).__init__()
        self.features = nn.Sequential(
            nn.Conv2d(3, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),
            
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),
            
            nn.Conv2d(128, 256, kernel_size=3, padding=1),
            nn.BatchNorm2d(256),
            nn.ReLU(inplace=True),
            nn.Conv2d(256, 256, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),
        )
        self.classifier = nn.Sequential(
            nn.Linear(256*4*4, 512),
            nn.ReLU(inplace=True),
            nn.Dropout(0.5),
            nn.Linear(512, 256),
            nn.ReLU(inplace=True),
            nn.Dropout(0.5),
            nn.Linear(256, 10),
        )

    def forward(self, x):
        x = self.features(x)
        x = x.view(x.size(0), -1)
        x = self.classifier(x)
        return x

class CIFAR10Classifier:
    def __init__(self, args):
        self.args = args
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.classes = ('plane', 'car', 'bird', 'cat', 'deer', 
                       'dog', 'frog', 'horse', 'ship', 'truck')
        
        # 初始化模型
        self.model = VGG7().to(self.device)
        self.criterion = nn.CrossEntropyLoss()
        self.optimizer = optim.Adam(self.model.parameters(), 
                                   lr=args.lr, 
                                   weight_decay=args.weight_decay)
        
        # 数据加载
        self._load_data()

    def _load_data(self):
        transform_train = transforms.Compose([
            transforms.RandomHorizontalFlip(),
            transforms.RandomCrop(32, padding=4),
            transforms.ToTensor(),
            transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2023, 0.1994, 0.2010)),
        ])

        transform_test = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2023, 0.1994, 0.2010)),
        ])

        trainset = torchvision.datasets.CIFAR10(
            root='./data', train=True, download=True, transform=transform_train)
        self.trainloader = DataLoader(trainset, batch_size=self.args.batch_size,
                                     shuffle=True, num_workers=2)

        testset = torchvision.datasets.CIFAR10(
            root='./data', train=False, download=True, transform=transform_test)
        self.testloader = DataLoader(testset, batch_size=self.args.batch_size,
                                    shuffle=False, num_workers=2)

    def train(self):
        print(f"\nStarting training with {self.args.epochs} epochs...")
        for epoch in range(self.args.epochs):
            self.model.train()
            total = 0
            correct = 0
            
            for inputs, targets in self.trainloader:
                inputs, targets = inputs.to(self.device), targets.to(self.device)
                
                self.optimizer.zero_grad()
                outputs = self.model(inputs)
                loss = self.criterion(outputs, targets)
                loss.backward()
                self.optimizer.step()
                
                _, predicted = outputs.max(1)
                total += targets.size(0)
                correct += predicted.eq(targets).sum().item()
            
            train_acc = 100 * correct / total
            if (epoch+1) % 5 == 0 or epoch == 0:
                test_acc = self.test()
                print(f"Epoch [{epoch+1}/{self.args.epochs}] | "
                      f"Train Acc: {train_acc:.2f}% | "
                      f"Test Acc: {test_acc:.2f}%")
        
        torch.save(self.model.state_dict(), self.args.save_path)
        print(f"Model saved to {self.args.save_path}")

    def test(self):
        self.model.eval()
        all_targets = []
        all_preds = []
        
        with torch.no_grad():
            for inputs, targets in self.testloader:
                inputs, targets = inputs.to(self.device), targets.to(self.device)
                outputs = self.model(inputs)
                _, predicted = outputs.max(1)
                
                all_targets.extend(targets.cpu().numpy())
                all_preds.extend(predicted.cpu().numpy())
        
        accuracy = 100 * np.sum(np.array(all_preds) == np.array(all_targets)) / len(all_targets)
        return accuracy

    def plot_confusion_matrix(self):
        self.model.eval()
        all_targets = []
        all_preds = []
        
        with torch.no_grad():
            for inputs, targets in self.testloader:
                inputs, targets = inputs.to(self.device), targets.to(self.device)
                outputs = self.model(inputs)
                _, predicted = outputs.max(1)
                
                all_targets.extend(targets.cpu().numpy())
                all_preds.extend(predicted.cpu().numpy())
        
        cm = confusion_matrix(all_targets, all_preds)
        plt.figure(figsize=(12, 10))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                   xticklabels=self.classes, 
                   yticklabels=self.classes)
        plt.title('Confusion Matrix')
        plt.xlabel('Predicted')
        plt.ylabel('True')
        plt.savefig('confusion_matrix.png')
        print("Confusion matrix saved to confusion_matrix.png")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='CIFAR10 Classification with VGG7')
    parser.add_argument('--train', action='store_true', help='Train the model')
    parser.add_argument('--test', action='store_true', help='Test the model')
    parser.add_argument('--plot', action='store_true', help='Plot confusion matrix')
    parser.add_argument('--epochs', type=int, default=20, help='Number of epochs')
    parser.add_argument('--batch_size', type=int, default=128, help='Batch size')
    parser.add_argument('--lr', type=float, default=0.0005, help='Learning rate')
    parser.add_argument('--weight_decay', type=float, default=5e-4, help='Weight decay')
    parser.add_argument('--save_path', type=str, default='cifar10_vgg7.pth', help='Model save path')
    parser.add_argument('--load_path', type=str, help='Model load path')
    args = parser.parse_args()

    classifier = CIFAR10Classifier(args)
    
    if args.load_path:
        classifier.model.load_state_dict(torch.load(args.load_path))
        print(f"Loaded model from {args.load_path}")
    
    if args.train:
        classifier.train()
    
    if args.test:
        if not args.load_path and not args.train:
            raise ValueError("For testing, either train first or provide --load_path")
        accuracy = classifier.test()
        print(f"\nFinal Test Accuracy: {accuracy:.2f}%")
    
    if args.plot:
        classifier.plot_confusion_matrix()
        