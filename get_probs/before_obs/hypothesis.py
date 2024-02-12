import sys, os, benchmark
import planners, translation

class Probabilistic :
	
	def __init__( self, domain_folder_path, planner_type, domain_name, ) :
		self.atoms = []
		self.cost_O = 0.0
		self.cost_Not_O = 0.0
		self.Delta_O = 0.0
		self.Delta_Not_O = 0.0
		self.Probability_O = 0.0
		self.Probability_Not_O = 0.0
		self.Plan_Time_O = 0.0
		self.Plan_Time_Not_O = 0.0
		self.solvable = True
		self.plan = []
		self.test_failed = False
		self.trans_time = 0.0
		self.plan_time = 0.0
		self.total_time = 0.0
		self.is_true = True
		self.reason = ""
		self.domain_folder_path = domain_folder_path
		self.domain_name = domain_name

		self.planner_type = planner_type

		 

	def walk( self, dir ) :
		entries = os.listdir( dir )
		for entry in entries :
			domain_path = os.path.join( entry, 'pr-domain.pddl' )
			domain_path = os.path.join( dir, domain_path )
			instance_path = os.path.join( entry, 'pr-problem.pddl' )
			instance_path = os.path.join( dir, instance_path )
			yield entry, domain_path, instance_path

	def test_for_sim( self, index, options  ) :
		import math, csv
		# generate the problem with G=H
		hyp_problem = 'hyp_%d_problem.pddl'%index
		self.generate_pddl_for_hyp_plan( hyp_problem )
		# derive problem with G_Obs
		domain_folder_path = self.domain_folder_path

		domain_folder = f"{domain_folder_path}/merged_domain.pddl"
		dom_with_const_path = f"{domain_folder_path}/merged_domain_with_constants.pddl"
		plnr_type = self.planner_type 


		dom_name = self.domain_name

		trans_cmd = translation.Probabilistic_PR( domain_folder, hyp_problem, 'obs.dat',dom_with_const_path, dom_name )


		#trans_cmd.convert_to_integers = True
		# trans_cmd.factor = 1000.0
		trans_cmd.execute()
		self.trans_time = 666.5
		os.system( 'mv prob-PR prob-%s-PR'%index )
		self.costs = dict()
		G_Obs_time = 0.0
		min_cost = 1e7

		for id, domain, instance in self.walk( 'prob-%s-PR'%index ) :	
			plan_for_G_Obs_cmd = planners.FD( domain, instance, index, plnr_type, 1000, 10000 )
			# if options.optimal :	
			# 	plan_for_G_Obs_cmd = planners.H2( domain, instance, index, options.max_time, options.max_memory )
			# else :
			# 	if options.use_hspr :
			# 		plan_for_G_Obs_cmd = planners.HSPr( domain, instance, index, options.max_time, options.max_memory )
			# 	elif options.use_FF :
			# 		plan_for_G_Obs_cmd = planners.Metric_FF( domain, instance, index, options.max_time, options.max_memory )	
			# 	else :
			# 		plan_for_G_Obs_cmd = planners.LAMA( domain, instance, index, options.max_time, options.max_memory )
			plan_for_G_Obs_cmd.execute()
			if plan_for_G_Obs_cmd.signal != 0 and plan_for_G_Obs_cmd.signal != 256 and plan_for_G_Obs_cmd.signal != 3072 and plan_for_G_Obs_cmd.signal != 64000:
				self.test_failed = True
				return
			G_Obs_time += plan_for_G_Obs_cmd.time
			if id == 'O' : self.Plan_Time_O = plan_for_G_Obs_cmd.time
			if id == 'neg-O' : self.Plan_Time_Not_O = plan_for_G_Obs_cmd.time

			if plan_for_G_Obs_cmd.signal == 3072 or plan_for_G_Obs_cmd.signal == 64000:
				self.costs[id] = 1e7 
			else:
				self.costs[id] = plan_for_G_Obs_cmd.cost


			# self.costs[id] = plan_for_G_Obs_cmd.cost 
			if self.costs[id]  < min_cost : 
				min_cost = self.costs[id]
		
			print('HIIIII')
			print('hyps id: ', id)
			print('domain:', domain)
			print('instance', instance)
			print('cost',self.costs[id])

		print("Min Cost:", min_cost)
		print("Costs:", self.costs)
		self.plan_time = G_Obs_time
		self.total_time = 0 + self.plan_time

		# P(O|G) / P( \neg O | G) = exp { -beta Delta(G,O) }
		# Delta(G,O) = cost(G,O) - cost(G,\neg O)

		if self.costs['neg-O'] == 1e7 and self.costs['O'] != 1e7:
			likelihood_ratio = 1e7

		else:
			likelihood_ratio = math.exp( -1.0*(self.costs['O']-self.costs['neg-O']) )
		# P(O|G) =  exp { -beta Delta(G,O) } / 1 + exp { -beta Delta(G,O) }
		
		self.Probability_O = likelihood_ratio / ( 1.0 + likelihood_ratio ) 
		self.Probability_Not_O = 1.0 - self.Probability_O		

		self.cost_O = self.costs['O']
		self.cost_Not_O = self.costs['neg-O']
	

	def test( self, index, max_time, max_mem, optimal = False, beta = 1.0  ) :
		import math, csv
		# generate the problem with G=H
		# hyp_problem = 'hyp_%d_problem.pddl'%index
		# self.generate_pddl_for_hyp_plan( hyp_problem )
		# derive problem with G_Obs
		# trans_cmd = translation.Probabilistic_PR( 'domain.pddl', hyp_problem, 'obs.dat' )
		# trans_cmd.execute()
		# self.trans_time = trans_cmd.time
		# os.system( 'mv prob-PR prob-%s-PR'%index )
		self.costs = dict()
		G_Obs_time = 0.0
		min_cost = 1e7
		time_bound = max_time
		if optimal :
			time_bound = max_time / 2
			for id, domain, instance in self.walk( 'prob-%s-PR'%index ) :	
				plan_for_G_Obs_cmd = planners.HSP( domain, instance, index, time_bound, max_mem )
				plan_for_G_Obs_cmd.execute()
				if id == 'O' : self.Plan_Time_O = plan_for_G_Obs_cmd.time
				if id == 'neg-O' : self.Plan_Time_Not_O = plan_for_G_Obs_cmd.time

				G_Obs_time += plan_for_G_Obs_cmd.time
				self.costs[id] = plan_for_G_Obs_cmd.cost
				if plan_for_G_Obs_cmd.cost < min_cost :
					min_cost = plan_for_G_Obs_cmd.cost

		if not optimal :
			#time_bound = max_time / 3
			#plan_for_G_cmd = planners.LAMA( 'domain.pddl', hyp_problem, index, time_bound, max_mem )
			#plan_for_G_cmd.execute()
			#if plan_for_G_cmd.cost < min_cost :
			#	min_cost = plan_for_G_cmd.cost
			#remainder = time_bound - plan_for_G_cmd.time
			#print >> sys.stdout, "Time remaining:", time_bound

			#if remainder > 0 :
			#	time_bound = (max_time / 3 ) + (remainder / 2 ) 
			time_bound = max_time / 2
			for id, domain, instance in self.walk( 'prob-%s-PR'%index ) :	
				plan_for_G_Obs_cmd = planners.LAMA( domain, instance, index, time_bound, max_mem )
				plan_for_G_Obs_cmd.execute()
				G_Obs_time += plan_for_G_Obs_cmd.time
				if id == 'O' : self.Plan_Time_O = plan_for_G_Obs_cmd.time
				if id == 'neg-O' : self.Plan_Time_Not_O = plan_for_G_Obs_cmd.time
				remainder = time_bound - plan_for_G_Obs_cmd.time
				if remainder > 0 :
					time_bound = time_bound + remainder
				self.costs[id] = plan_for_G_Obs_cmd.cost
				if plan_for_G_Obs_cmd.cost < min_cost :
					min_cost = plan_for_G_Obs_cmd.cost

		self.plan_time = G_Obs_time
		self.total_time = trans_cmd.time + self.plan_time

		# P(O|G) / P( \neg O | G) = exp { -beta Delta(G,O) }
		# Delta(G,O) = cost(G,O) - cost(G,\neg O)
		likelihood_ratio = math.exp( -beta*(self.costs['O']-self.costs['neg-O']) )
		# P(O|G) =  exp { -beta Delta(G,O) } / 1 + exp { -beta Delta(G,O) }
		self.Probability_O = likelihood_ratio / ( 1.0 + likelihood_ratio ) 
		self.Probability_Not_O = 1.0 - self.Probability_O		

		self.cost_O = self.costs['O']
		self.cost_Not_O = self.costs['neg-O']


	def load_plan( self, plan_name ) :
		instream = open( plan_name )
		self.plan = []
		for line in instream :
			line = line.strip()
			if line[0] == ';' : continue
			#_, _, stuff = line.partition(':')
			#op, _, _ = stuff.partition('[')
			_, _, stuff = custom_partition( line, ':' )
			op, _, _ = custom_partition( stuff, '[' )
			self.plan.append( op.strip().upper() )	
		instream.close()


	def generate_pddl_for_hyp_plan( self, out_name ) :
		domain_folder_path = self.domain_folder_path
		template_path = f"{domain_folder_path}/template.pddl"
		instream = open( template_path )
		outstream = open( out_name, 'w' )

		for line in instream:
			line = line.strip()
			if '<HYPOTHESIS>' not in line:
				print(line, file=outstream)
			else:
				for atom in self.atoms:
					print(atom, file=outstream)
		
		outstream.close()
		instream.close()

	def check_if_actual( self ) :
		real_hyp_atoms = []
		instream = open( 'real_hyp.dat' )
		for line in instream :
			real_hyp_atoms = [ tok.strip() for tok in line.split(',') ]
		instream.close()

		for atom in real_hyp_atoms :
			if not atom in self.atoms :
				self.is_true = False
				break

