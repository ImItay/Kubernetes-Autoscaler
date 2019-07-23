#!/usr/bin/env python

import sys
import time
import subprocess
from math import ceil

_verbose = False		

TARGET_CPU	= 50			# max CPU load we want for our pods
MAX_PODS	= 10			# max pods to scale into
SAMPLES		= 5			# set how many samples (~~seconds) to check before scaling

for key in range(1, len(sys.argv)):
	if sys.argv[key] == "--verbose":						# check whether we need to output
		_verbose = True if int(sys.argv[key+1]) == 1 else False
	elif sys.argv[key] == "--target-cpu":						# change target cpu
		TARGET_CPU = int(sys.argv[key+1])
		if TARGET_CPU <= 0:
			TARGET_CPU = 50
	elif sys.argv[key] == "--max-pods":						# change the maximum pods allowed
		MAX_PODS = int(sys.argv[key+1])
		if MAX_PODS <= 0:
			MAX_PODS = 10

if not _verbose:
	print("Running!")
	print("you might want to change setting by using:")
	print("\tscaler.py --verbose 1 --target-cpu 50 --max-pods 10")

timer		= 0			# time counter
currentPods	= 2			# starting point
lastSamples	= []			# keep samples of the last <SAMPLES> seconds CPU load

# make sure we have 2 pods at the start
subprocess.check_output('kubectl scale --replicas=2 deployment php-apache-manual', shell=True)

while(True):
	i = timer % SAMPLES		# set our iteration index
	
	cpu = 0.0			# reset the summation base
	getPods		= subprocess.check_output('kubectl get pods | grep php-apache-manual | cut -d \' \' -f1', shell=True).splitlines()		# extract pod names, by the required deployment
	podsStatus	= subprocess.check_output('kubectl get pods | grep php-apache-manual | cut -d \' \' -f4', shell=True).splitlines()		# extract pod statuses, by the required deployment
	
	for idx in range(0, len(getPods)):		# sum CPU utilization for all pods
		if podsStatus[idx] != "1/1":		# check if the pod is running, because if it isn't - running commands on it will crash the script
			if _verbose:
				print("pod {} isn't ready".format(getPods[idx]))
			continue
		
		# extract the CPU load from inside each of the pods, and grab it from the summery of the `top` command
		getTop = subprocess.check_output('kubectl exec {} -i -t -- top -b -d1 -n2 | grep -i "Cpu(s)"'.format(getPods[idx]), shell=True).splitlines()
		res = " ".join(getTop[1].split()).split(" ")
		
		try:	# wrap the casting - there are some cases that `top` doesn't returning a number in the right place, so when it happen - make sure we won't crash
			cpu += (float(res[1]) + float(res[3]) + float(res[5]))		# sum CPU by user-space + system + nice
		except ValueError:
			if _verbose:
				print("\tWarning: couldn't sum CPU for {}".format(getPods[idx]))
			pass
	
	lastSamples.append(cpu)			# add the current CPU sum to our samples array
	if _verbose:
		print("{}. total CPU usage: {}".format(i, cpu))
	
	if i == SAMPLES-1:			# if we're on the last sample - calculate the average load and divide by the target load, to decide how many pods we need
		averageLoad = sum(lastSamples) / len(lastSamples)
		scaledPods  = int(ceil(averageLoad/TARGET_CPU))			# divide current CPU by target CPU needed, round up and convert to natural number
		
		if _verbose:
			print("\t Average CPU load: {}".format(averageLoad))
		
		if scaledPods > MAX_PODS:					# don't pass the MAX_PODS allowed
			scaledPods = MAX_PODS
		
		if scaledPods < 2:						# don't get below the minimum pods allowed
			scaledPods = 2
		
		if scaledPods != currentPods:
			if _verbose:
				print("pods have scaled from {} to {}".format(currentPods, scaledPods))
			# scale the pods to the required amount
			subprocess.check_output('kubectl scale --replicas={} deployment php-apache-manual'.format(int(scaledPods)), shell=True)
			currentPods = scaledPods				# update the current pods value
			
			time.sleep(3)						# sleep extra 3 seconds, so the pods list will get to update
		
		del lastSamples[:]						# clear all the samples before re-summing
	
	timer += 1
	time.sleep(1)								# sleep for 1 second before doing it again
