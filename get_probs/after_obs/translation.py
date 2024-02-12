import benchmark
import os

class Probabilistic_PR :
	
	def __init__( self, domain, problem, obs, domain_with_constants, domain_name, max_time = 1800, max_mem = 2048 ) :
		self.domain = domain
		self.problem = problem
		self.obs_stream = obs
		self.max_time = max_time
		self.max_mem = max_mem
		self.convert_to_integers = False
		self.factor = 1.0

		self.domain_with_constants = domain_with_constants

		self.domain_name = domain_name

	def execute( self ) :
		# if not self.convert_to_integers :
		# 	cmd_string = './pr2plan -d %s -i %s -o %s -P'%(self.domain, self.problem, self.obs_stream)
		# else :
		# 	cmd_string = './pr2plan -d %s -i %s -o %s -P -Z %s'%(self.domain, self.problem, self.obs_stream, self.factor)


		print("len of obs: ", len(self.obs_stream))
		cmd_to_run = f"python t_pr2plan.py -d {self.domain_with_constants} -i {self.problem } -o {self.obs_stream} -d_n {self.domain_name}"


		os.system(cmd_to_run)

		print("Turguy")
		# self.log = benchmark.Log( '%s_%s_%s_transcription.log'%(self.domain, self.problem, self.obs_stream) )
		# self.signal, self.time = benchmark.run( cmd_string, self.max_time, self.max_mem, self.log )

