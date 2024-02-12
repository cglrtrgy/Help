import getopt
import os
import sys

def usage():
    print("Parameters:", file=sys.stderr)
    print("-e  --experiment <file>          Plan Recognition experiment files (tar'ed)", file=sys.stderr)
    print("-h  --help                       Get Help", file=sys.stderr)
    print("-t  --max-time <time>            Maximum allowed execution time (defaults to 1800 secs)", file=sys.stderr)
    print("-m  --max-memory <time>          Maximum allowed memory consumption (defaults to 1Gb)", file=sys.stderr)
    print("-O  --optimal                    Optimal Probabilistic PR", file=sys.stderr)
    print("-G  --greedy                     Greedy LAMA (takes first solution as best)", file=sys.stderr)
    print("-P  --hspr                       Use hspr for satisficing planning", file=sys.stderr)
    print("-F  --ff                         Use FF for satisficing planning", file=sys.stderr)
    print("-S  --simulation                 Simulation mode", file=sys.stderr)
    print("-b  --beta <value>               Parameter strictly positive which penalizes non--optimal behavior", file=sys.stderr)
    print("-D  --simulate-from-obs          Uses provided observations instead of generating them (Simulation mode)", file=sys.stderr)


class Program_Options :

	def __init__( self, args ) :
		try:
			opts, args = getopt.getopt(	args,
							"e:ht:m:OGSb:PFD",
							["experiment=",
							"help",
							"max-time=",
							"max-memory=",
							"beta=",
							"hspr",
							"ff",
							"optimal",
							"greedy",
							"simulation",
							"simulate-from-obs"] )
		except getopt.GetoptError :
			print("Missing or incorrect parameters specified!", file=sys.stderr)
			usage()
			sys.exit(1)

		self.exp_file = None
		self.domain_name = None
		self.instance_names = []
		self.max_time = 1800
		self.max_memory = 1024
		self.optimal = False
		self.greedy = False
		self.simulation = False
		self.use_hspr = False
		self.use_FF = False
		self.beta = 1.0
		self.simulate_from_obs = False

		for opcode, oparg in opts:
			if opcode in ('-h', '--help'):
				print("Help invoked!", file=sys.stderr)
				usage()
				sys.exit(0)
			if opcode in ('-e', '--experiment'):
				self.exp_file = oparg
				if not os.path.exists(self.exp_file):
					print("File", self.exp_file, "does not exist", file=sys.stderr)
					print("Aborting", file=sys.stderr)
					sys.exit(1)
			if opcode in ('-t', '--max-time'):
				try:
					self.max_time = int(oparg)
					if self.max_time <= 0:
						print("Maximum time must be greater than zero", file=sys.stderr)
						sys.exit(1)
				except ValueError:
					print("Time must be an integer", file=sys.stderr)
					sys.exit(1)
			if opcode in ('-b', '--beta'):
				try:
					self.beta = float(oparg)
					if self.beta <= 0.0:
						print("Beta must be a positive real number", file=sys.stderr)
						sys.exit(1)
				except ValueError:
					print("Beta must be a (positive) real number, rather than", oparg, file=sys.stderr)
					sys.exit(1)
			if opcode in ('-m', '--max-memory'):
				try:
					self.max_memory = int(oparg)
					if self.max_memory <= 0:
						print("Maximum memory must be greater than zero", file=sys.stderr)
						sys.exit(1)
				except ValueError:
					print("Memory amount must be an integer", file=sys.stderr)
					sys.exit(1)
			if opcode in ('-O', '--optimal'):
				self.optimal = True
			if opcode in ('-G', '--greedy'):
				self.greedy = True
			if opcode in ('-S', '--simulation'):
				self.simulation = True
			if opcode in ('-P', '--hspr'):
				self.use_hspr = True
			if opcode in ('-F', '--ff'):
				self.use_FF = True
			if opcode in ('-D', '--simulate-from-obs'):
				self.simulate_from_obs = True


			if self.exp_file is None:
				print("No experiment file was specified!!", file=sys.stderr)
				usage()
				sys.exit(1)

			os.system(f'tar jxvf {self.exp_file}')
			if not os.path.exists('domain.pddl'):
				print("No 'domain.pddl' file found in the experiment file!", file=sys.stderr)
				usage()
				sys.exit(1)
			if not os.path.exists('template.pddl'):
				print("No 'template.pddl' file found in the experiment file!", file=sys.stderr)
				usage()
				sys.exit(1)
			if not os.path.exists('hyps.dat'):
				print("No 'hyps.dat' file found in the experiment file!", file=sys.stderr)
				usage()
				sys.exit(1)
			if not self.simulation:
				if not os.path.exists('obs.dat'):
					print("No 'obs.dat' file found in the experiment file!", file=sys.stderr)
					usage()
					sys.exit(1)
				if not os.path.exists('real_hyp.dat'):
					print("No 'real_hyp.dat' file found in the experiment file!", file=sys.stderr)
					usage()
					sys.exit(1)


	def print_options(self):
		def print_yes():
			print("Yes")

		def print_no():
			print("No")

		print("Options set")
		print("===========")
		print("Experiment File:", self.exp_file)
		print("Max. Time Allowed", self.max_time)
		print("Max. Memory Allowed", self.max_memory)

