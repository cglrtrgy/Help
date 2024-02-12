import benchmark, os

class Planner :
	
	def __init__( self, domain, problem, index,planner_type, max_time = 14400, max_mem = 2048 ) :
		self.domain = domain
		self.problem = problem
		self.noext_problem = os.path.basename(self.problem).replace( '.pddl', '' )
		self.max_time = max_time
		self.max_mem = max_mem
		self.log_file = '%s-%s-%s.log'%(self.noext_problem, index, os.path.split( os.path.split( self.problem )[0])[-1])
		self.cost = 1e7
		self.planner_type = planner_type

class FD(Planner) :
	def __init__( self, domain, problem, index, planner_type, max_time = 14400, max_mem = 2048 ) :
		Planner.__init__( self, domain, problem, index,planner_type, max_time, max_mem )

	def execute( self ) :
		FD_PATH = "/s/chopin/b/grad/tcaglar/downward/fast-downward.py"
		
		if self.planner_type == 'optimal':
			print('Optimal planner running')
			domain_f = self.domain
			problem_f = self.problem
			rest = "--search 'astar(hmax())'"

			cmd_string = f"{FD_PATH} {domain_f} {problem_f} {rest}"
		
		
		if self.planner_type == 'non_optimal':
			print('non-Optimal planner running')
			domain_f = self.domain
			problem_f = self.problem
			rest = "--alias lama-first"
			cmd_string = f"{FD_PATH} {rest} {domain_f} {problem_f}"	


		self.log = benchmark.Log( self.log_file )
		self.signal, self.time = benchmark.run( cmd_string, self.max_time, self.max_mem, self.log )
		self.gather_data()

	def gather_data( self ) :
		if self.signal == 0  :
			# Open the file
			with open("sas_plan", "r") as file:
				# Read all lines
				lines = file.readlines()

			# Get the last line
			last_line = lines[-1]

			# Check if the last line contains "cost ="
			if "cost =" in last_line:
				# Extract the cost value
				cost_str = last_line.split("=")[-1].strip()
				self.cost = float(''.join(filter(str.isdigit, cost_str)))
				print("Cost value:", self.cost)
			else:
				print("No cost value found in the last line.")

			# instream = open( self.log_file )
			# for line in instream :
			# 	line = line.strip()
			# 	if 'Total cost of plan:' in line :
			# 		number = line.split(':')[1].strip() 
			# 		self.cost = float( number )
			# instream.close()	