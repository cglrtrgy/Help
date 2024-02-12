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
    
    try:
        true_index = [a_action.name==name_of_an_obs for a_action in init_domain_action_list].index(True) 
        obs_domain_action = init_domain_action_list[true_index]

    except ValueError:
        obs_domain_action = False
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



def extract_effects_from_an_action(action_object):
    add_effects = []
    delete_effects = []
    when_add_effects = []
    when_delete_effects = []
    when_condition_delete_effects = [] # New list for delete effects in When conditions
    when_condition_add_effects = [] # New list for add effects in When conditions
    
    if type(action_object) == And or type(action_object) == AndEffect:
        action_object = action_object.operands
    
    if type(action_object) == Predicate:
        add_effects.append(action_object)
        return delete_effects, add_effects, when_delete_effects, when_add_effects, when_condition_delete_effects, when_condition_add_effects

    for obj in action_object:
        if isinstance(obj, Predicate):
            add_effects.append(obj)
        elif isinstance(obj, Not):
            argument = obj.argument
            if isinstance(argument, Predicate):
                delete_effects.append(argument)
            else:
                dell, add, when_dell, when_add, cond_dell, cond_add = extract_effects_from_an_action([argument])
                add_effects.extend(add)
                delete_effects.extend(dell)
                when_add_effects.extend(when_add)
                when_delete_effects.extend(when_dell)
                when_condition_delete_effects.extend(cond_dell) # Extend new lists with recursion results
                when_condition_add_effects.extend(cond_add) # Extend new lists with recursion results
        elif isinstance(obj, When):
            condition = obj.condition
            effect = obj.effect
            when_add_effects.append([])
            when_delete_effects.append([])
            when_condition_delete_effects.append([]) # Add new empty list for this When condition's delete effects
            when_condition_add_effects.append([]) # Add new empty list for this When condition's add effects
            if not isinstance(condition, Not): # If the condition doesn't start with Not, process it
                if isinstance(condition, Predicate):
                    when_condition_add_effects[-1].append(condition)
                else:
                    dell, add = extract_effects_from_an_action([condition])[:2] # Recursively process condition
                    when_condition_add_effects[-1].extend(add)
                    when_condition_delete_effects[-1].extend(dell)
            if isinstance(effect, Predicate):
                when_add_effects[-1].append(effect)
            elif isinstance(effect, Not) and isinstance(effect.argument, Predicate):
                when_delete_effects[-1].append(effect.argument)
            else:
                dell, add, when_dell, when_add, cond_dell, cond_add = extract_effects_from_an_action([effect])
                when_add_effects[-1].extend(add)
                when_delete_effects[-1].extend(dell)
        elif isinstance(obj, And):
            for operand in obj.operands:
                if isinstance(operand, Predicate):
                    add_effects.append(operand)
                else:
                    dell, add, when_dell, when_add, cond_dell, cond_add = extract_effects_from_an_action([operand])
                    add_effects.extend(add)
                    delete_effects.extend(dell)
                    when_add_effects.extend(when_add)
                    when_delete_effects.extend(when_dell)
                    when_condition_delete_effects.extend(cond_dell) # Extend new lists with recursion results
                    when_condition_add_effects.extend(cond_add) # Extend new lists with recursion results
    return delete_effects, add_effects, when_delete_effects, when_add_effects, when_condition_delete_effects, when_condition_add_effects



def is_in_the_set(small_set, big_set):
    return all(element in big_set for element in small_set)

# Create an argument parser
parser = argparse.ArgumentParser(description='Script to iterate options to get updated problem.pddl')

# Add arguments for the paths
parser.add_argument('-d', '--domain', help='Path to  domain file', required=True)
parser.add_argument('-i', '--problem', help='Path to merged problem file', required=True)
parser.add_argument('-o', '--obs', help='Path to observation file', required=True)


# Parse the command-line arguments
args = parser.parse_args()


# Assign the paths to variables
path_to_merged_domain = args.domain
path_to_merged_problem = args.problem
path_to_observations = args.obs

merged_domain = parse_domain(path_to_merged_domain)
merged_problem = parse_problem(path_to_merged_problem)


raw_obs = load_obs(path_to_observations)

observation_list = [an_obs.replace('(', '').replace(')', '').replace(' ', '_') for an_obs in raw_obs]
merged_domain_action_list = list(merged_domain.actions)

# [print (an_action) for an_action in merged_domain_action_list]

all_modified_observations = [get_observation_list(an_obs) for an_obs in raw_obs]

#get copy of each action observed
frozen_matched_action_list =[]
for an_obs, an_row_obs in zip(all_modified_observations, raw_obs):
    an_obs_name = an_obs[0]
    an_obs_constants = an_obs[1]
    
    matched_action = get_matching_action(an_obs_name, merged_domain_action_list)
    if matched_action == False:
        break

    matched_action_frozen = copy.deepcopy(matched_action)
    
    frozen_matched_action_list.append(matched_action_frozen)



#create explaining actions for observations
observation_index = 0
extracted_add_del_eff_list=[]
extracted_add_del_effects = []

copied_action_list = []


for an_obs, an_row_obs in zip(all_modified_observations, raw_obs):
    if matched_action == False:
        break
    an_obs_name = an_obs[0]
    an_obs_constants = an_obs[1]
    
#     copied_action = copy.deepcopy(matched_action)
    #### 1- Create explain action for each observed action
    #we will create explain_actions with copied_action
    copied_action = copy.deepcopy(frozen_matched_action_list[observation_index])
    
    del_eff, add_eff, when_del_eff, when_add_eff, when_cond_del_eff, when_cond_add_eff = extract_effects_from_an_action(copied_action.effect)
    
    #get the parameter names like ['x', 'y'] for unstack ?x ?y or unstack(Variable(x) (Variable y))
    copied_action_parameters_list = [a_par.name for a_par in copied_action.parameters]
    
    grounded_delete_effects = ground_predicate_terms(copied_action_parameters_list, an_obs_constants, del_eff)
    grounded_add_effects = ground_predicate_terms(copied_action_parameters_list, an_obs_constants, add_eff)
    
    # grounded_when_del_eff_1 = ground_predicate_terms(copied_action_parameters_list, an_obs_constants, when_del_eff[0])
    # grounded_when_del_eff_2 = ground_predicate_terms(copied_action_parameters_list, an_obs_constants, when_del_eff[1])

    # grounded_when_add_eff_1 = ground_predicate_terms(copied_action_parameters_list, an_obs_constants, when_add_eff[0])
    # grounded_when_add_eff_2 = ground_predicate_terms(copied_action_parameters_list, an_obs_constants, when_add_eff[1])

    # grounded_when_cond_del_eff_1 = ground_predicate_terms(copied_action_parameters_list, an_obs_constants, when_cond_del_eff[0])
    # grounded_when_cond_del_eff_2 = ground_predicate_terms(copied_action_parameters_list, an_obs_constants, when_cond_del_eff[1])

    # grounded_when_cond_add_eff_1 = ground_predicate_terms(copied_action_parameters_list, an_obs_constants, when_cond_add_eff[0])
    # grounded_when_cond_add_eff_2 = ground_predicate_terms(copied_action_parameters_list, an_obs_constants, when_cond_add_eff[1])

#     grounded_when_add_eff = ground_predicate_terms(copied_action_parameters_list, an_obs_constants, when_add_eff)
    
    #Here we say 'Something went wrong' because merger creates 2 CE for each action
    #CE1.condition starts with Not(Preds)
    #CE2.condition is Preds, therefore we only store and check CE2.condition.
    #if it is met update the problem with CE2.effect
    #else update the problem with CE1.effect
    
    # if len(grounded_when_cond_add_eff_1)!=0 and len(grounded_when_cond_del_eff_1)!=0:
    #     print('Something went wrong')
        
    #if nots in  When's condition are in the init, don't use that conditional effect
    #So, we want to see flag_1 False, and Flag_2 True to use the when effect_2
    # flag_1= False
    # flag_2 = True
    
    # if len(grounded_when_cond_del_eff_2) > 0:
    #     flag_1 = is_in_the_set(grounded_when_cond_del_eff_2, merged_problem._init)
    # if len(grounded_when_cond_add_eff_2) > 0:
    #     flag_2 = is_in_the_set(grounded_when_cond_add_eff_2, merged_problem._init)
        
    
    merged_problem._init = merged_problem._init.difference(grounded_delete_effects)
    merged_problem._init = merged_problem._init.union(grounded_add_effects)
    
    # if flag_1 == False and flag_2 == True:
    #     merged_problem._init = merged_problem._init.difference(grounded_when_del_eff_2)
    #     merged_problem._init = merged_problem._init.union(grounded_when_add_eff_2)
    # else:
    #     merged_problem._init = merged_problem._init.difference(grounded_when_del_eff_1)
    #     merged_problem._init = merged_problem._init.union(grounded_when_add_eff_1)
        
        
    
    copied_action_list.append(copied_action)
    extracted_add_del_eff_list.append([del_eff, add_eff, when_del_eff, when_add_eff, when_cond_del_eff,when_cond_add_eff])
    

    
    observation_index += 1
    
## Create Merged Problem
iterated_problem = Problem("updated_problem",
        domain=merged_domain,
        # requirements=human_domain.requirements,
        objects=merged_problem.objects,
        init=merged_problem._init,
        goal=merged_problem.goal
)

problem_string = problem_to_string(iterated_problem).lower()

#File writer
with open("temp_iterated_problem.pddl", "w") as file_path_to_pddl:
    file_path_to_pddl.write(problem_string)   
