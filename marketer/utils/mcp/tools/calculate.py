from mcp.server.fastmcp import FastMCP


# 계산 함수들
def add(a: float, b: float) -> float:
    """두 수를 더합니다."""
    return a + b


def subtract(a: float, b: float) -> float:
    """첫 번째 수에서 두 번째 수를 뺍니다."""
    return a - b


def multiply(a: float, b: float) -> float:
    """두 수를 곱합니다."""
    return a * b


def divide(a: float, b: float) -> float | str:
    """첫 번째 수를 두 번째 수로 나눕니다."""
    return a / b if b != 0 else "Error: Division by zero"


# FastMCP 서버 생성
mcp = FastMCP("calculate")


# 연산 등록
@mcp.tool()
def calculate(operation: str, a: float, b: float) -> float | str:
    """기본 계산기 연산을 수행합니다."""
    operations = {
        "add": add,
        "subtract": subtract,
        "multiply": multiply,
        "divide": divide,
    }

    if operation not in operations:
        return f"Error: Unknown operation '{operation}'"

    return operations[operation](a, b)


if __name__ == "__main__":
    mcp.run()
