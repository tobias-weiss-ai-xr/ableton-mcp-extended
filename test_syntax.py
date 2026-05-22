import ast

with open('C:/Users/Tobias/git/ableton-mcp-extended/MCP_Server/browser_cache.py', 'r', encoding='utf-8') as f:
    content = f.read()

try:
    ast.parse(content)
    print('Syntax OK')
except SyntaxError as e:
    print(f'SyntaxError at line {e.lineno}: {e.msg}')
    # Print context around error
    lines = content.split('\n')
    start = max(0, e.lineno - 3)
    end = min(len(lines), e.lineno + 2)
    for i in range(start, end):
        marker = '>>> ' if i == e.lineno - 1 else '    '
        print(f'{marker}{i+1}: {repr(lines[i][:80])}')