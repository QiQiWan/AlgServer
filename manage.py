#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'algserver.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    # manage.py 文件中的 main 方法
    from django.core.management.commands.runserver import Command as Runserver  
    Runserver.default_addr = '127.0.0.1'  # 修改默认地址  
    Runserver.default_port = '8090'  # 修改默认端口  

    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()