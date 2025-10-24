import torch
import math
import torch.nn as nn
import torchvision.models as models
import torchvision.transforms as transforms
from torchvision.models import ResNet18_Weights
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import cv2
import os
from PIL import Image, ImageEnhance


class SketchSimilarityModel:
    def __init__(self, device='cpu'):
        self.device = torch.device(device)
        self.model = self._load_pretrained_model().to(self.device)
        self.transform = transforms.Compose([
            transforms.Lambda(self._preprocess_sketch),
            transforms.Resize((224, 224)),  # 调整为224x224以匹配ResNet输入
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                 std=[0.229, 0.224, 0.225])
        ])

    def _load_pretrained_model(self):
        """加载预训练的ResNet18模型并移除最后一层"""
        model = models.resnet18(weights=ResNet18_Weights.DEFAULT)
        # 保留除最后一层外的所有层
        model = torch.nn.Sequential(*list(model.children())[:-1])
        model.eval()
        return model

    def _preprocess_sketch(self, img):
        """强化预处理流程，突出草图线条特征"""
        # 转换为灰度图
        img = img.convert('L')

        # 锐化处理增强线条
        enhancer = ImageEnhance.Sharpness(img)
        img = enhancer.enhance(2.5)

        # 转换为numpy数组进行形态学操作
        img_array = np.array(img)

        # 使用Canny边缘检测
        edges = cv2.Canny(img_array, 50, 150)

        # 形态学闭运算，连接断开的线条
        kernel = np.ones((3, 3), np.uint8)
        closed_edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)

        # 转换回PIL图像并扩展为3通道
        processed_img = Image.fromarray(closed_edges).convert('RGB')
        return processed_img

    def extract_features(self, img_path):
        """提取图像特征"""
        img = Image.open(img_path)
        img = self.transform(img).unsqueeze(0).to(self.device)
        with torch.no_grad():
            features = self.model(img)
        # 展平特征向量
        return features.squeeze().cpu().numpy().flatten()


def calculate_sketch_similarity(img_path1, img_path2, device='cpu'):
    """计算两张草图的相似度"""
    model = SketchSimilarityModel(device=device)

    # 提取特征
    features1 = model.extract_features(img_path1)
    features2 = model.extract_features(img_path2)

    # 计算余弦相似度
    cos_sim = cosine_similarity([features1], [features2])[0][0]

    # 加载原始图像计算结构相似度(SSIM)
    img1 = Image.open(img_path1).convert('L')
    img2 = Image.open(img_path2).convert('L')
    img1 = img1.resize((224, 224))
    img2 = img2.resize((224, 224))
    ssim_score = calculate_ssim(np.array(img1), np.array(img2))

    # 综合相似度（给予结构相似度更高权重）
    combined_similarity = 0.6 * cos_sim + 0.4 * ssim_score
    if combined_similarity<=0.5:
        combined_similarity = combined_similarity/(0.5-0)*combined_similarity
    else:
        combined_similarity = 1-(1-combined_similarity)/(1-0.5)*(1-combined_similarity)
    #combined_similarity = 0.5*math.cos(math.pi*(combined_similarity+1))+0.5
    # 确保相似度在合理范围内
    combined_similarity = max(0.0, min(1.0, combined_similarity))

    return combined_similarity


def calculate_ssim(img1, img2):
    """计算两张图像的结构相似度"""
    # 确保图像值在0-255范围内
    img1 = img1.astype(np.float64)
    img2 = img2.astype(np.float64)

    # 计算均值
    mu1 = img1.mean()
    mu2 = img2.mean()

    # 计算方差
    sigma1_sq = ((img1 - mu1) ** 2).mean()
    sigma2_sq = ((img2 - mu2) ** 2).mean()
    sigma12 = ((img1 - mu1) * (img2 - mu2)).mean()

    # SSIM参数
    C1 = (0.01 * 255) ** 2
    C2 = (0.03 * 255) ** 2

    # 计算SSIM
    numerator = (2 * mu1 * mu2 + C1) * (2 * sigma12 + C2)
    denominator = (mu1 ** 2 + mu2 ** 2 + C1) * (sigma1_sq + sigma2_sq + C2)

    return numerator / denominator