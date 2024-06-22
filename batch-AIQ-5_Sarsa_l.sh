#!/bin/bash

#
# VARIABLES
#

# Reference machines with parameters to AIQ on
machines=(
BF
)

# Agents with parameters to run AIQ on
agents=(
	Sarsa_l,0.0,0.0,0.5,0.04,0.6
	Sarsa_l,0.0,0.0,0.5,0.03,0.6 
	Sarsa_l,0.0,0.0,0.5,0.02,0.8 
	Sarsa_l,0.0,0.0,0.5,0.01,0.9 
	Sarsa_l,0.0,0.0,0.5,0.005,0.95
	Sarsa_l,0.0,0.5,0.5,0.04,0.6 
	Sarsa_l,0.0,0.5,0.5,0.03,0.6 
	Sarsa_l,0.0,0.5,0.5,0.02,0.8 
	Sarsa_l,0.0,0.5,0.5,0.01,0.9 
	Sarsa_l,0.0,0.5,0.5,0.005,0.95
)

# Episode lenghts to test with
episodes=(
100000
)

# Sample size to test with
samples=(
10000
)

# CPU threads to use
threads=8

# Batch AIQ log file
batch_log=batch-AIQ-5.log

#
# MAIN SCRIPT
#

# Check for log directory
if [ ! -d log ]; then
	mkdir log
fi

# Check for log EL directory
if [ ! -d log-el ]; then
	mkdir log-el
fi
# Check for samples directory
if [ ! -d adaptive-samples ]; then
	mkdir adaptive-samples
fi

echo "`date +%F-%T`: Batch AIQ started on `hostname` using ${threads} threads." >> ${batch_log}
# For each machine, agent, episode lenght and sample size 
# test AIQ and log results
for _machine in ${machines[@]}
do
	for _agent in ${agents[@]}
	do
		for _episode in ${episodes[@]}
		do
			for _sample in ${samples[@]}
			do

			echo "`date +%F-%T`: Started round (${_machine}:${_agent}:${_episode}:${_sample})." >> ${batch_log}

			python3 AIQ.py --log --verbose_log_el --log_agent --log_agent_failures --log_interactions -t "${threads}" -r "${_machine}" -a "${_agent}" -l "${_episode}" -s "${_sample}"

			echo "`date +%F-%T`: Ended round (${_machine}:${_agent}:${_episode}:${_sample})." >> ${batch_log}

			done
		done
	done
done
echo "`date +%F-%T`: Batch AIQ ended." >> ${batch_log}
