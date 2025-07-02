import torch
import torchvision
import torchvision.transforms as transforms
import matplotlib.pyplot as plt
import numpy as np

# 定义数据预处理：转换为张量 + 中心裁剪为统一尺寸
target_size = 32  # 可修改为目标尺寸（如24或64）
transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Resize(target_size + 4),       # 先放大尺寸
    transforms.CenterCrop(target_size),      # 再中心裁剪
    # transforms.RandomCrop(target_size)      # 若需要随机裁剪可取消注释
])

# 下载并加载CIFAR10数据集
trainset = torchvision.datasets.CIFAR10(
    root='./data',
    train=True,
    download=True,
    transform=transform
)
trainloader = torch.utils.data.DataLoader(
    trainset,
    batch_size=64,
    shuffle=True
)

# 获取一个批次数据
dataiter = iter(trainloader)
images, labels = dataiter.__next__()

# 选择前10张图片并生成网格
selected_images = images[:10]
grid = torchvision.utils.make_grid(selected_images, nrow=10, padding=2)

# 转换为Matplotlib可显示格式
grid_np = grid.numpy().transpose((1, 2, 0))

# 绘制图像
plt.figure(figsize=(15, 2.5))
plt.imshow(grid_np)
plt.axis('off')
plt.title('CIFAR10 Sample Images')
plt.show()
