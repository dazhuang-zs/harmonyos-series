"""输入安全过滤：Prompt Injection 防御"""

import re

# Prompt Injection 关键词模式
INJECTION_PATTERNS = [
    # 直接指令覆盖
    r"忽略(之前|上面|以上)(的)?(所有|全部)?(指令|提示|规则)",
    r"ignore (previous|above|all) (instructions|prompts|rules)",
    r"disregard (previous|above|all) (instructions|prompts|rules)",
    r"forget (previous|above|all) (instructions|prompts|rules)",

    # 角色劫持
    r"你现在是",
    r"你不再是",
    r"从现在起你(是|变成|扮演)",
    r"you are now",
    r"act as (?:a |an )",
    r"pretend (?:you are|to be)",

    # 系统提示泄露
    r"(你的|你的系统|system) (prompt|提示词|指令)",
    r"show me (your|the) (system|initial) (prompt|instructions)",
    r"repeat (the|your) (system|initial) (prompt|instructions)",

    # 编码/解码绕过
    r"base64(编码|解码|decode|encode)",
    r"rot13",
    r"\\x[0-9a-fA-F]{2}",

    # 越狱尝试
    r"DAN(模式| mode)",
    r"jailbreak",
    r"developer mode",
    r"do anything now",
]

# 敏感关键词
SENSITIVE_KEYWORDS = [
    "密码", "password", "token", "secret", "api_key",
    "私钥", "private_key", "credential",
]

# 编译正则
_injection_regex = re.compile("|".join(INJECTION_PATTERNS), re.IGNORECASE)


class InputFilter:
    """输入安全过滤器"""

    def __init__(self, block_on_injection: bool = True):
        self.block_on_injection = block_on_injection
        self.blocked_count = 0
        self.total_checked = 0

    def check(self, user_input: str) -> dict:
        """
        检查用户输入是否安全

        Returns:
            {
                "safe": bool,
                "reason": str,  # 不安全的原因
                "risk_level": str,  # low / medium / high
            }
        """
        self.total_checked += 1

        # 检查 Prompt Injection
        injection_match = _injection_regex.search(user_input)
        if injection_match:
            self.blocked_count += 1
            return {
                "safe": False,
                "reason": f"检测到潜在的 Prompt Injection 攻击: '{injection_match.group()}'",
                "risk_level": "high",
            }

        # 检查输入长度
        if len(user_input) > 50000:
            return {
                "safe": False,
                "reason": "输入过长，可能包含恶意内容",
                "risk_level": "medium",
            }

        # 检查重复字符（可能的 DoS 攻击）
        if len(set(user_input)) < 5 and len(user_input) > 100:
            return {
                "safe": False,
                "reason": "输入包含大量重复字符",
                "risk_level": "medium",
            }

        return {"safe": True, "reason": "", "risk_level": "low"}

    def sanitize(self, user_input: str) -> str:
        """清理用户输入"""
        # 移除零宽字符
        cleaned = re.sub(r"[​‌‍﻿]", "", user_input)

        # 移除控制字符（保留换行和制表符）
        cleaned = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", cleaned)

        return cleaned.strip()

    def stats(self) -> dict:
        return {
            "total_checked": self.total_checked,
            "blocked_count": self.blocked_count,
            "block_rate": self.blocked_count / max(self.total_checked, 1),
        }


# 全局实例
input_filter = InputFilter()
