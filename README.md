# CS-File-Discord-Bot
A bot that integrates the board game "CS-File" into discord.

The bot is now running at a nas server.
However, when I designed to update the bot, there would be no warning before I restart or turn it off.

https://discord.com/api/oauth2/authorize?client_id=632199109792759808&permissions=0&scope=bot

*Use this link to invite the bot to the server*

The default command prefix is `.CSF` , you can use the command `.CSF help` to browse the guide.
The bot is unfinished. So there is no instructions and guidelines yet.

-------------------------

To run the script on your own VPS. 
> Install `python3` and `pip` in your machine.

> Use pip to install `discord.py`.

> Upload the files to a folder and run the `bot.py` at the background.


Run the script at background.
`python3 /path/to/the/folder/bot.py &`

To find the running process.
`ps ax | grep bot.py`

To kill the process.
`kill -9 {the bot.py id} &` or just
`kill {the bot.py id}`
