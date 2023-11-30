
from datetime import datetime

class Logger:
    
    def __init__(self, enable):
        self.log = []
        self.enable = enable
        self.file_name = './static/log/'+datetime.now().strftime('%Y-%m-%d')
        
    def info(self, message):
        if self.enable:
            fmt_msg = self.format_message('INFO',message)
            self.log.append(fmt_msg)
        
    def warn(self, message):
        if self.enable:
            fmt_msg = self.format_message('WARN',message)
            self.log.append(fmt_msg)

    def error(self, message):
        if self.enable:
            fmt_msg = self.format_message('ERRO',message)
            self.log.append(fmt_msg)
            self.save(self.file_name+'_error.log',fmt_msg)
    
    def format_message(self,type,message):
        fmt_msg = "{} {}: {}\n".format(datetime.now(), '['+type+']', message)
        return fmt_msg 
    
    def save(self,file_name,message):
        with open(file_name, 'a', encoding='utf-8') as file:
            file.write(message)