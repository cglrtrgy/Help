#last update Jul 30, 10:40 AM

from pddl.logic import Predicate, constants, variables
from pddl.core import Domain, Problem, Action, Requirements
from pddl.formatter import domain_to_string, problem_to_string
from pddl import parse_domain, parse_problem

from pddl.logic.effects import When, AndEffect
from pddl.logic.base import Not, And
from pddl.logic.predicates import EqualTo
from pddl.custom_types import name

import copy

import sys, os, csv


import argparse


def load_obs(obs_file_path) :
    obs = []
    # instream = open( 'block_test/obs.dat' )
    instream = open( obs_file_path )
    for line in instream :
        line = line.strip()
        obs.append( line )
    instream.close()
    return obs

def get_action_name_for_an_obs (an_row_obs):
    
    plain_name_merged = an_row_obs.replace('(', '').replace(')', '').replace(' ', '_')
    new_action_name = "EXPLAIN_OBS_"+plain_name_merged

            
    return new_action_name

def get_observation_list(a_raw_obs):
    
    observation_list = a_raw_obs.replace('(', '').replace(')', '').split(' ')
    observation_action_name = observation_list[0]

    #if observed action has operands, get them
    if len(observation_list)>1:
        observation_action_object_list = observation_list[1:]
    else:
        observation_action_object_list=[]

    
    return [observation_action_name,observation_action_object_list]

def get_matching_action(name_of_an_obs ,init_domain_action_list):
    
    true_index = [a_action.name==name_of_an_obs for a_action in init_domain_action_list].index(True)
    obs_domain_action = init_domain_action_list[true_index]
    
    return obs_domain_action

def extract_predicates_from_an_action(action_object):
    predicates = []
    
    if type(action_object)== And or type(action_object) == AndEffect:
        action_object = action_object.operands
    
    if type(action_object) == Predicate:
        predicates.append(action_object)
        return predicates

    for obj in action_object:
        if isinstance(obj, Predicate):
            predicates.append(obj)
        elif isinstance(obj, Not):
            argument = obj.argument
            if isinstance(argument, Predicate):
                predicates.append(argument)
            else:
                predicates.extend(extract_predicates_from_an_action([argument]))
        elif isinstance(obj, When):
            condition = obj.condition
            effect = obj.effect
            if isinstance(condition, Predicate):
                predicates.append(condition)
            else:
                predicates.extend(extract_predicates_from_an_action([condition]))
            if isinstance(effect, Predicate):
                predicates.append(effect)
            else:
                predicates.extend(extract_predicates_from_an_action([effect]))
        elif isinstance(obj, And):
            for operand in obj.operands:
                if isinstance(operand, Predicate):
                    predicates.append(operand)
                else:
                    predicates.extend(extract_predicates_from_an_action([operand]))

    return predicates


def ground_predicate_terms(variable_names, string_replacements, predicate_list):
    # variable_names = ('x', 'y')
    # string_replacements = ['e', 'g']
    for predicate in predicate_list:
        arity = predicate.arity
        if arity > 0:
            terms = list(predicate._terms)
            for i in range(len(terms)):
                
                #variable is ?x, ?y = Variable(x), Variable(y) etc
                variable = terms[i]
                
                
                if variable._name in variable_names:
                    index = variable_names.index(variable._name)
                    a_constant_name = string_replacements[index]                    
                    predicate._terms = list(predicate._terms)
                    predicate._terms[i] = constants(a_constant_name, types = variable.type_tags)[0]
                    predicate._terms = tuple(predicate._terms)

    return predicate_list

def add_predicates_to_action_effect (an_action, predicate_list):
    
    if type(an_action.effect) == AndEffect:
        an_action.effect._operands = list(an_action.effect._operands)
    
    an_action.effect._operands = predicate_list + an_action.effect._operands

def add_predicates_to_action_precondition (an_action, predicate_list):
    
    if type(an_action._precondition) == And:
        an_action._precondition._operands = list(an_action._precondition._operands)
        an_action._precondition._operands = predicate_list + an_action._precondition._operands
        
    if type(an_action._precondition) == Predicate:
        copied_precond = copy.deepcopy(an_action._precondition)
        
        #create temporary and because for some reason Predicate doesnt go to the operator list directly
        an_action._precondition = And('t','y')

        an_action._precondition._operands = predicate_list + [copied_precond]
    
    
    


# Create an argument parser
parser = argparse.ArgumentParser(description='Script to process input paths')

# Add arguments for the paths
parser.add_argument('-d', '--domain', help='Path to merged domain file')
parser.add_argument('-i', '--problem', help='Path to merged problem file')
parser.add_argument('-o', '--observations', help='Path to observations file')

parser.add_argument('-d_n', '--domain_name', help='Domain name for mixed types')


# Parse the command-line arguments
args = parser.parse_args()

# Assign the paths to variables
path_to_merged_domain = args.domain
path_to_merged_problem = args.problem
path_to_observations = args.observations


domain_name = args.domain_name

# Print the paths (optional)
# print("Path to merged domain file:", path_to_merged_domain)
# print("Path to merged problem file:", path_to_merged_problem)
# print("Path to observations file:", path_to_observations)


merged_domain = parse_domain(path_to_merged_domain)
merged_problem = parse_problem(path_to_merged_problem)
raw_obs = load_obs(path_to_observations)
observation_list = [an_obs.replace('(', '').replace(')', '').replace(' ', '_') for an_obs in raw_obs]

new_general_exp_predicates = [Predicate("EXPLAINED_FULL_OBS_SEQUENCE"), Predicate("NOT_EXPLAINED_FULL_OBS_SEQUENCE")]
new_explained_preds = [Predicate("EXPLAINED_" + an_obs) for an_obs in observation_list]
new_not_explained_preds = [Predicate("NOT_EXPLAINED_" + an_obs) for an_obs in observation_list]

new_predicates = new_explained_preds + new_not_explained_preds + new_general_exp_predicates


merged_domain_action_list = list(merged_domain.actions)


all_modified_observations = [get_observation_list(an_obs) for an_obs in raw_obs]
# print("all_modified_observations: ")
# print(all_modified_observations)

copied_action_list = []
new_explained_action_list =[]



#get copy of each action
frozen_matched_action_list =[]
for an_obs, an_row_obs in zip(all_modified_observations, raw_obs):
    an_obs_name = an_obs[0]
    an_obs_constants = an_obs[1]
    
    matched_action = get_matching_action(an_obs_name, merged_domain_action_list)
    
    matched_action_frozen = copy.deepcopy(matched_action)
    
    frozen_matched_action_list.append(matched_action_frozen)
    
    
    
    


#create explaining actions for observations
observation_index = 0
for an_obs, an_row_obs in zip(all_modified_observations, raw_obs):
    an_obs_name = an_obs[0]
    an_obs_constants = an_obs[1]
    
#     copied_action = copy.deepcopy(matched_action)
    #### 1- Create explain action for each observed action
    #we will create explain_actions with copied_action
    copied_action = copy.deepcopy(frozen_matched_action_list[observation_index])
    
    

        
    #get matched actions predicates in precondition and effects
    
    copied_action_preds_in_precondition_list = extract_predicates_from_an_action(copied_action.precondition)
    copied_action_preds_in_effect_list = extract_predicates_from_an_action(copied_action.effect)
    
    #get the parameter names like ['x', 'y'] for unstack ?x ?y or unstack(Variable(x) (Variable y))
    copied_action_parameters_list = [a_par.name for a_par in copied_action.parameters]
    
    #ground predicates in precondition and effect based on the observations
    grounded_precs = ground_predicate_terms(copied_action_parameters_list, an_obs_constants, copied_action_preds_in_precondition_list)
    grounded_effects = ground_predicate_terms(copied_action_parameters_list, an_obs_constants, copied_action_preds_in_effect_list)
    
    
    #use pddl name to match the type: e.g., name('Turgay')
    copied_action._name = name(get_action_name_for_an_obs(an_row_obs))
    copied_action._parameters = ()
    
      
    add_predicates_to_action_effect(copied_action, [new_explained_preds[observation_index],Not(new_not_explained_preds[observation_index])])
    
    
    #for the observation after the first one, add previous observation as precondition
    if observation_index > 0:
        add_predicates_to_action_precondition(copied_action,[new_explained_preds[observation_index-1]])
        
    #if this observation is the last one
    if len(raw_obs)-1 == observation_index:
        add_predicates_to_action_effect(copied_action, [new_general_exp_predicates[0],Not(new_general_exp_predicates[1])])

    new_explained_action_list.append(copied_action)
    ##----ENd of adding one exp_action----
    
    
    
    ### 2- Modify lifted actions
    #add equal sign to restric observed objects in the actions
    
    
    #this is original domain's action
    matched_action = get_matching_action(an_obs_name, merged_domain_action_list)
    
    parameters_list_for_first_obs_act = [a_par for a_par in matched_action.parameters]
    fur = tuple([EqualTo(a_par, constants(a_con, types = a_par.type_tags)[0] ) for a_par, a_con in zip(parameters_list_for_first_obs_act,an_obs_constants)])
    add_predicates_to_action_precondition(matched_action,[Not(And(*fur))])
    
    #add grounded actions for the observations:
    
    
    
    ### 3- Create grounded Actions for each observation except the first one
    if observation_index > 0:
        
        #i starts from 0, i+1 to get the current index for the obs list
        for i in [observation_index-1]:
            
            copied_action_grounded = copy.deepcopy(frozen_matched_action_list[observation_index])

                        
                #get matched actions predicates in precondition and effects
    
            copied_action_grounded_preds_in_precondition_list = extract_predicates_from_an_action(copied_action_grounded.precondition)
            copied_action_grounded_preds_in_effect_list = extract_predicates_from_an_action(copied_action_grounded.effect)

            #get the parameter names like ['x', 'y'] for unstack ?x ?y or unstack(Variable(x) (Variable y))
            copied_action_grounded_parameters_list = [a_par.name for a_par in copied_action_grounded.parameters]

            #ground predicates in precondition and effect based on the observations
            grounded_preconds = ground_predicate_terms(copied_action_grounded_parameters_list, an_obs_constants, copied_action_grounded_preds_in_precondition_list)
            grounded_effects = ground_predicate_terms(copied_action_grounded_parameters_list, an_obs_constants, copied_action_grounded_preds_in_effect_list)
        



            copied_action_grounded._parameters = ()
            copied_action_grounded._name = name(get_action_name_for_an_obs(an_row_obs)).split('EXPLAIN_OBS_')[1]
            
            add_predicates_to_action_precondition(copied_action_grounded,[new_not_explained_preds[:observation_index][i]]+[new_general_exp_predicates[1]])
            
            copied_action_list.append(copied_action_grounded)
        

    observation_index += 1
    

# Write Domain

all_predicates = list(merged_domain.predicates)+new_predicates
all_actions = new_explained_action_list + copied_action_list + merged_domain_action_list 

merged_domain._requirements = list(merged_domain._requirements)

if not Requirements.EQUALITY in merged_domain.requirements:
    merged_domain._requirements = merged_domain._requirements + [Requirements.EQUALITY ]

merged_domain = Domain("pr_to_plan_domain",
       requirements=merged_domain.requirements,
       types=merged_domain.types,
    #    constants=merged_domain.constants,
       predicates=all_predicates,
       actions=all_actions)

#make everything lower case
string_domain = domain_to_string(merged_domain).lower()


#I dont kow why equal signs dont print properly
string_domain = string_domain.replace('symbols.equal', '=')

folders = ["prob-PR/neg-O", "prob-PR/O"]
for folder in folders:
    os.makedirs(folder, exist_ok=True)
#------------update Jul 30, 10:40 AM------------------#

if domain_name != None and domain_name != 'None' :

    print ("domain_name: ", domain_name)
    # Your input string to replace with
    if domain_name == 'driverlog':
        input_string = "location locatable - object \n" + "\t\t\tdriver truck obj - locatable\n"+  "\t\t\tothergoals\n\t"
    if domain_name == 'logistics':
        input_string = "truck airplane - vehicle \n" + "\t\t\tpackage vehicle - physobj\n" + "\t\t\tairport location - place\n" +"\t\t\tcity place physobj - object\n" +"\t\t\tothergoals\n\t"
        
    # Find the starting and ending positions of '(:types' and ')'
    start_pos = string_domain.find('(:types')
    end_pos = string_domain.find(')', start_pos)


    modified_string_domain = string_domain[:start_pos + len('(:types')] + ' ' + input_string + string_domain[end_pos:]
    #File writer
    with open("prob-PR/neg-O/pr-domain.pddl", "w") as text_file:
        text_file.write(modified_string_domain)

    #File writer
    with open("prob-PR/O/pr-domain.pddl", "w") as text_file:
        text_file.write(modified_string_domain)

else:
    #File writer
    with open("prob-PR/neg-O/pr-domain.pddl", "w") as text_file:
        text_file.write(string_domain)

    #File writer
    with open("prob-PR/O/pr-domain.pddl", "w") as text_file:
        text_file.write(string_domain)

#------------update Jul 30, 10:40 AM------------------#
# Write Problem
all_preds_in_init = list(merged_problem.init) +new_not_explained_preds + [new_general_exp_predicates[1]]

neg_o_goals = [merged_problem.goal] + [new_general_exp_predicates[1]]
neg_o_goals = And(*neg_o_goals)

o_goals = [merged_problem.goal] + [new_general_exp_predicates[0]]
o_goals = And(*o_goals)

neg_o_merged_problem = Problem("pr_to_plan_problem",
        domain=merged_domain,
        requirements=merged_problem.requirements,
        objects=merged_problem.objects,
        init=all_preds_in_init,
        goal=neg_o_goals
)

o_merged_problem = Problem("pr_to_plan_problem",
        domain=merged_domain,
        requirements=merged_problem.requirements,
        objects=merged_problem.objects,
        init=all_preds_in_init,
        goal=o_goals
)

neg_o_problem_string = problem_to_string(neg_o_merged_problem).lower()
o_problem_string = problem_to_string(o_merged_problem).lower()

#File writer
with open("prob-PR/neg-O/pr-problem.pddl", "w") as text_file:
    text_file.write(neg_o_problem_string)

#File writer
with open("prob-PR/O/pr-problem.pddl", "w") as text_file:
    text_file.write(o_problem_string)