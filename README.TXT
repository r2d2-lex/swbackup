Backup switches configuration on TFTP

1. Install tftp server on Debian:
 # apt install tftpd-hpa
 # systemctl enable tftpd-hpa
 # vim /etc/default/tftpd-hpa

TFTP_USERNAME="tftp"
TFTP_DIRECTORY="/srv/tftp"
TFTP_ADDRESS="0.0.0.0:69"
TFTP_OPTIONS="-4 --create --secure -vvv"

 # systemctl restart tftpd-hpa
