from subprocess import Popen, PIPE

def create_files(filename,content):
  filecreate = Popen(["touch",filename+'.txt'], stdout=PIPE, stderr=PIPE)
  writeFile = Popen(['echo',content,'>>', filename+'.txt'], stdin=filecreate.stdout, stdout=PIPE, stderr=PIPE).communicate()
  return True

def get_all_files():
  process = Popen(["ls"], stdout=PIPE, stderr=PIPE)
  process2 = Popen(["col","-b"], stdin= process.stdout, stdout=PIPE, stderr=PIPE)
  return process2.communicate()[0].split('\n')


def delete_all_files():
  vip = Popen(["rm","-r","/home/filesystem_user/flask_test/parcial/prueba/*"], stdout=PIPE, stderr=PIPE).communicate()
  return True

def get_recent_files():
  rF = Popen(["ls", "-lat"], stdout=PIPE, stderr=PIPE)
  list = Popen(["awk",'{print $9}'], stdin=rF.stdout, stdout=PIPE, stderr=PIPE).communicate()
  return filter(None,list)
