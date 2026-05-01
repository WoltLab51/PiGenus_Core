# PiGenus Deployment

Copy service files to /etc/systemd/system/, then:

```bash
sudo systemctl daemon-reload
sudo systemctl enable pigenus
sudo systemctl start pigenus
```
