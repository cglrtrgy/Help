#last update: Jul 30 12:40 pm

from pddl.logic import Predicate, constants, variables
from pddl.core import Domain, Problem, Action, Requirements
from pddl.formatter import domain_to_string, problem_to_string
from pddl import parse_domain, parse_problem

from pddl.logic.effects import When, AndEffect
from pddl.logic.base import Not, And
from pddl.logic.predicates import EqualTo
from pddl.custom_types import name

import copy

import re

import itertools

import sys, os, csv

import argparse

def get_object_dict(object_list, domain_name):
        
    # Create an empty dictionary to store the objects
    object_dict = {}
    
    for an_object in object_list:
        # Get the type of the object
        name = list(an_object.type_tags)[0]
#         print(name)

        # Check if the name is already a key in the dictionary
        if name in object_dict:
            # If the name is already a key, append the object to the existing list of objects
            object_dict[name].append(an_object.name)
        else:
            # If the name is not already a key, create a new key-value pair with the name as the key and a new list containing the object
            object_dict[name] = [an_object.name]



#---------------------update: Jul 30 12:40 pm------------------------#
    if domain_name =='logistics_shadow': #this is for Sirine logistic domain
        # Merge the lists of 'truck' and 'collection_station' and add it as a new key-value pair
        object_dict['physobj'] = object_dict.get('truck', []) + object_dict.get('collection_station', [])
    
    if domain_name =='logistics':
        #first level types: airplane, airport, location, city, truck, package
        #second level 
            #1) vehicle = turck + airplane
            #2) physobj = vehicle + package
            #3) place = airport + location
            #4) object = physobj + place + city 
        
        # Merge the lists of 'truck' and 'collection_station' and add it as a new key-value pair
        object_dict['vehicle'] = object_dict.get('truck', []) + object_dict.get('airplane', [])
        object_dict['physobj'] = object_dict.get('vehicle', []) + object_dict.get('package', [])
        object_dict['place'] = object_dict.get('airport', []) + object_dict.get('location', [])
        object_dict['object'] = object_dict.get('physobj', []) + object_dict.get('place', []) + object_dict.get('city', [])
        
    
    if domain_name == 'barman_shadow':
        # Merge the lists of 'truck' and 'collection_station' and add it as a new key-value pair
        object_dict['beverage'] = object_dict.get('ingredient', []) + object_dict.get('cocktail', [])
        object_dict['container'] = object_dict.get('shot', []) + object_dict.get('shaker', [])

#---------------------update: Jul 30 12:40 pm------------------------#
    # Count the length of values for each key
    object_dict_length = {key: len(value) for key, value in object_dict.items()}
    
    return object_dict, object_dict_length


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

def get_action_name_for_an_obs(action_name, an_obs):
    new_action_name = '-'.join([action_name] + an_obs)
    return new_action_name

def is_in_the_set(small_set, big_set):
    return all(element in big_set for element in small_set)

def split_action_names(action_list):
    splitted_names = []
    
    for action in action_list:
        name_parts = action.name.split('-')
        name = ' '.join(name_parts)
        splitted_names.append(name)
    
    return splitted_names



# Create an argument parser
parser = argparse.ArgumentParser(description='Script to get next possible actions')

# Add arguments for the paths
parser.add_argument('-d', '--domain', help='Path to  domain file', required=True)
parser.add_argument('-i', '--problem', help='Path to merged problem file', required=True)

parser.add_argument('-d_n', '--domain_name', help='Domain name for mixed types')


# Parse the command-line arguments
args = parser.parse_args()

# Assign the paths to variables
domain_file_path = args.domain
problem_file_path = args.problem

domain_name = args.domain_name

if domain_name == None:
    init_domain_name = 'human_domain'
else:
    init_domain_name = domain_name



init_domain = parse_domain(domain_file_path)
init_problem = parse_problem(problem_file_path)

lifted_action_list = list(copy.deepcopy(init_domain.actions))

#from the problem file
object_list = sorted(list(init_problem.objects))
init_list = sorted(list(init_problem.init))


#get object dictionary
object_dict, object_dict_length = get_object_dict (object_list,init_domain_name)

new_grounded_action_list = []

for a_lifted_action in lifted_action_list:
    
    
    
    #get the parameter names like ['x', 'y'] for unstack ?x ?y or unstack(Variable(x) (Variable y))
#     copied_action_parameters_list = [a_par.name for a_par in copied_action.parameters]
    a_lifted_action_parameters_list = [[a_par.name, list(a_par.type_tags)[0]] for a_par in a_lifted_action.parameters]
    
    # Gather all object types from copied_action_parameters_list
    object_types = [item[1] for item in a_lifted_action_parameters_list]

    # Create a list of objects for each type
    object_lists = [object_dict[type_] for type_ in object_types]

    # Use itertools.product to generate all combinations
    combinations = list(itertools.product(*object_lists))
    
    
    for an_obs_constants in combinations:
        an_obs_constants = list(an_obs_constants)
        copied_action = copy.deepcopy(a_lifted_action)
        
        copied_action_preds_in_precondition_list = extract_predicates_from_an_action(copied_action.precondition)
        copied_action_preds_in_effect_list = extract_predicates_from_an_action(copied_action.effect)
        
        #get the parameter names like ['x', 'y'] for unstack ?x ?y or unstack(Variable(x) (Variable y))
        copied_action_parameters_list = [a_par.name for a_par in copied_action.parameters]

        #ground predicates in precondition and effect based on the observations
        grounded_precs = ground_predicate_terms(copied_action_parameters_list, an_obs_constants, copied_action_preds_in_precondition_list)
        grounded_effects = ground_predicate_terms(copied_action_parameters_list, an_obs_constants, copied_action_preds_in_effect_list)
        
        #use pddl name to match the type: e.g., name('Turgay')
        copied_action._name = name(get_action_name_for_an_obs(copied_action.name, an_obs_constants))
        copied_action._parameters = ()
        
        new_grounded_action_list.append(copied_action)
        
    
    
    

filtered_valid_action_list=[]

for a_grounded_action in new_grounded_action_list:
    del_eff, add_eff, _, _, _, _ = extract_effects_from_an_action(a_grounded_action.precondition)
    
    flag_1= False
    flag_2 = True
    
    if len(del_eff) > 0:
        flag_1 = is_in_the_set(del_eff, init_list)
    if len(add_eff) > 0:
        flag_2 = is_in_the_set(add_eff, init_list)
        
    if flag_1 == False and flag_2 == True:
        
        filtered_valid_action_list.append(a_grounded_action)
    
list_of_filtered_actions = split_action_names(filtered_valid_action_list)

# Write the filtered actions to a file
with open('temp_next_possible_actions.dat', 'w') as file:
    for i, action in enumerate(list_of_filtered_actions):
        filtered_action = f'({action})'  # Add parentheses to the action string
        file.write(filtered_action)
        if i < len(list_of_filtered_actions) - 1:
            file.write('\n')  # Write a newline character except for the last action