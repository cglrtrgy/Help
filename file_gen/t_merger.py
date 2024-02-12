## Last Update: Jul 30: 1.05pm

from pddl.logic import Predicate, constants, variables
from pddl.core import Domain, Problem, Action, Requirements
from pddl.formatter import domain_to_string, problem_to_string
from pddl import parse_domain, parse_problem

from pddl.logic.effects import When, AndEffect
from pddl.logic.base import Not, And

import copy

import sys, os, csv
import argparse


def write_lists_to_file(file_path, lists):
    with open(file_path, 'w') as file:
        for data_list in lists:
            formatted_list = ', '.join(data_list)  # Add a space after each comma
            file.write(formatted_list + '\n')



# Create an argument parser
parser = argparse.ArgumentParser(description='Script to process input paths')



# Add arguments for the paths
parser.add_argument('-h_d', '--human_domain', help='Path to human domain file', required=True)
parser.add_argument('-h_i', '--human_problem', help='Path to human problem file', required=True)

parser.add_argument('-r_d', '--robot_domain', help='Path to robot domain file', required=True)
parser.add_argument('-r_i', '--robot_problem', help='Path to robot problem file')

parser.add_argument('-d_n', '--domain_name', help='Domain name for mixed types')

# Parse the command-line arguments
args = parser.parse_args()

path_to_human_domain = args.human_domain
path_to_robot_domain = args.robot_domain


#for now, it is same for both human and robot
path_to_human_problem = args.human_problem
path_to_robot_problem = args.robot_problem


domain_name = args.domain_name


# Check if the optional argument was provided
if path_to_robot_problem is None:
    path_to_robot_problem = path_to_human_problem



robot_domain = parse_domain(path_to_robot_domain)
robot_problem = parse_problem(path_to_robot_problem)

human_domain = parse_domain(path_to_human_domain)
human_problem = parse_problem(path_to_human_problem)


## Merge Predicates
#create a predicate to capture robot failures

robot_failed = Predicate("robot_failed")
list_h_preds = list(human_domain.predicates)
list_r_preds = list(robot_domain.predicates)

#change robot predicates' names: add "r_"
for pred in list_r_preds:
    pred._name = "r_" + str(pred.name)

#merged domain's predicates
merged_preds = list_h_preds + list_r_preds
merged_preds.append(robot_failed)

## Merge Actions
list_h_actions = list(human_domain.actions)
list_r_actions = list(robot_domain.actions)

merged_action_list =[]

for h_action in list_h_actions:
    for r_action in list_r_actions:
        if str(h_action.name)==str(r_action.name):
            
            merged_effect_list = []
            
            #add r_ to robot's preconditions
            if hasattr(r_action.precondition, 'operands'):
                for precs in r_action.precondition.operands:
                    precs._name = "r_" + precs._name
            if hasattr(r_action.precondition, 'argument'):
                precs._name = "r_" + precs._name

            #if it is already predicate
            if type(r_action.precondition)==Predicate:
                r_action.precondition._name = "r_" + r_action.precondition._name
                

            #get human effects
            #first check if it is And, which means if it has operands
            if hasattr(h_action.effect, 'operands'):
                for h_eff_operand in h_action.effect.operands:
                    merged_effect_list.append(h_eff_operand)
            
            #else it must be Predicate (check this for Not effect later)
            elif type(h_action.effect) == Predicate:
                merged_effect_list.append(h_action.effect)
            else:
                raise ValueError("check human effect")


            
            #get robot effects
            #get robot effects with "r_" added to the predicates

            #1) it can be And (which can have Not's in it)
            if hasattr(r_action.effect, 'operands'):
                for r_eff_operand in r_action.effect.operands:
                    if type(r_eff_operand)== Not:
                        r_eff_operand.argument._name = "r_"+ r_eff_operand.argument._name
                    else:
                        r_eff_operand._name = "r_"+ r_eff_operand._name
            
            #2) it can be only Not - PRedicate
            elif type(r_action.effect)== Not:
                r_action.effect.argument._name = "r_"+ r_action.effect.argument._name

            #3) it can be only Predicate
            elif type(r_action.effect)== Predicate:
                r_action.effect._name = "r_" + r_action.effect._name
            else:
                raise ValueError("check Robot effect")

            
            #use robot effects in conditional effects
            ce_1 = When(~(r_action.precondition), (robot_failed))
            merged_effect_list.append(ce_1)
            
            #Second CE
            extra_r_act_prec = copy.deepcopy(r_action.precondition)
            if hasattr(extra_r_act_prec, 'operands'):
                extra_r_act_prec._operands = extra_r_act_prec._operands + [~(robot_failed)]
            else:
                extra_r_act_prec = And(* [extra_r_act_prec]+ [~(robot_failed)])


                
            ce_2 = When((extra_r_act_prec), (r_action.effect))
            merged_effect_list.append(ce_2)
            merged_effect_list = tuple(merged_effect_list)
            
            #Careful! AndEffect takes the elements not the list
            merged_effect_list = AndEffect(*merged_effect_list)
            print(merged_effect_list)
                         
            
            act = Action(
                    str(h_action.name),
                    parameters = h_action.parameters,
                    precondition = h_action.precondition,
                    effect = merged_effect_list
            )
            
            merged_action_list.append(act)
            
## Merge Types
merged_domain_types = copy.deepcopy(human_domain.types)
merged_domain_types.add('othergoals')

human_domain._requirements = list(human_domain._requirements)


## Create Merged Domain
merged_domain = Domain("merged_domain",
       requirements=human_domain._requirements + [Requirements.CONDITIONAL_EFFECTS],
       types=merged_domain_types,
    #    constants=human_domain.constants,
       predicates=merged_preds,
       actions=merged_action_list)

## Create Merged Domain
merged_domain_with_constants = Domain("merged_domain",
       requirements=human_domain._requirements + [Requirements.CONDITIONAL_EFFECTS],
       types=merged_domain_types,
       constants=human_domain.constants,
       predicates=merged_preds,
       actions=merged_action_list)

#make everything lower case
string_domain = domain_to_string(merged_domain).lower()


#make everything lower case
string_domain_2 = domain_to_string(merged_domain_with_constants).lower()


##--------------Last Update: Jul 30: 1.05pm---------------#
if domain_name != None:
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
    with open("merged_domain.pddl", "w") as text_file:
        text_file.write(modified_string_domain)

    # Find the starting and ending positions of '(:types' and ')'
    start_pos = string_domain_2.find('(:types')
    end_pos = string_domain_2.find(')', start_pos)   
    
    modified_string_domain_2 = string_domain_2[:start_pos + len('(:types')] + ' ' + input_string + string_domain_2[end_pos:]

    #File writer
    with open("merged_domain_with_constants.pddl", "w") as text_file:
        text_file.write(modified_string_domain_2)

##--------------Last Update: Jul 30: 1.05pm---------------#
else:
    #File writer
    with open("merged_domain.pddl", "w") as text_file:
        text_file.write(string_domain)


    #File writer
    with open("merged_domain_with_constants.pddl", "w") as text_file:
        text_file.write(string_domain_2)

## Merge problem objects
#Object for robot failure
rob_failure_object = constants("robot_failed", types=["othergoals"])

#Human problem objects:
human_problem_obj = list(human_problem.objects.copy())

#Merged problem's objects:
merged_objects_for_problem = rob_failure_object + human_problem_obj

## Merged Problem Inits
#change robot init predicate names: add "r_"
for robot_init in list(robot_problem.init):
    robot_init._name = "r_" + robot_init._name

merged_inits_for_problem = list(human_problem.init) + list(robot_problem.init)

## Merged Problem Goals

merged_goal_list = [human_problem.goal]+ [robot_failed]

merged_goal_list_2 = [human_problem.goal]+ [~robot_failed]

#Merge them with AND
merged_goal = And(*merged_goal_list)

merged_goal_2 = And(*merged_goal_list_2)

## Create Merged Problem
merged_problem = Problem("merged_problem",
        domain=merged_domain,
        # requirements=human_domain.requirements,
        objects=merged_objects_for_problem,
        init=merged_inits_for_problem,
        goal=merged_goal
)

merged_problem_2 = Problem("merged_problem",
        domain=merged_domain,
        # requirements=human_domain.requirements,
        objects=merged_objects_for_problem,
        init=merged_inits_for_problem,
        goal=merged_goal_2
)

problem_string = problem_to_string(merged_problem).lower()

problem_string_2 = problem_to_string(merged_problem_2).lower()






#File writer
with open("merged_problem.pddl", "w") as text_file:
    text_file.write(problem_string)







with open("merged_problem_for_obs.pddl", "w") as text_file:
    text_file.write(problem_string_2)




## Get hyps.dat file
# Sample input lists
list1 = [a_goal.__str__() for a_goal in merged_goal.operands]
list2 = [a_goal.__str__() for a_goal in merged_goal_2.operands]

# Writing to the file
write_lists_to_file('hyps.dat', [list1, list2])