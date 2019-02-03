# BusBar, 2-Feb-2019
# TED Talk Video https://www.youtube.com/watch?v=QuR969uMICM
# This Code is describing a coin flip game explained on Ted Talk, where I try to implement the game in D-Wave.

# If I want to check, whether QC cheated or not, I have to go back and check the coin state of the
# intermediate steps. To do this I have to ask QC. So, QC will 'lie" (possibly) as it will only show
# the coin states which lead to a win. Isn't this cheating ? Can anyone correct if I am wrong?

import dwavebinarycsp
from dwave.system.samplers import DWaveSampler
from dwave.system.composites import EmbeddingComposite
import random
from datetime import datetime

# Head is 0
# Tail is 1
# Flip is 1
# No flip is 0

def no_flip(fst,fl,nxt):
    if fl==0 and fst==nxt:
        return True
    else:
        return False

def get_final_flip(in_st, fl_st):

    if in_st==fl_st:
        return True
    else:
        return False

csp = dwavebinarycsp.ConstraintSatisfactionProblem(dwavebinarycsp.BINARY)

# Step 0 - Selecting the initial condition
random.seed(datetime.now())
initial_state=str(random.randint(0, 1))
csp.add_constraint([map(int,initial_state)],['initial_state'])
print('Random Initail State is %s. ' % ('tail' if initial_state=='1' else 'head'))

# Step 1 - Quantum Computer's decision to flip the coin
csp.add_constraint(no_flip,['initial_state','QC_flip1','first_state']) # Constraint for 'no flip' condition

# Step 2 - Human's decision to flip the coin
ans='a'
while ans.upper()!='Y' and ans.upper()!='N':
    ans=input('Do you want to flip the coin (y/n) :')
Human_flip1= 1 if  ans.upper()=='Y' else 0
csp.add_constraint(no_flip,['first_state','Human_flip','second_state']) # Constraint for 'no flip' condition

# Step 3 - Quantum Computer's decision to flip the coin
csp.add_constraint(no_flip,['second_state','QC_flip2','final_state']) # Constraint for 'no flip' condition
csp.add_constraint(get_final_flip,['initial_state','final_state']) # Constraint to satisfy winning condition

for n in range(8, 1, -1):
    try:
        bqm = dwavebinarycsp.stitch(csp, min_classical_gap=0.1, max_graph_size=n)
    except dwavebinarycsp.exceptions.ImpossibleBQM:
        print('Parameter max_graph_size =', n)

shots = 500
sampler = EmbeddingComposite(DWaveSampler())
response = sampler.sample(bqm, num_reads=shots)

print('************ Results ************** \n')

for res in response.data(['sample', 'energy', 'num_occurrences']):
    if res.energy<0:
        print('(%s)--> Quantum Computer: %s --> (%s) --> You: %s --> (%s) --> Quantum Computer : %s --> (%s). '
              'Therefore QC %s. (Engy= %05.2f | Proba = %05.2f %%)' %
              ('tail' if initial_state== '1' else 'head',
               'flipped' if res.sample['QC_flip1'] == 1 else 'Did not flip',
               'tail' if res.sample['first_state'] == 1 else 'head',
               'flipped' if Human_flip1 == 1 else 'Did not flip',
               'tail' if res.sample['second_state'] == 1 else 'head',
               'flipped' if res.sample['QC_flip2'] == 1 else 'Did not flip',
               'tail' if res.sample['final_state'] == 1 else 'head',
               'won' if res.sample['final_state'] == res.sample['initial_state'] else 'loss',
               res.energy, res.num_occurrences*100/shots))
