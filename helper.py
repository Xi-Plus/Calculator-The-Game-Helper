import argparse
import re
import copy


parser = argparse.ArgumentParser(description='Calculator The Game Helper')
parser.add_argument('start', type=int)
parser.add_argument('goal', type=int)
parser.add_argument('step', type=int)
parser.add_argument('buttons', type=str, nargs='+', help='Accept: +N, -N, *N, /N, N (Append), store, back, mirror, reverse, dropNN, shift>, shift<, N=>N, inv10, [+]N')

args = parser.parse_args()
start = args.start
goal = args.goal
step = args.step
buttons = args.buttons

actions = {}
for button in buttons:
	if button == 'store':
		actions['store'] = None
		actions['usestore'] = None
		continue

	if button in ['back', 'mirror', 'reverse', 'shift>', 'shift<', 'inv10']:
		actions[button] = None
		continue

	m = re.match(r'^\+(\d+)$', button)
	if m:
		actions[('add', m.group(1))] = int(m.group(1))
		continue

	m = re.match(r'^-(\d+)$', button)
	if m:
		actions[('sub', m.group(1))] = int(m.group(1))
		continue

	m = re.match(r'^\*(\d+)$', button)
	if m:
		actions[('mul', m.group(1))] = int(m.group(1))
		continue

	m = re.match(r'^/(\d+)$', button)
	if m:
		actions[('div', m.group(1))] = int(m.group(1))
		continue

	m = re.match(r'^(\d+)$', button)
	if m:
		actions[('append', int(m.group(1)))] = int(m.group(1))
		continue

	m = re.match(r'^drop(\d)(\d)$', button)
	if m:
		actions['drop'] = [int(m.group(1)), int(m.group(2))]
		continue

	m = re.match(r'^(\d+)=>(\d+)$', button)
	if m:
		actions[('replace', m.group(1), m.group(2))] = [m.group(1), m.group(2)]
		continue

	m = re.match(r'^\[\+](\d+)$', button)
	if m:
		actions[('buttonadd', m.group(1))] = int(m.group(1))
		continue

	exit('Unknown button: {}'.format(button))

def dfs(parm_ori):
	if parm_ori["step"] <= 0:
		return
	if len(str(parm_ori["value"])) > 8:
		return

	for action in parm_ori["actions"]:
		parm = copy.deepcopy(parm_ori)
		value = parm['value']
		actions = parm['actions']
		step = parm['step']
		log = parm['log']

		if type(action) is tuple:
			actionname = action[0]
		else:
			actionname = action

		if actionname == 'drop':
			continue

		if actionname == 'buttonadd':
			for act in actions:
				if type(actions[act]) is int and act != 'buttonadd':
					actions[act] += actions[action]
			step -= 1
			log.append('buttonadd {}'.format(actions[action]))

		elif actionname == 'store':
			if actions['usestore'] == value:
				continue
			actions['usestore'] = value
			log.append('store')

		elif actionname == 'usestore':
			if actions['usestore'] is None:
				continue
			value = str(value) + str(actions['usestore'])
			value = int(value)
			step -= 1
			log.append('usestore')

		elif actionname == 'back':
			value = str(value)
			value = value[:-1]
			if value == '' or value == '-':
				value = 0
			else:
				value = int(value)
			step -= 1
			log.append('back')

		elif actionname == 'mirror':
			value = str(value)
			value = value + value[::-1]
			value = int(value)
			step -= 1
			log.append('mirror')

		elif actionname == 'reverse':
			value = str(value)
			value = value[::-1]
			value = int(value)
			step -= 1
			log.append('reverse')

		elif actionname == 'shift>':
			value = str(value)
			value = value[-1] + value[:-1]
			value = int(value)
			step -= 1
			log.append('shift>')

		elif actionname == 'shift<':
			value = str(value)
			value = value[1:] + value[0]
			value = int(value)
			step -= 1
			log.append('shift<')

		elif actionname == 'inv10':
			value = str(value)
			value = list(value)
			newvalue = []
			for v in value:
				if v == '-':
					newvalue.append('-')
				elif v == '0':
					newvalue.append('0')
				else:
					newvalue.append(str(10-int(v)))
			value = "".join(newvalue)
			value = int(value)
			step -= 1
			log.append('inv10')

		elif actionname == 'add':
			value += actions[action]
			step -= 1
			log.append('+{}'.format(actions[action]))
			
		elif actionname == 'sub':
			value -= actions[action]
			step -= 1
			log.append('-{}'.format(actions[action]))
			
		elif actionname == 'mul':
			value *= actions[action]
			step -= 1
			log.append('*{}'.format(actions[action]))
			
		elif actionname == 'div':
			if value % actions[action] != 0:
				continue
			value = int(value / actions[action])
			step -= 1
			log.append('/{}'.format(actions[action]))

		elif actionname == 'append':
			value = value * 10 + actions[action]
			step -= 1
			log.append('append {}'.format(actions[action]))

		elif actionname == 'replace':
			value = str(value)
			value = value.replace(actions[action][0], actions[action][1])
			value = int(value)
			step -= 1
			log.append('replace {}=>{}'.format(actions[action][0], actions[action][1]))

		log.append(value)

		if 'drop' in actions:
			value = str(value)
			while len(value) >= actions['drop'][0]:
				temp = int(value[-actions['drop'][0]])
				value = value[:-actions['drop'][0]] + value[-actions['drop'][0]+1:]
				value = int(value)
				value += 10 ** (actions['drop'][1] - 1) * temp
				value = str(value)
				log.append('drop')
				log.append(value)
			value = int(value)

		# print("  "*(7-step), value, log)

		if value == goal:
			print(log)
			return
		elif step > 0:
			parm['value'] = value
			parm['actions'] = actions
			parm['step'] = step
			parm['log'] = log
			dfs(parm)
			pass

parm = {
	"value": start,
	"actions": actions,
	"step": step,
	"log": []
}
dfs(parm)
