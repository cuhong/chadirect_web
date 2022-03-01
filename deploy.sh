source /home/ubuntu/core/.env/bin/activate
git pull
python /home/ubuntu/core/src/manage.py migrate
sudo systemctl restart itechs-core.service
service supervisor restart

as-is : https://221.168.32.67:7001/api/service
to-be : https://apigw.infotech.co.kr/api/service (IP:PORT 221.168.37.75:443)