"""
功能测试脚本模板

用于测试具体功能或用户场景，通常涉及多个组件的交互。
"""

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# ============================================
# 测试配置和辅助函数
# ============================================

def login(driver, username: str, password: str):
    """执行登录操作"""
    driver.get("https://example.com/login")
    driver.find_element(By.ID, "username").send_keys(username)
    driver.find_element(By.ID, "password").send_keys(password)
    driver.find_element(By.ID, "login-button").click()
    WebDriverWait(driver, 10).until(
        EC.url_contains("dashboard")
    )


def wait_for_element(driver, by: By, value: str, timeout: int = 10):
    """等待元素出现"""
    return WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((by, value))
    )


# ============================================
# 功能测试
# ============================================

class Test[FeatureName]:
    """[功能名称] 测试类"""

    def test_[feature]_basic_flow(self, driver):
        """测试 [功能] 基本流程 - 成功场景"""
        # Arrange
        driver.get("https://example.com/[feature-page]")

        # Act - 执行功能操作
        element = wait_for_element(driver, By.ID, "action-button")
        element.click()

        # Assert - 验证结果
        success_message = wait_for_element(driver, By.CLASS_NAME, "success-message")
        assert "成功" in success_message.text

    def test_[feature]_with_invalid_input(self, driver):
        """测试 [功能] - 无效输入场景"""
        # Arrange
        driver.get("https://example.com/[feature-page]")
        input_field = wait_for_element(driver, By.ID, "input-field")

        # Act - 输入无效数据
        input_field.clear()
        input_field.send_keys("invalid_data")
        driver.find_element(By.ID, "submit-button").click()

        # Assert - 验证错误提示
        error_message = wait_for_element(driver, By.CLASS_NAME, "error-message")
        assert error_message.is_displayed()

    def test_[feature]_edge_case(self, driver):
        """测试 [功能] - 边界场景"""
        # 测试边界条件、空值、极限值等
        pass

    def test_[feature]_integration_with_other_module(self, driver):
        """测试 [功能] 与其他模块的集成"""
        # 测试跨模块交互
        pass
