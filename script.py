#!/usr/bin/env python
import	sched, time, subprocess
from threading import Timer

def clone():

	# Скачивание репозитория и копирование Dockerfile 
	cmd = 'git clone https://github.com/trtrtr95/testcase-pybash.git'
	cp = 'cp Dockerfile testcase-pybash'
	version = 1
	
	fcmd = subprocess.Popen(cmd, shell = True)
	fcmd.wait()
	fcp = subprocess.Popen(cp, shell = True)

	# Сборка первого билда
	build = 'docker build -t testcase-pybash:v.%s'%version +' testcase-pybash/'
	resbuild = subprocess.Popen(build, shell = True)
	resbuild.wait()
	# Запуск первого билда
	drun = 'docker run -p 80:80 -d --name testcase-v.%s'%version + ' testcase-pybash:v.%s'%version
	resdrun = subprocess.Popen(drun, shell = True)
	resdrun.wait()

clone()

def job():

	version = 1
	t = 120 # Заданный интервал в секундах

	def run():

		nonlocal version
		Timer(t, run).start ()


		# Проверка изменений во всех ветках репозитория, загрузка всех изменений и выгрузка списка веток в файл
		sync = 'cd testcase-pybash/ && git pull'
		fsync = subprocess.Popen(sync, shell = True, stderr = open('tmp1', 'w'), stdout = subprocess.PIPE)
		fsync.wait()
		fsync = fsync.stdout.read().strip()

		br = "cat tmp1 |grep origin |awk '{print $2}'"
		fbr = subprocess.Popen(br, shell = True, stdout = open('tmp2', 'w'))
		fbr.wait()

		file = open('tmp1', 'r')
		count = len(file.read())
		file.close()

		# Проверка наличия изменений в текущей ветке
		if count == 0:
			print("Already up to date. If you make changes to the repo, a new container will be created")
			rm = 'rm tmp1 tmp2'
			resrm = subprocess.Popen(rm, shell = True)
			resrm.wait()
		else:
			file = open('tmp2', 'r')
			for item in file.readlines(): #Идём по всем веткам
				branch = item.strip()
				check = 'cd testcase-pybash/ && git checkout %s'%branch
				fcheck = subprocess.Popen(check, shell = True)
				fcheck.wait()
				# Передача author и hash commit в label 
				logcm = "cd testcase-pybash/ && git log -n 1 |grep commit |awk '{print $2}'"		
				logat = "cd testcase-pybash/ && git log -n 1 |grep Author: |awk '{print $2 $3}'"
				flogcm = subprocess.Popen(logcm, shell = True, stdout = subprocess.PIPE)
				flogcm.wait()
				flogcm = flogcm.stdout.read().strip()
				flogat = subprocess.Popen(logat, shell = True, stdout = subprocess.PIPE)
				flogat.wait()
				flogat = flogat.stdout.read().strip()
				
				version+=1
				# Сборка нового билда
				build = 'docker build --label "commit hash=%s'%flogcm + '" --label "maintaner=%s'%flogat + '" --label "branch=%s'%branch + '" -t testcase-pybash:v.%s'%version +' testcase-pybash/'
				resbuild = subprocess.Popen(build, shell = True)
				resbuild.wait()
				# Остановка контейнера в случае повторного билда
				version = version - 1
				stop = 'docker stop testcase-v.%s'%version
				resstop = subprocess.Popen(stop, shell = True)
				version = version + 1 
				resstop.wait()
				# Запуск нового билда
				drun = 'docker run -p 80:80 -d --name testcase-v.%s'%version + ' testcase-pybash:v.%s'%version
				resdrun = subprocess.Popen(drun, shell = True)
				resdrun.wait()
		file.close()
	run ()
	rm = 'rm tmp1 tmp2'
	resrm = subprocess.Popen(rm, shell = True)
	resrm.wait()

job()



