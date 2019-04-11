from sys import *	
import numpy as np
from math import gcd
#from simso.core import Scheduler

def load_tasks(taskfile):
	f=open(taskfile,"r")
	data=f.read()
	f.close()

	data = data.split('\n')
	tasks = {}
	d_line = []
	n = 0
	lcm = 0
	deadline = 0
	for i in data:
		i=i.split()
		if len(i) > 0:
			tasks[n]={
				'D':int(i[2]), #absolute deadline
				'R':int(i[1]), #release time
				'C':int(i[0]), #computational amount
				'E':0} #wcet			    
			n = n+1	
	for i in range(n):
		d_line.insert(i,tasks[i]['D'])		
	lcm = np.lcm.reduce(d_line)
	#lcm = lcm_cal(tasks,n,deadline)
	return tasks,n,lcm

def lcm_cal(tasks,total,new_d):
	for j in range (0,total):
		if tasks[j]['D'] != new_d:
			old_d = new_d
			new_d = tasks[j]['D']
			if (old_d != 0 and new_d != 0):
				lcm_val = new_d * old_d / gcd (new_d,old_d)
				new_d = lcm_val
									
	return int(lcm_val)
	
def utilization(tasks,total,cores):
	first_c = 0
	second_c = 0	
	first_d = 0
	second_d = 0
	ur = 0.00
	
	for j in range (0,total):
		if (tasks[j]['C'] != 0 or tasks[j]['D'] != 0):
			second_c = first_c
			second_d = first_d
			first_c = tasks[j]['C']
			first_d = tasks[j]['D']
			ur = ur + (float(first_c) / float(first_d))
			
	print ("\nTotal Utilization Rate = %f\n" %(ur))
	if (ur > cores):
		print('Task set cannot be scheduled. Exiting\n')
		exit(1)
	else:
		print('Feasible. Proceeding with Algorithm\n')

def scheduler_edf(tasks, LCM,totalProcesses,cores): 
	earliestDeadline = []
	earliestDeadlineIndexTask = []
	remainCapacity = []
	nextDeadline = []
	processOnlineNewPeriod = []
	coreflag = []
	taskactivate = []
	#to initialize data
	for i in range (0,totalProcesses):
		nextDeadline.insert(i,tasks[i]['D'])
		remainCapacity.insert(i,tasks[i]['C'])
		processOnlineNewPeriod.insert(i,0)
		taskactivate.insert(i,0)
		print ("Task %d has di %d and ci of %d"%(i+1,nextDeadline[i],remainCapacity[i]))
		
	print ("")
	print (' ----------------------------------------')
	print ('| Time\t   : Task   \t\t\t|')
	print (' ----------------------------------------')
	print ("")
	
	#start scheduling...
	for time in range(0,LCM): 		
		for x in range (0,cores):
			coreflag.insert(x,0)
			earliestDeadline.insert(x,LCM)
			earliestDeadlineIndexTask.insert(x,-1)
			for j in range(0,totalProcesses):
				if tasks[j]['R'] <= time:
					taskactivate[j] = 1
					#print "now in core %d checking task %d for Earliest Deadline %d on NextDeadline of job %d with WCET %d assuming core flag is %d and previous core has been assigned to task %d"%(x+1,j+1, earliestDeadline[x], nextDeadline[j], remainCapacity[j],coreflag[x],earliestDeadlineIndexTask[x-1])
					#Using Earliest Deadline First As Basis Trigger, but once detected pre-emption, the task will be assigned to the same processor in the next iteration
					if remainCapacity[j] > 0 and earliestDeadline[x] > nextDeadline[j] and coreflag[x]!=1 and earliestDeadlineIndexTask[x-1]!=j:
						earliestDeadline[x] = nextDeadline[j]
						earliestDeadlineIndexTask[x] = j
						print ("Time %d to %d: Core %d on Task %d Deadline %d"%(time,time+1,x+1,j+1,earliestDeadline[x]))														
						remainCapacity[j]-=1
						coreflag[x]=1									
		
		for x in range (0,cores):
			if coreflag[x] == 0:
				print ("Time %d to %d: Core %d idle"%(time,time+1,x+1))
		
		#If period process is 0 at the next cycle, prepard to renew period
		for k in range(0,totalProcesses):
			if remainCapacity[k]>0 and (nextDeadline[k]-1==0 and taskactivate[k]==1):
				print ("Task %d misses deadline at time = %d, WCET remaining %d"%(k+1,time,remainCapacity[k]))
				exit(1)
			elif processOnlineNewPeriod[k] == (tasks[k]['D']-1) and taskactivate[k] == 1: 
				nextDeadline[k] = tasks[k]['D']
				remainCapacity[k] = tasks[k]['C']
				processOnlineNewPeriod[k] = 0					
			elif nextDeadline[k]>=0 and taskactivate[k] == 1:
				nextDeadline[k]-=1
				processOnlineNewPeriod[k]+=1							
		coreflag[x]=0
		print("----------------------------"	)
		
def scheduler_eltbf(tasks,LCM,totalTasks,cores):
	
	TB = []
	TF = []
	NewPeriod = []
	coreflag = []
	taskflag = []
	taskactivate = []
	C = []
	D = []
	E = []
	TBmin = []
	TBminindex = []
	
	for i in range (totalTasks):
		D.insert(i,tasks[i]['D'])
		C.insert(i,tasks[i]['C'])
		E.insert(i,0)
		NewPeriod.insert(i,0)
		taskactivate.insert(i,0)
		TB.insert(i,0)
		TF.insert(i,0)
		taskflag.insert(i,0)
		print ("Task %d has di %d and ci of %d"%(i+1,D[i],C[i]))
		
	print ("")
	print (' ----------------------------------------')
	print ('| Time\t   : Task   \t\t\t|')
	print (' ----------------------------------------')
	print ("")
		
	#start scheduling...
	for time in range(LCM): 		
		for j in range(totalTasks):			
			for x in range(cores):
				TBmin.insert(x,1000)
				TBminindex.insert(x,-1)
				coreflag.insert(x,0)
				if tasks[j]['R'] <= time:
					taskactivate[j] = 1
					TB[j] = D[j] - C[j] - NewPeriod[j]
					TF[j] = NewPeriod[j]
					#print ("Time %d to %d: Core %d on Task %d TB %d"%(time,time+1,x+1,TBminindex[x]+1,TBmin[TBminindex[x]]))		
					#print ("core at %d with task checking at %d --> TBmin is %d under Task %d"%(x+1, j+1, TBmin[x],TBminindex[x]+1))
		for n in range (0,cores):
			for k in range (0,totalTasks):
				#print ("core at %d with task checking at %d --> TBmin is %d under Task %d"%(n+1, k+1, TBmin[n],TBminindex[n]+1))
				if taskactivate[k] == 1 and TBmin[n] >= TB[k] and TBminindex[n] != k and coreflag[n] == 0 and taskflag[k] == 0 and TBminindex[n-1] != k and C[k] > 0 and E[n] != tasks[k]['C']:
					TBmin[n] = TB[k]
					TBminindex[n] = k
					coreflag[n] = 1
					taskflag[k] = 1
					C[k] -= 1
					E[k] += 1
					#print ("core at %d with task checking at %d --> TBmin is %d under Task %d"%(n+1, k+1, TBmin[n],TBminindex[n]+1))
					print ("Time %d to %d: Core %d on Task %d status = %d with TB %d with WCET %d having Deadline %d"%(time,time+1,n+1,TBminindex[n]+1,taskactivate[k],TBmin[TBminindex[n]],C[k],D[k]))			
		for i in range (totalTasks):
			if i != TBminindex[0] and i != TBminindex[1]:
				TB[i]-=1
				TF[i]+=1
		for k in range(totalTasks):	
			#print ("Task %d with deadline %d at time = %d, WCET remaining %d with NewPeriod %d"%(k+1,D[k],time,C[k],NewPeriod[k]))
			if C[k]>0 and D[k]-1<=0 and taskactivate[k] == 1:
				print ("Task %d misses deadline at time = %d, WCET remaining %d for Deadline %d with NewPeriod %d"%(k+1,time,C[k],D[k]-1,NewPeriod[k]))
				exit(1)
			elif NewPeriod[k] == (tasks[k]['D']-1): 
				D[k] = tasks[k]['D']
				C[k] = tasks[k]['C']
				E[k] = 0
				NewPeriod[k] = 0			
			#elif D[k]>0 and taskactivate[k] == 1:
			elif D[k]>0:
				D[k]-=1
				NewPeriod[k]+=1	
		
		for x in range (0,cores):
			if coreflag[x] == 0:
				print ("Time %d to %d: Core %d idle"%(time,time+1,x+1))
		
		for x in range(cores):
			coreflag[x] = 0
		for y in range (totalTasks):
			taskflag[y] = 0

		print("----------------------------"	)

def scheduler_lezl (tasks,LCM,totalTasks,cores):
	NewPeriod = []
	coreflag = []
	taskflag = []
	taskactivate = []
	C = []
	D = []
	E = []
	LE = []		#Large Execution List
	LX = []		#Laxity
	TaskIndex = []
	prevtasktoprocessor = []
	x = 0
	for i in range (totalTasks):
		D.insert(i,tasks[i]['D'])
		C.insert(i,tasks[i]['C'])
		E.insert(i,0)
		NewPeriod.insert(i,0)
		taskactivate.insert(i,0)
		taskflag.insert(i,0)
		LE.insert(i,-10)
		LX.insert(i,1000)
		print ("Task %d has di %d and ci of %d"%(i+1,D[i],C[i]))
	
	print ("")
	print (' ----------------------------------------')
	print ('| Time\t   : Task   \t\t\t|')
	print (' ----------------------------------------')
	print ("")
		
	#start scheduling...
	for time in range(LCM): 		
		for n in range(cores):
			coreflag.insert(n,0)
			TaskIndex.insert(n,0)	
			prevtasktoprocessor.insert(n,0)
		for j in range(totalTasks):			
			if tasks[j]['R'] <= time:
				taskactivate[j] = 1
				LE[j] = C[j]
				LX[j] = tasks[j]['D'] - C[j] - NewPeriod[j]
					
		LE.sort()
		x = 1
		for n in range(cores):
			TaskIndex[n] = LE[-x]-1
			x+=1
			print(n,TaskIndex[n])
			for j in range(totalTasks):
				if LX[j] == 0:
					TaskIndex[n] = j
					taskflag[n] = 1
					coreflag[n] = 1
				elif C[j] > 0 and coreflag[n] == 0:
					TaskIndex[n] = j
					taskflag[n] = 1
					coreflag[n] = 1
				
			
		for n in range(cores):
			for j in range(totalTasks):
				#print ("Time %d to %d: Core %d currently on Task %d LE %d vs Laxity %d --> max LEmatch %d"%(time,time+1,n+1,j+1,C[j],LX[j],TaskIndex[n]+1))
				if taskactivate[j] == 1 and coreflag[n] == 1 and taskflag[j] == 1 and C[j] > 0 and TaskIndex[n] == j:
					C[j]-=1
					E[j]+=1
					print ("Time %d to %d: Core %d on Task %d with WCET %d with Laxity %d"%(time,time+1,n+1,j+1,C[j],LX[j]))
					# elif LE[j] > 0:
						# prevtasktoprocessor[n] = j
						# coreflag[n] = 1
						# taskflag[j] = 1
						# C[j]-=1
						# E[j]+=1
						# print ("Time %d to %d: Core %d on Task %d Largest Execution %d with WCET %d with Laxity %d"%(time,time+1,n+1,j+1,LE[j],C[j],LX[j]))
				
				
		for k in range(totalTasks):	
			#print ("Task %d with deadline %d at time = %d, WCET remaining %d with NewPeriod %d"%(k+1,D[k],time,C[k],NewPeriod[k]))
			if C[k]>0 and D[k]-1<=0 and taskactivate[k] == 1:
				print ("Task %d misses deadline at time = %d, WCET remaining %d for Deadline %d with NewPeriod %d"%(k+1,time,C[k],D[k]-1,NewPeriod[k]))
				exit(1)
			elif NewPeriod[k] == (tasks[k]['D']-1): 
				D[k] = tasks[k]['D']
				C[k] = tasks[k]['C']
				E[k] = 0
				NewPeriod[k] = 0			
			#elif D[k]>0 and taskactivate[k] == 1:
			elif D[k]>0:
				D[k]-=1
				NewPeriod[k]+=1	
		
		for x in range (0,cores):
			if coreflag[x] == 0:
				print ("Time %d to %d: Core %d idle"%(time,time+1,x+1))
				# for j in range(totalTasks):
					# if C[j] > 0 and coreflag[x] != 1 and taskflag[j] != 1:
						# print ("Time %d to %d: Core %d on Task %d with WCET %d with Laxity %d"%(time,time+1,n+1,j+1,C[j],LX[j]))
						# coreflag[n] = 1
						# taskflag[j] = 1
						# C[j]-=1
						# E[j]+=1						
					
		for x in range(cores):
			coreflag[x] = 0
		for y in range (totalTasks):
			taskflag[y] = 0			
					
	
if __name__=='__main__':
	if len(argv) < 2:
		print ('\nSimulation Project: Testing %s using test data\n'%argv[0])
		#exit(1)
	task_main,total,hp = load_tasks("testfile.txt")
	print("-----------------------------------------")	
	print("Total Number of tasks : %d with LCM %d" %(total,hp))
	print("-----------------------------------------")	
	utilization(task_main,total,2)
	#s = scheduler_eltbf(task_main,hp,total,2)
	s = scheduler_lezl(task_main,hp,total,2)
	print("Scheduling complete")
	
	
	