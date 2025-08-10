#!/usr/bin/env python3

import os
import re
import math
import random
import multiprocessing
import copy
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
import traceback
from ast import literal_eval

TARGET_PATH = './src'
BEST_RESULT = 'best.txt'
LETTERS = None
BIGRAMS = None
TOP_BIGRAMS = None

EFFORT_GRID = [
	[4, 2, 2, 2, 10, 10, 2, 2, 2, 4],
	[1, 0, 0, 0, 6,   6, 0, 0, 0, 1],
	[3, 2, 2, 1, 10, 10, 1, 2, 2, 3],
]

FINGER_GRID = [
	[4, 3, 2, 1, 1, 5, 5, 6, 7, 8],
	[4, 3, 2, 1, 1, 5, 5, 6, 7, 8],
	[4, 3, 2, 1, 1, 5, 5, 6, 7, 8],
]

SCORE_RATES = {
	'effort': 1.0,
	'sfb': 0.3,
	'rollin': 0.1,
	'scissors': 0.5,
}

MAX_VALS = None
TWINS = set()
BEST_SCORE = 0

def analyze_target_single(full_path):
	letters = Counter()
	bigrams = Counter()
	pattern = re.compile('[a-z]+', re.IGNORECASE)
	#pattern = re.compile(r"[!\"#$%&'()*+,\-./:;<=>?@\[\\\]^_`{|}~]+")
	try:
		with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
			text = f.read()
			groups = pattern.findall(text)
			for g in groups:
				#word = g
				#word = [ch for ch in word]
				word = g.lower()
				word = [ch for ch in word if 'a' <= ch <= 'z']
				for ch in word:
					letters[ch] += 1
				for i in range(len(word)-1):
					if word[i] != word[i+1]:
						bigrams[word[i] + word[i+1]] += 1
	except (FileNotFoundError, PermissionError, IsADirectoryError) as e:
		print(f'Failed: {full_path} — {e}')
	return letters, bigrams

def analyze_target():
	global LETTERS, BIGRAMS, TOP_BIGRAMS

	extensions = [
		'.c', '.h',
		'.cpp', '.hpp',
		'.cc', '.hh',
		'.s', '.S',
		'.cs',
		'.java',
		'.py',
		'.js', '.ts',
		'.go',
		'.rs',
		'.php',
		'.swift',
		'.kt', '.kts',
		'.rb',
		'.m', '.mm',
		'.sh', '.bash', '.zsh',
		'.pl', '.pm',
		'.lua',
		'.md'
	]
	files = []
	for root, dirs, fs in os.walk(TARGET_PATH):
		for file in fs:
			if file.endswith(tuple(extensions)):
				files.append(os.path.join(root, file))
	letters = Counter()
	bigrams = Counter()
	with ProcessPoolExecutor(max_workers=multiprocessing.cpu_count()-1) as executor:
		for file_letters, file_bigrams in executor.map(analyze_target_single, files):
			letters += file_letters
			bigrams += file_bigrams
	LETTERS = letters
	BIGRAMS = bigrams

	total = sum(BIGRAMS.values())
	target = total * 0.9
	acc = 0
	TOP_BIGRAMS = Counter()
	for pair, count in BIGRAMS.most_common():
		if acc >= target:
			break
		TOP_BIGRAMS[pair] = count
		acc += count

	with open("analyze_result.tsv", "w", encoding="utf-8") as f:
		f.write("letter\tfrequency\n")
		for ch, count in LETTERS.most_common():
			f.write(f"{ch}\t{count}\n")

		f.write("\nbigram\tfrequency\n")
		for bg, count in TOP_BIGRAMS.most_common():
			f.write(f"{bg}\t{count}\n")

def make_initial_layout():
	grid = [] 
	coords = []
	for r in range(3):
		for c in range(10):
			coords.append((EFFORT_GRID[r][c], r, c))
	coords.sort()
	letters_sorted = [x[0] for x in LETTERS.most_common()]
	layout = [[' ' for _ in range(10)] for _ in range(3)]
	for i, (_, r, c) in enumerate(coords):
		if i < len(letters_sorted):
			layout[r][c] = letters_sorted[i]
	return layout

def print_layout(layout):
	for row in layout:
		print(row)
	print()

def calc_scores(layout):
	effort = 0
	sfb = 0
	rollin = 0
	scissors = 0
	pos = {}

	for r in range(3):
		for c in range(10):
			ch = layout[r][c]
			if ch != ' ':
				pos[ch] = (r, c)
				effort += LETTERS[ch] * EFFORT_GRID[r][c]

	for pair, count in TOP_BIGRAMS.items():
		a, b = pair[0], pair[1]
		if a not in pos or b not in pos:
			continue
		r1, c1 = pos[a]
		r2, c2 = pos[b]
		f1 = FINGER_GRID[r1][c1]
		f2 = FINGER_GRID[r2][c2]
		if (1 <= f1 <= 4 and 1 <= f2 <= 4) or (5 <= f1 <= 8 and 5 <= f2 <= 8):
			if f1 == f2:
				sfb += count
			elif abs(f1 - f2) == 1:
				if f2 < f1 and abs(r1 - r2) <= 1:
					rollin += count
				elif abs(r1 - r2) == 2:
					if not (
						(f1 == 2 and f2 == 1 and r1 == 0 and r2 == 2) or
						(f1 == 6 and f2 == 5 and r1 == 0 and r2 == 2)
					):
						scissors += count

	return (effort, sfb, rollin, scissors)

def calc_total_score(scores, weights=SCORE_RATES):
	effort, sfb, rollin, scissors = scores
	effort_norm = effort / MAX_VALS['effort'] if MAX_VALS['effort'] != 0 else 0
	sfb_norm = sfb / MAX_VALS['sfb'] if MAX_VALS['sfb'] != 0 else 0
	rollin_norm = rollin / MAX_VALS['rollin'] if MAX_VALS['rollin'] != 0 else 0
	scissors_norm = scissors / MAX_VALS['scissors'] if MAX_VALS['scissors'] != 0 else 0

	return (
		(1 - effort_norm) * weights['effort'] +
		(1 - sfb_norm) * weights['sfb'] +
		rollin_norm * weights['rollin'] +
		(1 - scissors_norm) * weights['scissors']
	)

def sort_layouts(layouts, weights=SCORE_RATES):
	global MAX_VALS, TWINS, BEST_SCORE
	scores = [calc_scores(l) for l in layouts]
	if MAX_VALS == None:
		MAX_VALS = {
			'effort': max(x[0] for x in scores),
			'sfb': max(x[1] for x in scores),
			'rollin': max(x[2] for x in scores),
			'scissors': max(x[3] for x in scores),
		}
	total_scores = [calc_total_score(s, weights) for s in scores]
	pairs = list(zip(layouts, total_scores))
	pairs_sorted = sorted(pairs, key=lambda x: x[1], reverse=True)

	if weights == SCORE_RATES:
		if pairs_sorted[0][1] > BEST_SCORE:
			BEST_SCORE = pairs_sorted[0][1]
			TWINS = {ltot(pairs_sorted[0][0])}
		else:
			for layout, score in pairs_sorted:
				if score == BEST_SCORE:
					TWINS.add(ltot(layout))
				else:
					break

	return pairs_sorted

def ltot(l):
	return tuple(tuple(r) for r in l)

def make_random(base_layout):
	layout = [row[:] for row in base_layout]
	positions = [(i, j) for i in range(len(layout)) for j in range(len(layout[0])) if layout[i][j] != ' ']
	keys = [layout[i][j] for i, j in positions]
	random.shuffle(keys)
	for idx, (i, j) in enumerate(positions):
		layout[i][j] = keys[idx]
	return layout
	
def make_population(base_layout, n):
	pop = set()
	pop.add(ltot(base_layout))
	while len(pop) < n:
		key = ltot(make_random(base_layout))
		if key not in pop:
			pop.add(key)
	return [[list(row) for row in l] for l in pop]

def crossover(parents, blank=' '):
	def flatten(layout):
		return [item for row in layout for item in row]
	def unflatten(flat, rows=3, cols=10):
		return [flat[i*cols:(i+1)*cols] for i in range(rows)]

	parent1 = flatten(parents[0])
	parent2 = flatten(parents[1])
	length = len(parent1)
	child = [None] * length

	for i in range(length):
		if parent1[i] == parent2[i]:
			child[i] = parent1[i]

	used = set([x for x in child if x is not None and x != blank])
	all_keys = [x for x in parent1 if x != blank]
	remain_keys = [k for k in all_keys if k not in used]

	random.shuffle(remain_keys)

	pos = 0
	for i in range(length):
		if child[i] is None:
			child[i] = remain_keys[pos]
			pos += 1

	return unflatten(child)

def optimize(base_layout, population_len=100, max_unimproved=100):
	population = make_population(base_layout, population_len)
	parents_len = int(population_len * 0.05)
	elites_len = int(population_len * 0.02)
	random_len = int(population_len * 0.5)

	unimproved = 0
	gen = 0
	prev = BEST_SCORE
	while True:
		gen += 1
		sorted_population = sort_layouts(population)

		if prev == BEST_SCORE:
			unimproved += 1
			if unimproved == max_unimproved:
				break
		else:
			unimproved = 0
			prev = BEST_SCORE

		progress = min(unimproved/max_unimproved, 1.0)
		sa_prob = 0.2 + 0.2 * progress
		effort_prob = 0.2 + sa_prob
		swap_prob = 0.3 - 0.1 * progress + effort_prob

		best_scores = calc_scores(sorted_population[0][0])
		print(f'[Gen{gen}] unimproved({unimproved}) twins({len(TWINS)})')
		print('\t'.join(f'{num:,}' for num in best_scores))
		print(f'{sorted_population[0][1]}')
		print_layout(sorted_population[0][0])

		parents = [x[0] for x in sorted_population[:parents_len]]
		for i in range(elites_len):
			parents[i] = optimize_sa(parents[i])
		elites = sort_layouts(parents[:elites_len])

		new_population = set()
		for l in elites:
			new_population.add(ltot(l[0]))
		for _ in range(random_len):
			new_population.add(ltot(make_random(elites[0][0])))

		attempts = 0
		max_attempts = 10000
		while len(new_population) < population_len and attempts < max_attempts:
			attempts += 1
			child = crossover([
				parents[random.randint(0,parents_len-1)],
				parents[random.randint(0,parents_len-1)]
			])
			r = random.random()
			if r < sa_prob:
				child = optimize_sa(child)
			elif r < effort_prob:
				child = optimize_effort(child)
			elif r < swap_prob:
				child = swap_multiple(child, 0, 2)
			new_population.add(ltot(child))

		population = [[list(r) for r in l] for l in new_population]
		if(attempts == max_attempts):
			print(f'max out len:{len(new_population)}')
			while len(population) < population_len:
				population.append(make_random(elites[0][0]))

	return fine_tune_effort(optimize_effort(optimize_sa(sort_layouts(population)[0][0])))

def swap_multiple(layout, temperature, fix=0):
	n = None
	if fix == 0:
		if temperature > 50:
			n = random.choices([4, 5, 6], weights=[0.5, 0.3, 0.2])[0]
		elif temperature > 10:
			n = random.choices([3, 4], weights=[0.7, 0.3])[0]
		else:
			n = random.choices([2, 3], weights=[0.8, 0.2])[0]
	else:
		n = fix

	coords = set()
	while len(coords) < n:
		r, c = random.randint(0, 2), random.randint(0, 9)
		if layout[r][c] != ' ':
			coords.add((r, c))
	coords = list(coords)

	new_layout = [row[:] for row in layout]

	shuffled = coords[:]
	random.shuffle(shuffled)

	for i in range(n):
		r1, c1 = coords[i]
		r2, c2 = shuffled[i]
		new_layout[r1][c1], new_layout[r2][c2] = new_layout[r2][c2], new_layout[r1][c1]

	return new_layout

def optimize_sa(base_layout, max_iter=10000, initial_temp=100.0, cooling_rate=0.9995):
	best_layout = [row[:] for row in base_layout]
	current_layout = [row[:] for row in base_layout]
	temperature = initial_temp

	for i in range(max_iter):
		weights = {
			'effort': random.uniform(0.5, 1.5),
			'sfb': random.uniform(0.1, 0.5),
			'rollin': random.uniform(0.05, 0.3),
			'scissors': random.uniform(0.2, 0.7)
		}
		new_layout = swap_multiple(current_layout, temperature)
		result = sort_layouts([new_layout, base_layout], weights)

		diff = result[0][1] - result[1][1]
		try:
			prob = math.exp(diff / temperature)
		except (OverflowError, ZeroDivisionError, TypeError):
			prob = 1.0

		if result[0][0] == new_layout or prob > random.random():
			current_layout = new_layout
			if result[0][0] == new_layout:
				best_layout = new_layout
				temperature *= 1.1

		temperature *= cooling_rate
		if temperature < 1e-3:
			print(i)
			break

	return optimize_bigrams(best_layout)

def optimize_effort_single(start_layout, order='effort_asc'):
	best_layout = [row[:] for row in start_layout]
	effort_levels = list({val for row in EFFORT_GRID for val in row if val < 10})

	if order == 'effort_asc':
		effort_levels.sort()
	elif order == 'effort_desc':
		effort_levels.sort(reverse=True)
	else:
		effort_counts = {val: sum(1 for r in range(3) for c in range(10) if EFFORT_GRID[r][c] == val) for val in effort_levels}
		if order == 'count_asc':
			effort_levels.sort(key=lambda x: effort_counts[x])
		elif order == 'count_desc':
			effort_levels.sort(key=lambda x: -effort_counts[x])

	for effort_level in effort_levels:
		group_coords = [(r, c) for r in range(3) for c in range(10) if EFFORT_GRID[r][c] == effort_level]

		for i in range(len(group_coords)):
			r1, c1 = group_coords[i]
			for j in range(i+1, len(group_coords)):
				r2, c2 = group_coords[j]
				if best_layout[r1][c1] == ' ' and best_layout[r2][c2] == ' ':
					continue
				new_layout = [row[:] for row in best_layout]
				new_layout[r1][c1], new_layout[r2][c2] = new_layout[r2][c2], new_layout[r1][c1]
				best_layout = sort_layouts([new_layout, best_layout])[0][0]

	return best_layout

def optimize_effort(start_layout):
	orders = ['effort_asc', 'effort_desc', 'count_asc', 'count_desc']
	with multiprocessing.Pool(processes=4, initializer=init_globals,
													 initargs=(LETTERS, EFFORT_GRID, FINGER_GRID, TOP_BIGRAMS)) as pool:
		results = pool.starmap(optimize_effort_single,
												 [(start_layout, order) for order in orders])
	sorted_layouts = sort_layouts(results)
	return sorted_layouts[0][0]

def init_globals(letters_, effort_grid_, finger_grid_, top_bigrams_):
	global LETTERS, EFFORT_GRID, FINGER_GRID, TOP_BIGRAMS
	LETTERS = letters_
	EFFORT_GRID = effort_grid_
	FINGER_GRID = finger_grid_
	TOP_BIGRAMS = top_bigrams_

def print_row_usage(layout):
	usage = [0]*10
	for r in range(3):
		for c in range(10):
			ch = layout[r][c]
			usage[c] += LETTERS[ch]
	total = sum(usage)

	for i, v in enumerate(usage):
		percent = (v/total)*100 if total else 0
		print(f'Row {i}: {percent:.2f}%')

def fine_tune_effort(layout):
	new_layout = [row[:] for row in layout]
	positions = [(r,c) for r in range(3) for c in range(10) if layout[r][c] != ' ']
	positions.sort(key=lambda pos: LETTERS.get(layout[pos[0]][pos[1]],0), reverse=True)
	for (r,c) in positions:
		best = (r,c)
		for dr in (-1,0,1):
			for dc in (-1,0,1):
				nr,nc=r+dr,c+dc
				if 0<=nr<3 and 0<=nc<10 and layout[nr][nc]!=' ':
					if EFFORT_GRID[nr][nc] < EFFORT_GRID[best[0]][best[1]]:
						best = (nr,nc)
		new_layout[r][c], new_layout[best[0]][best[1]] = new_layout[best[0]][best[1]], new_layout[r][c]
	return sort_layouts([new_layout, layout])[0][0]

def optimize_bigrams(layout, top_n=50, max_iter=500):
	new_layout = [row[:] for row in layout]
	common_pairs = sorted(TOP_BIGRAMS.items(), key=lambda x: x[1], reverse=True)[:top_n]
	def get_pos(ch):
		for r in range(3):
			for c in range(10):
				if new_layout[r][c] == ch:
					return (r, c)
		return None
	for _ in range(max_iter):
		improved = False
		for pair, freq in common_pairs:
			a, b = pair[0], pair[1]
			pos_a, pos_b = get_pos(a), get_pos(b)
			if not pos_a or not pos_b:
				continue
			dist = abs(pos_a[0] - pos_b[0]) + abs(pos_a[1] - pos_b[1])
			if dist > 2:
				best_swap = None
				for r in range(3):
					for c in range(10):
						if new_layout[r][c] != ' ':
							new_dist = abs(pos_a[0]-r) + abs(pos_a[1]-c)
							if new_dist < dist:
								best_swap = (r, c)
								dist = new_dist
				if best_swap:
					rb, cb = pos_b
					rs, cs = best_swap
					new_layout[rb][cb], new_layout[rs][cs] = new_layout[rs][cs], new_layout[rb][cb]
					improved = True
		if not improved:
			break
	return sort_layouts([new_layout, layout])[0][0]

def make_initial_set():
	init_layout = make_initial_layout()
	layouts = make_population(init_layout, 100)
	layouts.append(init_layout)

	current = []
	try:
		with open(BEST_RESULT, 'r') as f:
			for line in f:
				line = line.strip()
				if line.startswith('(') and line.endswith(')'):
					row = literal_eval(line)
					current.append(list(row))
					if len(current) == 3:
						layouts.append(current)
						current = []
	except FileNotFoundError:
		pass

	return sort_layouts(layouts)[0][0]

def print_twins():
	for l in [list(r) for r in TWINS]:
		s = calc_scores(l)
		print('\t'.join(f'{num:,}' for num in s))
		print_layout(l)
		print_row_usage(l)

def save_twins():
	with open(BEST_RESULT, 'a') as f:
		for l in [list(r) for r in TWINS]:
			s = calc_scores(l)
			print('\t'.join(f'{num:,}' for num in s), file=f)
			for lr in l:
				print(lr, file=f)
			print('', file=f)
		print('==================================================', file=f)

if __name__ == '__main__':
	analyze_target()

	l = make_initial_set()
	save_twins()
	print('[INIT]')
	print_layout(l)
	print_twins()

	while True:
		l = optimize(l)
		save_twins()
		print_twins()
