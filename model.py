import os
import math
import pandas as pd
import numpy as np
import random
import time
import random


SURGERIES_IN_CAMP = 1000
MIN_IOL = 6
MAX_IOL = 30
INPUT = '/Users/arthurbrant/Desktop/ethiopia_cleaned'


all_matrix = pd.read_csv(os.path.join(INPUT, 'all_matrix.csv'))
biometry = list(all_matrix[~all_matrix['biometry'].isnull()]['biometry'])
df = pd.read_csv(os.path.join(INPUT, 'recommended_lenses.csv'))
df = df.set_index('biometry power')
df['count'] = df['NUM_LENSES_ROUNDED']


def cost_function(diffs, num_underpowered):
	#return sum([abs(x) for x in diffs])
	return np.count_nonzero(diffs) + num_underpowered*5


def increment_frange(x, y, jump):
  while x <= y:
    yield x
    x += jump

def decrement_frange(x, y, jump):
  while x >= y:
    yield x
    x += jump


def get_diffs(df, column_name, subset):
	diffs = []
	num_underpowered = 0
	num_fudge_changes = 0
	for iol in subset:
		orig_iol = iol
		if FUDGE:
			iol += (round(np.random.normal(0, 2, 1)[0] * 2) / 2)
		if orig_iol != iol:
			num_fudge_changes += 1

		found_iol = False
		for implanted_iol in increment_frange(float(iol), MAX_IOL, 0.5):
			if df.loc[(implanted_iol, column_name)] > 0:
				df.loc[(implanted_iol, column_name)] -= 1
				diffs.append(implanted_iol - float(orig_iol))
				found_iol = True
				break
		if not found_iol:
			for implanted_iol in decrement_frange(float(iol), MIN_IOL, -0.5):
				if df.loc[(implanted_iol, column_name)] > 0:
					df.loc[(implanted_iol, column_name)] -= 1
					diffs.append(float(implanted_iol) - orig_iol)
					break
		if implanted_iol < orig_iol:
			num_underpowered += 1
	return diffs, num_underpowered



for i in range(99999999):
	print '**************************************'
	print i
	start_time = time.time()
	random.shuffle(biometry)
	subset = biometry[:SURGERIES_IN_CAMP]
	diff, num_underpowered = get_diffs(df.copy(), 'count', subset)
	start_cost = cost_function(diff, num_underpowered)
	if start_cost == 0:
		print '##########################################'
		continue

	best_remove_cost = 999999999
	best_remove_powers = []
	best_add_cost = 999999999
	best_add_powers = []


	for power_remove in range(MIN_IOL*2, (MAX_IOL*2)+1):
		power_remove = power_remove / 2.0
		if df.loc[(power_remove, 'count')] == 0:
			continue
		df.loc[(power_remove, 'count')] -= 1
		diff, num_underpowered = get_diffs(df.copy(), 'count', subset)
		cost = cost_function(diff, num_underpowered)
		if cost < best_remove_cost:
			best_remove_cost = cost
			best_remove_powers = [power_remove]
		elif cost == best_remove_cost:
			best_remove_powers.append(power_remove)
		df.loc[(power_remove, 'count')] += 1

	for power_add in range(MIN_IOL*2, (MAX_IOL*2)+1):
		power_add = power_add / 2.0
		df.loc[(power_add, 'count')] += 1
		diff, num_underpowered = get_diffs(df.copy(), 'count', subset)
		cost = cost_function(diff, num_underpowered)
		if cost < best_add_cost:
			best_add_cost = cost
			best_add_powers = [power_add]
		elif cost == best_add_cost:
			best_add_powers.append(power_add)

		df.loc[(power_add, 'count')] -= 1

	if start_cost == best_remove_cost  and start_cost == best_add_cost:
		pass
	else:
		print best_remove_powers
		print best_add_powers
		best_remove_random_choice = random.choice(best_remove_powers)
		best_add_random_choice = random.choice(best_add_powers)
		df.loc[(best_remove_random_choice, 'count')] -= 1
		df.loc[(best_add_random_choice, 'count')] += 1

	diff, num_underpowered = get_diffs(df.copy(), 'count', subset)
	end_cost = cost_function(diff, num_underpowered)

	print 'iteration time: %s' % str(time.time() - start_time)
	print 'power remove: %s' % best_remove_random_choice
	print 'power add: %s' % best_add_random_choice
	print 'start cost: %s' % start_cost
	print 'end cost: %s' % end_cost
	print df[df['count'] != 0]