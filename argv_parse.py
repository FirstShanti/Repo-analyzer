from man import man

def get_params(argv):
	argv = argv[1:]
	if len(argv) > 7:
		argv = argv[:7:]
	params = {'url': '', '-s': None, '-e': None, '-b': 'master'}
	
	if argv:
		params['url'] = argv[0]
		for i in argv[1:]:
			if i in params:
				if i in ['-s','-e'] and argv[argv.index(i) + 1] in ['-s','-e', '-b']:
					print(f'\n**Invalid input arguments**')
					print(man)
					exit()
				params[i] = argv[argv.index(i)+1]
			elif i.startswith('-') and i not in params:
				print(f'\nOption "{i}" not found')
				exit()
		return params
	else:
		return
