import torch
import torchvision
import torchvision.transforms as transforms
import matplotlib.pyplot as plt
import numpy as np
from torchvision.datasets import CIFAR10

# 定义图像变换（统一大小）
transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Resize(32),
    transforms.CenterCrop(32)
])

# 加载CIFAR10数据集
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

# 获取一个批次数据并显示
images, labels = next(iter(trainloader))
grid = torchvision.utils.make_grid(images[:10], nrow=10, padding=2)

plt.figure(figsize=(15, 3))
plt.imshow(grid.permute(1, 2, 0).numpy())
plt.axis('off')
plt.title('Task 1: Batch Images')
plt.show()


def compute_global_stats(loader):
    """
    精确计算数据集的全局均值和标准差
    返回形状为 (3,) 的均值张量和标准差张量 (对应RGB三通道)
    """
    # 初始化累加器
    sum_rgb = torch.zeros(3)      # 各通道像素总和
    sum_sq_rgb = torch.zeros(3)   # 各通道像素平方总和
    total_pixels = 0              # 总像素数
    
    for images, _ in trainloader:  # 遍历所有批次
        # 输入形状: [B, C, H, W] → [B, C, H*W]
        b, c, h, w = images.shape
        images_flat = images.view(b, c, -1)  # 展平空间维度
        
        # 累加各通道像素总和 (dim=2: 对每个通道的所有像素求和)
        sum_rgb += images_flat.sum(dim=2).sum(dim=0)  # → [C]
        
        # 累加各通道像素平方总和
        sum_sq_rgb += (images_flat ** 2).sum(dim=2).sum(dim=0)
        
        # 更新总像素数 (每个批次的像素数 = B * H * W)
        total_pixels += b * h * w

    # 计算全局均值
    global_mean = sum_rgb / total_pixels  # [C]
    
    # 计算全局标准差 (使用总体方差公式)
    global_std = torch.sqrt(
        (sum_sq_rgb / total_pixels) - (global_mean ** 2)
    )
    
    return global_mean, global_std

# 执行计算
global_mean, global_std = compute_global_stats(trainloader)
print(f"Global Mean (R, G, B): {global_mean.numpy().round(4)}")
print(f"Global Std  (R, G, B): {global_std.numpy().round(4)}")

# 3. 处理指定图像
selected_index = 7  # 选择第7张

# 获取原始图像张量 (未经归一化)
original_img, _ = trainset[selected_index]  # 形状 [C, H, W]

# 减去均值处理
minus_mean_img = original_img - global_mean.view(3, 1, 1)

# Z-score归一化处理
normalized_img = minus_mean_img / global_std.view(3, 1, 1)

# 4. 可视化对比
def denormalize_for_display(tensor, mean, std):
    """将归一化后的张量恢复到可显示范围 (0-1)"""
    tensor = tensor.clone()
    for c in range(3):
        tensor[c] = tensor[c] * std[c] + mean[c]
    return tensor.clamp(0, 1)

# 创建对比图
fig, axes = plt.subplots(1, 3, figsize=(12, 4))
titles = ['Original Image', 'After Mean Subtraction', 'After Z-score Normalization']
images = [original_img, minus_mean_img, normalized_img]

for ax, title, img in zip(axes, titles, images):
    # 转换张量格式: [C, H, W] → [H, W, C]
    np_img = img.numpy().transpose(1, 2, 0)
    
    # 对于归一化后的图像需要调整显示范围
    if title == 'After Z-score Normalization':
        np_img = (np_img - np_img.min()) / (np_img.max() - np_img.min())
    
    ax.imshow(np_img)
    ax.set_title(title, fontsize=10)
    ax.axis('off')

# 添加统计信息标注
stats_text = (
    f"Global Mean: {global_mean.numpy().round(4)}\n"
    f"Global Std:  {global_std.numpy().round(4)}"
)
plt.figtext(0.5, 0.02, stats_text, ha='center', fontsize=9)

plt.tight_layout()
plt.savefig('task2_comparison.png', dpi=200, bbox_inches='tight')
plt.show()


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

# 加载原始PIL格式数据集
testset = CIFAR10(root='./data', 
                train=False, 
                download=True,
                transform=None)  # 保持原始PIL格式

# 选择指定索引的10张图片
selected_indices = list(range(10))

# 创建大图画布
fig, axs = plt.subplots(10, 5, figsize=(15, 30))
plt.subplots_adjust(wspace=0.1, hspace=0.2)

# 处理并绘制每个图像
for row in range(10):
    # 获取原始PIL图像
    pil_img = testset[selected_indices[row]][0]
    
    # 原始图像（转换为Tensor）
    original_tensor = transform_original(pil_img)
    
    # 应用各种增强
    rotated_tensor = transform_rotate(pil_img)
    flipped_tensor = transform_flip(pil_img)
    cropped_tensor = transform_crop(pil_img)
    noisy_tensor = add_noise(original_tensor.clone())
    
    # 转换为显示格式
    displays = [
        original_tensor.numpy().transpose(1, 2, 0),
        rotated_tensor.numpy().transpose(1, 2, 0),
        flipped_tensor.numpy().transpose(1, 2, 0),
        cropped_tensor.numpy().transpose(1, 2, 0),
        noisy_tensor.numpy().transpose(1, 2, 0)
    ]
    
    # 绘制结果
    titles = ['Original', 'Rotated', 'Flipped', 'Cropped', 'Noisy']
    for col in range(5):
        axs[row, col].imshow(displays[col])
        axs[row, col].set_title(titles[col], fontsize=8)
        axs[row, col].axis('off')

plt.savefig('cifar10_augmentations.png', bbox_inches='tight', dpi=200)
plt.show()