"""
自定义任务列表插件，用 Unicode 字符替代 checkbox
"""

def plugin_task_lists(md):
    """
    任务列表插件：直接生成 Unicode 字符而非 checkbox
    
    Args:
        md: mistune markdown 实例
    """
    
    def parse_task_list(inline, m, state):
        """解析任务列表项"""
        text = m.group(0)
        return 'task_list', text
    
    # 注册 inline 解析规则
    md.inline.register('task_list', r'^\[([xX ])\]\s+', parse_task_list, before='link')
    
    # 渲染函数
    def render_task_list(renderer, text):
        """渲染任务列表项为 Unicode 字符"""
        import re
        match = re.match(r'^\[([xX ])\]\s+(.*)', text)
        if match:
            status = match.group(1)
            content = match.group(2)
            
            # 根据状态选择图标
            if status.lower() == 'x':
                icon = '✅ '
            else:
                icon = '☐ '
            
            return icon + content
        
        return text
    
    if md.renderer:
        md.renderer.register('task_list', render_task_list)
