# Simple Abyss webserver setup
This is one of the easiest and most effective ways to be able to view the documents you downloaded.

1. Download the FSM data.  If you create an ISO during the process, you'll need to right click and "mount" the ISO as a disk drive.
2. Download the Abyss web server from [Aprelium](https://aprelium.com/abyssws/download.php). There are Windows, Mac, and Linux versions so this should work for Mac users too.
3. Run the installer. 
4. Select the defaults
5. When it's done you'll get a message saying "Setup has completed. Abyss Web Server service was successfully restarted". However the service may or may not have actually started.
6. Go to your start menu and run the "Abyss Web Server Startup Configuration". ![Startup](/abyss-images/startup.png)
7. Change the startup method to "Install as a Windows Service" and leave "Start automatically on computer startup" selected. You'll get a confirmation which says "Abyss Web Server service is installed". ![Startup Method](/abyss-images/startup-method.jpg)
8. You will now configure the web server settings.  Go back to the start menu and select "Abyss Web Server X1". This will launch the configuration console in your web browser at http://127.0.0.1:9999/. You'll use the credentials you just created to log in
9. Select English
10. Create an administrative name and password to manage the configuration (admin/admin or admin/password is probably fine for this).
11. After clicking "OK" you'll be prompted to log in with the username and password you just set up.
12. Under the "Hosts" section click the "Configure" button
13. Click the "General" link/icon (first one)
14. Set your "Documents Path" to wherever you saved the FSM data to in step #1, then click "OK" in the bottom right corner.  I used my whole D:\ here because I have my whole FSM packaged as an ISO file, but you might have saved your download to C:\FSM-Download\ for instance.  If you do create an ISO using the make-iso.sh script, you will need to right-click and "mount" it before proceeding.  ![General](/abyss-images/general.png)
15. If you want to prevent anyone else from trying to use your PC (highly recommended), click the "Default Host On Port 80" navigation link and then click the "IP Address Control Rules" link/icon next and then add an "Allowed IP Address" of "127.0.0.1" and click "OK". Next set the "Virtual Path" to "/". Then click "OK" in the bottom right corner. (Note: I recommend doing this since I cannot vouch for the security of the Abyss web server or the Toyota TIS website code).  ![IP Restrictions](/abyss-images/ipaddress.png)
16. Click the "Abyss Web Server Console" link near the top to take you back to the "home page" for the configuration menus
17. Click the "Server Configuration" link
18. Next select "Mime Types".
19. In the "Custom MIME Types List" at the top, click "add". Create a MIME type of "text/html" and add an associated extension of "jsp". (Note: Setting this is the "magic sauce" which makes Abyss a viable webserver. I tried a few other servers like Fenix but they didn't support adding a JSP extension and without this your browser will just try to download the file locally instead of displaying it). ![Mime Types](/abyss-images/mimetypes.png)
20. Click "OK". You should have a banner prompting you to click "Restart" to apply your changes. Do so now.
21. Give it a few seconds to restart, and then point your browser to "http://127.0.0.1/"
22. Browse away!

For those who go the Abyss Web Server route, keep in mind you'll need to restart the webserver each time you reboot if you didn't configure it to start automatically at boot when you installed it as described above.  If you can't get to the administrative configuration interface at [http://127.0.0.1:9999/](http://127.0.0.1:9999/) then that's likely the issue.

Go to the Windows search and type "Abyss Web Server Startup Configuration". You can change it from "Manual Startup" to "Install as a Windows Service" (my preference) and click OK. Then hit CTRL-ALT-DEL and open Task Manager, go to the "Services" tab, right-click on "AbyssWebServer" and click "Start". From that point forward it should be running and it should start on future reboots for you. If you ever want to disable it just repeat this paragraph but change it to "Manual startup" or unselect the "start at boot" box and you can always start it by hand in the task manager services tab.
