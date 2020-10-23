systemctl --user stop speedbot
systemctl --user disable speedbot

cp . -r /usr/share/speedbot
cp speedbot.service /usr/lib/systemd/user

systemctl --user start speedbot
systemctl --user enable speedbot
