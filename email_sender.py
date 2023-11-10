import smtplib
from email.mime.text import MIMEText

class EmailSender:
    ''' 用于发送邮件 '''
    def __init__(self, from_addr, to_addr, passwd) -> None:
        self.from_addr = from_addr
        self.to_addr = to_addr
        self.passwd = passwd

    def send(self, title: str, txt:str):
        """ 发送消息 """
        msg = MIMEText(txt)
        msg['Subject'] = title
        msg['From'] = self.from_addr
        msg['To'] = self.to_addr

        s = smtplib.SMTP_SSL("smtp.qq.com", 465)
        s.login(self.from_addr, self.passwd)
        s.sendmail(self.from_addr, self.to_addr, msg.as_string())
        s.quit()

if __name__ == '__main__':
    email = EmailSender('发送邮箱', '接收邮箱', '密钥（qq邮箱可以查看）')
    email.send("邮件标题", "邮件内容")
    pass