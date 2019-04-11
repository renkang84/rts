#NUMPY version setuptools 39.1.0 is installed
#NUMPY version 1.16.2 installed
#Tested on python 2.7.10 (using Python (x,y) for Matlibplot simulation

from fractions import gcd
import numpy as np

def lcm_cal(d,total):
	new_d = 0
	for j in range (0,total):
		if d[j] != new_d:
			old_d = new_d
			new_d = d[j]
			if (old_d != 0 and new_d != 0):
				lcm_val = new_d * old_d / gcd (new_d,old_d)
				new_d = lcm_val
									
	return lcm_val

def utilization(d,c,total):
	first_c = 0
	second_c = 0	
	first_d = 0
	second_d = 0
	ur = 0.00
	
	for j in range (0,total):
		if (c[j] != 0 or d[j] != 0):
			second_c = first_c
			second_d = first_d
			first_c = c[j]
			first_d = d[j]
			ur = ur + (float(first_c) / float(first_d))
			
	print "\nTotal Utilization Rate = %f" %(ur)	

def main():
	n = 30 #where you input the amount of task list required
	d = []
	c = []
	r = []
	f = open("test_file.txt","w+") #where you mod the file type for reference
	#np.random.seed(1)
	for i in range(n):
		d.insert(i,np.random.randint(100,high=1000))  
		c.insert(i,np.random.randint(1,high=10))
		r.insert(i,0)
	#HP = np.lcm.reduce(d)
	for i in range(n):
		#r.insert(i,np.random.randint(0,high=(d[i]-c[i]+1)))
		print "%d %d %d"%(c[i],r[i],d[i])
		f.write("%d %d %d\n"%(c[i],r[i],d[i]))
	
	
	#print HP
	print lcm_cal(d,n)
	utilization(d,c,n)
	f.close()
	
	
if __name__== "__main__":
	main()