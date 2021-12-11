# Simple Abyss webserver setup
This is one of the easiest and most effective ways to be able to view the documents you downloaded.

1. Download the FSM data
2. Download the Abyss web server from [Aprelium](https://aprelium.com/abyssws/download.php). There are Windows, Mac, and Linux versions so this should work for Mac users too.
3. Run the installer. When it's done you'll have to set up an administrative name and password to manage the configuration (admin/admin or admin/password is probably fine for this). The installer will then launch your web browser and direct you to log in at http://127.0.0.1:9999/. You'll use the credentials you just created to log in.
4. Under the "Hosts" section click the "Configure" button
5. Click the "General" link/icon (first one)
6. Set your "Documents Path" to wherever you saved the FSM data to in step #1, then click "OK" in the bottom right corner.  I used my whole D:\ here but you might have saved your download to C:\FSM-Download\ for instance.  ![General](/abyss-images/general.png)
7. If you want to prevent anyone else from trying to use your PC, click the "IP Address Control Rules" link/icon next and then add an "Allowed IP Address" of "127.0.0.1" and click "OK". Next set the "Virtual Path" to "/". Then click "OK" in the bottom right corner. (Note: I recommend doing this since I cannot vouch for the security of the Abyss web server or the Toyota TIS website code).  ![IP Restrictions](/abyss-images/ipaddress.png)
8. Click the "Abyss Web Server Console" link near the top to take you back to the "home page" for the configuration menus
9. Click the "Server Configuration" link
10. Next select "Mime Types".
11. In the "Custom MIME Types List" at the top, click "add". Create a MIME type of "text/html" and add an associated extension of "jsp". (Note: Setting this is the "magic sauce" which makes Abyss a viable webserver. I tried a few other servers like Fenix but they didn't support adding a JSP extension and without this your browser will just try to download the file locally instead of displaying it). ![Mime Types](/abyss-images/mimetypes.png)
12. Click "OK". You should have a banner prompting you to click "Restart" to apply your changes. Do so now.
13. Give it a few seconds to restart, and then point your browser to "http://127.0.0.1/"
14. Browse away!

For those who go the Abyss Web Server route, keep in mind you'll need to restart the webserver each time you reboot if you didn't configure it to start automatically at boot when you installed it.  If you can't get to the administrative configuration interface at [http://127.0.0.1:9999/](http://127.0.0.1:9999/) then that's likely the issue.

Go to the Windows search and type "Abyss Web Server Startup Configuration". You can change it from "Manual Startup" to "Install as a Windows Service" (my preference) and click OK. Then hit CTRL-ALT-DEL and open Task Manager, go to the "Services" tab, right-click on "AbyssWebServer" and click "Start". From that point forward it should be running and it should start on future reboots for you. If you ever want to disable it just repeat this paragraph but change it to "Manual startup" or unselect the "start at boot" box and you can always start it by hand in the task manager services tab.
