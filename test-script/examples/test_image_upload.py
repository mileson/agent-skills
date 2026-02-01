"""
图片上传功能测试

测试用户上传图片的完整流程，包括文件选择、上传、进度显示、结果展示等。
"""

import pytest
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


@pytest.fixture
def driver():
    """初始化浏览器驱动"""
    driver = webdriver.Chrome()
    driver.implicitly_wait(10)
    yield driver
    driver.quit()


# ============================================
# 图片上传功能测试
# ============================================

class TestImageUpload:
    """图片上传功能测试类"""

    def test_upload_image_success(self, driver):
        """测试图片上传 - 成功场景"""
        # Arrange
        driver.get("https://example.com/upload")
        file_input = driver.find_element(By.ID, "file-input")

        # 获取测试图片路径
        test_image = os.path.join(os.path.dirname(__file__), "fixtures", "test_image.jpg")

        # Act - 选择并上传文件
        file_input.send_keys(test_image)
        driver.find_element(By.ID, "upload-button").click()

        # Assert - 验证上传成功
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CLASS_NAME, "upload-success"))
        )
        success_msg = driver.find_element(By.CLASS_NAME, "upload-success")
        assert "上传成功" in success_msg.text

    def test_upload_image_invalid_format(self, driver):
        """测试图片上传 - 无效文件格式"""
        # Arrange
        driver.get("https://example.com/upload")
        file_input = driver.find_element(By.ID, "file-input")
        test_file = os.path.join(os.path.dirname(__file__), "fixtures", "test.txt")

        # Act - 尝试上传非图片文件
        file_input.send_keys(test_file)
        driver.find_element(By.ID, "upload-button").click()

        # Assert - 验证错误提示
        error_msg = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "upload-error"))
        )
        assert "不支持的文件格式" in error_msg.text

    def test_upload_image_size_limit(self, driver):
        """测试图片上传 - 文件大小超限"""
        # Arrange
        driver.get("https://example.com/upload")
        file_input = driver.find_element(By.ID, "file-input")
        large_image = os.path.join(os.path.dirname(__file__), "fixtures", "large_image.jpg")

        # Act - 尝试上传超大文件
        file_input.send_keys(large_image)
        driver.find_element(By.ID, "upload-button").click()

        # Assert - 验证大小限制错误
        error_msg = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "upload-error"))
        )
        assert "文件过大" in error_msg.text

    def test_upload_progress_display(self, driver):
        """测试上传进度显示"""
        # Arrange
        driver.get("https://example.com/upload")
        file_input = driver.find_element(By.ID, "file-input")
        test_image = os.path.join(os.path.dirname(__file__), "fixtures", "test_image.jpg")

        # Act - 上传文件
        file_input.send_keys(test_image)
        driver.find_element(By.ID, "upload-button").click()

        # Assert - 验证进度条显示
        progress_bar = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, "upload-progress"))
        )
        assert progress_bar.is_displayed()

    def test_upload_multiple_images(self, driver):
        """测试批量上传图片"""
        # Arrange
        driver.get("https://example.com/upload")
        file_input = driver.find_element(By.ID, "file-input")
        test_images = [
            os.path.join(os.path.dirname(__file__), "fixtures", f"image_{i}.jpg")
            for i in range(1, 4)
        ]

        # Act - 批量上传
        for image in test_images:
            file_input.send_keys(image)
        driver.find_element(By.ID, "upload-button").click()

        # Assert - 验证所有图片上传成功
        WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.CLASS_NAME, "upload-success"))
        )
        uploaded_count = driver.find_elements(By.CLASS_NAME, "uploaded-item")
        assert len(uploaded_count) == 3
