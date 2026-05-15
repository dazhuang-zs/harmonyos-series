"""输出安全校验：防止恶意代码和敏感信息泄露"""

import re

# 危险代码模式
DANGEROUS_CODE_PATTERNS = [
    # 文件系统破坏
    r"rm\s+-rf\s+/",
    r"os\.remove\(|os\.rmdir\(|shutil\.rmtree\(",
    r"fs\.(unlink|rm|rmdir)\(",

    # 命令注入
    r"subprocess\.call\(.*shell\s*=\s*True",
    r"os\.system\(",
    r"exec\(|eval\(",
    r"child_process\.",

    # 网络外传
    r"curl\s+.*\|\s*(bash|sh)",
    r"wget\s+.*\|\s*(bash|sh)",
    r"fetch\(.*\.then\(.*eval",

    # 密钥/凭证硬编码
    r"(api[_-]?key|password|secret|token)\s*=\s*['\"][^'\"]{8,}['\"]",

    # SQL 注入
    r"(DROP|DELETE|TRUNCATE)\s+TABLE",
    r"';\s*(DROP|DELETE|INSERT|UPDATE)",
]

# 敏感信息模式
SENSITIVE_PATTERNS = [
    # API Keys
    r"sk-[a-zA-Z0-9]{20,}",
    r"AKIA[0-9A-Z]{16}",
    r"ghp_[a-zA-Z0-9]{36}",

    # 私钥
    r"-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----",

    # 内部 IP
    r"10\.\d{1,3}\.\d{1,3}\.\d{1,3}",
    r"172\.(1[6-9]|2[0-9]|3[01])\.\d{1,3}\.\d{1,3}",
    r"192\.168\.\d{1,3}\.\d{1,3}",
]

_dangerous_regex = re.compile("|".join(DANGEROUS_CODE_PATTERNS), re.IGNORECASE)
_sensitive_regex = re.compile("|".join(SENSITIVE_PATTERNS))


class OutputFilter:
    """输出安全过滤器"""

    def __init__(self):
        self.total_checked = 0
        self.flagged_count = 0

    def check(self, output: str) -> dict:
        """
        检查 LLM 输出是否安全

        Returns:
            {
                "safe": bool,
                "warnings": list[str],
                "risk_level": str,
            }
        """
        self.total_checked += 1
        warnings = []

        # 检查危险代码
        dangerous_match = _dangerous_regex.search(output)
        if dangerous_match:
            self.flagged_count += 1
            warnings.append(f"检测到潜在危险代码: '{dangerous_match.group()[:50]}'")

        # 检查敏感信息泄露
        sensitive_match = _sensitive_regex.search(output)
        if sensitive_match:
            self.flagged_count += 1
            warnings.append(f"检测到可能的敏感信息: '{sensitive_match.group()[:30]}...'")

        risk_level = "high" if len(warnings) >= 2 else "medium" if warnings else "low"

        return {
            "safe": len(warnings) == 0,
            "warnings": warnings,
            "risk_level": risk_level,
        }

    def sanitize(self, output: str) -> str:
        """清理输出中的敏感信息"""
        cleaned = _sensitive_regex.sub("[REDACTED]", output)
        return cleaned

    def stats(self) -> dict:
        return {
            "total_checked": self.total_checked,
            "flagged_count": self.flagged_count,
            "flag_rate": self.flagged_count / max(self.total_checked, 1),
        }


# 全局实例
output_filter = OutputFilter()
