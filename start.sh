cp . -r /usr/share/speedbot
cp speedbot.service /usr/lib/systemd/user

systemctl --user enable speedbot
systemctl --user stop speedbot
systemctl --user start speedbot
