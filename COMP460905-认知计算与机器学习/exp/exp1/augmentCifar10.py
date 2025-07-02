import torch
import torchvision
import torchvision.transforms as transforms
import matplotlib.pyplot as plt
import numpy as np
from torchvision.datasets import CIFAR10

# 定义图像变换操作
transform_original = transforms.Compose([
    transforms.ToTensor()
])

# 定义不同的图像变换
transform_rotate = transforms.Compose([
    transforms.RandomRotation(30),
    transforms.ToTensor()
])

transform_flip = transforms.Compose([
    transforms.RandomHorizontalFlip(p=1),
    transforms.ToTensor()
])

transform_crop = transforms.Compose([
    transforms.RandomCrop(32, padding=4),
    transforms.ToTensor()
])

def add_noise(tensor):
    noise = torch.randn(tensor.size()) * 0.1
    return torch.clamp(tensor + noise, 0, 1)

# 加载CIFAR10数据集
testset = CIFAR10(root='./data', train=False, download=True, transform=transform_original)

# 选择指定索引的10张图片（这里选择前10张）
selected_indices = list(range(10))
images = [testset[i]  :reference[]{#0} for i in selected_indices]

# 创建大图画布
fig, axs = plt.subplots(10, 5, figsize=(15, 30))
plt.subplots_adjust(wspace=0.1, hspace=0.2)

# 处理并绘制每个图像
for row in range(10):
    # 原始图像
    original_img = images[row].numpy().transpose((1, 2, 0))
    axs[row, 0].imshow(original_img)
    axs[row, 0].set_title("Original", fontsize=8)
    
    # 旋转后的图像
    rotated_img = transform_rotate(testset[selected_indices[row]]  :reference[]{#0}.numpy().transpose((1, 2, 0)))
    axs[row, 1].imshow(rotated_img.numpy().transpose((1, 2, 0)))
    axs[row, 1].set_title("Rotated", fontsize=8)
    
    # 翻转后的图像
    flipped_img = transform_flip(testset[selected_indices[row]]  :reference[]{#0}.numpy().transpose((1, 2, 0)))
    axs[row, 2].imshow(flipped_img.numpy().transpose((1, 2, 0)))
    axs[row, 2].set_title("Flipped", fontsize=8)
    
    # 裁剪后的图像
    cropped_img = transform_crop(testset[selected_indices[row]]  :reference[]{#0}.numpy().transpose((1, 2, 0)))
    axs[row, 3].imshow(cropped_img.numpy().transpose((1, 2, 0)))
    axs[row, 3].set_title("Cropped", fontsize=8)
    
    # 加噪声后的图像
    noisy_img = add_noise(images[row])
    axs[row, 4].imshow(noisy_img.numpy().transpose((1, 2, 0)))
    axs[row, 4].set_title("Noisy", fontsize=8)

# 关闭所有坐标轴
for ax in axs.flat:
    ax.axis('off')

plt.savefig('cifar10_augmentations.png', bbox_inches='tight', dpi=200)
plt.show()
