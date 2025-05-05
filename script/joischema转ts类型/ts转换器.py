import re

# Joi schema 作为字符串
joi_schema = """
import Joi from 'joi'

export const register_login_schema = Joi.object({
    account: Joi.string().pattern(/^(1[3-9]\\d{9}|[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,})$/).required().messages({
        'string.pattern.base': '账号必须是有效的手机号码或电子邮件地址',
        'string.empty': '账号是必填项'
    }),
    password: Joi.string().pattern(/^(?=.*[A-Za-z])(?=.*\\d)[A-Za-z\\d]{6,20}$/).required().messages({
        'string.pattern.base': '密码必须是6-20个字符长，并且包含至少一个字母和一个数字',
        'string.empty': '密码是必填项',
    })
})
"""

# 正则表达式用于提取字段及其验证规则
field_pattern = re.compile(r"(\w+):\s*Joi\.(\w+)\(([^)]*)\)", re.DOTALL)

# 查找所有字段
fields = field_pattern.findall(joi_schema)



def extract_type(joi_rule):
    """根据 Joi 规则返回对应的 TypeScript 类型"""
    if 'string().pattern' in joi_rule:
        return 'string'  # 匹配 pattern
    elif 'string()' in joi_rule:
        return 'string'  # 普通的 string 类型
    elif 'number()' in joi_rule:
        return 'number'
    elif 'boolean()' in joi_rule:
        return 'boolean'
    return 'any'  # 默认类型

# 生成 TypeScript 类型
ts_types = {}
for field, joi_type, joi_rule in fields:
    # 只考虑需要的验证规则（如 pattern、empty、required 等）
    if any(rule in joi_rule for rule in validation_rules):
        ts_types[field] = extract_type(joi_rule)

# 输出 TypeScript 类型定义
ts_definition = "export interface RegisterLogin {\n"
for field, ts_type in ts_types.items():
    ts_definition += f"  {field}: {ts_type};\n"
ts_definition += "}"

print(ts_definition)
