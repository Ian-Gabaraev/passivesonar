Create a new service file for your script in the `````/etc/systemd/system/````` directory. You'll need root privileges to create this file. 
We'll name it systemd_listen.service.

```bash
sudo systemctl daemon-reload
sudo systemctl start systemd_listen.service
sudo systemctl enable systemd_listen.service
sudo systemctl status systemd_listen.service
journalctl -u systemd_listen.service -f

```