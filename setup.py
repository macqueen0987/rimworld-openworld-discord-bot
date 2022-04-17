import os

commands = [
    'python -m pip install --upgrade pip',
    'python -m pip install -U discord.py',
    'pip install importlib',
    'pip install asyncio',
    'pip install requests',
    'pip install beautifulsoup4'
]

# some not very well made setup.
# if you are planning to run only mod updates, all you need is bottom 3
for i in commands:
    os.system(i)