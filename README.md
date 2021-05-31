# CS-File-Discord-Bot
A bot that integrates the board game "CS-File" into discord.  
I do not own any copyrights of all the image involved in this project.  

The bot is currently running at a NAS.  
However, when I designed to update the bot, there would be no warning before I restart or turn it off.  

https://discord.com/api/oauth2/authorize?client_id=632199109792759808&permissions=8&scope=bot  
*Use this link to invite the bot to the server*

The default command prefix is `.CSF` , you can use the command `.CSF help` to browse the guide.  
The bot is unfinished. So there is no instructions and guidelines yet.

-------------------------

To run the script on your own VPS. You have to make yourself a new discord bot

Check https://discord.com/developers/applications for more informations

0. Clone this project  
`git clone https://github.com/danni-boii/CS-File-Discord-Bot.git`

1. Modify the token setting  
Put your bot token at line 2 in this file [/setting/json](/setting.json#L2)  
  ```json
      "TOKEN":"[Your Discord Bot Token Here]" ,
  ```

2. Install `python3` and `pip` in your machine.  
e.g. At ubuntu `apt-get install python3 pip`
 
3. Use pip to install `discord.py`.  
`pip install discord.py`
 
4. Upload the files to a folder and run the `bot.py` at the background.

---

### Run the script at background.

`nohup python3 /path/to/the/folder/bot.py &`

### To find the running process.

`ps ax | grep bot.py`

### To kill the process.

`kill -9 {the bot.py id} &`  
or just  
`kill {the bot.py id}`
